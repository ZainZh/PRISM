#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 20/3/2024 18:00
# @Author  : Zheng SUN
# @Company : The Chinese University of Hong Kong
# @File    : utilize.py
# @Project : FlyingSpectral

import numpy as np
import sympy as sp
from collections import Counter


def get_reflective_plate(vertex_position, inline_slope, inline_intercept):
    """
    This function is used to calculate the reflective line's slope and intercept and the intersection point.

    Args:
        vertex_position [list]: the prism's vertex position, the first four vertices are the bottom vertices, the last
        four vertices are the top vertices.
        inline_slope [float]: the incident line's slope
        inline_intercept [float]: the incident line's intercept

    Returns:
        intersection_point [list]: the intersection point.
        slope [list]: the reflective line's slope.
        intercept [list]: the reflective line's intercept.
    """
    t = sp.symbols("t")
    vertex_position_y = vertex_position[:, 1]
    line_y_list = [
        (vertex_position_y[i], vertex_position_y[i + 1])
        for i in range(len(vertex_position_y) - 1)
    ]
    line_y_list.append((vertex_position_y[-1], vertex_position_y[0]))
    reflective_line_info = []

    for start, end in line_y_list:
        start_point = vertex_position[np.where(vertex_position_y == start)[0][-1]]
        end_point = vertex_position[np.where(vertex_position_y == end)[0][-1]]
        # the parameter equation P = P0 + t(P1 - P0), P0 = (x0, y0), P1 = (x1, y1)
        # the equation of the line is y = slope * x + intercept
        # the equation of the parameter equation is y = start_point[1] + t * (end_point[1] - start_point[1]) - slope * (
        #             start_point[0] + t * (end_point[0] - start_point[0]))
        t_solution = sp.solve(
            start_point[1]
            + t * (end_point[1] - start_point[1])
            - inline_slope * (start_point[0] + t * (end_point[0] - start_point[0]))
            - inline_intercept,
            t,
        )
        slope = (end_point[1] - start_point[1]) / (end_point[0] - start_point[0])
        intercept = start_point[1] - slope * start_point[0]
        if len(t_solution) == 0:
            continue
        else:
            t_solution = t_solution[0]
            if 0 <= t_solution <= 1:
                x_solution = start_point[0] + t_solution * (
                    end_point[0] - start_point[0]
                )
                y_solution = start_point[1] + t_solution * (
                    end_point[1] - start_point[1]
                )
                reflective_line_info.append([x_solution, y_solution, slope, intercept])
    if len(reflective_line_info) == 0:
        print_warning("The camera is not in the reflective plane's range")
        return None, None, None
    left_intersection_index = reflective_line_info.index(
        min(reflective_line_info, key=lambda x: x[0])
    )
    intersection_point = np.array([
        reflective_line_info[left_intersection_index][0],
        reflective_line_info[left_intersection_index][1],
    ])
    return (
        intersection_point,
        reflective_line_info[left_intersection_index][2],
        reflective_line_info[left_intersection_index][3],
    )


def get_vertex_position(prism_position, vertex_num, circumcised_radius, rotation_angle):
    """
    This function is used to calculate the prism's vertex position
    Args:
        prism_position [list]: the prism's position, (x, y).
        vertex_num [int]: the number of vertices
        circumcised_radius [float]: the prism's circumcised radius

    Returns:
        vertex_position [list]: the prism's vertex position, the first four vertices are the bottom vertices,
        the last four vertices are the top vertices.
    """
    vertex_position = []
    for i in range(vertex_num + 1):
        point = np.array(
            [
                circumcised_radius
                * np.cos(
                    (-180 / vertex_num + (-360/vertex_num * i) + rotation_angle) / 180 * np.pi
                )
                + prism_position[0],
                circumcised_radius
                * np.sin(
                    (-180 / vertex_num + (-360/vertex_num * i) + rotation_angle) / 180 * np.pi
                )
                + prism_position[1],
            ]
        )
        vertex_position.append(point)
    return np.array(vertex_position)

def get_reflection_line(m1, b1, m2, b2):
    """
    This function is used to calculate the reflective line's slope and intercept
    Args:
        m1: the incident line's slope
        b1: the incident line's intercept
        m2: the reflective plane's slope
        b2: the reflective plane's intercept

    Returns:
        m_reflected: the reflective line's slope
        b_reflected: the reflective line's intercept
        R: the reflective vector
    """
    # calculate the intersection point
    x_intersection = (b2 - b1) / (m1 - m2) if m1 - m2 != 0 else b1
    y_intersection = m1 * x_intersection + b1

    # calculate the reflective plate's normal vector
    N = np.array([-m2, 1])
    N_normalized = N / np.linalg.norm(N)

    # calculate the incident vector
    I = np.array([1, m1])

    # calculate the reflective vector
    R = I - 2 * np.dot(I, N_normalized) * N_normalized

    # calculate the reflective line's slope and intercept
    m_reflected = R[1] / R[0]
    b_reflected = y_intersection - m_reflected * x_intersection

    return m_reflected, b_reflected, R

def print_debug(*args):
    """Print information with green."""
    print("".join(["\033[1m\033[92m", _preprocess_print(*args), "\033[0m"]))


def print_info(*args):
    """Print information with sky blue."""
    print("".join(["\033[1m\033[94m", _preprocess_print(*args), "\033[0m"]))


def print_warning(*args):
    """Print a warning with yellow."""
    print("".join(["\033[1m\033[93m", _preprocess_print(*args), "\033[0m"]))


def print_error(*args):
    """Print error with red."""
    print("".join(["\033[1m\033[91m", _preprocess_print(*args), "\033[0m"]))


def _preprocess_print(*args):
    """Preprocess the input for colorful printing.

    Args:
        args (Any|None): One or more any type arguments to print.

    Returns:
        str Msg to print.
    """
    str_args = ""
    for a in args:
        if isinstance(a, np.ndarray):
            str_args += "\n" + np.array2string(a, separator=", ")
        else:
            str_args += " " + str(a)
    separate_with_newline = str_args.split("\n")
    extra_whitespaces_removed = []
    for b in separate_with_newline:
        extra_whitespaces_removed.append(" ".join(b.split()))
    return "\n".join(extra_whitespaces_removed)
