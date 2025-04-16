//
// Created by SUN Zheng on 2024/9/3.
//

#include "robot_socket.h"
#include "nachi_api.h"
#include <iostream>
#include <sstream>
#include <map>
#include <ModbusController.h>
// box_point - on_box_point - mid-point -target_point - mid-point  - on_box_point - box_point
int main() {
    nachi::NachiApi nachi_api;
    Position a_point = {183, 50., 250};
    printf("a_point: %f, %f, %f\n", a_point.x, a_point.y, a_point.z);
    nachi_api.et_ToTargetPosition({a_point});
    std::cout << "Sent response" << std::endl;
    nachi_api.close_all();

}


//
