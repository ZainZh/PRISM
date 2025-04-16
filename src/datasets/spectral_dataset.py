# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/14
# @Address  : clover Lab @ CUHK
# @FileName : spectral_dataset.py

# @Description : TODO
import torch
from torch.utils.data import Dataset
import scipy.io as sio
import os
from src.datasets.utils.common import get_subdirectories
from src.datasets.utils.load_spectral import LoadSpectralFromSpecim, LoadSpectralFromNumpy
from src.datasets.transforms import MNFTransform, ClipTransform
import numpy as np
import spectral
import json
class SpectralDataset(Dataset):
    def __init__(self, root_dir, transform=None, patch_size=9):
        """

        Args:
            root_dir:
            transform:
        """
        self.root_dir = root_dir
        self.spectral_images_dir = os.path.join(self.root_dir, "raw_images")
        self.mat_file = os.path.join(
            self.root_dir, "spectral_annotations/spectral_gt.mat"
        )
        self.wavelength_dict = json.load(open(os.path.join(self.root_dir, "../bands.json")))
        self.spectral_images_list = get_subdirectories(self.spectral_images_dir)
        self.transform = transform
        self.patch_size = patch_size

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        image_name = self.spectral_images_list[idx]
        # for testing results, no ground truth is needed.

        data = spectral.envi.open(
            os.path.join(self.spectral_images_dir, image_name, "capture/envi", f"{image_name}_reflectance.hdr")).load()
        data = np.array(data)
        if not os.path.exists(os.path.join(self.root_dir, self.mat_file)):
            self.mat = None
            labels = None
            print(f"no label and data for {image_name}")

        else:
            self.mat = sio.loadmat(os.path.join(self.root_dir, self.mat_file))
            try:
                labels = self.mat[image_name]
            except KeyError:
                labels = None
                print(f"no label for {image_name}")

        if self.transform:
            if isinstance(self.transform, MNFTransform):
                data = self.transform(data)
            # Denoise the data
            elif isinstance(self.transform, ClipTransform):
                data, labels = self.transform(data, labels, self.wavelength_dict)

        return data, labels

    def __len__(self):
        return len(self.spectral_images_list)
