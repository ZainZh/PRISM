//
//
#include <nachi_api.h>
#include <vector>

#include "OpenNR-IF.h"

#define EXT_AXIS (1)

const float TO_METER = 0.001;
const float TO_MM = 1000.;

const float TO_DEG = 180. / M_PI;
const float TO_RAD = M_PI / 180.;

using namespace std;

namespace nachi {
    NachiApi::NachiApi() {
        initConnect();
        et_initconnect();

        SetConsoleOutputCP(CP_UTF8);
        // 设置控制台输入编码（如果需要）
        SetConsoleCP(CP_UTF8);
    }



    NachiApi::~NachiApi() {
        close_all();
    }

    void NachiApi::close_all() {
        if (nXmlOpenId > 0)
            NR_Close(nXmlOpenId);
        if (et_nXmlOpenId > 0)
            NR_Close(et_nXmlOpenId);
    }

    bool NachiApi::initConnect() {
        memset(&info, 0, sizeof(info));
        info.pcAddrs = &ip_address[0];
        info.lKind = NR_DATA_XML;

        nXmlOpenId = NR_Open(&info);
        int nEEr = NR_CtrlStep(nXmlOpenId, 0);
        if (0 < nXmlOpenId) {
            printf("Connection to %s established", ip_address.c_str(),"\n");
            return true;
        } else {
            printf("Connection error: %d", nXmlOpenId,"\n");
            return false;
        }
    }

    void NachiApi::et_initconnect() {
        NACHI_COMMIF_INFO info_external;
        ZeroMemory(&info_external, sizeof(info_external));
        info_external.pcAddrs = &et_ip_address[0]; //连接ip
        info_external.lPortNo = et_ip_port; //链接端口号
        info_external.lRetry = 0; //重新连接次数
        info_external.lSendTimeOut = 0; //超时时间
        info_external.lCommSide = NR_OBJECT_INTERNAL; //连接对象控制柜0
        info_external.lMode = 0; //连接模式
        info_external.lKind = NR_DATA_REAL; //连接类型(实时通讯）
        et_nXmlOpenId = NR_Open(&info_external);
        if (0 < et_nXmlOpenId) {
            printf("Connection to external tracking %s established", et_ip_address.c_str());
        } else {
            printf("Connection to external tracking error: %d", et_nXmlOpenId);
        }
        NR_CtrlMotor(nXmlOpenId, 1);
        Sleep(300);
        NR_CtrlRun(nXmlOpenId, 1, 1);
        Sleep(100);
        NR_Close(nXmlOpenId);
        Sleep(100);


        ZeroMemory(&et_setpData, sizeof(et_setpData));
        et_setpData.nTime = 10;
        et_setpData.stCtrl.ushEstopBit = 0; //停止命令
        et_setpData.stCtrl.ushFinishBit = 0; //外部跟踪是否完成
        et_setpData.stCtrl.ushOrderBit = 0; //作命令(0:指尖位置命令,1:关节角命令)
        et_setpData.stCtrl.ushProtcolBit = 1; //协议类型(1:Fixerd)
        et_setpData.stCtrl.ushRsv = 12;
    }

    bool NachiApi::getJointStates() {
        if (nXmlOpenId < 0) {
            printf("No connection to robot");
            return false;
        }

        std::vector<float> curr_js_temp;

        float fValue[axes_num];
        memset(&fValue, 0, sizeof(fValue));

        int nErr = NR_AcsAxisTheta(nXmlOpenId, fValue, 1, axes_num);
        if (NR_E_NORMAL == nErr) {
            for (int nAxis = 0; nAxis < 6; nAxis++) {
                // printf("Axis%d angle: %8.2f[deg]\n", (nAxis + 1), fValue[nAxis]);
                curr_js_temp.push_back(fValue[nAxis] * TO_RAD);
                if (nAxis == 1) {
                    curr_js_temp[nAxis] -= M_PI_2;
                }
            }
            for (int i = 0; i < 6; i++) {
                currentJointPosition[i] = curr_js_temp[i];
            }
            return true;
        } else {
            printf("Read joint states error: %d", nErr);
            return false;
        }
    }


    Position NachiApi::getTipPose() {
        if (nXmlOpenId < 0) {
            printf("No connection to robot");
        }
        float fValue[6];
        memset(&fValue, 0, sizeof(fValue));
        int nErr = NR_AcsToolTipPos(nXmlOpenId, fValue, 1, axes_num);
        if (NR_E_NORMAL == nErr) {
            currentTCPPose.x = fValue[0];
            currentTCPPose.y = fValue[1];
            currentTCPPose.z = fValue[2];
            currentTCPPose.roll = fValue[3];
            currentTCPPose.pitch = fValue[4];
            currentTCPPose.yaw = fValue[5];

            return currentTCPPose;
        } else {
            printf("Read joint states error: %d", nErr);
        }
    }

