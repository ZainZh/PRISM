cmake_minimum_required(VERSION 3.28)
project(device)

# for .h files
include_directories(specim/include nachi/include libmodbus/include)

# for .lib files
link_directories("C:/Program Files (x86)/Specim/SDKs/Lumo_Sensor_SDK/2023_726/bin/x64")
link_directories("C:/Program Files/nachi/OpenNR-IF")
link_directories(libmodbus/lib)


# add the executable
add_executable(specim specim/scripts/specim.cpp
        specim/lib/specim_camera.cpp specim/scripts/socket.cpp
)

add_executable(nachi_test nachi/scripts/execute_external_tracking.cpp
            nachi/lib/nachi_api.cpp
            nachi/lib/robot_socket.cpp
             nachi/include/robot_socket.h
            libmodbus/scripts/ModbusController.cpp
            libmodbus/include/ModbusController.h)

add_executable(external_tracking nachi/scripts/external_tracking.cpp
        nachi/lib/nachi_api.cpp
        nachi/lib/robot_socket.cpp
        nachi/include/robot_socket.h)

add_executable(external_tracking_1 nachi/scripts/external_tracking_1.cpp
        nachi/lib/nachi_api.cpp)

add_executable(modbus_suction libmodbus/scripts/ModbusController.cpp
        libmodbus/include/ModbusController.h)

# link the library
target_link_libraries(specim "C:/Program Files (x86)/Specim/SDKs/Lumo_Sensor_SDK/2023_726/bin/x64/SpecSensor.lib" Ws2_32)
target_link_libraries(modbus_suction modbus)
target_link_libraries(nachi_test OpenNR-IF modbus Ws2_32)
target_link_libraries(external_tracking OpenNR-IF modbus Ws2_32)
target_link_libraries(external_tracking_1 OpenNR-IF)






