#include "specim_camera.h"
#include "socket.h"


std::vector<FrameData> g_frameDataList;
std::atomic<bool> startSignal(false);
std::atomic<bool> stopSignal(false);
std::atomic<bool> finishSignal(false);

void listen_for_signals() {
    SocketConnection signalSocket("127.0.0.1", 8081);

    
    while (true) {
        std::string signal = signalSocket.receive_signal();
        if (signal == "START") {
            startSignal = true;
        } else if (signal == "STOP") {
            stopSignal = true;
        } else if (signal == "FINISH") {
            finishSignal = true;
            break;
        }
    }

    signalSocket.close_socket();
}




int main() {


    SI_Load(L"");
    SpecimCamera camera;

    camera.set_spatial_binning(1);
    camera.set_frame_rate(323.0f);
    std::this_thread::sleep_for(std::chrono::seconds(2));
    camera.set_exposure_time(3.f);

    camera.get_image_info();





        SocketConnection data_socket("127.0.0.1",8080);


    std::thread signalThread(listen_for_signals);
    while (not finishSignal) {
        while (true) {
            if (startSignal or finishSignal)
            {
                break;
            }
        }
        startSignal = false;
        // camera.capture_frames();
        camera.start_acquisition();
        auto start = std::chrono::high_resolution_clock::now();
        while (true) {
            if (stopSignal or finishSignal)
            {
                break;
            }
        }
        stopSignal = false;
        auto stop = std::chrono::high_resolution_clock::now();
        camera.stop_acquisition();

        data_socket.send_frames(g_frameDataList);

        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
        std::cout << "Time taken for acquisition: " << duration.count() << " milliseconds" << std::endl;

        for (auto& frame : g_frameDataList) {
            delete[] frame.pFrameBuffer;
        }
        g_frameDataList.clear();
    }
    printf("camera close\n");
    camera.close_camera();
    // socket.close_socket();

    return 0;
}
