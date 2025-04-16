import numpy as np
import transform as transform
import robotics as robotics
from omegaconf import OmegaConf
import os.path as osp
import cv2 as cv
import matplotlib.pyplot as plt

def is_array_like(array):
    """"""
    if isinstance(array, str):
        return False
    return hasattr(array, "__len__") and hasattr(array, "__iter__")


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


def sd_pose(pose, check=False):
    """Standardize the input pose to the 4x4 homogeneous transformation matrix SE(3).

    Args:
        pose (np.ndarray): Values denoting a pose/transformation.
        check (bool): If true, will check if the input is legal.

    Returns:
        np.ndarray: 4x4 transform matrix in SE(3).

    Raises:
        ValueError: If check and check failed.
        NotImplementedError: If the input type or shape is not supported.
    """
    if isinstance(pose, np.ndarray):
        if pose.ndim == 1 and pose.size == 7:
            t = pose[:3]
            q = pose[3:]
            tm = transform.translation_matrix(t)
            rm = transform.quaternion_matrix(q)
            if check and not robotics.test_if_SE3(rm):
                raise ValueError("Matrix is not in SE3")
            # make sure to let tm left product rm
            return np.dot(tm, rm)
        elif pose.ndim == 1 and pose.size == 6:
            t = pose[:3]
            rpy = pose[3:]
            tm = transform.translation_matrix(t)
            rm = transform.euler_matrix(rpy[0], rpy[1], rpy[2])
            if check and not robotics.test_if_SE3(rm):
                raise ValueError("Matrix is not in SE3")
            return np.dot(tm, rm)
        elif pose.shape == (4, 4):
            if check and not robotics.test_if_SE3(pose):
                raise ValueError("Matrix is not in SE3")
            return pose
        else:
            raise NotImplementedError(
                f"Numpy array of shape {pose.shape} is not supported"
            )
    elif isinstance(pose, list) or isinstance(pose, tuple):
        return sd_pose(np.array(pose, dtype=float))
    else:
        raise NotImplementedError("Pose of type {} is not supported".format(type(pose)))


def load_omega_config(config_name):
    """Load the configs listed in config_name.yaml.

    Args:
        config_name (str): Name of the config file.

    Returns:
        (dict): A dict of configs.
    """
    return OmegaConf.load(
        osp.join(osp.dirname(__file__), "../config/{}.yaml".format(config_name))
    )


def update_omega_config(config_name, key, value):
    """Update the content of the config file config_name.yaml in the predefined path.
    If the configuration file has not yet been created, create the file and write the specified key value into it.

    If it has been created:
    1) If the `key` is new to the existed configurations, create this key and assign its value with `value`.
    2) If the `key` is already there, override its value with `value`.

    Other keys and their values are not affected, but are passed on to the newly created configuration file which
    overwrites the original file.

    Args:
        config_name (str): Name of the config file not including suffix (.yaml).
        key (Any): Key of the item.
        value (Any): Value of the item whose key is `key`.
    """
    if isinstance(value, np.ndarray):
        value = value.tolist()
    config_item = OmegaConf.create({key: value})
    config_file = osp.join(osp.dirname(__file__), f""
                                                  f"../config/{config_name}.yaml")
    if osp.exists(config_file):
        loaded = OmegaConf.load(config_file)
    else:
        loaded = None
    if loaded:
        if key in loaded:
            OmegaConf.update(loaded, key, value)
        else:
            loaded = OmegaConf.merge(config_item, loaded)
    else:
        loaded = config_item
    OmegaConf.save(loaded, f=config_file)


def get_point(event, x, y, flags, param):
    if event == cv.EVENT_LBUTTONDOWN:
        # 输出坐标
        print("clicking: ", x, y)
        # 在传入参数图像上画出该点
        cv.circle(param, (x, y), 1, (255, 255, 255), thickness=-1)


def click_and_get_pixel(image):
    """
    Click the image and get the clicked point's pixel.
    :param image: The image you want to get the point pixels or numpy array
    :return:
    """
    if isinstance(image, str):
        image = cv.imread(image)
    elif not isinstance(image, np.ndarray):
        raise ValueError("Image should be a path or a numpy array")
    cv.namedWindow("image")
    cv.setMouseCallback("image", get_point, image)
    while True:
        cv.imshow("image", image)
        if cv.waitKey(20) & 0xFF == 27:
            break

    cv.destroyAllWindows()


3


def generate_pseudo_rgb_image(nir_array):
    pseudo_image = cv.merge([nir_array[:, :, 150], nir_array[:, :, 200], nir_array[:, :, 300]])
    pseudo_image = pseudo_image ** (1 / 2.2)
    pseudo_image = cv.merge((rescale(pseudo_image[:, :, 0]),
                             rescale(pseudo_image[:, :, 1]),
                             rescale(pseudo_image[:, :, 2])))
    return pseudo_image


