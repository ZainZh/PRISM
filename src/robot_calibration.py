import numpy as np
import sys
import os

from common import (
    load_omega_config,
    update_omega_config,
    print_info,
    print_warning,
    print_error,
    expect_yes_no_input,
    expect_float_input,
)
from transform import rigid_transform_3d


class RobotCalibration(object):
    def __init__(self, robot_config, chessboard_config):
        """Initialize the robot calibration object.

        Args:
            robot_config (str): Name of the YAML file for the robot configuration.
            chessboard_config: Name of the YAML file for the calibration chessboard configuration.
        """
        self._robot_config_name = robot_config
        self._robot_config = load_omega_config(robot_config)
        self._robot_ip = self._robot_config["ip"]
        self._robot_id = self._robot_config["id"]

        self._chessboard_config = load_omega_config(chessboard_config)
        self._chessboard_corner_columns = self._chessboard_config["corner_columns"]
        self._chessboard_corner_rows = self._chessboard_config["corner_rows"]
        self._chessboard_pattern_width = self._chessboard_config["pattern_width"]
        self._chessboard_pattern_height = self._chessboard_config["pattern_height"]
        self._chessboard_square_size = self._chessboard_config["square_size"]  # mm
        self._chessboard_thickness = self._chessboard_config["thickness"]  # mm

        self._corners_to_pick = ("top_left", "top_right", "bottom_right", "bottom_left")
        self._register_values = []

    @property
    def _four_corner_points(self):
        """Return the calibration board's four corner points' 3D coordinates in the board's local frame:
        1) the origin of the frame is the top-left corner of the board
        2) the +X axis points to the feed forward direction and is parallel with the board plate
        3) the +Y axis points to the left of the board
        4) the +Z axis points from the back of the board to the pattern

        The four points are ordered clock-wise starting from the top-left corner.

        Returns:
            ndarray
        """
        return np.array(
            [
                [0, 0, 0],
                [0, -self._chessboard_pattern_width, 0],
                [-self._chessboard_pattern_height, -self._chessboard_pattern_width, 0],
                [-self._chessboard_pattern_height, 0, 0],
            ],
            dtype=float,
        )

    def _check_robot_connection(self):
        """Check if the connection to the robot could be established with ping running in an infinite loop.

        Returns:
            None
        """
        while os.system("ping -c 1 " + self._robot_ip) != 0:
            print_warning(
                f"Trying to ping the robot at {self._robot_id}, please wait ..."
            )

    def _get_conveyor_translation_vector(self, corner_set_1, corner_set_2):
        """Get the normalized translation vector denoting the convey direction represented
        in the robot frame.

        Args:
            corner_set_1: ndarray (4, 3) First set of corners' coordinates in the robot frame.
            corner_set_2: ndarray (4, 3) Second set of corners' coordinates in the robot frame.

        Returns:
            ndarray (3, ) The normalized translation vector pointing from 1 to 2.
        """
        raw_vectors = np.mean(corner_set_2 - corner_set_1, axis=0)
        robot_measured_distance = np.linalg.norm(raw_vectors)
        # TODO check if this gives real distance in mm
        encoder_measured_distance = np.fabs(
            self._register_values[-1] - self._register_values[-2]
        )
        if not np.allclose(
            robot_measured_distance, encoder_measured_distance, atol=5e1
        ):
            print_warning(
                f"Robot measured conveyor translation {robot_measured_distance} "
                f"is different from encoder measured {encoder_measured_distance}"
            )
        else:
            print_info(
                f"Robot measured conveyor translation distance {robot_measured_distance} \n"
                f"Encoder measured conveyor translation distance {encoder_measured_distance}"
            )
        return raw_vectors / robot_measured_distance

    def _get_world_to_robot_transform(self, corner_set_1):
        """Get the world frame to robot frame transform matrix.

        Args:
            corner_set_1: ndarray (4, 3) First set of corners' coordinates in the robot frame.
            corner_set_2: ndarray (4, 3) Second set of corners' coordinates in the robot frame.

        Returns:
            ndarray (4, 4) World frame to robot frame transform matrix (SE3).
        """
        # conveyor_translation_vector = self._get_conveyor_translation_vector(
        #     corner_set_1, corner_set_2
        # )
        # translated_corner_set_1 = corner_set_1 - conveyor_translation_vector * np.fabs(
        #     self._register_values[0] - self._register_values[1]
        # )

        world_to_robot_transform = rigid_transform_3d(
            self._four_corner_points.T, corner_set_1
        )
        print_info(
            "The world to robot transform matrix is:",
            world_to_robot_transform,
        )
        update_omega_config(
            self._robot_config_name, "transform", world_to_robot_transform
        )
        return world_to_robot_transform

    def _get_conveyor_register_number(self):
        """"""
        return expect_float_input(
            f"Please input the current register number for {self._robot_id}: "
        )

    def _pre_check(self):
        """"""
        if not expect_yes_no_input(
            "Did you move the chessboard after camera calibration?",
            is_yes_default=False,
        ):
            print_error(
                "Please redo the calibration and DO NOT move the chessboard after camera calibration"
            )
            sys.exit()
        # Add the initial register value
        self._register_values.append(self._get_conveyor_register_number())

    def _check_robot_workspace(self):
        """"""
        if not expect_yes_no_input(
            "Is the chessboard inside the robot's workspace?",
            is_yes_default=True,
        ):
            print_error("Please redo the calibration")
            sys.exit()

        self._register_values.append(self._get_conveyor_register_number())

    def _get_corners_in_robot_frame(self):
        """Given the chessboard corners to pick with the tip of the robot, get the corner's coordinates
        (X_r, Y_r, Z_r) in the robot frame and store them into the return ndarray.

        Returns:
            ndarray (4, 3) Corners' coordinates in the robot frame.
        """
        corners_in_robot_frame = []
        for corner_id in self._corners_to_pick:
            print_warning(f"Move the tip to stab the chessboard's {corner_id} corner")
            X_r = expect_float_input(f"Input the {corner_id} corner's X_r reading: ")
            Y_r = expect_float_input(f"Input the {corner_id} corner's Y_r reading: ")
            Z_r = expect_float_input(f"Input the {corner_id} corner's Z_r reading: ")
            corners_in_robot_frame.append([X_r, Y_r, Z_r])
            print_info(
                f"Picked {corner_id} corner's coordinates in the robot frame\n",
                corners_in_robot_frame,
            )
        return np.array(corners_in_robot_frame)

    def _verify_transform_matrix(self, world_to_robot_transform):
        """Verify the calculated world to robot transform matrix by mapping the (5, 5) corner
        from the world frame to the robot frame and compare measured values in the robot frame.

        Args:
            world_to_robot_transform: ndarray (4, 4) World to robot frame transform matrix in SE3.

        Returns:
            None.
        """
        world_corner_point_for_verification = np.array(
            [
                -100.0 + self._register_values[-1] - self._register_values[0],
                -100,
                0.0,
                1.0,
            ],
            dtype=float,
        )
        estimated_corner_point = (
            np.linalg.inv(world_to_robot_transform)
            @ world_corner_point_for_verification
        )

        print_info(
            f"Move the tip to stab the chessboard's verification corner point (5, 5)"
        )
        picked_corner_point_x = expect_float_input("The point's X_r coordinate is: ")
        picked_corner_point_y = expect_float_input("The point's Y_r coordinate is: ")
        picked_corner_point_z = expect_float_input("The point's Z_r coordinate is: ")

        error = (
            np.linalg.norm(
                (
                    [
                        picked_corner_point_x - estimated_corner_point[0],
                        picked_corner_point_y - estimated_corner_point[1],
                        picked_corner_point_z - estimated_corner_point[2],
                    ]
                )
            )
            / 3.0
        )
        print_info("The calibration error is ", error, " mm.")

    def calibrate(self):
        """"""
        # self._check_robot_connection()
        print_info("Successfully connected the robot, start calibrating!")
        print_info("__________________________________________________________________")

        self._pre_check()
        print_info("__________________________________________________________________")

        # print_info(
        #     "Run the conveyor to transport the chessboard to the 1st canonical position in the robot's workspace"
        # )
        # self._check_robot_workspace()

        corners_set_1 = self._get_corners_in_robot_frame()
        # print_info("__________________________________________________________________")
        #
        # print_info(
        #     "Run the conveyor to transport the chessboard to the 2nd canonical position in the robot's workspace"
        # )
        # self._check_robot_workspace()

        # corners_set_2 = self._get_corners_in_robot_frame()
        print_info("__________________________________________________________________")

        world_to_robot_transform = self._get_world_to_robot_transform(
            corners_set_1.T
        )
        print_info("__________________________________________________________________")
        self._verify_transform_matrix(world_to_robot_transform)
