#include "robot_socket.h"


RobotConnection::RobotConnection(const std::string &serverIP, int serverPort)
    : serverIP(serverIP), serverPort(serverPort) {
    init_socket();
};

void RobotConnection::connect_socket() {
    // 连接到服务器
    if (connect(sock, (struct sockaddr *) &server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Connection failed with error: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return;
    }
}

void RobotConnection::init_socket() {
    // 初始化 WinSock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        std::cerr << "WSAStartup failed with error: " << iResult << std::endl;
        return;
    }
    // 创建套接字
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == INVALID_SOCKET) {
        std::cerr << "Socket creation failed with error: " << WSAGetLastError() << std::endl;
        WSACleanup();
        return;
    }

    // 设置服务器地址
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(serverPort);
    inet_pton(AF_INET, serverIP.c_str(), &server_addr.sin_addr);
    connect_socket();
}

std::vector<std::string> RobotConnection::receive_data() const {
    char buffer[1024];
    int bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytesReceived > 0) {
        buffer[bytesReceived] = '\0';
        std::string receivedData(buffer);

        // Parse the comma-separated values
        std::vector<std::string> parsedData;
        std::stringstream ss(receivedData);
        std::string token;

        while (std::getline(ss, token, ',')) {
            parsedData.push_back(token);
        }

        return parsedData; // Return a vector of the parsed strings (x, y, class_id)
    }

    return {}; // Return an empty vector if nothing was received
}


void RobotConnection::close_socket() const {
    // 关闭连接
    closesocket(sock);
    WSACleanup();
}


std::string RobotConnection::receive_signal() const {
    char buffer[1024];
    int bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytesReceived > 0) {
        buffer[bytesReceived] = '\0';
        return std::string(buffer);
    }
    return "";
}

bool RobotConnection::send_bool(bool value) const {
    char boolByte = value ? 1 : 0;  // 将布尔值转换为字节
    int result = send(sock, &boolByte, sizeof(boolByte), 0);  // 发送字节
    if (result == SOCKET_ERROR) {
        std::cerr << "Send failed with error: " << WSAGetLastError() << std::endl;
        return false;  // 发送失败
    }
    return true;  // 发送成功
}