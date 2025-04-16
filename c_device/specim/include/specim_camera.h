//
// Created by SUN Zheng on 2024/7/24.
//

#ifndef SPECIM_CAMERA_H
#define SPECIM_CAMERA_H
#include <chrono>
#include <iostream>
#include "SI_errors.h"
#include "SI_sensor.h"
#include "SI_types.h"
#include "string"
#include <tchar.h>
#include <iostream>
#include <cstring>
#include <iomanip> // 添加此行以包含 iomanip 头文件
#include <vector>

//According to the newest official documentation, no need to include the license path in the header file.
#define license_path L""


//Camera Index:  FX10e (different from the cameras)
#define camera_index 17

//Camera Parameters
#define pixel_width 1024

//number of pixels in the height of the image
#define pixel_height 1024


struct FrameData {
    SI_U8* pFrameBuffer;
    SI_64 nFrameSize;
    SI_64 nFrameNumber;
    std::int64_t timestamp_ms;
    FrameData(SI_U8* buffer, SI_64 size, SI_64 number)
        : pFrameBuffer(buffer), nFrameSize(size), nFrameNumber(number) {
        auto now = std::chrono::high_resolution_clock::now();
        timestamp_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
    }
};

class SpecimCamera {
    friend int onDataCallback(SI_U8* buffer, SI_64 frame_size, SI_64 frame_number, void* userdata);
public:
    SpecimCamera();
    void init_camera();
    void open_camera();
    void close_camera();
    void get_image_info() const;
    void capture_single_frame(SI_U8* &pFrameBuffer, SI_64 &nFrameSize, SI_64 &nFrameNumber);
    void set_frame_rate(float frameRate);
    void set_exposure_time(float exposureTime);
    void set_spatial_binning(int binning);
    void capture_frames() const;
    void register_data_callback() const;
    void start_acquisition() const;
    void stop_acquisition() const;



private:

    SI_H camera_handle = 0;
    int nError = siNoError;
    double frame_rate = 50; //FPS
    double exposure_time = 0.6; //ms
    SI_64 image_width = 1024;
    SI_U8 FrameBuffer = 0;

};
int onDataCallback(SI_U8 * pFrameBuffer, SI_64 nFrameSize, SI_64 nFrameNumber, void* pContext);
#endif //SPECIM_CAMERA_H