using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows.Forms;

using SL160_LoaderDemo.Properties;

namespace SL160_LoaderDemo
{
    public partial class Form1 : Form
    {

        private string[] lastErr = { "OK",   //  0                         
                                    "Err: NOT INITIALISED",  //1
                                    "Err: NOT SETUP", //2
                                    "Err: GRIPPER HOMING FAILED",//3
                                    "Err: INVALID HOTEL",//4
                                    "Err: INVALID PLATE",//5
                                    "",//6
                                    "Err: PLATE IN GRIPPER",//7
                                    "Err: PLATE ON STAGE",//8
                                    "Err: INVALID STATE CHANGE",//9
                                    "Err: HOTEL IN USE REMOVED",//10
                                    "Err: WRONG PLATESENSOR STATE", //11
                                    "Err: STAGE MOVED OFF LOAD POINT",//12
                                    "Err: COMMS ERROR", //13
                                    "Err: AXIS STALLED", //14
                                };

        int currentRobotStatus = 0;
        int currentRobotState = 0;
        int lastRobotstate = 0;
        int lastRobotStatus = 0;
        int lastRobotErr = 0;
        int previewState = 0;
        int connectedState = 0;
        int lastConnectedState = 0;
        bool pollStatus = true;

        private void RobotStatusHandling_DoWork(object sender, DoWorkEventArgs e)
        {
            try
            {
                while (true)
                {
                    Thread.Sleep(200);
                        
                    if (pollStatus == true)
                        RobotStatusHandling.ReportProgress(currentRobotStatus);
                }
            }
            catch (Exception rsh)
            {
                /* ignore */
                string s = rsh.Message;
            }
        }



        public string GetLastErrorAsString(int err)
        {
            return lastErr[System.Math.Abs(err)];
        }

        public string StatusBitToString(int bit, string T, string F)
        {
            if ((currentRobotStatus & bit) == bit)
                return T;
            else
                return F;
        }

        public bool StatusBitIsSet(int bit)
        {
            if ((currentRobotStatus & bit) == bit)
                return true;
            else
                return false;
        }

        public bool SL160StateEquals(int state)
        {
            if ((currentRobotStatus & Prior.SL160_STATE_STATEMASK) == state)
                return true;
            else
                return false;
        }

        public bool SL160StateNotEquals(int state)
        {
            return !SL160StateEquals(state);
        }

        public int GetStateFromStatus(int status)
        {
            return status & Prior.SL160_STATE_STATEMASK;
        }

        public string GetStateAsString(int majorState)
        {
            switch (majorState)
            {

                case Prior.SL160_STATE_UNKNOWN:
                    return "UNKNOWN";

                case Prior.SL160_STATE_SETUP:
                    return "SETUP";

                case Prior.SL160_STATE_INITIALISE:
                    return "INITIALISING";

                case Prior.SL160_STATE_STOP:
                    return "STOP";

                case Prior.SL160_STATE_IDLE:
                    return "IDLE";

                case Prior.SL160_STATE_TXF_TOSTAGE:
                    return "LOADING TRAY";

                case Prior.SL160_STATE_TXF_FROMSTAGE:
                    return "UNLOADING TRAY";

                case Prior.SL160_STATE_SCANHOTEL:
                    return "SCANNING HOTEL";
                  
                case Prior.SL160_STATE_LOAD_HOTELS:
                    return "INSERTING HOTELS";

                case Prior.SL160_STATE_UNLOAD_HOTELS :
                    return "EJECTING HOTELS";

                default:
                    return "STATE_UNKNOWN";
            }
        }

        string statusRx = "";

        private void PollStatus()
        {
            string status = "";
            if ((err = priorSDK.Cmd(sessionID, "sl160.status.get", ref status,false)) == Prior.PRIOR_OK)
            {
                currentRobotStatus = Convert.ToInt32(status);
            }
        }

        private void HandleTiming()
        {
            currentRobotState = GetStateFromStatus(currentRobotStatus);

            if (currentRobotState != lastRobotstate)
            {
                if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                {
                    myStopWatch.Stop();
                    long elapsed = myStopWatch.ElapsedMilliseconds / 1000;
                    lbltime.Text = elapsed.ToString() + "s";
                }
                else
                {
                    myStopWatch.Restart();
                }

                lastRobotstate = currentRobotState;
            }
        }