    bool NachiApi::getTipSpeed() {
        if (nXmlOpenId < 0) {
            printf("No connection to robot");
            return false;
        }
        int nErr = NR_AcsTcpSpeed(nXmlOpenId, &currentTcpSpeed, 1, 1);
        if (NR_E_NORMAL == nErr) {
            return true;
        } else {
            printf("Read joint states error: %d", nErr);
            return false;
        }
    }


    void NachiApi::executeLinearMovement(const std::vector<float> &target_pose, const string &pose_method)
    /// target_pose: [x, y, z, roll, pitch, yaw] mm, deg
    /// pose_method: "absolute" or "relative"
    {
        if (nXmlOpenId < 0) {
            printf("No connection to robot");
            return;
        }
        int speed_accelerate_setting[2] = {1, 1};
        int nErr_speed_accelerate_flag = NR_AcsGlobalInt(nXmlOpenId, speed_accelerate_setting, true, 60, 4);
        if (NR_E_NORMAL != nErr_speed_accelerate_flag) {
            printf("write speed and accelerate flag Error: %d\n", nErr_speed_accelerate_flag);
        }
        if (pose_method == "relative") {
            NR_POSE fvalue = {
                static_cast<float>(target_pose[0]),
                static_cast<float>(target_pose[1]),
                static_cast<float>(target_pose[2]),
                static_cast<float>(target_pose[3]),
                static_cast<float>(target_pose[4]),
                static_cast<float>(target_pose[5])
            };
            // int nErr = NR_AcsGlobalFloat(nXmlOpenId, fvalue, 1, 77, 6);
            float fExtPos[3];
            memset(&fExtPos, 0, sizeof(fExtPos));
            int nErr = NR_CtrlMoveXR(nXmlOpenId, &fvalue, 2, 1, 0, fExtPos, EXT_AXIS);
            if (NR_E_NORMAL != nErr) {
                printf("write tip's position Error: %d\n", nErr);
            }
        } else if (pose_method == "absolute") {
            float fvalue[6] = {
                static_cast<float>(target_pose[0]),
                static_cast<float>(target_pose[1]),
                static_cast<float>(target_pose[2]),
                static_cast<float>(target_pose[3]),
                static_cast<float>(target_pose[4]),
                static_cast<float>(target_pose[5])
            };
            int nErr = NR_AcsGlobalFloat(nXmlOpenId, fvalue, 1, 77, 6);
            if (NR_E_NORMAL != nErr) {
                printf("write tip's position Error: %d\n", nErr);
            }
        } else {
            printf("Invalid pose method");
        }
    }

    /// target_pose: [x, y, z, roll, pitch, yaw] mm, deg
    void NachiApi::et_ToTargetPosition(const vector<Position> &target_positions) {
        int nEEr = NR_GetAll(et_nXmlOpenId, &et_currentData, NR_ACCESS_NO_WAIT);
        currentTCPPose = {
            et_currentData.ustData.stStd.fCurTcpPos[0], et_currentData.ustData.stStd.fCurTcpPos[1],
            et_currentData.ustData.stStd.fCurTcpPos[2],
            et_currentData.ustData.stStd.fCurTcpPos[3], et_currentData.ustData.stStd.fCurTcpPos[4],
            et_currentData.ustData.stStd.fCurTcpPos[5]
        };
        vector<Position> path_points = {currentTCPPose};
        path_points.insert(path_points.end(), target_positions.begin(), target_positions.end());
        std::vector<Position> path = generatePath(path_points, step_size);
        et_execute_path(path);
        printf("finished");
    }

