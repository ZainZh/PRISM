//
// Created by SUN Zheng on 2024/9/23.
//

// ModbusController.h

#ifndef MODBUSCONTROLLER_H
#define MODBUSCONTROLLER_H

#include <modbus.h>
#include <string>

class ModbusController {
public:
    // 构造函数：初始化Modbus RTU
    ModbusController(const std::string& port, int baud, char parity, int data_bit, int stop_bit, int slave_id);

    // 初始化和连接Modbus设备
    bool init();

    // 写入单个线圈（位）
    bool writeCoil(int coil_addr, int status);

    // 关闭连接并释放资源
    void close();

    // 析构函数：确保资源释放
    ~ModbusController();

private:
    modbus_t *ctx;  // Modbus RTU上下文
    std::string port;
    int baud;
    char parity;
    int data_bit;
    int stop_bit;
    int slave_id;
};

#endif // MODBUSCONTROLLER_H