        private void UpdateLastError()
        {
            if ((err = priorSDK.Cmd(sessionID, "sl160.lasterror.get", ref statusRx, false)) == Prior.PRIOR_OK)
            {
                lastRobotErr = Convert.ToInt32(statusRx);
            }
        }

        private void UpdateSL160StatusFlags()
        {
          
           if (currentRobotStatus != lastRobotStatus)
           {
                UpdateLastError();
                
                if (StatusBitIsSet(Prior.SL160_LOADER_ERROR))
                {
                    lblError.Text = "ERROR";
                    lblError.BackColor = Color.Red;
                }
                else
                {
                    lblError.Text = "";
                    lblError.BackColor = SystemColors.Control;
                }

               

                /* display status bits */
                lblEject.Text = StatusBitToString(Prior.SL160_LOADER_HOTELEJECTED, "HOTELS EJECTED", "");
                lblNotInitialised.Text = StatusBitToString(Prior.SL160_LOADER_NOTINITIALISED, "NOT INITIALISED", "");
                lblNotSetup.Text = StatusBitToString(Prior.SL160_LOADER_NOTSETUP, "NOT SETUP", "");

                if (StatusBitIsSet(Prior.SL160_LOADER_NOTIDLE))
                {
                     lblNotIdle.Text = "ACTIVE";
                     lblNotIdle.BackColor = Color.Yellow;
                }
                else
                {
                    lblNotIdle.Text = "IDLE";
                    lblNotIdle.BackColor =  SystemColors.Control;
                }

                lblCassetteNotScanned.Text = StatusBitToString(Prior.SL160_LOADER_HOTELNOTSCANNED, "NOT SCANNED", "");
                lblInvalidSlide.Text = StatusBitToString(Prior.SL160_LOADER_INVALIDTRAY, "INVALID TRAY", "");
                lblInvalidCassette.Text = StatusBitToString(Prior.SL160_LOADER_INVALIDHOTEL, "INVALID HOTEL", "");

                if (StatusBitIsSet(Prior.SL160_LOADER_TRAYONSTAGE))
                {
                    lblSlideOnStage.Text = "TRAY ON STAGE";
                    lblSlideOnStage.BackColor = Color.LightGreen;
                }
                else
                {
                    lblSlideOnStage.Text = "";
                    lblSlideOnStage.BackColor = SystemColors.Control;
                }

                lblCommsError.Text = StatusBitToString(Prior.SL160_LOADER_COMMSERROR, "COMMS ERR", "");
                lblSlideSensorError.Text = StatusBitToString(Prior.SL160_LOADER_TRAYSENSORERROR, "TRAY SENSOR ERR", "");

                if (StatusBitIsSet(Prior.SL160_LOADER_AXISSTALLED))
                {
                    int axis;

                    if ((err = priorSDK.Cmd(sessionID, "sl160.stalledaxis.get", ref statusRx, false)) != Prior.PRIOR_OK)
                    {
                        return;
                    }

                    axis = Convert.ToInt32(statusRx);

                    if (axis == 1)
                        lblStallError.Text = "X AXIS STALLED";
                    if (axis == 2)
                        lblStallError.Text = "Y AXIS STALLED";
                    if (axis == 3)
                        lblStallError.Text = "Z AXIS STALLED";
                }
                else
                    lblStallError.Text = "";
            }

            lblstate.Text = GetStateAsString(GetStateFromStatus(currentRobotStatus));

            lbllasterror.Text = GetLastErrorAsString(lastRobotErr);

            lastRobotStatus = currentRobotStatus;

            if ((err = priorSDK.Cmd(sessionID, "sl160.previewstate.get", ref statusRx, false)) == Prior.PRIOR_OK)
            {
                previewState = Convert.ToInt32(statusRx);

                btnPreview.Text = "Preview " + previewState.ToString();

                if (previewState == 0)
                {
                    btnPreview.Enabled = false;
                }
                else
                {
                    btnPreview.Enabled = true;
                }
            }
        }

        private void RobotStatusHandling_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            PollStatus();

            if ((currentRobotStatus & Prior.SL160_LOADER_NOTCONNECTED) != 0)
                connectedState = 0;
            else
                connectedState = 1;

