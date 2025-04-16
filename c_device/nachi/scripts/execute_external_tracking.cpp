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
    RobotConnection server("127.0.0.10", 9090);
    ModbusController modbusController("\\\\.\\COM6", 38400, 'N', 8, 1, 1);
    // 初始化和连接
    if (!modbusController.init()) {
        std::cerr << "Failed to initialize Modbus connection\n";
        return -1;
    }
    nachi::NachiApi nachi_api;

    std::map<std::string, Position> box_position;

    box_position["black_acetate"] = {-63, -314.09, 30};
    box_position["black_linen"] = {81, -314.09, 30};
    box_position["black_silk"] = {71, 342.86, 30};
    box_position["black_wool"] = {-74, 342.86, 30};


    while (true) {
        std::vector<std::string> data = server.receive_data();
        if (data.empty()) {
            break; // Connection closed or error occurred
        }


        // Parse the received data

        float x, y;
        string class_id;
        try {
            x = std::stof(data[0]); // 将第一个字符串转换为float
            y = std::stof(data[1]); // 将第二个字符串转换为float
        } catch (const std::invalid_argument &e) {
            std::cerr << "Invalid argument: " << e.what() << std::endl;
        } catch (const std::out_of_range &e) {
            std::cerr << "Out of range: " << e.what() << std::endl;
        }

        // 读取 class_id
        class_id = data[2];
        std::cout << "    Parsed data: x=" << x << ", y=" << y << ", class_id=" << class_id << std::endl;
        //execute the robot movement
        if (class_id != "black_acetate" && class_id != "black_linen" && class_id != "black_silk" && class_id !=
            "black_wool") {
            std::cerr << "Invalid class_id: " << class_id << std::endl;
            server.send_bool(true);
            continue;
        }
        Position box_point = box_position[class_id];
        Position on_box_point = {box_point.x, box_point.y, 250};
        Position mid_point = {183, 0., 250};
        Position target_point = {x, y, 250};
        Position suction_point = {x, y, 193.5};

        printf("on_box_point: %f, %f, %f\n", on_box_point.x, on_box_point.y, on_box_point.z);
        printf("box_point: %f, %f, %f\n", box_point.x, box_point.y, box_point.z);
        printf("mid_point: %f, %f, %f\n", mid_point.x, mid_point.y, mid_point.z);
        printf("target_point: %f, %f, %f\n", target_point.x, target_point.y, target_point.z);
        // nachi_api.et_ToTargetPosition({mid_point, target_point, mid_point, on_box_point, box_point, on_box_point,});
        nachi_api.et_ToTargetPosition({mid_point, target_point, suction_point});
        modbusController.writeCoil(0, 1);
        nachi_api.et_ToTargetPosition({target_point, mid_point, on_box_point, box_point});
        modbusController.writeCoil(0, 0);
        nachi_api.et_ToTargetPosition({on_box_point,});
        server.send_bool(true);
        std::cout << "Sent response" << std::endl;
    }
    server.close_socket();
    return 0;
}


//
