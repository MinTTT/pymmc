namespace SL160_LoaderDemo
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.connectToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.editINIToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loaderINIToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.optionsToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.singleStepModeToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.doSoakToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.scanOnlySoakToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.stageRasterEnabledToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.loggingToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.enabledToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.helpToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.grpStatus = new System.Windows.Forms.GroupBox();
            this.lblEject = new System.Windows.Forms.Label();
            this.lblStallError = new System.Windows.Forms.Label();
            this.lblSlideSensorError = new System.Windows.Forms.Label();
            this.lblCommsError = new System.Windows.Forms.Label();
            this.lblCassetteNotScanned = new System.Windows.Forms.Label();
            this.lblNotIdle = new System.Windows.Forms.Label();
            this.lblSlideOnStage = new System.Windows.Forms.Label();
            this.lblInvalidCassette = new System.Windows.Forms.Label();
            this.lblInvalidSlide = new System.Windows.Forms.Label();
            this.lblNotSetup = new System.Windows.Forms.Label();
            this.lblNotInitialised = new System.Windows.Forms.Label();
            this.lblNotConnected = new System.Windows.Forms.Label();
            this.lblError = new System.Windows.Forms.Label();
            this.statusStrip = new System.Windows.Forms.StatusStrip();
            this.lblstate = new System.Windows.Forms.ToolStripStatusLabel();
            this.lbltime = new System.Windows.Forms.ToolStripStatusLabel();
            this.lblSoakCount = new System.Windows.Forms.ToolStripStatusLabel();
            this.lbllasterror = new System.Windows.Forms.ToolStripStatusLabel();
            this.grpMover = new System.Windows.Forms.GroupBox();
            this.chkSTM = new System.Windows.Forms.CheckBox();
            this.chkHLM = new System.Windows.Forms.CheckBox();
            this.chkHSM = new System.Windows.Forms.CheckBox();
            this.chkVelocity = new System.Windows.Forms.CheckBox();
            this.rb10mm = new System.Windows.Forms.RadioButton();
            this.rb1mm = new System.Windows.Forms.RadioButton();
            this.rbpoint1mm = new System.Windows.Forms.RadioButton();
            this.Yminus = new System.Windows.Forms.Button();
            this.Yplus = new System.Windows.Forms.Button();
            this.label3 = new System.Windows.Forms.Label();
            this.Zminus = new System.Windows.Forms.Button();
            this.Zplus = new System.Windows.Forms.Button();
            this.label2 = new System.Windows.Forms.Label();
            this.Xminus = new System.Windows.Forms.Button();
            this.Xplus = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.grpSetup = new System.Windows.Forms.GroupBox();
            this.lstHelp = new System.Windows.Forms.ListBox();
            this.btnAction = new System.Windows.Forms.Button();
            this.grpAction = new System.Windows.Forms.GroupBox();
            this.btnPreview = new System.Windows.Forms.Button();
            this.btnLoadHotels = new System.Windows.Forms.Button();
            this.btnEjectHotels = new System.Windows.Forms.Button();
            this.btnToHotel = new System.Windows.Forms.Button();
            this.btnToStage = new System.Windows.Forms.Button();
            this.grpHotel1 = new System.Windows.Forms.GroupBox();
            this.btnScan1 = new System.Windows.Forms.Button();
            this.btndummy = new System.Windows.Forms.Button();
            this.btnSingle = new System.Windows.Forms.Button();
            this.btnStop = new System.Windows.Forms.Button();
            this.grpHotel2 = new System.Windows.Forms.GroupBox();
            this.btnScan2 = new System.Windows.Forms.Button();
            this.menuStrip1.SuspendLayout();
            this.grpStatus.SuspendLayout();
            this.statusStrip.SuspendLayout();
            this.grpMover.SuspendLayout();
            this.grpSetup.SuspendLayout();
            this.grpAction.SuspendLayout();
            this.grpHotel1.SuspendLayout();
            this.grpHotel2.SuspendLayout();
            this.SuspendLayout();
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.connectToolStripMenuItem,
            this.editINIToolStripMenuItem,
            this.optionsToolStripMenuItem,
            this.loggingToolStripMenuItem,
            this.helpToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(1268, 28);
            this.menuStrip1.TabIndex = 0;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // connectToolStripMenuItem
            // 
            this.connectToolStripMenuItem.Name = "connectToolStripMenuItem";
            this.connectToolStripMenuItem.Size = new System.Drawing.Size(75, 24);
            this.connectToolStripMenuItem.Text = "Connect";
            this.connectToolStripMenuItem.Click += new System.EventHandler(this.connectToolStripMenuItem_Click);
            // 
            // editINIToolStripMenuItem
            // 
            this.editINIToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.loaderINIToolStripMenuItem});
            this.editINIToolStripMenuItem.Enabled = false;
            this.editINIToolStripMenuItem.Name = "editINIToolStripMenuItem";
            this.editINIToolStripMenuItem.Size = new System.Drawing.Size(47, 24);
            this.editINIToolStripMenuItem.Text = "Edit";
            // 
            // loaderINIToolStripMenuItem
            // 
            this.loaderINIToolStripMenuItem.Name = "loaderINIToolStripMenuItem";
            this.loaderINIToolStripMenuItem.Size = new System.Drawing.Size(144, 24);
            this.loaderINIToolStripMenuItem.Text = "loader INI";
            this.loaderINIToolStripMenuItem.Click += new System.EventHandler(this.loaderINIToolStripMenuItem_Click);
            // 
            // optionsToolStripMenuItem
            // 
            this.optionsToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.singleStepModeToolStripMenuItem,
            this.doSoakToolStripMenuItem,
            this.scanOnlySoakToolStripMenuItem,
            this.stageRasterEnabledToolStripMenuItem});
            this.optionsToolStripMenuItem.Enabled = false;
            this.optionsToolStripMenuItem.Name = "optionsToolStripMenuItem";
            this.optionsToolStripMenuItem.Size = new System.Drawing.Size(73, 24);
            this.optionsToolStripMenuItem.Text = "Options";
            // 
            // singleStepModeToolStripMenuItem
            // 
            this.singleStepModeToolStripMenuItem.CheckOnClick = true;
            this.singleStepModeToolStripMenuItem.Name = "singleStepModeToolStripMenuItem";
            this.singleStepModeToolStripMenuItem.Size = new System.Drawing.Size(219, 24);
            this.singleStepModeToolStripMenuItem.Text = "Single Step Mode";
            this.singleStepModeToolStripMenuItem.Click += new System.EventHandler(this.singleStepModeToolStripMenuItem_Click);
            // 
            // doSoakToolStripMenuItem
            // 
            this.doSoakToolStripMenuItem.CheckOnClick = true;
            this.doSoakToolStripMenuItem.Name = "doSoakToolStripMenuItem";
            this.doSoakToolStripMenuItem.Size = new System.Drawing.Size(219, 24);
            this.doSoakToolStripMenuItem.Text = "Full Soak";
            this.doSoakToolStripMenuItem.Click += new System.EventHandler(this.doSoakToolStripMenuItem_Click);
            // 
            // scanOnlySoakToolStripMenuItem
            // 
            this.scanOnlySoakToolStripMenuItem.CheckOnClick = true;
            this.scanOnlySoakToolStripMenuItem.Name = "scanOnlySoakToolStripMenuItem";
            this.scanOnlySoakToolStripMenuItem.Size = new System.Drawing.Size(219, 24);
            this.scanOnlySoakToolStripMenuItem.Text = "Scan Hotel Soak";
            this.scanOnlySoakToolStripMenuItem.Click += new System.EventHandler(this.scanOnlySoakToolStripMenuItem_Click);
            // 
            // stageRasterEnabledToolStripMenuItem
            // 
            this.stageRasterEnabledToolStripMenuItem.CheckOnClick = true;
            this.stageRasterEnabledToolStripMenuItem.Name = "stageRasterEnabledToolStripMenuItem";
            this.stageRasterEnabledToolStripMenuItem.Size = new System.Drawing.Size(219, 24);
            this.stageRasterEnabledToolStripMenuItem.Text = "Stage Raster Enabled";
            // 
            // loggingToolStripMenuItem
            // 
            this.loggingToolStripMenuItem.CheckOnClick = true;
            this.loggingToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.enabledToolStripMenuItem});
            this.loggingToolStripMenuItem.Name = "loggingToolStripMenuItem";
            this.loggingToolStripMenuItem.Size = new System.Drawing.Size(76, 24);
            this.loggingToolStripMenuItem.Text = "Logging";
            // 
            // enabledToolStripMenuItem
            // 
            this.enabledToolStripMenuItem.CheckOnClick = true;
            this.enabledToolStripMenuItem.Name = "enabledToolStripMenuItem";
            this.enabledToolStripMenuItem.Size = new System.Drawing.Size(99, 24);
            this.enabledToolStripMenuItem.Text = "Off";
            this.enabledToolStripMenuItem.Click += new System.EventHandler(this.enabledToolStripMenuItem_Click);
            // 
            // helpToolStripMenuItem
            // 
            this.helpToolStripMenuItem.Name = "helpToolStripMenuItem";
            this.helpToolStripMenuItem.Size = new System.Drawing.Size(53, 24);
            this.helpToolStripMenuItem.Text = "Help";
            this.helpToolStripMenuItem.Click += new System.EventHandler(this.helpToolStripMenuItem_Click);
            // 
            // grpStatus
            // 
            this.grpStatus.BackColor = System.Drawing.SystemColors.Control;
            this.grpStatus.Controls.Add(this.lblEject);
            this.grpStatus.Controls.Add(this.lblStallError);
            this.grpStatus.Controls.Add(this.lblSlideSensorError);
            this.grpStatus.Controls.Add(this.lblCommsError);
            this.grpStatus.Controls.Add(this.lblCassetteNotScanned);
            this.grpStatus.Controls.Add(this.lblNotIdle);
            this.grpStatus.Controls.Add(this.lblSlideOnStage);
            this.grpStatus.Controls.Add(this.lblInvalidCassette);
            this.grpStatus.Controls.Add(this.lblInvalidSlide);
            this.grpStatus.Controls.Add(this.lblNotSetup);
            this.grpStatus.Controls.Add(this.lblNotInitialised);
            this.grpStatus.Controls.Add(this.lblNotConnected);
            this.grpStatus.Controls.Add(this.lblError);
            this.grpStatus.Font = new System.Drawing.Font("Microsoft Sans Serif", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.grpStatus.ForeColor = System.Drawing.SystemColors.ControlText;
            this.grpStatus.Location = new System.Drawing.Point(354, 56);
            this.grpStatus.Name = "grpStatus";
            this.grpStatus.Padding = new System.Windows.Forms.Padding(0);
            this.grpStatus.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.grpStatus.Size = new System.Drawing.Size(184, 458);
            this.grpStatus.TabIndex = 779;
            this.grpStatus.TabStop = false;
            this.grpStatus.Text = "Loader Status";
            // 
            // lblEject
            // 
            this.lblEject.BackColor = System.Drawing.SystemColors.Control;
            this.lblEject.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblEject.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblEject.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblEject.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblEject.Location = new System.Drawing.Point(8, 325);
            this.lblEject.Name = "lblEject";
            this.lblEject.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblEject.Size = new System.Drawing.Size(164, 23);
            this.lblEject.TabIndex = 762;
            this.lblEject.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblStallError
            // 
            this.lblStallError.BackColor = System.Drawing.SystemColors.Control;
            this.lblStallError.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblStallError.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblStallError.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblStallError.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblStallError.Location = new System.Drawing.Point(8, 418);
            this.lblStallError.Name = "lblStallError";
            this.lblStallError.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblStallError.Size = new System.Drawing.Size(164, 23);
            this.lblStallError.TabIndex = 761;
            this.lblStallError.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblSlideSensorError
            // 
            this.lblSlideSensorError.BackColor = System.Drawing.SystemColors.Control;
            this.lblSlideSensorError.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblSlideSensorError.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblSlideSensorError.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSlideSensorError.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblSlideSensorError.Location = new System.Drawing.Point(8, 387);
            this.lblSlideSensorError.Name = "lblSlideSensorError";
            this.lblSlideSensorError.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblSlideSensorError.Size = new System.Drawing.Size(164, 23);
            this.lblSlideSensorError.TabIndex = 759;
            this.lblSlideSensorError.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblCommsError
            // 
            this.lblCommsError.BackColor = System.Drawing.SystemColors.Control;
            this.lblCommsError.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblCommsError.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblCommsError.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCommsError.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblCommsError.Location = new System.Drawing.Point(8, 356);
            this.lblCommsError.Name = "lblCommsError";
            this.lblCommsError.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblCommsError.Size = new System.Drawing.Size(164, 23);
            this.lblCommsError.TabIndex = 758;
            this.lblCommsError.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblCassetteNotScanned
            // 
            this.lblCassetteNotScanned.BackColor = System.Drawing.SystemColors.Control;
            this.lblCassetteNotScanned.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblCassetteNotScanned.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblCassetteNotScanned.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCassetteNotScanned.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblCassetteNotScanned.Location = new System.Drawing.Point(8, 294);
            this.lblCassetteNotScanned.Name = "lblCassetteNotScanned";
            this.lblCassetteNotScanned.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblCassetteNotScanned.Size = new System.Drawing.Size(164, 23);
            this.lblCassetteNotScanned.TabIndex = 22;
            this.lblCassetteNotScanned.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblNotIdle
            // 
            this.lblNotIdle.BackColor = System.Drawing.SystemColors.Control;
            this.lblNotIdle.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblNotIdle.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblNotIdle.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblNotIdle.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblNotIdle.Location = new System.Drawing.Point(8, 170);
            this.lblNotIdle.Name = "lblNotIdle";
            this.lblNotIdle.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblNotIdle.Size = new System.Drawing.Size(164, 23);
            this.lblNotIdle.TabIndex = 19;
            this.lblNotIdle.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblSlideOnStage
            // 
            this.lblSlideOnStage.BackColor = System.Drawing.SystemColors.Control;
            this.lblSlideOnStage.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblSlideOnStage.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblSlideOnStage.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSlideOnStage.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblSlideOnStage.Location = new System.Drawing.Point(8, 201);
            this.lblSlideOnStage.Name = "lblSlideOnStage";
            this.lblSlideOnStage.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblSlideOnStage.Size = new System.Drawing.Size(164, 23);
            this.lblSlideOnStage.TabIndex = 16;
            this.lblSlideOnStage.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblInvalidCassette
            // 
            this.lblInvalidCassette.BackColor = System.Drawing.SystemColors.Control;
            this.lblInvalidCassette.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblInvalidCassette.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblInvalidCassette.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblInvalidCassette.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblInvalidCassette.Location = new System.Drawing.Point(8, 263);
            this.lblInvalidCassette.Name = "lblInvalidCassette";
            this.lblInvalidCassette.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblInvalidCassette.Size = new System.Drawing.Size(164, 23);
            this.lblInvalidCassette.TabIndex = 15;
            this.lblInvalidCassette.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblInvalidSlide
            // 
            this.lblInvalidSlide.BackColor = System.Drawing.SystemColors.Control;
            this.lblInvalidSlide.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblInvalidSlide.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblInvalidSlide.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblInvalidSlide.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblInvalidSlide.Location = new System.Drawing.Point(8, 232);
            this.lblInvalidSlide.Name = "lblInvalidSlide";
            this.lblInvalidSlide.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblInvalidSlide.Size = new System.Drawing.Size(164, 23);
            this.lblInvalidSlide.TabIndex = 14;
            this.lblInvalidSlide.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblNotSetup
            // 
            this.lblNotSetup.BackColor = System.Drawing.SystemColors.Control;
            this.lblNotSetup.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblNotSetup.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblNotSetup.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblNotSetup.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblNotSetup.Location = new System.Drawing.Point(8, 139);
            this.lblNotSetup.Name = "lblNotSetup";
            this.lblNotSetup.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblNotSetup.Size = new System.Drawing.Size(164, 23);
            this.lblNotSetup.TabIndex = 13;
            this.lblNotSetup.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblNotInitialised
            // 
            this.lblNotInitialised.BackColor = System.Drawing.SystemColors.Control;
            this.lblNotInitialised.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblNotInitialised.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblNotInitialised.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblNotInitialised.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblNotInitialised.Location = new System.Drawing.Point(8, 108);
            this.lblNotInitialised.Name = "lblNotInitialised";
            this.lblNotInitialised.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblNotInitialised.Size = new System.Drawing.Size(164, 23);
            this.lblNotInitialised.TabIndex = 12;
            this.lblNotInitialised.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblNotConnected
            // 
            this.lblNotConnected.BackColor = System.Drawing.SystemColors.Control;
            this.lblNotConnected.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblNotConnected.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblNotConnected.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblNotConnected.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblNotConnected.Location = new System.Drawing.Point(8, 77);
            this.lblNotConnected.Name = "lblNotConnected";
            this.lblNotConnected.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblNotConnected.Size = new System.Drawing.Size(164, 23);
            this.lblNotConnected.TabIndex = 11;
            this.lblNotConnected.Text = "NOT CONNECTED";
            this.lblNotConnected.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // lblError
            // 
            this.lblError.BackColor = System.Drawing.SystemColors.Control;
            this.lblError.BorderStyle = System.Windows.Forms.BorderStyle.Fixed3D;
            this.lblError.Cursor = System.Windows.Forms.Cursors.Default;
            this.lblError.Font = new System.Drawing.Font("Times New Roman", 7.8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblError.ForeColor = System.Drawing.SystemColors.ControlText;
            this.lblError.Location = new System.Drawing.Point(8, 46);
            this.lblError.Name = "lblError";
            this.lblError.RightToLeft = System.Windows.Forms.RightToLeft.No;
            this.lblError.Size = new System.Drawing.Size(164, 23);
            this.lblError.TabIndex = 10;
            this.lblError.Text = "ERROR";
            this.lblError.TextAlign = System.Drawing.ContentAlignment.MiddleCenter;
            // 
            // statusStrip
            // 
            this.statusStrip.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.lblstate,
            this.lbltime,
            this.lblSoakCount,
            this.lbllasterror});
            this.statusStrip.Location = new System.Drawing.Point(0, 617);
            this.statusStrip.Name = "statusStrip";
            this.statusStrip.Size = new System.Drawing.Size(1268, 26);
            this.statusStrip.TabIndex = 780;
            this.statusStrip.Text = "statusStrip1";
            // 
            // lblstate
            // 
            this.lblstate.BorderSides = ((System.Windows.Forms.ToolStripStatusLabelBorderSides)((((System.Windows.Forms.ToolStripStatusLabelBorderSides.Left | System.Windows.Forms.ToolStripStatusLabelBorderSides.Top) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Right) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Bottom)));
            this.lblstate.BorderStyle = System.Windows.Forms.Border3DStyle.Sunken;
            this.lblstate.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblstate.Name = "lblstate";
            this.lblstate.Size = new System.Drawing.Size(135, 21);
            this.lblstate.Text = "TXF_FROMSTAGE";
            // 
            // lbltime
            // 
            this.lbltime.BorderSides = ((System.Windows.Forms.ToolStripStatusLabelBorderSides)((((System.Windows.Forms.ToolStripStatusLabelBorderSides.Left | System.Windows.Forms.ToolStripStatusLabelBorderSides.Top) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Right) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Bottom)));
            this.lbltime.BorderStyle = System.Windows.Forms.Border3DStyle.Sunken;
            this.lbltime.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lbltime.Name = "lbltime";
            this.lbltime.Size = new System.Drawing.Size(32, 21);
            this.lbltime.Text = "12s";
            // 
            // lblSoakCount
            // 
            this.lblSoakCount.BorderSides = ((System.Windows.Forms.ToolStripStatusLabelBorderSides)((((System.Windows.Forms.ToolStripStatusLabelBorderSides.Left | System.Windows.Forms.ToolStripStatusLabelBorderSides.Top) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Right) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Bottom)));
            this.lblSoakCount.BorderStyle = System.Windows.Forms.Border3DStyle.Sunken;
            this.lblSoakCount.Name = "lblSoakCount";
            this.lblSoakCount.Size = new System.Drawing.Size(4, 21);
            // 
            // lbllasterror
            // 
            this.lbllasterror.BorderSides = ((System.Windows.Forms.ToolStripStatusLabelBorderSides)((((System.Windows.Forms.ToolStripStatusLabelBorderSides.Left | System.Windows.Forms.ToolStripStatusLabelBorderSides.Top) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Right) 
            | System.Windows.Forms.ToolStripStatusLabelBorderSides.Bottom)));
            this.lbllasterror.BorderStyle = System.Windows.Forms.Border3DStyle.Sunken;
            this.lbllasterror.Font = new System.Drawing.Font("Times New Roman", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lbllasterror.Name = "lbllasterror";
            this.lbllasterror.Size = new System.Drawing.Size(86, 21);
            this.lbllasterror.Text = "LAST_ERR";
            this.lbllasterror.Click += new System.EventHandler(this.lbllasterror_Click);
            // 
            // grpMover
            // 
            this.grpMover.Controls.Add(this.chkSTM);
            this.grpMover.Controls.Add(this.chkHLM);
            this.grpMover.Controls.Add(this.chkHSM);
            this.grpMover.Controls.Add(this.chkVelocity);
            this.grpMover.Controls.Add(this.rb10mm);
            this.grpMover.Controls.Add(this.rb1mm);
            this.grpMover.Controls.Add(this.rbpoint1mm);
            this.grpMover.Controls.Add(this.Yminus);
            this.grpMover.Controls.Add(this.Yplus);
            this.grpMover.Controls.Add(this.label3);
            this.grpMover.Controls.Add(this.Zminus);
            this.grpMover.Controls.Add(this.Zplus);
            this.grpMover.Controls.Add(this.label2);
            this.grpMover.Controls.Add(this.Xminus);
            this.grpMover.Controls.Add(this.Xplus);
            this.grpMover.Controls.Add(this.label1);
            this.grpMover.Location = new System.Drawing.Point(557, 416);
            this.grpMover.Name = "grpMover";
            this.grpMover.Size = new System.Drawing.Size(631, 187);
            this.grpMover.TabIndex = 799;
            this.grpMover.TabStop = false;
            this.grpMover.Text = "Manual Mover (Jog)";
            // 
            // chkSTM
            // 
            this.chkSTM.AutoSize = true;
            this.chkSTM.Location = new System.Drawing.Point(474, 142);
            this.chkSTM.Name = "chkSTM";
            this.chkSTM.Size = new System.Drawing.Size(116, 21);
            this.chkSTM.TabIndex = 824;
            this.chkSTM.Text = "STM disabled";
            this.chkSTM.UseVisualStyleBackColor = true;
            this.chkSTM.CheckedChanged += new System.EventHandler(this.chkSTM_CheckedChanged);
            // 
            // chkHLM
            // 
            this.chkHLM.AutoSize = true;
            this.chkHLM.Location = new System.Drawing.Point(474, 87);
            this.chkHLM.Name = "chkHLM";
            this.chkHLM.Size = new System.Drawing.Size(116, 21);
            this.chkHLM.TabIndex = 823;
            this.chkHLM.Text = "HLM disabled";
            this.chkHLM.UseVisualStyleBackColor = true;
            this.chkHLM.CheckedChanged += new System.EventHandler(this.chkHLM_CheckedChanged);
            // 
            // chkHSM
            // 
            this.chkHSM.AutoSize = true;
            this.chkHSM.Location = new System.Drawing.Point(473, 29);
            this.chkHSM.Name = "chkHSM";
            this.chkHSM.Size = new System.Drawing.Size(117, 21);
            this.chkHSM.TabIndex = 822;
            this.chkHSM.Text = "HSM disabled";
            this.chkHSM.UseVisualStyleBackColor = true;
            this.chkHSM.CheckedChanged += new System.EventHandler(this.chkHSM_CheckedChanged);
            // 
            // chkVelocity
            // 
            this.chkVelocity.AutoSize = true;
            this.chkVelocity.Checked = true;
            this.chkVelocity.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkVelocity.Location = new System.Drawing.Point(25, 143);
            this.chkVelocity.Name = "chkVelocity";
            this.chkVelocity.Size = new System.Drawing.Size(116, 21);
            this.chkVelocity.TabIndex = 821;
            this.chkVelocity.Text = "velocity mode";
            this.chkVelocity.UseVisualStyleBackColor = true;
            this.chkVelocity.CheckedChanged += new System.EventHandler(this.chkVelocity_CheckedChanged);
            // 
            // rb10mm
            // 
            this.rb10mm.AutoSize = true;
            this.rb10mm.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.2F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.rb10mm.Location = new System.Drawing.Point(25, 104);
            this.rb10mm.Name = "rb10mm";
            this.rb10mm.Size = new System.Drawing.Size(81, 24);
            this.rb10mm.TabIndex = 20;
            this.rb10mm.Text = "10 mm";
            this.rb10mm.UseVisualStyleBackColor = true;
            this.rb10mm.CheckedChanged += new System.EventHandler(this.rb10mm_CheckedChanged);
            // 
            // rb1mm
            // 
            this.rb1mm.AutoSize = true;
            this.rb1mm.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.2F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.rb1mm.Location = new System.Drawing.Point(25, 69);
            this.rb1mm.Name = "rb1mm";
            this.rb1mm.Size = new System.Drawing.Size(72, 24);
            this.rb1mm.TabIndex = 19;
            this.rb1mm.Text = "1 mm";
            this.rb1mm.UseVisualStyleBackColor = true;
            this.rb1mm.CheckedChanged += new System.EventHandler(this.rb1mm_CheckedChanged);
            // 
            // rbpoint1mm
            // 
            this.rbpoint1mm.AutoSize = true;
            this.rbpoint1mm.Checked = true;
            this.rbpoint1mm.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.2F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.rbpoint1mm.Location = new System.Drawing.Point(25, 34);
            this.rbpoint1mm.Name = "rbpoint1mm";
            this.rbpoint1mm.Size = new System.Drawing.Size(85, 24);
            this.rbpoint1mm.TabIndex = 19;
            this.rbpoint1mm.TabStop = true;
            this.rbpoint1mm.Text = "0.1 mm";
            this.rbpoint1mm.UseVisualStyleBackColor = true;
            this.rbpoint1mm.CheckedChanged += new System.EventHandler(this.rbpoint1mm_CheckedChanged);
            // 
            // Yminus
            // 
            this.Yminus.BackColor = System.Drawing.SystemColors.Control;
            this.Yminus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Yminus.Location = new System.Drawing.Point(291, 75);
            this.Yminus.Margin = new System.Windows.Forms.Padding(4);
            this.Yminus.Name = "Yminus";
            this.Yminus.Size = new System.Drawing.Size(60, 40);
            this.Yminus.TabIndex = 14;
            this.Yminus.Text = "-";
            this.Yminus.UseVisualStyleBackColor = false;
            // 
            // Yplus
            // 
            this.Yplus.BackColor = System.Drawing.SystemColors.Control;
            this.Yplus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Yplus.Location = new System.Drawing.Point(407, 75);
            this.Yplus.Margin = new System.Windows.Forms.Padding(4);
            this.Yplus.Name = "Yplus";
            this.Yplus.Size = new System.Drawing.Size(60, 40);
            this.Yplus.TabIndex = 15;
            this.Yplus.Text = "+";
            this.Yplus.UseVisualStyleBackColor = false;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.BackColor = System.Drawing.SystemColors.Control;
            this.label3.Location = new System.Drawing.Point(362, 88);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(37, 17);
            this.label3.TabIndex = 805;
            this.label3.Text = "HLM";
            // 
            // Zminus
            // 
            this.Zminus.BackColor = System.Drawing.SystemColors.Control;
            this.Zminus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Zminus.Location = new System.Drawing.Point(291, 132);
            this.Zminus.Margin = new System.Windows.Forms.Padding(4);
            this.Zminus.Name = "Zminus";
            this.Zminus.Size = new System.Drawing.Size(60, 40);
            this.Zminus.TabIndex = 16;
            this.Zminus.Text = "-";
            this.Zminus.UseVisualStyleBackColor = false;
            // 
            // Zplus
            // 
            this.Zplus.BackColor = System.Drawing.SystemColors.Control;
            this.Zplus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Zplus.Location = new System.Drawing.Point(407, 132);
            this.Zplus.Margin = new System.Windows.Forms.Padding(4);
            this.Zplus.Name = "Zplus";
            this.Zplus.Size = new System.Drawing.Size(60, 40);
            this.Zplus.TabIndex = 17;
            this.Zplus.Text = "+";
            this.Zplus.UseVisualStyleBackColor = false;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.BackColor = System.Drawing.SystemColors.Control;
            this.label2.Location = new System.Drawing.Point(364, 143);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(37, 17);
            this.label2.TabIndex = 802;
            this.label2.Text = "STM";
            // 
            // Xminus
            // 
            this.Xminus.BackColor = System.Drawing.SystemColors.Control;
            this.Xminus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Xminus.Location = new System.Drawing.Point(291, 18);
            this.Xminus.Margin = new System.Windows.Forms.Padding(4);
            this.Xminus.Name = "Xminus";
            this.Xminus.Size = new System.Drawing.Size(60, 40);
            this.Xminus.TabIndex = 12;
            this.Xminus.Text = "-";
            this.Xminus.UseVisualStyleBackColor = false;
            // 
            // Xplus
            // 
            this.Xplus.BackColor = System.Drawing.SystemColors.Control;
            this.Xplus.Font = new System.Drawing.Font("Microsoft Sans Serif", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Xplus.Location = new System.Drawing.Point(407, 18);
            this.Xplus.Margin = new System.Windows.Forms.Padding(4);
            this.Xplus.Name = "Xplus";
            this.Xplus.Size = new System.Drawing.Size(60, 40);
            this.Xplus.TabIndex = 13;
            this.Xplus.Text = "+";
            this.Xplus.UseVisualStyleBackColor = false;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.BackColor = System.Drawing.SystemColors.Control;
            this.label1.Location = new System.Drawing.Point(361, 29);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(38, 17);
            this.label1.TabIndex = 799;
            this.label1.Text = "HSM";
            // 
            // grpSetup
            // 
            this.grpSetup.Controls.Add(this.lstHelp);
            this.grpSetup.Controls.Add(this.btnAction);
            this.grpSetup.Location = new System.Drawing.Point(557, 56);
            this.grpSetup.Name = "grpSetup";
            this.grpSetup.Size = new System.Drawing.Size(659, 354);
            this.grpSetup.TabIndex = 800;
            this.grpSetup.TabStop = false;
            this.grpSetup.Text = "Initialise";
            // 
            // lstHelp
            // 
            this.lstHelp.Font = new System.Drawing.Font("Microsoft Sans Serif", 10.2F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lstHelp.FormattingEnabled = true;
            this.lstHelp.ItemHeight = 20;
            this.lstHelp.Items.AddRange(new object[] {
            " ",
            "Click \'Save and Exit\' to leave calibration. This will take several seconds."});
            this.lstHelp.Location = new System.Drawing.Point(10, 24);
            this.lstHelp.Name = "lstHelp";
            this.lstHelp.Size = new System.Drawing.Size(638, 264);
            this.lstHelp.TabIndex = 21;
            // 
            // btnAction
            // 
            this.btnAction.Location = new System.Drawing.Point(10, 302);
            this.btnAction.Name = "btnAction";
            this.btnAction.Size = new System.Drawing.Size(208, 39);
            this.btnAction.TabIndex = 0;
            this.btnAction.Text = "Initialise";
            this.btnAction.UseVisualStyleBackColor = true;
            this.btnAction.Click += new System.EventHandler(this.btnAction_Click);
            // 
            // grpAction
            // 
            this.grpAction.Controls.Add(this.btnPreview);
            this.grpAction.Controls.Add(this.btnLoadHotels);
            this.grpAction.Controls.Add(this.btnEjectHotels);
            this.grpAction.Controls.Add(this.btnToHotel);
            this.grpAction.Controls.Add(this.btnToStage);
            this.grpAction.Enabled = false;
            this.grpAction.Location = new System.Drawing.Point(8, 56);
            this.grpAction.Name = "grpAction";
            this.grpAction.Size = new System.Drawing.Size(128, 310);
            this.grpAction.TabIndex = 816;
            this.grpAction.TabStop = false;
            this.grpAction.Text = "Action";
            // 
            // btnPreview
            // 
            this.btnPreview.Location = new System.Drawing.Point(8, 170);
            this.btnPreview.Name = "btnPreview";
            this.btnPreview.Size = new System.Drawing.Size(110, 30);
            this.btnPreview.TabIndex = 7;
            this.btnPreview.Text = "Preview 1?";
            this.btnPreview.UseVisualStyleBackColor = true;
            this.btnPreview.Click += new System.EventHandler(this.btnPreview_Click);
            // 
            // btnLoadHotels
            // 
            this.btnLoadHotels.Location = new System.Drawing.Point(8, 266);
            this.btnLoadHotels.Name = "btnLoadHotels";
            this.btnLoadHotels.Size = new System.Drawing.Size(110, 30);
            this.btnLoadHotels.TabIndex = 10;
            this.btnLoadHotels.Text = "Insert Hotels";
            this.btnLoadHotels.UseVisualStyleBackColor = true;
            this.btnLoadHotels.Click += new System.EventHandler(this.btnLoadHotels_Click);
            // 
            // btnEjectHotels
            // 
            this.btnEjectHotels.Location = new System.Drawing.Point(8, 222);
            this.btnEjectHotels.Name = "btnEjectHotels";
            this.btnEjectHotels.Size = new System.Drawing.Size(110, 30);
            this.btnEjectHotels.TabIndex = 9;
            this.btnEjectHotels.Text = "Eject Hotels";
            this.btnEjectHotels.UseVisualStyleBackColor = true;
            this.btnEjectHotels.Click += new System.EventHandler(this.btnEjectHotels_Click);
            // 
            // btnToHotel
            // 
            this.btnToHotel.Location = new System.Drawing.Point(9, 97);
            this.btnToHotel.Name = "btnToHotel";
            this.btnToHotel.Size = new System.Drawing.Size(110, 48);
            this.btnToHotel.TabIndex = 8;
            this.btnToHotel.Text = "Unload Tray\r\nFrom Stage";
            this.btnToHotel.UseVisualStyleBackColor = true;
            this.btnToHotel.Click += new System.EventHandler(this.btnToHotel_Click);
            // 
            // btnToStage
            // 
            this.btnToStage.Location = new System.Drawing.Point(9, 37);
            this.btnToStage.Name = "btnToStage";
            this.btnToStage.Size = new System.Drawing.Size(110, 48);
            this.btnToStage.TabIndex = 6;
            this.btnToStage.Text = "Load Tray\r\nTo Stage";
            this.btnToStage.UseVisualStyleBackColor = true;
            this.btnToStage.Click += new System.EventHandler(this.btnToStage_Click);
            // 
            // grpHotel1
            // 
            this.grpHotel1.Controls.Add(this.btnScan1);
            this.grpHotel1.Enabled = false;
            this.grpHotel1.Location = new System.Drawing.Point(142, 56);
            this.grpHotel1.Name = "grpHotel1";
            this.grpHotel1.Size = new System.Drawing.Size(100, 547);
            this.grpHotel1.TabIndex = 8;
            this.grpHotel1.TabStop = false;
            this.grpHotel1.Tag = "1";
            this.grpHotel1.Text = "Hotel 1";
            // 
            // btnScan1
            // 
            this.btnScan1.Location = new System.Drawing.Point(9, 511);
            this.btnScan1.Name = "btnScan1";
            this.btnScan1.Size = new System.Drawing.Size(82, 30);
            this.btnScan1.TabIndex = 4;
            this.btnScan1.Text = "Scan";
            this.btnScan1.UseVisualStyleBackColor = true;
            this.btnScan1.Click += new System.EventHandler(this.btnScan1_Click);
            // 
            // btndummy
            // 
            this.btndummy.Location = new System.Drawing.Point(1247, 278);
            this.btndummy.Name = "btndummy";
            this.btndummy.Size = new System.Drawing.Size(114, 39);
            this.btndummy.TabIndex = 0;
            this.btndummy.Text = "dummy";
            this.btndummy.UseVisualStyleBackColor = true;
            // 
            // btnSingle
            // 
            this.btnSingle.Enabled = false;
            this.btnSingle.Location = new System.Drawing.Point(16, 567);
            this.btnSingle.Name = "btnSingle";
            this.btnSingle.Size = new System.Drawing.Size(110, 30);
            this.btnSingle.TabIndex = 817;
            this.btnSingle.Text = "Single step";
            this.btnSingle.UseVisualStyleBackColor = true;
            this.btnSingle.Click += new System.EventHandler(this.btnSingle_Click);
            // 
            // btnStop
            // 
            this.btnStop.Enabled = false;
            this.btnStop.Location = new System.Drawing.Point(392, 567);
            this.btnStop.Name = "btnStop";
            this.btnStop.Size = new System.Drawing.Size(110, 30);
            this.btnStop.TabIndex = 818;
            this.btnStop.Text = "Stop";
            this.btnStop.UseVisualStyleBackColor = true;
            this.btnStop.Click += new System.EventHandler(this.btnStop_Click);
            // 
            // grpHotel2
            // 
            this.grpHotel2.Controls.Add(this.btnScan2);
            this.grpHotel2.Enabled = false;
            this.grpHotel2.Location = new System.Drawing.Point(248, 56);
            this.grpHotel2.Name = "grpHotel2";
            this.grpHotel2.Size = new System.Drawing.Size(100, 547);
            this.grpHotel2.TabIndex = 819;
            this.grpHotel2.TabStop = false;
            this.grpHotel2.Tag = "2";
            this.grpHotel2.Text = "Hotel 2";
            // 
            // btnScan2
            // 
            this.btnScan2.Location = new System.Drawing.Point(9, 511);
            this.btnScan2.Name = "btnScan2";
            this.btnScan2.Size = new System.Drawing.Size(82, 30);
            this.btnScan2.TabIndex = 5;
            this.btnScan2.Text = "Scan";
            this.btnScan2.UseVisualStyleBackColor = true;
            this.btnScan2.Click += new System.EventHandler(this.btnScan2_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1268, 643);
            this.Controls.Add(this.grpHotel2);
            this.Controls.Add(this.btnStop);
            this.Controls.Add(this.btnSingle);
            this.Controls.Add(this.btndummy);
            this.Controls.Add(this.grpHotel1);
            this.Controls.Add(this.grpAction);
            this.Controls.Add(this.grpSetup);
            this.Controls.Add(this.grpMover);
            this.Controls.Add(this.statusStrip);
            this.Controls.Add(this.grpStatus);
            this.Controls.Add(this.menuStrip1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.MainMenuStrip = this.menuStrip1;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "SL160_Demo";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.Form1_FormClosing);
            this.Load += new System.EventHandler(this.Form1_Load);
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.grpStatus.ResumeLayout(false);
            this.statusStrip.ResumeLayout(false);
            this.statusStrip.PerformLayout();
            this.grpMover.ResumeLayout(false);
            this.grpMover.PerformLayout();
            this.grpSetup.ResumeLayout(false);
            this.grpAction.ResumeLayout(false);
            this.grpHotel1.ResumeLayout(false);
            this.grpHotel2.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem connectToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem editINIToolStripMenuItem;
        public System.Windows.Forms.GroupBox grpStatus;
        public System.Windows.Forms.Label lblStallError;
        public System.Windows.Forms.Label lblSlideSensorError;
        public System.Windows.Forms.Label lblCommsError;
        public System.Windows.Forms.Label lblCassetteNotScanned;
        public System.Windows.Forms.Label lblNotIdle;
        public System.Windows.Forms.Label lblSlideOnStage;
        public System.Windows.Forms.Label lblInvalidCassette;
        public System.Windows.Forms.Label lblInvalidSlide;
        public System.Windows.Forms.Label lblNotSetup;
        public System.Windows.Forms.Label lblNotInitialised;
        public System.Windows.Forms.Label lblNotConnected;
        public System.Windows.Forms.Label lblError;
        private System.Windows.Forms.StatusStrip statusStrip;
        private System.Windows.Forms.GroupBox grpMover;
        private System.Windows.Forms.Button Yminus;
        private System.Windows.Forms.Button Yplus;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Button Zminus;
        private System.Windows.Forms.Button Zplus;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button Xminus;
        private System.Windows.Forms.Button Xplus;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.GroupBox grpSetup;
        private System.Windows.Forms.ListBox lstHelp;
        private System.Windows.Forms.Button btnAction;
        private System.Windows.Forms.ToolStripStatusLabel lblstate;
        private System.Windows.Forms.ToolStripStatusLabel lbltime;
        private System.Windows.Forms.ToolStripStatusLabel lbllasterror;
        private System.Windows.Forms.ToolStripMenuItem optionsToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem singleStepModeToolStripMenuItem;
        private System.Windows.Forms.GroupBox grpAction;
        private System.Windows.Forms.Button btnToHotel;
        private System.Windows.Forms.Button btnToStage;
        private System.Windows.Forms.GroupBox grpHotel1;
        private System.Windows.Forms.ToolStripMenuItem helpToolStripMenuItem;
        private System.Windows.Forms.Button btndummy;
        private System.Windows.Forms.ToolStripMenuItem doSoakToolStripMenuItem;
        private System.Windows.Forms.Button btnSingle;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.ToolStripMenuItem loaderINIToolStripMenuItem;
        private System.Windows.Forms.ToolStripStatusLabel lblSoakCount;
        private System.Windows.Forms.GroupBox grpHotel2;
        private System.Windows.Forms.Button btnLoadHotels;
        private System.Windows.Forms.Button btnEjectHotels;
        private System.Windows.Forms.RadioButton rb10mm;
        private System.Windows.Forms.RadioButton rb1mm;
        private System.Windows.Forms.RadioButton rbpoint1mm;
        private System.Windows.Forms.Button btnPreview;
        private System.Windows.Forms.Button btnScan1;
        private System.Windows.Forms.Button btnScan2;
        private System.Windows.Forms.CheckBox chkVelocity;
        private System.Windows.Forms.CheckBox chkSTM;
        private System.Windows.Forms.CheckBox chkHLM;
        private System.Windows.Forms.CheckBox chkHSM;
        private System.Windows.Forms.ToolStripMenuItem loggingToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem enabledToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem scanOnlySoakToolStripMenuItem;
        public System.Windows.Forms.Label lblEject;
        private System.Windows.Forms.ToolStripMenuItem stageRasterEnabledToolStripMenuItem;
    }
}