def rescale(gray_img, min_value=0, max_value=255):
    if len(np.shape(gray_img)) != 2:
        print("Image is not grayscale")
    rescaled_img = np.interp(gray_img, (np.nanmin(gray_img), np.nanmax(gray_img)), (min_value, max_value))
    return rescaled_img.astype('uint8')


def expect_yes_no_input(hint, is_yes_default=True):
    """Get user input for a yes/no choice.

    Args:
        hint: str Hint for the user to input.
        is_yes_default: bool If true, 'yes' will be considered as the default when empty input was given.
                        Otherwise, 'no' will be considered as the default choice.

    Returns:
        bool If the choice matches the default.
    """
    if is_yes_default:
        suffix = "(Y/n):"
        default = "yes"
    else:
        suffix = "(y/N):"
        default = "no"
    flag = input(" ".join((hint, suffix))).lower()

    expected_flags = ["", "y", "n"]
    while flag not in expected_flags:
        print_warning(
            f"Illegal input {flag}, valid inputs should be Y/y/N/n or ENTER for the default: {default}"
        )
        return expect_yes_no_input(hint, is_yes_default)

    if is_yes_default:
        return flag != "n"
    else:
        return flag != "y"


def expect_float_input(hint):
    """Get user input for obtaining a float number.

    Args:
        hint (str): Hint for the user to input.

    Returns:
        float: User input value.
    """
    user_input = expect_any_input(hint)
    while not is_float_compatible(user_input):
        print_warning(
            f"Illegal input '{user_input}', valid input should be a float number"
        )
        return expect_float_input(hint)
    return float(user_input)


def is_float_compatible(string):
    """Check if the string can be converted to a float.

    Args:
        string (str): Input string.

    Returns:
        bool: True if the string can be converted to a float, false otherwise.
    """
    string = string.lstrip("-")
    s_dot = string.split(".")
    if len(s_dot) > 2:
        return False
    s_e_plus = string.split("e+")
    if len(s_e_plus) == 2:
        return is_float_compatible("".join(s_e_plus))
    s_e_minus = string.split("e-")
    if len(s_e_minus) == 2:
        return is_float_compatible("".join(s_e_minus))
    s_e = string.split("e")
    if len(s_e) == 2:
        return is_float_compatible("".join(s_e))

    for si in s_dot:
        if not si.isdigit():
            return False
    return True


def expect_any_input(hint):
    """Get any kind of user input.

    Args:
        hint (str): Hint to the user.

    Returns:
        Any user input.
    """
    if not isinstance(hint, str):
        hint = str(hint)
    if not hint.endswith(" "):
        hint += " "
    return input(hint)


def get_contours(image, bbox):
    """
    Get the contours of the image under the bbox.
    Args:
        image:
        bbox:

    Returns: all contours pixels

    """
    x1, y1, x2, y2 = bbox
    cropped_image = image[y1:y2, x1:x2]

    # 转换为灰度图像
    gray = cv.cvtColor(cropped_image, cv.COLOR_BGR2GRAY)

    # 应用高斯模糊
    blurred = cv.GaussianBlur(gray, (5, 5), 0)

    # 使用Canny边缘检测算法
    edges = cv.Canny(blurred, 50, 150)

    # 查找轮廓
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    max_contour = max(contours, key=cv.contourArea)

    # 将轮廓坐标转换回原图的坐标系
    adjusted_max_contour = max_contour + np.array([x1, y1])

    contour_image = image.copy()

    cv.drawContours(contour_image, [adjusted_max_contour], -1, (0, 255, 0), 2)
    # 将轮廓坐标转换回原图的坐标系
    adjusted_contours = [contour + np.array([x1, y1]) for contour in contours]

    # contour_areas = [cv.contourArea(contour) for contour in contours]
    return contour_image, adjusted_contours


def get_contours_bbox(contours):
    """
    Get the bounding box of the contour.
    Args:
        contours:

    Returns:
        bbox: [min_x, min_y, max_x, max_y]
    """
    all_points = np.vstack(contours)
    x_values = all_points[:, 0, 0]

    # 计算x的最小值和最大值
    min_x = np.min(x_values)
    max_x = np.max(x_values)

    y_values = all_points[:, 0, 1]

    min_y = np.min(y_values)
    max_y = np.max(y_values)

    return [min_x, min_y, max_x, max_y]


def get_threshold_mask(image, threshold):
    """
    Get the mask of the image with the threshold.
    Args:
        image:
        threshold:

    Returns:
        mask: the mask of the image with the threshold.
    """
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, mask = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY_INV)
    return mask





