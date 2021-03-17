using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WASLV2_LoaderDemo
{
    public partial class help : Form
    {
        StringBuilder _version;

        public help(StringBuilder ver)
        {
            InitializeComponent();

            _version = ver;
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void help_Load(object sender, EventArgs e)
        {
            listBox1.Items.Add(Application.ProductName + " " + Application.ProductVersion);
            listBox1.Items.Add("PriorScientificSDK " + _version.ToString());
            listBox1.Items.Add("");
            listBox1.Items.Add("WASLV2 Loader Calibration and soak test application");
            listBox1.Items.Add("");
            listBox1.Items.Add("1. Connect to PS3 and WASLV2 Loader using 'Connect' menu entry");
            listBox1.Items.Add("");
            listBox1.Items.Add("2. Follow instructions to Initialise the robot.");
            listBox1.Items.Add("");
            listBox1.Items.Add("3. Follow instructions to perform calibration during production.");
            listBox1.Items.Add("   Calibration data for loader is stored in stage eeprom and used to create");
            listBox1.Items.Add("   a user customizeable configuration file C:/ProgramData/Prior/WASLV2_LOADER_DATA-0.INI");
            listBox1.Items.Add("   NOTE: user application must use the same stage co-ordinate system and stage units as this program.");
            listBox1.Items.Add("   The exact stage initialisation sequence can be seen in the source for this program");
            listBox1.Items.Add("   Stage (0,0) point is stage front-right. Increasing position counts when moving back-left");
            listBox1.Items.Add("");
            listBox1.Items.Add("   The Jog buttons when clicked move the HLM and STM robot axes in 0.1/1/10mm steps.");
            listBox1.Items.Add("   In velocity mode these button when held down will move the robot axes ");
            listBox1.Items.Add("   at 0.1/1/10mm/s respectively");
            listBox1.Items.Add("");
            listBox1.Items.Add("   The stage will be automatically moved to the correct position to perform a scan/load/unload function");
            listBox1.Items.Add("");
            listBox1.Items.Add("4. 'Scan' function performs an auto detect of trays in apartments. Detected trays are marked in green");
            listBox1.Items.Add("");
            listBox1.Items.Add("5. 'Load Tray To Stage' button click followed by green apartment click will transfer that tray to the stage.");
            listBox1.Items.Add("   the tray will pause at preview 1/2/3/4 positions, click preview button to continue from each point.");
            listBox1.Items.Add("   (The preview is handled automatically during the automated soak routine)");
            listBox1.Items.Add("");
            listBox1.Items.Add("6. 'Unload Tray From Stage' button click followed by empty apartment click will transfer tray on stage to the empty apartment.");
            listBox1.Items.Add("");
            listBox1.Items.Add("7. 'Eject Hotels' click presents hotel to user for removal");
            listBox1.Items.Add("");
            listBox1.Items.Add("8. 'Insert Hotels' indicates a new hotel has been fitted");
            listBox1.Items.Add("");
            listBox1.Items.Add("9. 'options->single step mode' is a debug facility that allows the robot ");
            listBox1.Items.Add("    to be 'single stepped' through its operation. Useful during installation.");
            listBox1.Items.Add("");
            listBox1.Items.Add("10. 'options->start/stop soak' will start/stop an automated soak routine that will");
            listBox1.Items.Add("     cycle through all trays that have been detected during the scan");
            listBox1.Items.Add("");
            listBox1.Items.Add("Contact Prior Scientific for additional help");
        }
    }
}
