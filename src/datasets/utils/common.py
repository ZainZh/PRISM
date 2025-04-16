# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/10
# @Address  : clover Lab @ CUHK
# @FileName : common.py

# @Description : TODO
import numpy as np
import os
from sklearn.feature_extraction import image


def generate_data_set(spectral: np.ndarray, ground_truth_labels: np.ndarray):
    coords = np.indices(ground_truth_labels.shape[:2]).reshape(2, -1).T
    np.random.shuffle(coords)
    quarter = len(coords) // 4
    train_set = coords[: int(3 / 4 * quarter)]
    test_set = coords[int(3 / 4 * quarter) :]

    train_x = spectral[train_set[:, 0], train_set[:, 1], :]
    train_y = ground_truth_labels[train_set[:, 0], train_set[:, 1]]

    test_x = spectral[test_set[:, 0], test_set[:, 1], :]
    test_y = ground_truth_labels[test_set[:, 0], test_set[:, 1]]
    return train_x, train_y, test_x, test_y


def get_subdirectories(directory):
    return [
        name
        for name in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, name))
    ]


def data_pad_zero(data, patch_size):
    """
    Pad the data with zero to make the data can be divided by patch_size
    Args:
        data:
        patch_size:

    Returns:

    """
    patch_length = patch_size // 2
    data_padded = np.lib.pad(
        data,
        ((patch_length, patch_length), (patch_length, patch_length), (0, 0)),
        "constant",
        constant_values=0,
    )
    return data_padded


def index_assignment(index, row, col, pad_length):
    new_assign = {}  # dictionary.
    for counter, value in enumerate(index):
        assign_0 = value // col + pad_length
        assign_1 = value % col + pad_length
        new_assign[counter] = [assign_0, assign_1]
    return new_assign


def select_patch(data_padded, pos_x, pos_y, patch_length):
    selected_patch = data_padded[
        pos_x - patch_length : pos_x + patch_length + 1,
        pos_y - patch_length : pos_y + patch_length + 1,
    ]
    return selected_patch


def hsi_create_patch(data_padded, patch_size):
    patches = image.extract_patches_2d(data_padded, [patch_size, patch_size])
    return data_padded
