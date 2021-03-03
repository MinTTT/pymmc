/**
 * @file    WASLV2_LoaderDemo
 * @author	Rob Wicker  (rwicker@prior.com)
 * @date    4/12/2020
 * @brief   This project contains an WASLV2_LoaderDemo utility
 * @copyright   Copyright (c) 2020- Prior Scientific Instruments Ltd. All rights reserved
 *
 *
 * The project is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
 * 
 * HISTORY
 * 
 * 1.1      4/12/20      initial version - copied from SL160 1.3 and modified accordingly
 */

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using System.Diagnostics;

using System.IO;
using WASLV2_LoaderDemo.Properties;

namespace WASLV2_LoaderDemo
{
    public partial class Form1 : Form
    {
        StringBuilder dllVersion = new StringBuilder();

        int maxApartments = 20;
        int maxHotels = 1;

        int err;
        int sessionID = -1;

        string userTx = "";
        string userRx = "";

        /* background thread that handles the status updates from the loader */
        private BackgroundWorker RobotStatusHandling = new BackgroundWorker();

        Stopwatch myStopWatch = new Stopwatch();

        /* create a c# wrapper class for the Prior DLL */
        SDK priorSDK = new SDK();

        /* WASLV2 has one hotel with 20 apartments, each apartment has an associated tray with 4 slides */
        Button[] hotel1;

        public Form1()
        {
            InitializeComponent();
        }


        private void Form1_Load(object sender, EventArgs e)
        {
            /* check for DLL */
            try
            {
                if ((err = priorSDK.GetVersion(dllVersion)) != Prior.PRIOR_OK)
                {
                    MessageBox.Show("Error getting Prior SDK version (" + err.ToString() + ")");
                    this.Close();
                    return;
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error accessing PriorScientificSDK.dll (" + ex.Message + ")");
                this.Close();
                return;
            }

            /* initiliase DLL, *must* be done first */
            if ((err = priorSDK.Initialise()) != Prior.PRIOR_OK)
            {
                MessageBox.Show("Error (" + err.ToString() + ") Initialising SDK " + dllVersion);
                this.Close();
                return;
            }

            lblstate.Text = "         ";
            lbltime.Text = "    ";
            lbllasterror.Text = "          ";

            this.Width = grpSetup.Left + 10;


            /* use buttons as apartment visuals */
            hotel1 = new Button[maxApartments];


            /* create the hotel apartments 
            */
            createApartments(grpHotel1, hotel1);

            grpHotel1.Enabled = false;

            /* create a session in the DLL, this gives us one controller and an WASLV2 loader. Multiple connections allow control of multiple
            * stage/loaders but is outside the brief for this demo
            */
            if ((sessionID = priorSDK.OpenSession()) != Prior.PRIOR_OK)
            {
                MessageBox.Show("Error (" + sessionID.ToString() + ") Creating session in SDK " + dllVersion);
                this.Close();
                return;
            }

            RobotStatusHandling.WorkerReportsProgress = true;
            RobotStatusHandling.WorkerSupportsCancellation = true;
            RobotStatusHandling.ProgressChanged += new ProgressChangedEventHandler(RobotStatusHandling_ProgressChanged);
            RobotStatusHandling.DoWork += new DoWorkEventHandler(RobotStatusHandling_DoWork);

            RobotStatusHandling.RunWorkerAsync();

            chkVelocity.Checked = false;
            chkHLM.Checked = true;
            chkSTM.Checked = true;
        }

        private void createApartments(GroupBox grp, Button[] hotel)
        {
            int apartment;

            for (apartment = 0; apartment < maxApartments; apartment++)
            {
                // Create a Button object 
                Button apt = new Button();

                // Set Button properties
                apt.Height = 18;
                apt.Width = grp.Width - 18;
                apt.BackColor = SystemColors.Control;
                apt.ForeColor = SystemColors.ControlText;
                apt.Location = new Point(9, 15 + (maxApartments - 1 - apartment) * 20);
                apt.Tag = grp.Tag + " " + (apartment + 1).ToString();
                apt.TabStop = false;

                apt.Click += new EventHandler(button1_Click);
                grp.Controls.Add(apt);
                hotel[apartment] = apt;
            }
        }

        private int Connect()
        {
            string value = "";
            int port = 0;
            long open = Prior.PRIOR_OK;

            /* try to connect to the stage controller */
            value = Settings.Default.PS3PORT;
            open = Prior.PRIOR_OK;

            do
            {
                if (InputBox.Show("WASLV2 Connection",
                                    "Enter Com Port:", ref value) != DialogResult.OK)
                {
                    return -1;
                }

                port = Convert.ToInt32(value);

                /* WASLV2 inside the PS3, so connect to PS3 first */
                open = priorSDK.Cmd(sessionID, "controller.connect " + port.ToString(), ref userRx);

                if (open != Prior.PRIOR_OK)
                {
                    value = "0";
                }
            }
            while (open != Prior.PRIOR_OK);

            Settings.Default.PS3PORT = value;

            /* then try to connect to the waslv2 - it actually doesnt matter what you use here as the port number but for 
             * clarity use the PS3 port opened above 
             */
            userTx = "waslv2.connect " + port.ToString();
            open = priorSDK.Cmd(sessionID, userTx, ref userRx, false);

            if (open != Prior.PRIOR_OK)
            {
                /* Should NOT fail ! 
                 */
                MessageBox.Show("Error (" + open.ToString() + ") connecting to WASLV2 Loader", "Error ",
                   MessageBoxButtons.OK, MessageBoxIcon.Error);

                priorSDK.CloseSession(sessionID);
                return -1;
            }


            /* IMPORTANT:
             * WASLV2 uses stage front right as zero reference point. Reported positions are incrementing
             * as stage moves backward and left. stage resolution is in microns. This demo program and the 
             * stored calibration data is dependent on these settings. Changing stage orientation/resolution 
             * from user program will invalidate stored calibration and this programs functionality.
             * It is possible for user to change but requires modifications in the demo app and re-calibration
             */

            /* 
             * default PS3 stage movement +y+y = stage front and right
            * set orientation of stage -x-y = increasing position as stage moves back/left
            */
            priorSDK.Cmd(sessionID, "controller.stage.hostdirection.set -1 -1", ref userRx, false);


            /* grab some initial status from the loader */
            PollStatus();

            /* save the selected control port */
            Settings.Default.ODSPORT = value;
            Settings.Default.Save();

            return Prior.PRIOR_OK;
        }

        private void Disconnect()
        {
            try
            {
                int err;

                /* re-enable any joystick fitted */
                err = priorSDK.Cmd(sessionID, "controller.stage.joyxyz.on", ref userRx, false);

                /* disconnect from stage controller and loader */
                err = priorSDK.Cmd(sessionID, "waslv2.disconnect", ref userRx, false);
                err = priorSDK.Cmd(sessionID, "controller.disconnect", ref userRx, false);
            }
            catch (Exception a)
            {
                MessageBox.Show("Disconnect(): " + a.Message);
            }
        }

        private void connectToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (connectedState == 0)
            {
                if (Connect() != 0)
                {
                    return;
                }
            }
            else
            {
                Disconnect();
            }
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (sessionID >= 0)
            {
                Disconnect();

                /* close session */
                err = priorSDK.CloseSession(sessionID);
            }
        }