            if (connectedState != lastConnectedState)
            {
                SetScreenByState();

                lastConnectedState = connectedState;
            }

            HandleTiming();

          

            /* check for hotel fitted status */
            if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 1", ref statusRx,false)) == Prior.PRIOR_OK)
            {
                if (statusRx.Equals("1") == true)
                {
                    if (grpHotel1.Enabled == false)
                    {
                        grpHotel1.Enabled = true;
                    }
                }
                else
                {
                    if (grpHotel1.Enabled == true)
                    {
                        grpHotel1.Enabled = false;
                    }
                }
            }    
            
            /* check for hotel fitted status */
            if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 2", ref statusRx,false)) == Prior.PRIOR_OK)
            {
                if (statusRx.Equals("1") == true)
                {
                    if (grpHotel2.Enabled == false)
                    {
                        grpHotel2.Enabled = true;
                    }
                }
                else
                {
                    if (grpHotel2.Enabled == true)
                    {
                        grpHotel2.Enabled = false;
                    }
                }
            }

            UpdateSL160StatusFlags();

            /* keep track of plates */
          
            int tray = 0;

            for (tray = 0; tray < 20; tray++)
            {
                if (grpHotel1.Enabled == true)
                {
                    if ((err = priorSDK.Cmd(sessionID, "sl160.trayfitted.get 1 " + (tray + 1).ToString(), ref statusRx, false)) == Prior.PRIOR_OK)
                    {
                        if (statusRx.Equals("1") == true)
                        {
                            if (hotel1[tray].BackColor != Color.LightGreen)
                                hotel1[tray].BackColor = Color.LightGreen;
                        }
                        else
                        {
                            if (hotel1[tray].BackColor != SystemColors.Control)
                                hotel1[tray].BackColor = SystemColors.Control;
                        }
                    }
                }
                else
                {
                    if (hotel1[tray].BackColor != SystemColors.Control)
                        hotel1[tray].BackColor = SystemColors.Control;
                }

                if (grpHotel2.Enabled == true)
                {
                    if ((err = priorSDK.Cmd(sessionID, "sl160.trayfitted.get 2 " + (tray + 1).ToString(), ref statusRx, false)) == Prior.PRIOR_OK)
                    {
                        if (statusRx.Equals("1") == true)
                        {
                            if (hotel2[tray].BackColor != Color.LightGreen)
                                hotel2[tray].BackColor = Color.LightGreen;
                        }
                        else
                        {
                            if (hotel2[tray].BackColor != SystemColors.Control)
                                hotel2[tray].BackColor = SystemColors.Control;
                        }
                    }
                }
                else
                {
                    if (hotel2[tray].BackColor != SystemColors.Control)
                        hotel2[tray].BackColor = SystemColors.Control;
                }
            }

            lastRobotStatus = currentRobotStatus;

            DoSoak();
        }

        enum SoakState
        {
            soakIdle,
            soakStart,
            soakFindNextTray,
            soakTransferToStage,

            soakPreview1,
            soakPreview2, 
            soakPreview3,
            soakPreview4,
            soakTrayLoaded,

            soakDoStageRaster,
            soakTransferToHotel,

            soakScan1,
            soakScan2
        };

        SoakState mySoakState = SoakState.soakIdle;
        int soakTray = 1;
        int soakCount = 0;

        List<string> raster = new List<string>{ 
                                "50000 50000", 
                                "40000 50000",
                                "40000 40000",
                                "50000 40000" };
        int rasterIndex = 0;

        private void StartSoak()
        {   
            /* start a soak transferring available trays between hotel and stage and back
             * */
            mySoakState = SoakState.soakStart;
            soakCount = 0;
            grpAction.Enabled = false;
            grpHotel1.Enabled = false;
            userRequest = transferType.transferNone;
        }

        private void StartScanSoak()
        {
            /* start a soak scanning only hotel apartments. 
             * */
            mySoakState = SoakState.soakScan1; 
            soakCount = 0;
            grpAction.Enabled = false;
            grpHotel1.Enabled = false;
            userRequest = transferType.transferNone;
        }
          
