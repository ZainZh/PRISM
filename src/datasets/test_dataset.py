# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/14
# @Address  : clover Lab @ CUHK
# @FileName : spectral_dataset.py

# @Description : TODO
import torch
from torch.utils.data import Dataset
from src.datasets.transforms import MNFTransform
import numpy as np


class TestDataset(Dataset):
    def __init__(self, data, transform=MNFTransform(0.3), patch_size=9):
        """

        Args:
            data(torch.Tensor):
            root_dir:
            transform:
        """
        self.data = data
        self.transform = transform
        self.inputs = self.data[0]
        if self.transform:
            # Denoise the data
            self.inputs = torch.from_numpy(self.transform(self.inputs.numpy()))

        self.labels = self.data[1]
        h, w, c = self.inputs.shape
        self.coordinates = self.get_image_coordinates(h, w)
        self.transform = transform
        self.patch_size = patch_size

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()
        patch = self.get_patch(self.coordinates[idx])
        print("idx", idx)
        return patch

    def get_random_patch(self):
        h, w, c = self.inputs.shape
        i = np.random.randint(0, h - self.patch_size)
        j = np.random.randint(0, w - self.patch_size)
        patch = self.inputs[i : i + self.patch_size, j : j + self.patch_size, :]
        label_patch = self.labels[i, j]
        return patch, label_patch

    def get_patch(self, index):
        h, w, c = self.inputs.shape

        i = np.clip(index[0], 0, h - self.patch_size)
        j = np.clip(index[1], 0, w - self.patch_size)
        patch = self.inputs[i : i + self.patch_size, j : j + self.patch_size, :]
        return torch.from_numpy(patch).to(torch.float)

    def get_image_coordinates(self, image_height, image_width):
        # 使用 np.indices 获取一个图像的所有坐标
        coordinates_list = [
            [x, y] for y in range(image_height) for x in range(image_width)
        ]
        return coordinates_list

    def __len__(self):
        return len(self.coordinates)
