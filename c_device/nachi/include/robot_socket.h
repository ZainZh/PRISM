//
// Created by SUN Zheng on 2024/9/13.
//

#ifndef ROBOT_SOCKET_H
#define ROBOT_SOCKET_H
//
// Created by SUN Zheng on 2024/7/25.

#include "specim_camera.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <thread>
#include <atomic>


class RobotConnection {
public:
    RobotConnection(const std::string &serverIP, int serverPort);

    void init_socket();

    void connect_socket();

    void close_socket() const;

    [[nodiscard]] std::vector<std::string> receive_data() const;

    [[nodiscard]] std::string receive_signal() const;

    bool send_bool(bool value) const;

private:
    WSADATA wsaData;
    struct sockaddr_in server_addr;
    int iResult;
    int sock;
    std::string serverIP;
    int serverPort;
};


#endif //ROBOT_SOCKET_H
