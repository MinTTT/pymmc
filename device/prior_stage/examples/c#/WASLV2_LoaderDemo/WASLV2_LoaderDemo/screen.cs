using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.IO;
using WASLV2_LoaderDemo.Properties;

namespace WASLV2_LoaderDemo
{
    public partial class Form1 : Form
    {
        enum ScreenState
        {
            Idle,
            Init,

            EjectHotels,
            LoadTray,
            LoadHotels,
            SetCalibration,
            EjectHotelsAgain,
            UnloadTray,
            End
        }

        ScreenState state = ScreenState.Idle;

       

        private void ShowError(int err)
        {
            priorSDK.Cmd(sessionID, "waslv2.getlasterror", ref userRx);
            MessageBox.Show("SDK error (" + err.ToString() + " getlasterror =  " + userRx);
        }

        private int StageBusy()
        {
            if ((err = priorSDK.Cmd(sessionID, "controller.stage.busy.get", ref userRx)) != Prior.PRIOR_OK)
            {
                return 0;
            }
            else
                return Convert.ToInt32(userRx);
        }

        private void WaitUntilStageIdle()
        {

            // do NOT use in backround thread!!!
            do
            {
                Application.DoEvents();
                Thread.Sleep(100);
            }
            while (StageBusy() != 0);
        }



        private int InitRobot()
        {
            /* start the robot initialisation */
            if ((err = priorSDK.Cmd(sessionID, "waslv2.initialise", ref userRx)) != Prior.PRIOR_OK)
            {
                return err;
            }


            /* wait until initialisation complete by checking status
             * minimum initialistaion will retract the STM allowing recovery from a shutdown that 
             * potentially may have left a tray or the STM partly in an apartment
             * Internally the waslv2.initialise also checks the controller.flag status to 
             * determine warm or cold start conditions
             */
            do
            {
                PollStatus();
                Application.DoEvents();
                Thread.Sleep(100);
            }
            while (WASLV2StateEquals(Prior.WASLV2_STATE_INITIALISE));

            return 0;
        }

