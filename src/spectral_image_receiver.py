import socket
import numpy as np
import struct
from common import print_debug
import cv2
import pandas as pd

class ImageReceiver:
    def __init__(self, server_ip, data_port, signal_port, header_size=24):
        self.server_ip = server_ip
        self.data_port = data_port
        self.signal_port = signal_port
        self.header_size = header_size
        self.data_socket = None
        self.signal_socket = None
        self.data_conn = None
        self.signal_conn = None
        self.frame_dict = {}

    def setup_connections(self):
        # Setup data socket
        try:
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.bind((self.server_ip, self.data_port))
            self.data_socket.listen(1)
            print("Waiting for data connection...")
            self.data_conn, addr = self.data_socket.accept()
            print(f"Data connected by {addr}")
        except Exception as e:
            print(f"Failed to bind or accept data connection: {e}")
            return False

        # Setup signal socket
        try:
            self.signal_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.signal_socket.bind((self.server_ip, self.signal_port))
            self.signal_socket.listen(1)
            print("Waiting for signal connection...")
            self.signal_conn, sign_addr = self.signal_socket.accept()
            print(f"Signal connected by {sign_addr}")
        except Exception as e:
            print(f"Failed to bind or accept signal connection: {e}")
            return False

        return True

    def send_signal(self, signal):
        try:
            self.signal_conn.sendall(signal.encode('utf-8'))
        except Exception as e:
            print(f"Error sending signal '{signal}': {e}")

    def receive_image(self):
        frames = []
        frame_numbers = []
        timestamps = []
        while True:
            try:
                header = self.data_conn.recv(self.header_size)
                if not header:
                    continue
                try:
                    frame_size, frame_number, timestamp_ms = struct.unpack('qqq', header)
                except Exception as e:
                    print_debug(f"Error unpacking header: {e}")
                    continue

                if frame_number == -1:
                    print("Finished receiving data")
                    break

                data = b''
                while len(data) < frame_size:
                    packet = self.data_conn.recv(frame_size - len(data))
                    if not packet:
                        break
                    data += packet

                if len(data) != frame_size:
                    print("Incomplete data received")
                    break

                image = np.frombuffer(data, dtype=np.uint16).reshape((448, 512))
                frames.append(np.transpose(image))
                frame_numbers.append(frame_number)
                timestamps.append(timestamp_ms)

            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        self.frame_dict["frame_number"] = frame_numbers
        self.frame_dict["timestamp_ms"] = timestamps
        self.frame_dict["frames"] = np.array(frames)
        # print(f"Received frame number: {frame_numbers[-2]}")
        return self.frame_dict

    def close_connections(self):
        if self.signal_conn:
            self.signal_conn.close()
        if self.data_conn:
            self.data_conn.close()
        if self.signal_socket:
            self.signal_socket.close()
        if self.data_socket:
            self.data_socket.close()

    def is_connected(self):
        return self.data_conn is not None and self.signal_conn is not None

def calculate_detection_line_position(theta, r=73.5, n=10, H=348):
    x_A = r * np.cos(np.deg2rad(theta))
    y_A = r * np.sin(np.deg2rad(theta))

    x_B = r * np.cos(np.deg2rad(theta - 360 / n))
    y_B = r * np.sin(np.deg2rad(theta - 360 / n))

    x_C = x_B + (x_A - x_B) * (-np.sqrt(2) / 2 * r - y_B) / (y_A - y_B)
    y_C = -np.sqrt(2) / 2 * r

    m_AB = (y_A - y_B) / (x_A - x_B)

    vertor_vertical = np.array([-m_AB, 1])

    N_vertical = vertor_vertical / np.linalg.norm(vertor_vertical)

    I_incident = np.array([1, 0])
    R_reflected = I_incident - 2 * np.dot(I_incident, N_vertical) * N_vertical

    m_ref = R_reflected[1] / R_reflected[0]

    y_D = -np.sqrt(2) / 2 * r - H

    x_D = (y_D - y_C) / m_ref + x_C

    return x_D

def inverse_calculate_detection_line_position(x_D_target, r=73.5, n=10, H=348):
    """
    通过给定的 x_D 反推出 θ。假设 θ 在 -45 到 -9 之间。
    """
    # 定义搜索范围
    theta_range = np.linspace(-45, -9, 1000)  # 在 -45 到 -9 之间搜索

    closest_theta = None
    smallest_diff = float('inf')

    # 在指定范围内搜索最接近的 θ
    for theta in theta_range:
        x_D =calculate_detection_line_position(theta, r, n, H)
        diff = abs(x_D - x_D_target)
        if diff < smallest_diff:
            smallest_diff = diff
            closest_theta = theta
    return closest_theta