        enum transferType
        {
            transferNone,
            transferToStage,
            transferToHotel
        };

        transferType userRequest = transferType.transferNone;

        private void btnToStage_Click(object sender, EventArgs e)
        {
            if (WASLV2StateEquals(Prior.WASLV2_STATE_IDLE))
            {
                userRequest = transferType.transferToStage;
            }
        }

        private void btnToHotel_Click(object sender, EventArgs e)
        {
            if (WASLV2StateEquals(Prior.WASLV2_STATE_IDLE))
            {
                userRequest = transferType.transferToHotel;
            }
        }



        private void button1_Click(object sender, EventArgs e)
        {
            /* all plate button click events come though here. The controls tag selects the hotel/apartment number */

            string tag = ((Button)sender).Tag.ToString();

            if (userRequest == transferType.transferToHotel)
            {
                if (StageBusy() == 0)
                    priorSDK.Cmd(sessionID, "waslv2.movetohotel " + tag, ref userRx);
                else
                    MessageBox.Show("Stage is currently busy!", "Error ",
                                      MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else
                if (userRequest == transferType.transferToStage)
                {
                    if (StageBusy() == 0)
                        priorSDK.Cmd(sessionID, "waslv2.movetostage " + tag, ref userRx);
                    else
                        MessageBox.Show("Stage is currently busy!", "Error ",
                                          MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
                else
                {
                    // ignore
                }

            userRequest = transferType.transferNone;
        }


        private void singleStepModeToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (singleStepModeToolStripMenuItem.Checked == true)
            {
                priorSDK.Cmd(sessionID, "waslv2.singlestepmode.set 1", ref userRx);
            }
            else
            {
                priorSDK.Cmd(sessionID, "waslv2.singlestepmode.set 0", ref userRx);
            }

            btnSingle.Enabled = singleStepModeToolStripMenuItem.Checked;
        }

        private void lbllasterror_Click(object sender, EventArgs e)
        {
            priorSDK.Cmd(sessionID, "waslv2.lasterror.clear", ref userRx);
        }

        private void helpToolStripMenuItem_Click(object sender, EventArgs e)
        {
            Form h = new help(dllVersion);

            h.Show();
        }

        private int mmToCounts(int axis, double mm)
        {
            int counts = 0;

            switch (axis)
            {
                case Prior.WASLV2_HSM:
                {
                    counts = Convert.ToInt32((2000.0 * mm) / 6.0);
                    break;
                }

                case Prior.WASLV2_HLM:
                {
                    counts = Convert.ToInt32((2000.0 * mm) / 2.0);
                    break;
                }

                case Prior.WASLV2_STM:
                {
                    counts = Convert.ToInt32((2000.0 * mm) / 6.0);
                    break;
                }
            }

            return counts;
        }

        private void AxisJogBy(int axis, double mm)
        {
            priorSDK.Cmd(sessionID, "waslv2.axis.busy.get " + axis.ToString(), ref userRx);

            if (userRx.Equals("0") == true)
            {
                int pos = 0;
                int counts = 0;

                counts = mmToCounts(axis, mm);
                priorSDK.Cmd(sessionID, "waslv2.axis.position.get " + axis.ToString(), ref userRx);

                pos += Convert.ToInt32(userRx);
                pos += counts;

                AxisMoveTo(axis, pos);
            }
        }

        private void AxisMoveAtVelocity(int axis, double mmpers)
        {
            int counts;

            counts = mmToCounts(axis, mmpers);
            priorSDK.Cmd(sessionID, "waslv2.axis.move-at-velocity " + axis.ToString() + " " + counts.ToString(), ref userRx);
        }


        private void doSoakToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (doSoakToolStripMenuItem.Checked == true)
            {
                if (WASLV2StateNotEquals(Prior.WASLV2_STATE_IDLE) || (mySoakState != SoakState.soakIdle) )
                {
                    MessageBox.Show("System must be Idle to Start Full Soak", "Error ",
                        MessageBoxButtons.OK, MessageBoxIcon.Information);

                    doSoakToolStripMenuItem.Checked = false;
                }
                else
                {
                    int platesFitted = 0;
                    int plate;
                    int hotel;

                    for (hotel = 1; hotel <= maxHotels; hotel++)
                    {
                        for (plate = 1; plate <= maxApartments; plate++)
                        {
                            if ((err = priorSDK.Cmd(sessionID, "waslv2.trayfitted.get " + hotel.ToString() + " " + plate.ToString(), ref userRx, false))
                                                                == Prior.PRIOR_OK)
                            {
                                platesFitted += Convert.ToInt32(userRx);
                            }
                        }
                    }

                    if (platesFitted > 0)
                    {
                        /* turn joystick off and wait in case joystick was active and stage moving
                         */
                        priorSDK.Cmd(sessionID, "controller.stage.joyxyz.off", ref userRx, false);
                        WaitUntilStageIdle();

                        ///* get stage to load position
                        // */
                        //MoveStageToLoadPosition();
                        //WaitUntilStageIdle();

                        StartSoak();
                    }
                    else
                    {
                        MessageBox.Show("There must be at least one tray in hotels", "Error ",
                                        MessageBoxButtons.OK, MessageBoxIcon.Information);

                        doSoakToolStripMenuItem.Checked = false;
                    }

                }
            }
            else
            {
                if (mySoakState < SoakState.soakScan1)
                    StopSoak();
            }
        }

        private void scanOnlySoakToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (scanOnlySoakToolStripMenuItem.Checked == true)
            {
                if (WASLV2StateNotEquals(Prior.WASLV2_STATE_IDLE) || (mySoakState != SoakState.soakIdle))
                {
                    MessageBox.Show("System must be Idle to Start Full Soak", "Error ",
                                            MessageBoxButtons.OK, MessageBoxIcon.Information);

                    scanOnlySoakToolStripMenuItem.Checked = false;
                }
                else
                {
                    int fitted = 0;

                    if ((err = priorSDK.Cmd(sessionID, "waslv2.hotelfitted.get 1", ref userRx, false)) == Prior.PRIOR_OK)
                    {
                        fitted += Convert.ToInt32(userRx);
                    }

                    //if ((err = priorSDK.Cmd(sessionID, "waslv2.hotelfitted.get 2", ref userRx, false)) == Prior.PRIOR_OK)
                    //{
                    //    fitted += Convert.ToInt32(userRx);
                    //}

                    if (fitted != 0)
                    {
                        StartScanSoak();
                    }
                    else
                    {
                        MessageBox.Show("There must be a hotel fitted", "Error ",
                                        MessageBoxButtons.OK, MessageBoxIcon.Information);

                        scanOnlySoakToolStripMenuItem.Checked = false;
                    }
                }
            }
            else
            {
                if (mySoakState >= SoakState.soakScan1)
                    StopSoak();
            }
        }

        private void btnSingle_Click(object sender, EventArgs e)
        {
            /* send single step command */
            priorSDK.Cmd(sessionID, "waslv2.singlestep", ref userRx);
        }

        private void btnStop_Click(object sender, EventArgs e)
        {
            /* emergency stop */
            priorSDK.Cmd(sessionID, "waslv2.stop", ref userRx);
            StopSoak();
        }

        private void loaderINIToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string parameters;

            if (sessionID < 0)
                MessageBox.Show("No valid session yet");
            else
            {
                parameters = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData) + "/Prior/WASLV2_LOADER_DATA-" + sessionID.ToString() + ".ini";
                System.Diagnostics.Process.Start("Notepad.exe", parameters);
            }
        }

