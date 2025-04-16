// example2.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <windows.h>
#include "SI_sensor.h"
#include "SI_errors.h"

#define LICENSE_PATH L""

SI_H g_hDevice = 0;

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

int _tmain(int argc, _TCHAR* argv[])
{
	// Creates the necessary variables
	int nError = siNoError;
	int nDeviceIndex = -1;
	SI_U8* pFrameBuffer = 0;
	SI_64 nBufferSize = 0;
	SI_64 nFrameSize = 0;
	SI_64 nFrameNumber = 0;

	// Loads SpecSensor and get the device count
	wprintf(L"Loading SpecSensor...\n");
	SI_CHK(SI_Load(LICENSE_PATH));
	
	// Select a device
	nDeviceIndex = SelectDevice();	
	
	if (nDeviceIndex == -1)
	{
		return 0;
	}

	// Opens the camera handle
	SI_CHK(SI_Open(nDeviceIndex, &g_hDevice));
	SI_CHK(SI_Command(g_hDevice, L"Initialize"));

	// Sets frame rate and exposure
	SI_CHK(SI_SetFloat(g_hDevice, L"Camera.FrameRate", 25.0));
	SI_CHK(SI_SetFloat(g_hDevice, L"Camera.ExposureTime", 3.0));

	// Creates a buffer to receive the frame data
	SI_CHK(SI_GetInt(g_hDevice, L"Camera.Image.SizeBytes", &nBufferSize));
	SI_CHK(SI_CreateBuffer(g_hDevice, nBufferSize, (void**)&pFrameBuffer));

	// Starts the acquisition, acquires 100 frames and stops the acquisition
	SI_CHK(SI_Command(g_hDevice, L"Acquisition.Start"));

	for(int n = 0; n < 100; n++)
	{
		SI_CHK(SI_Wait(g_hDevice, pFrameBuffer, &nFrameSize, &nFrameNumber, 1000));
		// Do something interesting with the frame pointer (pFrameBuffer)
		wprintf(L"Frame number: %d\n", nFrameNumber);
	}

	SI_CHK(SI_Command(g_hDevice, L"Acquisition.Stop"));


Error:
	if (SI_FAILED(nError))
	{
		char szInput[256] = "";
		wprintf(L"An error occurred: %s\n", SI_GetErrorString(nError));
		wprintf(L"Enter a character and press enter to exit\n");
		scanf_s("%s", &szInput, 255);

	}
	else
	{
		char szInput[256] = "";
		wprintf(L"It all went well!\n");
		wprintf(L"Enter a character and press enter to exit\n");
		scanf_s("%s", &szInput, 255);
	}

	// Cleanups the buffer, closes the camera and unloads SpecSensor
	SI_DisposeBuffer(g_hDevice, pFrameBuffer);
	SI_Close(g_hDevice);
	SI_Unload();

	return SI_FAILED(nError) ? -1 : 0;
}

