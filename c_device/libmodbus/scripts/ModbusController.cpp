#include <iostream>
#include <modbus.h>
#include <windows.h>
#include <ModbusController.h>

ModbusController::ModbusController(const std::string &port, int baud, char parity, int data_bit, int stop_bit,
                                   int slave_id)
    : ctx(nullptr), port(port), baud(baud), parity(parity), data_bit(data_bit), stop_bit(stop_bit), slave_id(slave_id) {
}

// 初始化并连接Modbus设备
bool ModbusController::init() {
    ctx = modbus_new_rtu(port.c_str(), baud, parity, data_bit, stop_bit);
    if (ctx == nullptr) {
        std::cerr << "Unable to create the libmodbus context\n";
        return false;
    }

    if (modbus_set_slave(ctx, slave_id) == -1) {
        std::cerr << "Failed to set slave: " << modbus_strerror(errno) << '\n';
        return false;
    }

    if (modbus_connect(ctx) == -1) {
        std::cerr << "Connection failed: " << modbus_strerror(errno) << '\n';
        modbus_free(ctx);
        return false;
    }
    return true;
}

// 写入单个线圈
bool ModbusController::writeCoil(int coil_addr, int status) {
    modbus_write_bit(ctx, coil_addr, status) == -1;
    return true;
}

// 关闭Modbus连接
void ModbusController::close() {
    if (ctx) {
        modbus_close(ctx);
        modbus_free(ctx);
        ctx = nullptr;
    }
}

// 析构函数
ModbusController::~ModbusController() {
    close();
}

// int main() {
//     // 创建ModbusController对象并初始化
//     ModbusController modbusController("\\\\.\\COM3", 38400, 'N', 8, 1, 1);
//
//     // 初始化和连接
//     if (!modbusController.init()) {
//         std::cerr << "Failed to initialize Modbus connection\n";
//         return -1;
//     }
//
//     // 写入1到地址0的线圈
//     if (!modbusController.writeCoil(0, 1)) {
//         std::cerr << "Failed to set coil\n";
//     }
//
//     // 等待1秒
//     Sleep(1000);
//
//     // 关闭地址0的线圈
//     if (!modbusController.writeCoil(0, 0)) {
//         std::cerr << "Failed to reset coil\n";
//     }
//
//     // 关闭连接并释放资源（由析构函数自动处理）
//     return 0;
// }
