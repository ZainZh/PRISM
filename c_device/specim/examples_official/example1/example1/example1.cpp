#include "stdafx.h"
#include "SI_sensor.h"
#include "SI_errors.h"

#define LICENSE_PATH L"C:/Users/Public/Documents/Specim/SpecSensor.lic"

int _tmain(int argc, _TCHAR* argv[])
{
	// Create the necessary variables
	int nError = siNoError;
	SI_64 nDeviceCount = 0;
	SI_WC szDeviceName[4096];
	SI_WC szDeviceDescription[4096];

	// Load SpecSensor and get the device count
	SI_CHK(SI_Load(LICENSE_PATH));
	SI_CHK(SI_GetInt(SI_SYSTEM, L"DeviceCount", &nDeviceCount));
	
	wprintf(L"Device count: %d\n", nDeviceCount);


	// Iterate through each devices to print their name and description
	for (int n = 0; n < nDeviceCount; n++)
	{
		SI_CHK(SI_GetEnumStringByIndex(SI_SYSTEM, L"DeviceName", n, szDeviceName, 4096));
		SI_CHK(SI_GetEnumStringByIndex(SI_SYSTEM, L"DeviceDescription", n, szDeviceDescription, 4096));
		wprintf(L"Device %d:\n", n);
		wprintf(L"\tName: %s\n", szDeviceName);
		wprintf(L"\tDescription: %s\n", szDeviceDescription);
	}

	// Unload the library
	SI_CHK(SI_Unload());

	wprintf(L"\r\nPress any key to quit...\r\n");

	getchar();
		
Error:
	return 0;
}

