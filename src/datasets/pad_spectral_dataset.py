# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/14
# @Address  : clover Lab @ CUHK
# @FileName : spectral_dataset.py

# @Description : TODO
import torch
from torch.utils.data import Dataset
import numpy as np



class PadDataset(Dataset):
    def __init__(
        self,
        raw_data: torch.Tensor,
        transform=None,
        patch_size=9,
        cnn_shape="3D",
    ):
        """

        Args:
            raw_data(torch.Tensor):
            root_dir:
            transform:
        """
        self.raw_data = raw_data
        self.transform = transform
        self.cnn_shape = cnn_shape
        self.data = self.raw_data[0]
        if self.transform:
            # Denoise the data
            if isinstance(self.data, np.ndarray):
                self.data = torch.from_numpy(self.transform(self.data))
            else:
                self.data = torch.from_numpy(self.transform(self.data.numpy()))

        self.label = self.raw_data[1]
        if isinstance(self.label, torch.Tensor):
            self.label = self.label.numpy()
        self.transform = transform
        self.patch_size = patch_size

        # 保留所有数据的位置索引，无需筛选
        self.indices = [(x, y) for x in range(self.data.shape[0]) for y in range(self.data.shape[1])]
        self.flip_augmentation = False
        self.radiation_augmentation = False
        self.mixture_augmentation = False
        self.center_pixel = True

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        x, y = self.indices[idx]
        # for 1d cnn
        if self.cnn_shape == "1D":
            data = self.data[x, y]
            label = self.label[x, y]
            data = np.asarray(np.copy(data), dtype="float32")
            label = np.asarray(np.copy(label), dtype="int64")
            data = torch.from_numpy(data)
            label = torch.from_numpy(label)
            return data, label

        # 对于2D patch（3D CNN 或者非1D）
        H, W = self.data.shape[0], self.data.shape[1]
        half = self.patch_size // 2
        # 计算理论上的 patch 边界（可能超出原图）
        x1 = x - half
        y1 = y - half
        x2 = x1 + self.patch_size
        y2 = y1 + self.patch_size

        # 计算需要补零的各边宽度
        pad_top = max(0, -x1)
        pad_left = max(0, -y1)
        pad_bottom = max(0, x2 - H)
        pad_right = max(0, y2 - W)

        # 安全的切片范围（在原图内）
        x1_safe = max(x1, 0)
        y1_safe = max(y1, 0)
        x2_safe = min(x2, H)
        y2_safe = min(y2, W)

        # -----------------------------
        # 构造 patch，先为数据创建一个全零张量
        if self.cnn_shape == "3D":
            # 假设 data 的 shape 为 (H, W, channels)
            channels = self.data.shape[2]
            patch = torch.zeros((self.patch_size, self.patch_size, channels), dtype=self.data.dtype)
        else:
            patch = torch.zeros((self.patch_size, self.patch_size), dtype=self.data.dtype)

        # 确定复制到 patch 中的目标区域位置
        dest_x1 = pad_top
        dest_y1 = pad_left
        dest_x2 = dest_x1 + (x2_safe - x1_safe)
        dest_y2 = dest_y1 + (y2_safe - y1_safe)
        patch[dest_x1:dest_x2, dest_y1:dest_y2] = self.data[x1_safe:x2_safe, y1_safe:y2_safe].to(torch.float32)

        # -----------------------------
        # 对 label 进行同样的操作（label 为 numpy 数组）
        label_patch = np.zeros((self.patch_size, self.patch_size), dtype=self.label.dtype)
        label_patch[dest_x1:dest_x2, dest_y1:dest_y2] = self.label[x1_safe:x2_safe, y1_safe:y2_safe]

        # 数据增强（如翻转、辐射噪声、混合噪声等），仅对 patch_size >1 有意义

        # 将 label_patch 转换为 torch.Tensor
        label_tensor = torch.from_numpy(label_patch.astype("int64"))

        # 如果需要只取中心像素作为 label
        if self.center_pixel and self.patch_size > 1:
            label_new = label_tensor[self.patch_size // 2, self.patch_size // 2]
        else:
            label_new = label_tensor

        # 如果是3D cnn，则对数据维度进行转换
        if self.cnn_shape == "3D":
            # 将 shape 从 (patch_size, patch_size, channels) 转换为 (channels, patch_size, patch_size)
            data = np.asarray(np.copy(patch).transpose((2, 0, 1)), dtype="float32")
            data = torch.from_numpy(data)
            # 增加 batch 维度，得到 (1, channels, patch_size, patch_size)
            data = data.unsqueeze(0)
        else:
            data = patch

        return data, label_new

    @staticmethod
    def flip(*arrays):
        horizontal = np.random.random() > 0.5
        vertical = np.random.random() > 0.5
        if horizontal:
            arrays = [np.fliplr(arr) for arr in arrays]
        if vertical:
            arrays = [np.flipud(arr) for arr in arrays]
        return arrays

    @staticmethod
    def radiation_noise(data, alpha_range=(0.9, 1.1), beta=1 / 25):
        alpha = np.random.uniform(*alpha_range)
        noise = np.random.normal(loc=0.0, scale=1.0, size=data.shape)
        return alpha * data + beta * noise

    def mixture_noise(self, data, label, beta=1 / 25):
        alpha1, alpha2 = np.random.uniform(0.01, 1.0, size=2)
        noise = np.random.normal(loc=0.0, scale=1.0, size=data.shape)
        data2 = np.zeros_like(data)
        for idx, value in np.ndenumerate(label):
            l_indices = np.nonzero(self.label == value)[0]
            l_indice = np.random.choice(l_indices)
            assert self.label[l_indice] == value
            x, y = self.indices[l_indice]
            data2[idx] = self.data[x, y]
        return (alpha1 * data + alpha2 * data2) / (alpha1 + alpha2) + beta * noise

    def get_random_patch(self):
        h, w, c = self.data.shape
        i = np.random.randint(0, h - self.patch_size)
        j = np.random.randint(0, w - self.patch_size)
        patch = self.data[i : i + self.patch_size, j : j + self.patch_size, :]
        label_patch = self.label[i, j]
        return patch, label_patch

    def __len__(self):
        return len(self.indices)