        private void btnEjectHotels_Click(object sender, EventArgs e)
        {
            if (WASLV2StateEquals(Prior.WASLV2_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                /* unload hotels */
                priorSDK.Cmd(sessionID, "waslv2.unloadhotels", ref userRx);
            }
        }

        private void btnLoadHotels_Click(object sender, EventArgs e)
        {
            if (WASLV2StateEquals(Prior.WASLV2_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                /* load hotels*/
                priorSDK.Cmd(sessionID, "waslv2.loadhotels", ref userRx);
            }
        }

        private void rbpoint1mm_CheckedChanged(object sender, EventArgs e)
        {
            if (rbpoint1mm.Checked == true)
                millimetres = 0.1;
        }

        private void rb1mm_CheckedChanged(object sender, EventArgs e)
        {
            if (rb1mm.Checked == true)
                millimetres = 1.0;
        }

        private void rb10mm_CheckedChanged(object sender, EventArgs e)
        {
            if (rb10mm.Checked == true)
                millimetres = 10.0;
        }

        private void btnPreview_Click(object sender, EventArgs e)
        {
            priorSDK.Cmd(sessionID, "waslv2.previewstate.set 0", ref userRx);
        }

        private void btnScan1_Click(object sender, EventArgs e)
        {
            if (WASLV2StateEquals(Prior.WASLV2_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                if (StageBusy() == 0)
                {
                    /* scan hotel 1*/
                    priorSDK.Cmd(sessionID, "waslv2.scanhotel 1", ref userRx);
                }
                else
                    MessageBox.Show("Stage is currently busy!", "Error ",
                                      MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }


        private void chkVelocity_CheckedChanged(object sender, EventArgs e)
        {

            if (chkVelocity.Checked == false)
            {
                grpMover.Text = "Manual Mover (Jog)";
                rbpoint1mm.Text = "0.1 mm";
                rb1mm.Text = "1 mm";
                rb10mm.Text = "10 mm";
            }
            else
            {
                grpMover.Text = "Manual Mover (velocity)";
                rbpoint1mm.Text = "0.1 mm/s";
                rb1mm.Text = "1 mm/s";
                rb10mm.Text = "10 mm/s";
            }
        }

        private double millimetres = 0.1;


        private void chkHLM_CheckedChanged(object sender, EventArgs e)
        {
            if (chkHLM.Checked == true)
            {
                HLMplus.Enabled = false;
                HLMminus.Enabled = false;
            }
            else
            {
                HLMplus.Enabled = true;
                HLMminus.Enabled = true;
            }
        }

        private void chkSTS_CheckedChanged(object sender, EventArgs e)
        {
            if (chkSTM.Checked == true)
            {
                STMplus.Enabled = false;
                STMminus.Enabled = false;
            }
            else
            {
                STMplus.Enabled = true;
                STMminus.Enabled = true;
            }
        }

        private void enabledToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (enabledToolStripMenuItem.Checked == true)
            {
                err = priorSDK.Cmd(sessionID, "dll.log.on", ref userRx);
                enabledToolStripMenuItem.Text = "On";
            }
            else
            {
                err = priorSDK.Cmd(sessionID, "dll.log.off", ref userRx);
                enabledToolStripMenuItem.Text = "Off";
            }
        }

        private void HLMminus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.WASLV2_HLM, -millimetres);
        }

        private void HLMplus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.WASLV2_HLM, millimetres);
        }

        private void HLMplus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_HLM, millimetres);
        }

        private void HLMplus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_HLM, 0);
        }

        private void HLMminus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_HLM, -millimetres);
        }

        private void HLMminus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_HLM, 0);
        }

        private void STMminus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.WASLV2_STM, -millimetres);
        }

        private void STMplus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.WASLV2_STM, millimetres);
        }

        private void STMminus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_STM, -millimetres);
        }

        private void STMminus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_STM, 0);
        }

        private void STMplus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_STM, millimetres);
        }

        private void STMplus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.WASLV2_STM, 0);
        }
    }
}
