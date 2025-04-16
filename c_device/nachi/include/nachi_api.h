//
// Created by SUN Zheng on 2024/9/3.
//

#ifndef NACHI_API_H
#define NACHI_API_H
#include <cmath>
#include <nachi_api.h>
#include <iostream>
#include <string.h>
#include <vector>
#include <windows.h>
#include "OpenNR-IF.h"



using namespace std;
struct Position {
    float x,y,z;
    float roll =90.,pitch = 0. ,yaw =180;
};

namespace nachi {
    class NachiApi {
    public:
        NachiApi();

        ~NachiApi();

        bool initConnect();
        void et_initconnect();
        void close_all();
        bool getJointStates();

        Position getTipPose();

        bool getTipSpeed();

        int axes_num = 6;
        std::vector<float> currentJointPosition = {};
        Position currentTCPPose;
        float currentTcpSpeed = 0;

        void executeLinearMovement(const std::vector<float> &target_pose, const string &pose_method);
        void et_ToTargetPosition(const vector<Position> &target_positions);
        void et_execute_path(std::vector<Position> &path);

    private:
        int nXmlOpenId = {};
        int et_nXmlOpenId = {};
        NACHI_COMMIF_INFO info = {};
        std::string ip_address = "192.168.1.2";
        std::string et_ip_address = "192.168.1.3";
        int et_ip_port = 5050;
        double step_size = 5;
        double dis_tolerance_during_motion = 5;

        NR_SET_REAL_DATA_ALL et_setpData;
        NR_GET_REAL_DATA_ALL et_currentData;


    };

}

double distance(const Position& A, const Position& B);
std::vector<Position> generatePath(const vector<Position> &target_positions, double stepSize);
double oritentation_distance(const Position &A, const Position &B);
#endif //NACHI_API_H
