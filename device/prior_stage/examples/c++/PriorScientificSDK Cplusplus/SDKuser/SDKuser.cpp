// SDKuser.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "PriorScientificSDK.h"
#include <iostream> 
using namespace std; 

/* PriorScientificSDK.dll implicitly linked through PriorScientificSDK.lib. See solution properties */

/*  use c++ interface from PriorScientificSDK.h */
PriorScientificSDK priorSDK;

/* uncomment when real hw available */
//#define realhw

char rx[1000];
int ret;
int sessionID = 0;

int  cmd(char *tx)
{
	cout <<  tx << endl;
	if (!(ret = priorSDK.Cmd(sessionID,tx,rx)))
		cout <<  "OK " << rx << endl;
	else
		cout << "Api error " << ret << endl;

	system("pause");

	return 0;
}

int _tmain(int argc, _TCHAR* argv[])
{
	int stageFitted = 0;
	int stageBusy = 0;

	rx[0] = 0;

	/* always call Initialise first */
	ret = priorSDK.Initialise();

	if (ret != PRIOR_OK)
	{
		cout << "Error initialising " << ret << endl;
		return -1;
	}
	else
		cout << "Ok initialising " << ret << endl;
	
	/* get version number, check ret = 0, and rx contains correct version information */
	ret = priorSDK.Version((char *const)rx);

	cout << "dll version api ret=" << ret << ", version=" << rx << endl;

	/* create the session, can be up to 10 */
	sessionID = priorSDK.OpenSession();

	if (sessionID < 0)
	{
		cout << "Error getting sessionId " << ret << endl;
		return -1;
	}
	else
		cout << "sessionId " << sessionID << endl;
	
	/* calling again should get next sessionID as return value */
	sessionID = priorSDK.OpenSession();

	if (sessionID < 0)
	{
		cout << "Error getting sessionId " << ret << endl;
		return -1;
	}
	else
		cout << "sessionId " << sessionID << endl;


#ifndef realhw	
	/* the following two cmds use a built in API test command 
	* which returns the first paramater as the API return code and
	* the second parameter string is copied back to the user via rx buffer
	*/
	ret = priorSDK.Cmd(sessionID,"dll.apitest 33 goodresponse",rx);
	cout << "api response " << ret << ", rx = " << rx << endl;
	system("pause");

	ret = priorSDK.Cmd(sessionID,"dll.apitest -300 stillgoodresponse",rx);
	cout << "api response " << ret << ", rx = " << rx << endl;
	system("pause");
#else
	cout << "connecting ..." << endl;
	/* substitute with your com port Id */
	cmd ("controller.connect 1");
	
	/* test an illegal command */
	cmd("controller.stage.position.getx");

	/* see if stage fitted */
	cmd("controller.stage.name.get");

	if (!strcmp(rx,"NONE"))
	{
		cout << "no stage!" << endl;
		return -1;
	}

	/* get current XY position in default units of microns */
	cmd("controller.stage.position.get");

	/* re-define this current position as 1234,5678 */
	cmd("controller.stage.position.set 1234 5678");

	/* check it worked */
	cmd("controller.stage.position.get");

	/* set it back to 0,0 */
	cmd("controller.stage.position.set 0 0");
	cmd("controller.stage.position.get");

	/* start a move to a new position */
	cmd("controller.stage.goto-position 1234 5678");

	/*  normally you would poll 'controller.stage.busy.get' until response = 0 */
	do
	{
		priorSDK.Cmd(sessionID,"controller.stage.busy.get",rx);

		stageBusy = atoi(rx);
	} while (stageBusy != 0);

	/* example velocity move of 10u/s in both x and y */
	cmd("controller.stage.move-at-velocity 10 10");

	/* see busy status */
	cmd("controller.stage.busy.get");

	/* stop velocity move */
	cmd("controller.stage.move-at-velocity 0 0");

	/* see busy status */
	cmd("controller.stage.busy.get");

	/* see new position */
	cmd("controller.stage.position.get");

	/* disconnect cleanly from controller */
	cmd ("controller.disconnect");

#endif

	ret = priorSDK.CloseSession(sessionID);
	cout << "CloseSession " << ret << endl;

	system("pause");

	return 0;
}

