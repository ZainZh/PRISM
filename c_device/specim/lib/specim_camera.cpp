#include "specim_camera.h"


extern std::vector<FrameData> g_frameDataList;
SpecimCamera::SpecimCamera() {
    //初始化相机
    init_camera();
}

void SpecimCamera::init_camera() {
    open_camera();
    get_image_info();
    register_data_callback();
}

void SpecimCamera::get_image_info() const{
    SI_64 height = 0;
    SI_64 width = 0;
    SI_64 bytes = 0;
    SI_64 bit_depth = 0;
    SI_64 frame_size;
    double frame_rate;
    double exposure_time;

    SI_GetInt(camera_handle, L"Camera.Image.Width", &width);
    SI_GetInt(camera_handle, L"Camera.Image.Height", &height);
    SI_GetInt(camera_handle, L"Camera.Image.SizeBytes", &bytes);
    SI_GetInt(camera_handle, L"Camera.BitDepth", &bit_depth);
    SI_GetInt(camera_handle, L"Camera.Image.SizeBytes", &frame_size);
    SI_GetFloat(camera_handle, L"Camera.ExposureTime", &exposure_time);
    SI_GetFloat(camera_handle, L"Camera.FrameRate", &frame_rate);

    // 打印获取到的信息
    std::wcout << L"Image Width: " << width << L" pixels\n";
    std::wcout << L"Image Height: " << height << L" pixels\n";
    std::wcout << L"Image Size: " << bytes << L" bytes\n";
    std::wcout << L"Bit Depth: " << bit_depth << L" bits\n";
    std::wcout << L"Frame Size: " << frame_size << L" bytes\n";
    std::wcout << L"Exposure Time: " << exposure_time << L" ms\n";
    std::wcout << L"Frame Rate: " << frame_rate << L" fps\n";
}

//according to the manual, SI_Wait function is not recommended to use for handling the high performance situation.
//It is recommended to use the SI_RegisterDataCallback function instead.
void SpecimCamera::capture_single_frame(SI_U8 * &pFrameBuffer, SI_64 &nFrameSize, SI_64 &nFrameNumber) {
    nError = SI_GetInt(camera_handle, L"Camera.Image.SizeBytes", &nFrameSize);
    if (nError != siNoError) {
        std::cerr << "Error getting frame size: " << nError << std::endl;
        return;
    }

    pFrameBuffer = new SI_U8[nFrameSize];

    nError = SI_Command(camera_handle, L"Acquisition.Start");
    if (nError != siNoError) {
        std::cerr << "Error starting acquisition: " << nError << std::endl;
        delete[] pFrameBuffer;
        pFrameBuffer = nullptr;
        return;
    }

    nError = SI_Wait(camera_handle, pFrameBuffer, &nFrameSize, &nFrameNumber, 1000);
    if (nError != siNoError) {
        std::cerr << "Error capturing frame: " << nError << std::endl;
    }
}

void SpecimCamera::register_data_callback() const
{
    SI_64 res = 0;
    res = SI_RegisterDataCallback(camera_handle, onDataCallback, nullptr);
    if (nError != siNoError) {
        std::cerr << "register data callback failed, error code: " << nError << std::endl;
    }
}

void SpecimCamera::capture_frames() const {
    int nAction = 0;
    wprintf(L"Select an action:\n\t0: exit\n\t1: start acquisition\n\t2: stop acquisition\n");
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
            SI_Command(camera_handle, L"Acquisition.Start");
        }
        else if (nAction == 2)
        {
            wprintf(L"Stop acquisition");
            SI_Command(camera_handle, L"Acquisition.Stop");
        }

        wprintf(L"Select an action:\n\t0: exit\n\t1: start acquisition\n\t2: stop acquisition\n");
    }
}

void SpecimCamera::start_acquisition() const {
    wprintf(L"Start acquisition");
    SI_Command(camera_handle, L"Acquisition.Start");
}


void SpecimCamera::stop_acquisition() const {
    wprintf(L"Stop acquisition");
    SI_Command(camera_handle, L"Acquisition.Stop");
    SI_U8* newBuffer = new SI_U8[1];
    // send a signal frame_number = -1 to the onDataCallback to stop the loop
    g_frameDataList.emplace_back(newBuffer, 1, -1);
}


//ms
void SpecimCamera::set_frame_rate(float frameRate) {
    nError = SI_SetFloat(camera_handle, L"Camera.FrameRate", frameRate);
    if (nError != siNoError) {
        std::cerr << "Error setting frame rate: " << nError << std::endl;
    }
}

//ms
void SpecimCamera::set_exposure_time(float exposureTime) {
    nError = SI_SetFloat(camera_handle, L"Camera.ExposureTime", exposureTime);
    if (nError != siNoError) {
        std::cerr << "Error setting exposure time: " << nError << std::endl;
    }
}
// 0-1x, 1-2x, 2-4x, 3-8x
void SpecimCamera::set_spatial_binning(int spatialBinning) {
    nError = SI_SetEnumIndex(camera_handle, L"Camera.Binning.Spatial", spatialBinning);
    if (nError != siNoError) {
        std::cerr << "Error setting spatial binning: " << nError << std::endl;
    }
}
void SpecimCamera::open_camera() {
    nError = SI_Open(17, &camera_handle);
    nError = SI_Command(camera_handle, L"Initialize");
    if (nError != siNoError) {
        std::cerr << "Error opening the camera:" << nError << std::endl;
        return;
    }
}

void SpecimCamera::close_camera() {
    nError = SI_Close(camera_handle);
    if (nError != siNoError) {
        std::cerr << "Error closing the camera:" << nError << std::endl;
        return;
    }
    SI_Unload();
}

int onDataCallback(SI_U8 * pFrameBuffer, SI_64 nFrameSize, SI_64 nFrameNumber, void* pContext) {

    SI_U8* newBuffer = new SI_U8[nFrameSize];
    std::memcpy(newBuffer, pFrameBuffer, nFrameSize);
    g_frameDataList.emplace_back(newBuffer, nFrameSize, nFrameNumber);

    wprintf(L"Frame Number: %lld\n", nFrameNumber);
    wprintf(L"Frame Size: %lld\n", nFrameSize);
    return 1;
}
