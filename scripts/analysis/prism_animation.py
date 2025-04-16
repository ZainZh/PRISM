#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/2024 13:52
# @Author  : Zheng SUN
# @Company : The Chinese University of Hong Kong
# @File    : prism_optimization.py
# @Project : FlyingSpectral

# This file is used to optimize the camera's position to get the maximum sight range.,
"""

"""

import math
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from utilize import get_reflective_plate, get_vertex_position, get_reflection_line
from common import load_omega_config
from datetime import datetime
import csv
import os


class PrismOptimization(object):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.xdata, self.ydata = [], []
        (self.line_1,) = plt.plot([], [], "r-", animated=True)
        (self.line_2,) = plt.plot([], [], "b-", animated=True)
        (self.line_3,) = plt.plot([], [], "g-", animated=True)
        self.ax.set_title("Real-Time Plot")
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.save_path = os.path.join("log")
        self.log_file_name = (
                "camera_height_optimization"
                + datetime.now().strftime("%Y%m%d_%H%M%S")
                + ".csv"
                  ""
        )
        self.config = load_omega_config("animation")
        self.prism_position = self.config["prism_position"]
        self.vertex_num = self.config["vertex_num"]
        self.circumcised_radius = self.config["circumcised_radius"]
        self.prism_position = self.config["prism_position"]
        self.camera_position_y = self.prism_position[1] - math.sqrt(2)/2 * self.circumcised_radius
        self.camera_slope = 0.0
        self.camera_intercept = self.camera_position_y
        self.rotating_prism = None
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def write_dict_to_csv(self, contents):
        """Store contents to corresponding labels in the CSV file.

        Args:

            contents (dict): The dict to be saved into the CSV file.

        Returns:
            None
        """
        assert isinstance(contents, dict), print(
            "Content type is not 'dict' but '{}'".format(type(contents))
        )
        csv_path = os.path.join(self.save_path, self.log_file_name)
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a") as csvfile:
            dict_writer = csv.DictWriter(csvfile, fieldnames=contents.keys())
            if not file_exists:
                dict_writer.writeheader()
            dict_writer.writerow(contents)

    def init_figure(self):
        self.ax.set_xlim(self.config["x_lim"][0], self.config["x_lim"][1])
        self.ax.set_ylim(self.config["y_lim"][0], self.config["y_lim"][1])
        return (self.line_1, self.line_2, self.line_3)

    def update(self, frames, percentage=0):
        print("frames: ", frames)
        rotation_angle = frames
        vertex_position_list = get_vertex_position(
            self.prism_position,
            self.vertex_num,
            self.circumcised_radius,
            rotation_angle,
        )
        vertex_position = np.array(vertex_position_list)
        intersection_point, reflective_plane_slope, reflective_plane_intercept = get_reflective_plate(
            vertex_position, self.camera_slope, self.camera_intercept
        )


        if reflective_plane_slope is None:
            print("The camera is not in the reflective plane's range")
            return None, None, None
        camera_point = np.array([-20, self.camera_position_y])

        reflected_slope, reflected_intercept, reflected_vector = get_reflection_line(
            0, camera_point[1], reflective_plane_slope, reflective_plane_intercept
        )

        if reflective_plane_slope < 0:
            reflected_point_y = self.config["plane_y"]
            reflected_point_x = (
                                        reflected_point_y - reflected_intercept
                                ) / reflected_slope
            degree = math.degrees(math.atan(reflected_slope))
            record_dict = dict(
                frame=frames,
                reflected_point_x=reflected_point_x,
                percentage=percentage,
                degree=degree,
            )
            print("reflected_point_x: ", reflected_point_x)
            self.write_dict_to_csv(record_dict)
        else:
            reflected_point_y = self.camera_position_y + 20
            reflected_point_x = (
                                        reflected_point_y - reflected_intercept
                                ) / reflected_slope

        return (
            vertex_position,
            intersection_point,
            [reflected_point_x, reflected_point_y],
        )

    def figure_update(self, frames):
        # define the original prism vertex's position, counting in clockwise order  ,
        # the first four vertices are the bottom vertices, the last four vertices are the top vertices.
        # the coordinate system is located at the center of the prism's bottom face, the x-axis is pointing to the right,
        # the y-axis is pointing to the front
        vertex_position, intersection_point, reflected_point = self.update(frames)


        camera_point = np.array([-20, self.camera_position_y])
        # rotary wheel
        self.line_1.set_data(vertex_position[:, 0], vertex_position[:, 1])

        #
        self.line_2.set_data(
            np.array((camera_point[0], intersection_point[0], reflected_point[0])),
            np.array((camera_point[1], intersection_point[1], reflected_point[1])),
        )
        self.line_3.set_data(np.array((self.config["x_lim"][0], self.config["x_lim"][1])), np.array((0, 0)))
        return (self.line_1, self.line_2, self.line_3)

    def live(self):
        # 创建FuncAnimation对象，生成动画
        self.rotating_prism = FuncAnimation(
            self.fig,
            self.figure_update,
            frames=np.arange(0, 720, 1),
            init_func=self.init_figure,
            blit=True,
        )
        self.ax.set_aspect("equal")
        plt.show()

    def data_saver(self):
        for percentage in np.arange(0, -1, -0.05):
            print("percentage: ", percentage)
            for frame in np.arange(0, 720, 1):
                self.camera_position_y = (
                        self.config["circumcised_radius"] * percentage + self.config["prism_position"][1]
                )
                self.camera_slope = 0.0
                self.camera_intercept = self.camera_position_y
                vertex_position, intersection_point, reflected_point = self.update(
                    frame, percentage
                )


if __name__ == "__main__":
    # plt.ion()
    prism_opti = PrismOptimization()
    prism_opti.live()
