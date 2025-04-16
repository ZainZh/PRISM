#include "socket.h"


SocketConnection::SocketConnection(const std::string& serverIP, int serverPort)
    : serverIP(serverIP), serverPort(serverPort)
{
   init_socket();
};

void SocketConnection::connect_socket() {
    // 连接到服务器
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Connection failed with error: " << WSAGetLastError() << std::endl;
        closesocket(sock);
        WSACleanup();
        return;
    }
    else {
        std::cout << "Connected to server " << serverIP << " on port " << serverPort << std::endl;
    }
}

void SocketConnection::init_socket() {
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


void SocketConnection::send_frames(const std::vector<FrameData>& frameDataList) const
{
    for (const auto& frame : frameDataList) {
        // 发送帧大小和帧编号（元数据）
        SI_64 frameSize = frame.nFrameSize;
        SI_64 frameNumber = frame.nFrameNumber;
        std::int64_t timestamp_ms = frame.timestamp_ms;

        // 将元数据转换为字节数组发送
        char header[sizeof(SI_64) * 2 + sizeof(std::int64_t)];
        std::memcpy(header, &frameSize, sizeof(SI_64));
        std::memcpy(header + sizeof(SI_64), &frameNumber, sizeof(SI_64));
        std::memcpy(header + sizeof(SI_64)*2, &timestamp_ms, sizeof(std::int64_t));
        if (send(sock, header, sizeof(header), 0) == SOCKET_ERROR) {
            std::cerr << "Failed to send frame metadata, error: " << WSAGetLastError() << std::endl;
            return;
        }

        // 发送帧数据
        if (send(sock, reinterpret_cast<const char*>(frame.pFrameBuffer), frame.nFrameSize, 0) == SOCKET_ERROR) {
            std::cerr << "Send failed with error: " << WSAGetLastError() << std::endl;
            return;
        }

        std::cout << "Frame " << frameNumber << " data sent successfully." << std::endl;
    }
}

void SocketConnection::close_socket() const {
    // 关闭连接
    closesocket(sock);
    WSACleanup();
}

std::string SocketConnection::receive_signal() const{
    char buffer[1024];
    int bytesReceived = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytesReceived > 0) {
        buffer[bytesReceived] = '\0';
        return std::string(buffer);
    }
    return "";
}