        private void StopSoak()
        {
            /* stop any active soak 
             * */
            mySoakState = SoakState.soakIdle;
            grpAction.Enabled = true;
            grpHotel1.Enabled = true;
            doSoakToolStripMenuItem.Checked = false;
            scanOnlySoakToolStripMenuItem.Checked = false;
            priorSDK.Cmd(sessionID, "controller.stage.joyxyz.on", ref userRx, false);
        }

        private string GetHotelAndTray(int tray)
        {
            if (tray <= 20)
                return "1 " + tray.ToString();
            else
                return "2 " + (tray - 20).ToString();
        }

        private void AquireImage()
        {
            /* Hook for user based objective image aquisition */
        }

        private void AquirePreviewImage()
        {
            /* Hook for user based preview image aquisition */
        }

        private void DoSoak()
        {
            if (mySoakState != SoakState.soakIdle)
            {
                if (StatusBitIsSet(Prior.SL160_LOADER_ERROR))
                {
                    /* cancel the soak if an error is raised */
                    StopSoak();
                }
            }

            /* state machine for soak test */
            switch (mySoakState)
            {
                case SoakState.soakIdle:
                {
                    soakTray = 0;
                    break;
                }

                case SoakState.soakStart:
                {
                    /* cycle aound the known fitted trays in the hotels 
                     */
                    mySoakState = SoakState.soakFindNextTray;
                   
                    break;
                }

                case SoakState.soakFindNextTray:
                {
                    /* wait for loader to be idle 
                     */
                    if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                    {
                        do
                        {
                            lblSoakCount.Text = soakCount.ToString();

                            soakTray++;
                            if (soakTray > 40)
                                soakTray = 1;

                            if ((err = priorSDK.Cmd(sessionID, "sl160.trayfitted.get " + GetHotelAndTray(soakTray), ref statusRx, false)) != Prior.PRIOR_OK)
                            {
                                StopSoak();
                                return;
                            }
                        }
                        while (statusRx.Equals("0"));

                        mySoakState = SoakState.soakTransferToStage;
                    }

                    break;
                }

                case SoakState.soakTransferToStage:
                {
                    if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                    {
                        if ((err = priorSDK.Cmd(sessionID, "sl160.movetostage "
                                                 + GetHotelAndTray(soakTray), ref statusRx, false)) == Prior.PRIOR_OK)
                        {
                            /* dll will set the previewstate from zero to preview station number when STM is ready 
                             */
                            mySoakState = SoakState.soakPreview1;
                        }
                        else
                        {
                            StopSoak();
                            return;
                        }
                    }

                    break;
                }

                case SoakState.soakPreview1:
                {
                    if (previewState == 1)
                    {
                        /* ASSERT: we have arrived at the first preview station, this would be the hook to add your preview capture
                         * solution ie webcam image capture etc. This comment also applies to preview station 2/3/4 below.
                         * 
                         * NOTE: it is *NOT* allowed to move the stage at this point as the tray will still be partially in the hotel.
                         *       if you want to preview scan with a low mag objective then do that when the tray is fully loaded 
                         *       you *MUST* index through these preview states even if you dont image each slide.
                         */

                        AquirePreviewImage();

                        /* signal loader to continue */
                        priorSDK.Cmd(sessionID, "sl160.previewstate.set 0", ref statusRx, false);
                        mySoakState = SoakState.soakPreview2;
                    }

                    break;
                }

                case SoakState.soakPreview2:
                {
                    if (previewState == 2)
                    {
                        AquirePreviewImage();

                        /* signal loader to continue */
                        priorSDK.Cmd(sessionID, "sl160.previewstate.set 0", ref statusRx, false);
                        mySoakState = SoakState.soakPreview3;
                    }

                    break;
                }

                case SoakState.soakPreview3:
                {
                    if (previewState == 3)
                    {
                        AquirePreviewImage();

                        /* signal loader to continue */
                        priorSDK.Cmd(sessionID, "sl160.previewstate.set 0", ref statusRx, false);
                        mySoakState = SoakState.soakPreview4;
                    }

                    break;
                }

                case SoakState.soakPreview4:
                {
                    if (previewState == 4)
                    {
                        AquirePreviewImage();

                        /* signal loader to continue */
                        priorSDK.Cmd(sessionID, "sl160.previewstate.set 0", ref statusRx, false);
                        mySoakState = SoakState.soakTrayLoaded;
                    }

                    break;
                }

                case SoakState.soakTrayLoaded:
                {
                    if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                    {
                        /* ASSERT: tray loaded - no need to check if tray there as soak would abort if error raised */
                        if (stageRasterEnabledToolStripMenuItem.Checked == false)
                        {
                            /* dont scan the slides, just put the tray back */
                            mySoakState = SoakState.soakTransferToHotel;
                        }
                        else
                        {
                            rasterIndex = 0;

                            /* start move to first position in our raster pattern. This is very much simplified here as a group of points
                             * purely for use as an example only. Any real system would have probably constructed a scan pattern(s) based
                             * on the preview image. Also a real application would have to control focus and manage objective escape sequence
                             */

                            if ((err = priorSDK.Cmd(sessionID, "controller.stage.goto-position " + raster[rasterIndex], ref userRx)) == Prior.PRIOR_OK)
                            {
                                mySoakState = SoakState.soakDoStageRaster;
                            }
                            else
                            {
                                StopSoak();
                                return;
                            }
                        }
                    }
                    break;
                }

                case SoakState.soakDoStageRaster:
                {
                    if (StageBusy() == 0)
                    {
                        /* ASSERT: stage movement stopped, should be at rasterIndex position. 
                         */
                        AquireImage();

                        rasterIndex++;

                        if (rasterIndex == raster.Count)
                        {
                            /* scan finished */
                            mySoakState = SoakState.soakTransferToHotel;
                        }
                        else
                        {
                            if ((err = priorSDK.Cmd(sessionID, "controller.stage.goto-position " + raster[rasterIndex], ref userRx)) == Prior.PRIOR_OK)
                            {
                               /* stay in this state waiting for completed move */
                            }
                            else
                            {
                                StopSoak();
                                return;
                            }
                        }
                    }

                    break;
                }

                case SoakState.soakTransferToHotel:
                {
                    /* ASSERT: stage and loader are idle
                     */
                    if ((err = priorSDK.Cmd(sessionID, "sl160.movetohotel "
                                            + GetHotelAndTray(soakTray), ref statusRx, false)) == Prior.PRIOR_OK)
                    {
                        soakCount++;
                        mySoakState = SoakState.soakFindNextTray;
                    }
                    else
                    {
                        StopSoak();
                        return;
                    }

                    break;
                }

                /* hotel soak scan requires both hotels to be fitted, else the soak aborts. It then cycles indefinetly scanning
                 * each hotel in turn, execising the lifting/swapping hotels functions of the loader
                 */
                case SoakState.soakScan1:
                {
                    if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                    {
                        if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 1", ref userRx, false)) != Prior.PRIOR_OK)
                        {
                            StopSoak();
                            return;
                        }
                        else
                        {
                            if (userRx.Equals("1") == true)
                            {
                                if ((err = priorSDK.Cmd(sessionID, "sl160.scanhotel 1", ref userRx, false)) == Prior.PRIOR_OK)
                                {
                                    soakCount++;
                                    lblSoakCount.Text = soakCount.ToString();
                                    mySoakState = SoakState.soakScan2;
                                }
                                else
                                {
                                    StopSoak();
                                    return;
                                }
                            }
                            else
                                mySoakState = SoakState.soakScan2;
                        }
                    }

                    break;
                }

                case SoakState.soakScan2:
                {
                    if (SL160StateEquals(Prior.SL160_STATE_IDLE))
                    {
                        if ((err = priorSDK.Cmd(sessionID, "sl160.hotelfitted.get 2", ref userRx, false)) != Prior.PRIOR_OK)
                        {
                            StopSoak();
                            return;
                        }
                        else
                        {
                            if (userRx.Equals("1") == true)
                            {
                                if ((err = priorSDK.Cmd(sessionID, "sl160.scanhotel 2", ref userRx, false)) == Prior.PRIOR_OK)
                                {
                                    soakCount++;
                                    lblSoakCount.Text = soakCount.ToString();
                                    mySoakState = SoakState.soakScan1;
                                }
                                else
                                {
                                    StopSoak();
                                    return;
                                }
                            }
                            else
                                mySoakState = SoakState.soakScan1;
                        }
                    }

                    break;
                }
            }
        }
    }
}