class ImagePostProcessor:
    def __init__(self, frame_info_dict, motor_info_list, rpm):
        self.frame_dict = frame_info_dict
        self.wheel_rpm = rpm / 10
        self.motor_info = motor_info_list
        self.motor_info_list = motor_info_list
        self.frames = self.frame_dict["frames"]
        self.frame_height, self.frame_width, self.frame_channels = self.frame_dict["frames"].shape
        self.ideal_width = 512
        self.ideal_height = 871
        self.blank_frames_image = np.zeros((self.ideal_height, self.ideal_width, self.frame_channels))
        self.blank_pseudo_rgb_image = np.zeros((self.ideal_height, self.ideal_width, 3))
        self.degree_compenstation = -9
        # camera related parameters
        self.camera_start_timestamp = self.frame_dict["timestamp_ms"][0]
        self.camera_end_timestamp = self.frame_dict["timestamp_ms"][-1]
        self.capture_time = (self.camera_end_timestamp - self.camera_start_timestamp) / 1000
        self.time_per_frame = self.capture_time / self.frame_height

        # motor related parameters
        self.signal_transmission_time = (self.camera_start_timestamp - self.motor_info[2]) / 1000
        self.motor_actual_start_position = self.motor_info_list[
                                               0] / 1000 + self.signal_transmission_time * self.wheel_rpm / 60 * 360
        self.motor_actual_position_per_frame = self.wheel_rpm / 60 * 360 * self.time_per_frame
        self.limited_position_left = self.calculate_detection_line_position(-45)
        self.limited_position_right = self.calculate_detection_line_position(-9)

    def get_motor_actual_position_percentage(self, frame_number):
        degree = self.motor_actual_start_position + frame_number * self.motor_actual_position_per_frame + self.degree_compenstation
        adjusted_degree = ((degree + 45) % 36) - 45
        if adjusted_degree > -9:
            adjusted_degree -= 36
        position = self.calculate_detection_line_position(adjusted_degree)
        percentage = (position - self.limited_position_left) / (
                self.limited_position_right - self.limited_position_left)
        return percentage

    @staticmethod
    def calculate_detection_line_position(theta, r=73.5, n=10, H=348):
        x_A = r * np.cos(np.deg2rad(theta))
        y_A = r * np.sin(np.deg2rad(theta))

        x_B = r * np.cos(np.deg2rad(theta - 360 / n))
        y_B = r * np.sin(np.deg2rad(theta - 360 / n))

        x_C = x_B + (x_A - x_B) * (-np.sqrt(2) / 2 * r - y_B) / (y_A - y_B)
        y_C = -np.sqrt(2) / 2 * r

        m_AB = (y_A - y_B) / (x_A - x_B)

        vertor_vertical = np.array([-m_AB, 1])

        N_vertical = vertor_vertical / np.linalg.norm(vertor_vertical)

        I_incident = np.array([1, 0])
        R_reflected = I_incident - 2 * np.dot(I_incident, N_vertical) * N_vertical

        m_ref = R_reflected[1] / R_reflected[0]

        y_D = -np.sqrt(2) / 2 * r - H

        x_D = (y_D - y_C) / m_ref + x_C

        return x_D

    def generate_pseudo_rgb_image(self, nir_array):
        pseudo_image = cv2.merge([nir_array[:, :, 150], nir_array[:, :, 200], nir_array[:, :, 300]])
        pseudo_image = pseudo_image ** (1 / 2.2)
        pseudo_image = cv2.merge((self.rescale(pseudo_image[:, :, 0]),
                                  self.rescale(pseudo_image[:, :, 1]),
                                  self.rescale(pseudo_image[:, :, 2])))
        return pseudo_image

    @staticmethod
    def rescale(gray_img, min_value=0, max_value=255):
        if len(np.shape(gray_img)) != 2:
            print("Image is not grayscale")
        rescaled_img = np.interp(gray_img, (np.nanmin(gray_img), np.nanmax(gray_img)), (min_value, max_value))
        return rescaled_img.astype('uint8')

    def process_image(self, image):
        pass

    @staticmethod
    def save_dict_to_excel(dictionary, filename):
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(dictionary)
        # Write the DataFrame to an Excel file
        df.to_excel(filename, index=False)

    @staticmethod
    def get_rounded_data_dict(data_dict):
        # 初始化一个空字典来存储结果
        rounded_data = {}

        # 遍历原始字典
        for key, value in data_dict.items():
            # 将值四舍五入到最近的整数
            rounded_value = round(value)

            # 如果该整数已经在结果字典中，检查并更新为更接近的值
            if rounded_value in rounded_data:
                # 如果当前值更接近四舍五入后的值，则更新
                if abs(rounded_value - value) < abs(rounded_value - rounded_data[rounded_value][1]):
                    rounded_data[rounded_value] = (key, value)
            else:
                # 如果该整数不在结果字典中，直接添加
                rounded_data[rounded_value] = (key, value)

        # 创建最终结果字典，只保留键和值

        return rounded_data

    def get_final_frames(self, pixel_dict):
        rounded_dict = self.get_rounded_data_dict(pixel_dict)
        origin_pseudo_rgb_image = self.generate_pseudo_rgb_image(self.frames)
        for key, value in rounded_dict.items():
            frame_index = value[0]
            self.blank_frames_image[key - 1] = self.frames[frame_index]
            self.blank_pseudo_rgb_image[key - 1] = origin_pseudo_rgb_image[frame_index]
        return self.blank_frames_image