    void NachiApi::et_execute_path(std::vector<Position> &path) {
        for (const auto &point: path) {
            int nEEr = NR_GetAll(et_nXmlOpenId, &et_currentData, NR_ACCESS_NO_WAIT);
            // printf("next_target_position: %f, %f, %f, %f ,%f,%f\n", point.x,point.y, point.z);

            et_setpData.ustData.stStd.fComTcpPos[0] = point.x;
            et_setpData.ustData.stStd.fComTcpPos[1] = point.y;
            et_setpData.ustData.stStd.fComTcpPos[2] = point.z;
            et_setpData.ustData.stStd.fComTcpPos[3] = point.roll;
            et_setpData.ustData.stStd.fComTcpPos[4] = point.pitch;
            if (et_currentData.ustData.stStd.fCurTcpPos[5] >0 ) {
                et_setpData.ustData.stStd.fComTcpPos[5] = 179.9;
            }
            else {
                et_setpData.ustData.stStd.fComTcpPos[5] = -179.9;
            }
            et_setpData.nTime = et_currentData.nTime;
            nEEr = NR_SetAll(et_nXmlOpenId, &et_setpData, NR_ACCESS_NO_WAIT);
            // printf("set执行结果;%d\n", nEEr);
            currentTCPPose = {
                et_currentData.ustData.stStd.fCurTcpPos[0], et_currentData.ustData.stStd.fCurTcpPos[1],
                et_currentData.ustData.stStd.fCurTcpPos[2],
                et_currentData.ustData.stStd.fCurTcpPos[3], et_currentData.ustData.stStd.fCurTcpPos[4],
                et_currentData.ustData.stStd.fCurTcpPos[5]
            };
            while (distance(currentTCPPose, point) > dis_tolerance_during_motion){
                nEEr = NR_GetAll(et_nXmlOpenId, &et_currentData, NR_ACCESS_NO_WAIT);
                currentTCPPose = {
                    et_currentData.ustData.stStd.fCurTcpPos[0], et_currentData.ustData.stStd.fCurTcpPos[1],
                    et_currentData.ustData.stStd.fCurTcpPos[2],
                    et_currentData.ustData.stStd.fCurTcpPos[3], et_currentData.ustData.stStd.fCurTcpPos[4],
                    et_currentData.ustData.stStd.fCurTcpPos[5]
                };
            }
            printf("Current position；%f,%f,%f,%f,%f,%f\n", et_currentData.ustData.stStd.fCurTcpPos[0],
                   et_currentData.ustData.stStd.fCurTcpPos[1], et_currentData.ustData.stStd.fCurTcpPos[2],
                   et_currentData.ustData.stStd.fCurTcpPos[3], et_currentData.ustData.stStd.fCurTcpPos[4],
                   et_currentData.ustData.stStd.fCurTcpPos[5]);
        }
        int nEEr = NR_SetAll(et_nXmlOpenId, &et_setpData, NR_ACCESS_NO_WAIT);
        while (distance(currentTCPPose, path.back()) > 1) {
            nEEr = NR_GetAll(et_nXmlOpenId, &et_currentData, NR_ACCESS_NO_WAIT);
            currentTCPPose = {
                et_currentData.ustData.stStd.fCurTcpPos[0], et_currentData.ustData.stStd.fCurTcpPos[1],
                et_currentData.ustData.stStd.fCurTcpPos[2],
                et_currentData.ustData.stStd.fCurTcpPos[3], et_currentData.ustData.stStd.fCurTcpPos[4],
                et_currentData.ustData.stStd.fCurTcpPos[5]
            };
        }
    }
} // namespace nachi
double distance(const Position &A, const Position &B) {
    return std::sqrt(std::pow(B.x - A.x, 2) +
                     std::pow(B.y - A.y, 2) +
                     std::pow(B.z - A.z, 2));
}

double oritentation_distance(const Position &A, const Position &B) {
    return std::sqrt(std::pow(B.pitch - A.pitch, 2) +
                     std::pow(B.roll - A.roll, 2) +
                     std::pow(B.yaw - A.yaw, 2));
}

std::vector<Position> generatePath(const vector<Position> &target_positions, double stepSize) {
    std::vector<Position> path;

    for (size_t idx = 0; idx < target_positions.size() - 1; ++idx) {
        const Position &start_pose = target_positions[idx];
        const Position &end_pose = target_positions[idx + 1];

        // 计算这两个点之间的距离
        double dist = distance(start_pose, end_pose);
        int numSteps = static_cast<int>(dist / stepSize); // 计算需要的步数

        // 插值生成路径点
        for (int i = 0; i <= numSteps; ++i) {
            double t = static_cast<double>(i) / numSteps; // 归一化参数 t 从 0 到 1

            Position intermediate;
            intermediate.x = start_pose.x + t * (end_pose.x - start_pose.x);
            intermediate.y = start_pose.y + t * (end_pose.y - start_pose.y);
            intermediate.z = start_pose.z + t * (end_pose.z - start_pose.z);



            intermediate.roll = start_pose.roll + t * (end_pose.roll - start_pose.roll);
            intermediate.pitch = start_pose.pitch + t * (end_pose.pitch - start_pose.pitch);
            intermediate.yaw = start_pose.yaw + t * (end_pose.yaw - start_pose.yaw);

            path.push_back(intermediate);
        }
    }

    // 将最后一个点加入到路径中，确保终点也包括
    path.push_back(target_positions.back());

    return path;
}