        private int InitStage()
        {
            int flags;

            /* NOTE: stage calibration is based on the configuration of the controller used by this program. ie step size, travel direction etc
             * the stage load/unload positions stored are essential for correct operation. The stage travel is setup to be consistent with the DESI 
             * system previously supplied. If the users application does not follow this exact initialisation sequence or modifies the stage geometry 
             * then loading/unloading will not be correct.
             * If the user wants a different configuration then they are free to modifiy this calibration program accordingly. Consult with Prior 
             * Tech support team on how to do this.
             */

            /* check warm start flags */
            if ((err = priorSDK.Cmd(sessionID, "controller.flag.get", ref userRx)) != Prior.PRIOR_OK)
            {
                return err;
            }

            /* warm start flags returned in hex string format */
            flags = Convert.ToInt32(userRx, 16);

            if (flags == 0)
            {
                /* do stage initialisation, independent of stage orientation as that already been setup 
                 * goto limits first
                 */

                if ((err = priorSDK.Cmd(sessionID, "controller.stage.move-at-velocity " +
                                                (-10000).ToString() + " " + (-10000).ToString(), ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                WaitUntilStageIdle();


                /* set temp zero pos */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.position.set 0 0", ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                /* move off slightly */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.goto-position 1000 1000", ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                WaitUntilStageIdle();

                /* slow into limits */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.move-at-velocity " +
                                               (-500).ToString() + " " + (-500).ToString(), ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                WaitUntilStageIdle();

                /* set temp zero pos */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.position.set 0 0", ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                /* move off slightly */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.goto-position 1000 1000", ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }

                WaitUntilStageIdle();

                /* set real zero co-ordinates to avoid having to hit switch again */
                if ((err = priorSDK.Cmd(sessionID, "controller.stage.position.set 0 0", ref userRx)) != Prior.PRIOR_OK)
                {
                    return err;
                }
            }

            flags |= 0x1000;

            if ((err = priorSDK.Cmd(sessionID, "controller.flag.set " + flags.ToString("X"), ref userRx)) != Prior.PRIOR_OK)
            {
                return err;
            }

            return Prior.PRIOR_OK;
        }

        private void SetScreenByState()
        {
            if (StatusBitIsSet(Prior.WASLV2_LOADER_NOTCONNECTED))
            {
                /* show disconnected screen */
                this.Width = grpSetup.Left + 10;

                grpAction.Enabled = false;

                connectToolStripMenuItem.Text = "Connect";

                editINIToolStripMenuItem.Enabled = false;
                optionsToolStripMenuItem.Enabled = false;

                grpHotel1.Enabled = false;

                lblNotConnected.Text = "NOT CONNECTED";

                UpdateLastError();
            }
            else
            {
                lblNotConnected.Text = "";
                connectToolStripMenuItem.Text = "DisConnect";
                editINIToolStripMenuItem.Enabled = true;

                if (StatusBitIsSet(Prior.WASLV2_LOADER_NOTINITIALISED))
                {
                    /* show init screen */
                    this.Width = btndummy.Left + 10;
                    btnAction.Text = "Initialise";
                    state = ScreenState.Init;
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add("1. Click 'Initialise' to auto initialise system.");
                    lstHelp.Items.Add("");
                    lstHelp.Items.Add("If the loader has been powered down since last connection then a ");
                    lstHelp.Items.Add("full initialisation of the loader and the stage will occur.");
                    lstHelp.Items.Add("");
                    lstHelp.Items.Add("If loader has not been powered down then correct positioning is maintained");
                    lstHelp.Items.Add("and only the STM axis is moved to safe position.");
                    grpAction.Enabled = false;
                }
                else
                if (StatusBitIsSet(Prior.WASLV2_LOADER_NOTSETUP))
                {
                    connectToolStripMenuItem.Text = "DisConnect";

                    /* show setup screen screen */
                    this.Width = btndummy.Left + 10;
                    btnAction.Text = "Eject Hotels";
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add(" ");
                    lstHelp.Items.Add("'Eject Hotels' to start calibration.");
                    grpAction.Enabled = false;

                    state = ScreenState.EjectHotels;
                }
                else
                {
                    /* show normal run screen */
                    this.Width = grpSetup.Left + 10;

                    optionsToolStripMenuItem.Enabled = true;

                    grpAction.Enabled = true;
                }
            }

        }

        private void btnAction_Click(object sender, EventArgs e)
        {
            switch (state)
            {
                case ScreenState.Idle:
                {
                    break;
                }

                case ScreenState.Init:
                {
                    btnStop.Enabled = true;
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add("Loader initialising - please wait");
                    btnAction.Enabled = false;

                    if ((err = InitRobot()) != Prior.PRIOR_OK)
                    {
                        MessageBox.Show("There was a problem initialising the loader (" + err.ToString() + ")", "Error",
                                                           MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    };

                    if ((err = InitStage()) != Prior.PRIOR_OK)
                    {
                        MessageBox.Show("There was a problem initialising the stage (" + err.ToString() + ")", "Error",
                                                           MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    };

                    /* check whether setup is required */
                    if (StatusBitIsSet(Prior.WASLV2_LOADER_NOTSETUP))
                    {
                        string serial = "0";
                        if (InputBox.Show("serial number", "Enter serial number:", ref serial) != DialogResult.OK)
                            serial = "0";

                        priorSDK.Cmd(sessionID, "waslv2.serialnumber.set " + serial, ref userRx);
                    }

                    btnAction.Enabled = true;
                    SetScreenByState();

                    break;
                }

                case ScreenState.EjectHotels:
                {
                    btnAction.Enabled = false;
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add("Waiting for hotel ejection to complete...");
                    lstHelp.Refresh();

                    if ((err = priorSDK.Cmd(sessionID, "waslv2.unloadhotels", ref userRx)) == Prior.PRIOR_OK)
                    {
                        /* wait until unload complete by checking status */
                        do
                        {
                            PollStatus();
                            Application.DoEvents();
                            Thread.Sleep(200);
                        }
                        while (WASLV2StateNotEquals(Prior.WASLV2_STATE_IDLE));
                    }
                    else
                    {
                        MessageBox.Show("Cannot eject hotel (" + err.ToString() + ")", "Error",
                                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }

                    lstHelp.Items.Add("Waiting for STM positioning to complete...");
                    lstHelp.Refresh();
                    /* move STM out to 200mm, so tray can be fitted by user, 
                    */
                    AxisMoveTo(Prior.WASLV2_STM, mmToCounts(Prior.WASLV2_STM, 200));
                    WaitAxisNotBusy(Prior.WASLV2_STM);

                    btnAction.Text = "Load Tray";
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add(" ");
                    lstHelp.Items.Add("Fit tray to STM and then click 'Load Tray' to continue");
                    btnAction.Enabled = true;

                    state = ScreenState.LoadTray;

                    break;
                }

                case ScreenState.LoadTray:
                {
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add("Wait for STM and stage to re-position...");
                    lstHelp.Refresh();
                    btnAction.Enabled = false;

                    /* move STM back to 80mm,  */
                    AxisMoveTo(Prior.WASLV2_STM, mmToCounts(Prior.WASLV2_STM, 80));
                    WaitAxisNotBusy(Prior.WASLV2_STM);

                    /* TODO: move stage to somewhere nearby the correct loading position */
                    if ((err = priorSDK.Cmd(sessionID, "controller.stage.goto-position 105000 75800", ref userRx)) == Prior.PRIOR_OK)
                    {
                        WaitUntilStageIdle();

                        btnAction.Text = "Load Hotels";
                        lstHelp.Items.Clear();
                        lstHelp.Items.Add(" ");
                        lstHelp.Items.Add("Fit hotel 1 and click 'Load Hotels' to continue");

                        state = ScreenState.LoadHotels;
                    }
                    else
                        MessageBox.Show("Error moving stage (" + err.ToString() + ")", "Error",
                                                         MessageBoxButtons.OK, MessageBoxIcon.Error);

                    btnAction.Enabled = true;
                    break;
                }

                case ScreenState.LoadHotels:
                {
                    lstHelp.Items.Clear();
                    lstHelp.Items.Add("Waiting for hotel loading to complete...");
                    lstHelp.Refresh();

                    if ((err = priorSDK.Cmd(sessionID, "waslv2.loadhotels", ref userRx)) == Prior.PRIOR_OK)
                    {
                        /* wait until unload complete by checking status */
                        do
                        {
                            PollStatus();
                            Application.DoEvents();
                            Thread.Sleep(200);
                        }
                        while (WASLV2StateNotEquals(Prior.WASLV2_STATE_IDLE));
                    }
                    else
                    {
                        MessageBox.Show("Cannot load hotel (" + err.ToString() + ")", "Error",
                                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }

                    /* move HLM by 30mm, gets us pretty much to the right place */
                    AxisJogBy(Prior.WASLV2_HLM, 30.0);
                    WaitAxisNotBusy(Prior.WASLV2_HLM);

                    btnAction.Enabled = true;
                    chkHLM.Checked = true;
                    chkSTM.Checked = false;
                    lstHelp.Items.Clear();
                    btnAction.Text = "Store Calibration";

                    lstHelp.Items.Add("Using joystick, drive stage to align tray with hotel 1 apartment 20.");
                    lstHelp.Items.Add("Ensure stage activates the stage clamp.");

                    lstHelp.Items.Add("Insert tray with STM jog so that LHS marker is aligned with hotel apartment entrance");
                    lstHelp.Items.Add("Always approach this position from the insert direction.");
                    lstHelp.Items.Add("if you insert too far then pull out and re-insert");
                    lstHelp.Items.Add("ENSURE tray is flat on stage and apartment floor by using HLM jog.");
                    lstHelp.Items.Add("ENSURE STM arm is central in tray. Move stage Y to centralise.");

                    lstHelp.Items.Add("Refer to detailed instuctions in WASL Production Procedure doc.");
                    lstHelp.Items.Add("");
                    lstHelp.Items.Add("Press 'Store Calibration' to store setup when happy with alignment.");

                    state = ScreenState.SetCalibration;
                    break;
                }

                case ScreenState.SetCalibration:
                {
                    if (MessageBox.Show("Confirm store calibration position", "Confirm",
                                    MessageBoxButtons.YesNo, MessageBoxIcon.Question) == System.Windows.Forms.DialogResult.Yes)
                    {
                        /* if user positioned correctly to marker then there is 20mm to go to back of the hotel */
                        AxisJogBy(Prior.WASLV2_STM, 20.0);
                        WaitAxisNotBusy(Prior.WASLV2_STM);

                        if ((err = priorSDK.Cmd(sessionID, "waslv2.calibration.set", ref userRx)) == Prior.PRIOR_OK)
                        {
                            /* retract Z slightly to unstick paddle from clamp */
                            AxisJogBy(Prior.WASLV2_STM, -2.0);
                            WaitAxisNotBusy(Prior.WASLV2_STM);

                            /* move HLM up 4mm slightly  */
                            AxisJogBy(Prior.WASLV2_HLM, 4.0);
                            WaitAxisNotBusy(Prior.WASLV2_HLM);

                            /* back off by 30mm */
                            AxisJogBy(Prior.WASLV2_STM, -30.0);
                            WaitAxisNotBusy(Prior.WASLV2_STM);

                            btnAction.Text = "Eject";
                            lstHelp.Items.Clear();
                            lstHelp.Items.Add("Click 'Eject' to eject hotel and continue");

                            state = ScreenState.EjectHotelsAgain;
                        }
                        else
                        {
                            MessageBox.Show("Error setting calibration data (" + err.ToString() + ")", "Error",
                                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                        }
                    }

                    break;
                }

                case ScreenState.EjectHotelsAgain:
                {
                    if ((err = priorSDK.Cmd(sessionID, "waslv2.unloadhotels", ref userRx)) == Prior.PRIOR_OK)
                    {
                        btnAction.Enabled = false;
                        lstHelp.Items.Clear();
                        lstHelp.Items.Add("Waiting for hotel ejection...");
                        lstHelp.Refresh();

                        /* wait until unload complete by checking status  */
                        do
                        {
                            PollStatus();
                            Application.DoEvents();
                            Thread.Sleep(200);
                        }
                        while (WASLV2StateNotEquals(Prior.WASLV2_STATE_IDLE));

                        btnAction.Enabled = true;
                        btnAction.Text = "Save and exit";

                        lstHelp.Items.Clear();
                        lstHelp.Items.Add("Save Setup to stage eeprom and exit");
                        lstHelp.Items.Add("stage may twitch if stepper motor or drift if linear");
                        lstHelp.Items.Add("");
                        lstHelp.Items.Add("Click 'Save and Exit' to leave calibration. This will take several seconds.");

                        state = ScreenState.End;
                    }
                    else
                        MessageBox.Show("Cannot eject hotels (" + err.ToString() + ")", "Error",
                                    MessageBoxButtons.OK, MessageBoxIcon.Error);

                    break;
                }

                case ScreenState.End:
                {
                    lstHelp.Items.Add("Saving please wait...");
                    Application.DoEvents();

                    if ((err = priorSDK.Cmd(sessionID, "waslv2.calibration.save", ref userRx)) == Prior.PRIOR_OK)
                    {
                        btnAction.Enabled = true;
                        state = ScreenState.Idle;
                        PollStatus();
                        SetScreenByState();
                    }
                    else
                    {
                        MessageBox.Show("Error saving calibration (" + err.ToString() + ")", "Error",
                                    MessageBoxButtons.OK, MessageBoxIcon.Error);

                        lstHelp.Items.Add("Error saving calibration (" + err.ToString() + ")");
                    }

                    break;
                }
            }
        }



        private int MoveStageToLoadPosition()
        {
            priorSDK.Cmd(sessionID, "waslv2.calibration.stagexy.get", ref userRx);

            userRx = userRx.Replace(',', ' ');
            priorSDK.Cmd(sessionID, "controller.stage.goto-position " + userRx, ref userRx);
            WaitUntilStageIdle();
              
            return 0;
        }
        
        private void AxisMoveTo(int axis, int pos)
        {
            priorSDK.Cmd(sessionID, "waslv2.axis.goto " + axis.ToString() + " " + pos.ToString(), ref userRx);
        }

        private int WaitAxisNotBusy(int axis)
        {
            int busy = 0;

            do
            {
                Application.DoEvents();
                Thread.Sleep(100);

                priorSDK.Cmd(sessionID, "waslv2.axis.busy.get " + axis.ToString(), ref userRx);
                busy = Convert.ToInt32(userRx);
            }
            while (busy != 0);

            return busy;
        }
    }
}
