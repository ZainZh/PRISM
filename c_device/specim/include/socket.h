//
// Created by SUN Zheng on 2024/7/25.
//

#ifndef SOCKET_H
#define SOCKET_H
#include "specim_camera.h"
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <thread>
#include <atomic>



class SocketConnection {
public:
   SocketConnection(const std::string& serverIP, int serverPort);
   void init_socket();

   std::vector<std::string> receive_data();

   void connect_socket();
   void send_frames(const std::vector<FrameData>& frameDataList) const;
   void close_socket() const;
   [[nodiscard]] std::string receive_signal() const;


private:
   WSADATA wsaData;
   struct sockaddr_in server_addr;
   int iResult;
   int sock;
   std::string serverIP;
   int serverPort;
};



#endif //SOCKET_H
