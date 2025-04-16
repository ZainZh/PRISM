from camera_calibration import CameraCalibration
from robot_calibration import RobotCalibration
import cv2


if __name__ == "__main__":
    rgb_camera_calibration = CameraCalibration("chessboard", "rgb_camera")
    rgb_camera_calibration.calibrate()


    #
    #
    # pseudo_rgb_image = "../chessboard.png"
    # pseudo_bgr_image = cv2.imread(pseudo_rgb_image)
    # spectral_camera_calibration = CameraCalibration("chessboard", "spectral_camera")
    # spectral_camera_calibration.calibrate_single_image(pseudo_bgr_image)

    #
    # robot_calibration = RobotCalibration("nachi", "chessboard")
    # robot_calibration.calibrate()
