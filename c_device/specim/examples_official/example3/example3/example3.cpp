// example3.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
#include "SI_sensor.h"
#include "SI_errors.h"

#define LICENSE_PATH L"C:/Users/Public/Documents/Specim/SpecSensor.lic"

SI_H g_hDevice = 0;

int SI_IMPEXP_CONV onDataCallback(SI_U8* _pBuffer, SI_64 _nFrameSize, SI_64 _nFrameNumber, void* _pContext);


int SelectDevice(void)
{
	int nError = siNoError;
	SI_64 nDeviceCount = 0;
	SI_WC szDeviceName[4096];
	int nIndex = -1;

	SI_CHK(SI_GetInt(SI_SYSTEM, L"DeviceCount", &nDeviceCount));
	wprintf(L"Device count: %d\n", nDeviceCount);

	// Iterate through each devices to print their name
	for (int n = 0; n < nDeviceCount; n++)
	{
		SI_CHK(SI_GetEnumStringByIndex(SI_SYSTEM, L"DeviceName", n, szDeviceName, 4096));
		wprintf(L"\t%d: %s\n", n, szDeviceName);
	}

	// Select a device
	wprintf(L"Select a device: ");
	scanf_s("%d", &nIndex);

	if ((nIndex >= nDeviceCount) || (nIndex == -1))
	{
		wprintf(L"Invalid index");
		return -1;
	}

Error:
	return nIndex;
}


int SI_IMPEXP_CONV FeatureCallback1(SI_H Hndl, SI_WC* Feature, void* Context)
{
	if(wcscmp(Feature, L"Camera.ExposureTime") == 0)
	{
		wprintf(L"FeatureCallback1: Camera.ExposureTime\n");
	}
	else if(wcscmp(Feature, L"Camera.FrameRate") == 0)
	{
		wprintf(L"FeatureCallback1: Camera.FrameRate\n");
	}

	return 0;
}


int SI_IMPEXP_CONV FeatureCallback2(SI_H Hndl, SI_WC* Feature, void* Context)
{
	if(wcscmp(Feature, L"Camera.ExposureTime") == 0)
	{
		wprintf(L"FeatureCallback2: Camera.ExposureTime\n");
	}

	return 0;
}


int SI_IMPEXP_CONV onDataCallback(SI_U8* _pBuffer, SI_64 _nFrameSize, SI_64 _nFrameNumber, void* _pContext)
{
	wprintf(L"%d ", _nFrameNumber);
	return 0;
}


int _tmain(int argc, _TCHAR* argv[])
{
	// Create the necessary variables
	int nError = siNoError;
	int nDeviceIndex = -1;
	int nAction = 0;
	wchar_t szMessage[] = L"Select an action:\n\t0: exit\n\t1: start acquisition\n\t2: stop acquisition\n";

	// Load SpecSensor and get the device count
	wprintf(L"Loading SpecSensor...\n");
	SI_CHK(SI_Load(LICENSE_PATH));

	// Select a device
	nDeviceIndex = SelectDevice();
	
	// Open the device and set the callbacks
	SI_CHK(SI_Open(nDeviceIndex, &g_hDevice));
	SI_CHK(SI_Command(g_hDevice, L"Initialize"));
	SI_CHK(SI_RegisterFeatureCallback(g_hDevice, L"Camera.FrameRate", FeatureCallback1, 0));
	SI_CHK(SI_RegisterFeatureCallback(g_hDevice, L"Camera.ExposureTime", FeatureCallback1, 0));
	SI_CHK(SI_RegisterFeatureCallback(g_hDevice, L"Camera.ExposureTime", FeatureCallback2, 0));
	SI_CHK(SI_RegisterDataCallback(g_hDevice, onDataCallback, 0));

	// Prompt commands
	wprintf(L"%s", szMessage);
	while(scanf("%d", &nAction))
	{
		if (nAction == 0)
		{
			wprintf(L"Bye bye!");
			break;
		}
		else if (nAction == 1)
		{
			wprintf(L"Start acquisition");
			SI_CHK(SI_Command(g_hDevice, L"Acquisition.Start"));
		}
		else if (nAction == 2)
		{
			wprintf(L"Stop acquisition");
			SI_CHK(SI_Command(g_hDevice, L"Acquisition.Stop"));
		}

		wprintf(L"%s", szMessage);
	}

	
Error:
	if (SI_FAILED(nError))
	{
		wprintf(L"An error occurred: %s\n", SI_GetErrorString(nError));
	}

	SI_Close(g_hDevice);
	SI_Unload();

	return SI_FAILED(nError) ? -1 : 0;
}

