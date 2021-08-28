/**
 * @file    SL160_LoaderDemo
 * @author	Rob Wicker  (rwicker@prior.com)
 * @date    5/5/2020
 * @brief   This project contains an SL160_LoaderDemo utility
 * @copyright   Copyright (c) 2020- Prior Scientific Instruments Ltd. All rights reserved
 *
 *
 * 
 * HISTORY
 * 
 * 1.8      5/7/21      reverse joystick X default direction
 * 1.7      14/5/21     fixed bug in SDK class. tx/rx stringbuilders should not be static. Causes threading issues. 
 * 1.6      5/3/21      position the stage close to the load/unload target such that the clamp automatically
 *                      opens when user is prompted to insert tray during production calibration
 * 1.5      5/1/21      Added a simple stage raster example during soak
 *                      reworked calibration to use Load/unload hotels dll api calls.
 * 1.4      4/1/21      move STM out a further 10mm when user inserts tray during calibration
 *                      HSM jog buttons enabled by default
 * 1.3      19/11/20    STM axes is now encoded
 * 1.2      5/11/20     HLM and HSM are now encoded axes (STM to follow)
 * 1.1      1/4/20      initial version
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
using SL160_LoaderDemo.Properties;

namespace SL160_LoaderDemo
{
    public partial class Form1 : Form
    {
        StringBuilder dllVersion = new StringBuilder();

        int maxApartments = 20;
        int maxHotels = 2;

        int err;
        int sessionID = -1;

        string userTx = "";
        string userRx = "";

        /* background thread that handles the status updates from the loader */
        private BackgroundWorker RobotStatusHandling = new BackgroundWorker();

        Stopwatch myStopWatch = new Stopwatch();

        /* create a c# wrapper class for the Prior DLL */
        SDK priorSDK = new SDK();

        /* SL160 has two hotel with 20 apartments, each apartment has an associated tray with 4 slides */
        Button[] hotel1;
        Button[] hotel2;

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

            /* initiliase DLL, *must* be done before opening a session */
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
            hotel2 = new Button[maxApartments];


            /* create the hotel apartments 
            */
            createApartments(grpHotel1, hotel1);
            createApartments(grpHotel2, hotel2);

            grpHotel1.Enabled = false;
            grpHotel2.Enabled = false;

            /* create a session in the DLL, this gives us one controller and an Sl160 loader. Multiple connections allow control of multiple
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
            chkHSM.Checked = true;
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
                if (InputBox.Show("SL160 Connection",
                                    "Enter Com Port:", ref value) != DialogResult.OK)
                {
                    return -1;
                }

                port = Convert.ToInt32(value);

                /* SL160 inside the PS3, so connect to PS3 first */
                open = priorSDK.Cmd(sessionID, "controller.connect " + port.ToString(), ref userRx);

                if (open != Prior.PRIOR_OK)
                {
                    value = "0";
                }
            }
            while (open != Prior.PRIOR_OK);

            Settings.Default.PS3PORT = value;

            /* then try to connect to the sl160 - it actually doesnt matter what you use here as the port number but for 
             * clarity use the PS3 port opened above 
             */
            userTx = "sl160.connect " + port.ToString();
            open = priorSDK.Cmd(sessionID, userTx, ref userRx, false);

            if (open != Prior.PRIOR_OK)
            {
                /* Should NOT fail ! 
                 */
                MessageBox.Show("Error (" + open.ToString() + ") connecting to SL160 Loader", "Error ",
                   MessageBoxButtons.OK, MessageBoxIcon.Error);

                priorSDK.CloseSession(sessionID);
                return -1;
            }


            /* IMPORTANT:
             * Prior SL160 uses stage back right as zero reference point. Reported positions are incrementing
             * as stage moves forward and left. stage resolution is in microns. This demo program and the 
             * stored calibration data is dependent on these settings. Changing stage orientation/resolution 
             * from user program will invalidate stored calibration and this programs functionality.
             * It is possible for user to change but requires modifications in the demo app and re-calibration
             */

            /* 
             * default PS3 stage movment +y+y = stage front and right
            * set orientation of stage -x+y = stage left and stage forward 
            */
            priorSDK.Cmd(sessionID, "controller.stage.hostdirection.set -1 1", ref userRx, false);

            priorSDK.Cmd(sessionID, "controller.stage.joystickdirection.set -1 1", ref userRx, false);

            /* grab some initial status from the loader */
            PollStatus();

            /* save the selected control port */
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

                err = priorSDK.Cmd(sessionID, "sl160.disconnect", ref userRx, false);
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
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
            {
                userRequest = transferType.transferToStage;
            }
        }

        private void btnToHotel_Click(object sender, EventArgs e)
        {
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
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
                    priorSDK.Cmd(sessionID, "sl160.movetohotel " + tag, ref userRx);
                else
                    MessageBox.Show("Stage is currently busy!", "Error ",
                                      MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            else
                if (userRequest == transferType.transferToStage)
                {
                    if (StageBusy() == 0)
                        priorSDK.Cmd(sessionID, "sl160.movetostage " + tag, ref userRx);
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
                priorSDK.Cmd(sessionID, "sl160.singlestepmode.set 1", ref userRx);
            }
            else
            {
                priorSDK.Cmd(sessionID, "sl160.singlestepmode.set 0", ref userRx);
            }

            btnSingle.Enabled = singleStepModeToolStripMenuItem.Checked;
        }

        private void lbllasterror_Click(object sender, EventArgs e)
        {
            priorSDK.Cmd(sessionID, "sl160.lasterror.clear", ref userRx);
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
                case Prior.SL160_HSM:
                {
                    //proto has 500 line encoder, 2000 counts/rev
                    counts = Convert.ToInt32((2000.0 * mm) / 6.0);
                    break;
                }

                case Prior.SL160_HLM:
                {
                    // proto has 500 line encoder, 2000 counts/rev
                    counts = Convert.ToInt32((2000.0 * mm) / 2.0);
                    break;
                }

                case Prior.SL160_STM:
                {
                    // proto has 500 line encoder, 2000 counts/rev
                    counts = Convert.ToInt32((2000.0 * mm) / 6.0);
                    break;
                }
            }

            return counts;
        }

        private void AxisJogBy(int axis, double mm)
        {
            priorSDK.Cmd(sessionID, "sl160.axis.busy.get " + axis.ToString(), ref userRx);

            if (userRx.Equals("0") == true)
            {
                int pos = 0;
                int counts = 0;

                counts = mmToCounts(axis, mm);
                priorSDK.Cmd(sessionID, "sl160.axis.position.get " + axis.ToString(), ref userRx);

                pos += Convert.ToInt32(userRx);
                pos += counts;

                AxisMoveTo(axis, pos);
            }
        }

        private void AxisMoveAtVelocity(int axis, double mmpers)
        {
            int counts;

            counts = mmToCounts(axis, mmpers);
            priorSDK.Cmd(sessionID, "sl160.axis.move-at-velocity " + axis.ToString() + " " + counts.ToString(), ref userRx);
        }


        private void doSoakToolStripMenuItem_Click(object sender, EventArgs e)
        {
            if (doSoakToolStripMenuItem.Checked == true)
            {
                if (SL160StateNotEquals(Prior.SL160_STATE_IDLE) || (mySoakState != SoakState.soakIdle) )
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
                            if ((err = priorSDK.Cmd(sessionID, "sl160.trayfitted.get " + hotel.ToString() + " " + plate.ToString(), ref userRx, false))
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
                if (SL160StateNotEquals(Prior.SL160_STATE_IDLE) || (mySoakState != SoakState.soakIdle))
                {
                    MessageBox.Show("System must be Idle to Start Full Soak", "Error ",
                                            MessageBoxButtons.OK, MessageBoxIcon.Information);

                    scanOnlySoakToolStripMenuItem.Checked = false;
                }
                else
                {
                    int fitted = 0;

                    if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 1", ref userRx, false)) == Prior.PRIOR_OK)
                    {
                        fitted += Convert.ToInt32(userRx);
                    }

                    if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 2", ref userRx, false)) == Prior.PRIOR_OK)
                    {
                        fitted += Convert.ToInt32(userRx);
                    }

                    if (fitted != 0)
                    {
                        StartScanSoak();
                    }
                    else
                    {
                        MessageBox.Show("There must be at least one hotel fitted", "Error ",
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
            priorSDK.Cmd(sessionID, "sl160.singlestep", ref userRx);
        }

        private void btnStop_Click(object sender, EventArgs e)
        {
            /* emergency stop */
            priorSDK.Cmd(sessionID, "sl160.stop", ref userRx);
            StopSoak();
        }

        private void loaderINIToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string parameters;

            if (sessionID < 0)
                MessageBox.Show("No valid session yet");
            else
            {
                parameters = Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData) + "/Prior/SL160_LOADER_DATA-" + sessionID.ToString() + ".ini";
                System.Diagnostics.Process.Start("Notepad.exe", parameters);
            }
        }

        private void btnEjectHotels_Click(object sender, EventArgs e)
        {
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                /* unload hotels */
                priorSDK.Cmd(sessionID, "sl160.unloadhotels", ref userRx);
            }
        }

        private void btnLoadHotels_Click(object sender, EventArgs e)
        {
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                /* load hotels*/
                priorSDK.Cmd(sessionID, "sl160.loadhotels", ref userRx);
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
            priorSDK.Cmd(sessionID, "sl160.previewstate.set 0", ref userRx);
        }

        private void btnScan1_Click(object sender, EventArgs e)
        {
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                if (StageBusy() == 0)
                {
                    /* scan hotel 1*/
                    priorSDK.Cmd(sessionID, "sl160.scanhotel 1", ref userRx);
                }
                else
                    MessageBox.Show("Stage is currently busy!", "Error ",
                                      MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnScan2_Click(object sender, EventArgs e)
        {
            if (SL160StateEquals(Prior.SL160_STATE_IDLE))
            {
                userRequest = transferType.transferNone;

                if (StageBusy() == 0)
                {
                    /* scan hotel 2*/
                    priorSDK.Cmd(sessionID, "sl160.scanhotel 2", ref userRx);
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

                try
                {
                    Xminus.Click += Xminus_Click;
                    Xplus.Click += Xplus_Click;
                    Yminus.Click += Yminus_Click;
                    Yplus.Click += Yplus_Click;
                    Zminus.Click += Zminus_Click;
                    Zplus.Click += Zplus_Click;

                    Xminus.MouseDown -= Xminus_MouseDown;
                    Xminus.MouseUp -= Xminus_MouseUp;
                    Xplus.MouseDown -= Xplus_MouseDown;
                    Xplus.MouseUp -= Xplus_MouseUp;

                    Yminus.MouseDown -= Yminus_MouseDown;
                    Yminus.MouseUp -= Yminus_MouseUp;
                    Yplus.MouseDown -= Yplus_MouseDown;
                    Yplus.MouseUp -= Yplus_MouseUp;

                    Zminus.MouseDown -= Zminus_MouseDown;
                    Zminus.MouseUp -= Zminus_MouseUp;
                    Zplus.MouseDown -= Zplus_MouseDown;
                    Zplus.MouseUp -= Zplus_MouseUp;
                }
                catch (Exception aa)
                {
                    MessageBox.Show(aa.Message);
                }
            }
            else
            {
                grpMover.Text = "Manual Mover (velocity)";
                rbpoint1mm.Text = "0.1 mm/s";
                rb1mm.Text = "1 mm/s";
                rb10mm.Text = "10 mm/s";

                try
                {
                    Xminus.Click -= Xminus_Click;
                    Xplus.Click -= Xplus_Click;
                    Yminus.Click -= Yminus_Click;
                    Yplus.Click -= Yplus_Click;
                    Zminus.Click -= Zminus_Click;
                    Zplus.Click -= Zplus_Click;

                    Xminus.MouseDown += Xminus_MouseDown;
                    Xminus.MouseUp += Xminus_MouseUp;
                    Xplus.MouseDown += Xplus_MouseDown;
                    Xplus.MouseUp += Xplus_MouseUp;

                    Yminus.MouseDown += Yminus_MouseDown;
                    Yminus.MouseUp += Yminus_MouseUp;
                    Yplus.MouseDown += Yplus_MouseDown;
                    Yplus.MouseUp += Yplus_MouseUp;

                    Zminus.MouseDown += Zminus_MouseDown;
                    Zminus.MouseUp += Zminus_MouseUp;
                    Zplus.MouseDown += Zplus_MouseDown;
                    Zplus.MouseUp += Zplus_MouseUp;
                }
                catch (Exception aa)
                {
                    MessageBox.Show(aa.Message);
                }
            }
        }

        private double millimetres = 0.1;

        private void Xminus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_HSM, -millimetres);
        }

        private void Xplus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_HSM, millimetres);
        }

        private void Yminus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_HLM, -millimetres);
        }

        private void Yplus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_HLM, millimetres);
        }

        private void Zminus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_STM, -millimetres);
        }

        private void Zplus_Click(object sender, EventArgs e)
        {
            if (chkVelocity.Checked == false)
                AxisJogBy(Prior.SL160_STM, millimetres);
        }

        private void Xminus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HSM, -millimetres);
        }

        private void Xminus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HSM, 0);
        }

        private void Xplus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HSM, millimetres);
        }

        private void Xplus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HSM, 0);
        }

        private void Yminus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HLM, -millimetres);
        }

        private void Yminus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HLM, 0);
        }

        private void Yplus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HLM, millimetres);
        }

        private void Yplus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_HLM, 0);
        }

        private void Zminus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_STM, -millimetres);
        }

        private void Zminus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_STM, 0);
        }

        private void Zplus_MouseDown(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_STM, millimetres);
        }

        private void Zplus_MouseUp(object sender, MouseEventArgs e)
        {
            if (chkVelocity.Checked == true)
                AxisMoveAtVelocity(Prior.SL160_STM, 0);
        }

        private void chkHSM_CheckedChanged(object sender, EventArgs e)
        {
            if (chkHSM.Checked == true)
            {
                Xplus.Enabled = false;
                Xminus.Enabled = false;
            }
            else
            {
                Xplus.Enabled = true;
                Xminus.Enabled = true;
            }
        }

        private void chkHLM_CheckedChanged(object sender, EventArgs e)
        {
            if (chkHLM.Checked == true)
            {
                Yplus.Enabled = false;
                Yminus.Enabled = false;
            }
            else
            {
                Yplus.Enabled = true;
                Yminus.Enabled = true;
            }
        }

        private void chkSTM_CheckedChanged(object sender, EventArgs e)
        {
            if (chkSTM.Checked == true)
            {
                Zplus.Enabled = false;
                Zminus.Enabled = false;
            }
            else
            {
                Zplus.Enabled = true;
                Zminus.Enabled = true;
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
    }
}
