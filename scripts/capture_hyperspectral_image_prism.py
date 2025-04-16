import numpy as np
import cv2
from src.modbus_motor_IPOS_mode import ModbusMotor_IPOSMODE as MotorControl
from spectral_image_receiver import ImageReceiver, ImagePostProcessor
import pandas as pd
import os


def calculate_position(r, theta, n, H):
    x_A = r * np.cos(np.deg2rad(theta))
    y_A = r * np.sin(np.deg2rad(theta))

    x_B = r * np.cos(np.deg2rad(theta - 360 / n))
    y_B = r * np.sin(np.deg2rad(theta - 360 / n))

    x_C = x_B + (x_A - x_B) * (-np.sqrt(2) / 2 * r - y_B) / (y_A - y_B)
    y_C = -np.sqrt(2) / 2 * r

    m_AB = (y_A - y_B) / (x_A - x_B)

    vector_AB = np.array([1, m_AB])

    vertor_vertical = np.array([-m_AB, 1])

    N_vertical = vertor_vertical / np.linalg.norm(vertor_vertical)

    I_incident = np.array([1, 0])
    R_reflected = I_incident - 2 * np.dot(I_incident, N_vertical) * N_vertical

    m_ref = R_reflected[1] / R_reflected[0]

    y_D = -np.sqrt(2) / 2 * r - H

    x_D = (y_D - y_C) / m_ref + x_C

    return x_D




def adding_black_row(image):
    new_shape = (image.shape[0] * 2, image.shape[1], image.shape[2])
    new_array = np.zeros(new_shape)
    new_array[::2] = image
    return new_array


if __name__ == "__main__":
    receiver = ImageReceiver(server_ip='127.0.0.1', data_port=8080, signal_port=8081)
    motor = MotorControl()
    motor.back_to_origin()
    rpm = 16
    lu_per_s = int((360 * rpm * 100) / 60)
    motor.set_velocity(rpm)
    motor_dict = {}
    timestamp_list = []
    current_position_list = []
    motor_start_position = 0
    motor_start_timestamp = 0
    experimental_signal_transmission_time = 0.07

    if receiver.setup_connections():
        start_signal_sent = False
        stop_signal_sent = False
        motor.set_absolutely_position(200000)
        ideal_start_position = 72000
        setting_position = ideal_start_position - lu_per_s * experimental_signal_transmission_time
        while True:
            current_position, timestamp = motor.get_position()
            current_position_list.append(current_position)
            timestamp_list.append(timestamp)
            if current_position >= setting_position and not start_signal_sent:
                motor_start_position = current_position
                motor_start_timestamp = timestamp
                receiver.send_signal("START")
                start_signal_sent = True
            if current_position >= setting_position + 36000 and not stop_signal_sent:
                receiver.send_signal("STOP")
                motor_end_position = current_position
                motor_end_timestamp = timestamp
                stop_signal_sent = True
                break
        print(f"Time taken {(motor_end_timestamp - motor_start_timestamp) / 1000} secovvnds")
        print("start_position: ", motor_start_position / 1000, "degree")
        print("end_position: ", motor_end_position / 1000, "degree")
        motor_info_list = [motor_start_position, motor_end_position, motor_start_timestamp, motor_end_timestamp]
        frames_dict = receiver.receive_image()

        image_post_processor = ImagePostProcessor(frames_dict, motor_info_list, rpm)
        print("transmission_time: ", image_post_processor.signal_transmission_time)
        print("motor_actual_start_position: ", image_post_processor.motor_actual_start_position)
        pixel_dict = {}
        for i in range(len(frames_dict["frames"])):
            percentage = image_post_processor.get_motor_actual_position_percentage(i)
            pixel_dict[i] = percentage * image_post_processor.ideal_height
        final_frames = image_post_processor.get_final_frames(pixel_dict)
        pseudo_rgb_image = image_post_processor.generate_pseudo_rgb_image(final_frames)
        # pseudo_rgb_image_1 = image_post_processor.generate_pseudo_rgb_image(frames_dict["frames"])
        name = "chart_60cm"
        cv2.imwrite(f"{name}.png",
                    image_post_processor.blank_pseudo_rgb_image)
        save_location = fr"C:\Users\SUN Zheng\OneDrive - The Chinese University of Hong Kong\CUHK学习\研究工作\高光谱相机项目\论文相关\光谱数据\衣物\cloth\{name}"
        if not os.path.exists(save_location):
            os.makedirs(save_location)
        np.save(f"{save_location}/{name}.npy", final_frames)
        cv2.imwrite(f"{name}.png", pseudo_rgb_image)
        motor.motor_stop()
        receiver.close_connections()
