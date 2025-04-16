# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/15
# @Address  : clover Lab @ CUHK
# @FileName : transforms.py

# @Description : MNF transform for spectral image.
#                Computes Minimum Noise Fraction / Noise-Adjusted Principal Components.
#                Reference:Lee, James B., A. Stephen Woodyatt, and Mark Berman.
#                “Enhancement of high spectral resolution remote-sensing data by a noise-adjusted principal components
#                transform.” Geoscience and Remote Sensing, IEEE Transactions on 28.3 (1990): 295-304.
#                https://ieeexplore.ieee.org/document/3001

import spectral as spy
import math
import numpy as np


class MNFTransform:
    def __init__(self, mnf_ratio):
        self.mnf_ratio = mnf_ratio

    def __call__(self, data):
        denoised_bands = math.ceil(self.mnf_ratio * data.shape[-1])
        mnfr = spy.mnf(spy.calc_stats(data), spy.noise_from_diffs(data))
        denoised_data = mnfr.reduce(data, num=denoised_bands)

        return denoised_data

    def __repr__(self):
        return f"MNFTransform({self.mnf_ratio})"


class ClipTransform:
    """
    keep the spectral data where the wavelength is between min_target_wavelength and max_target_wavelength
    """

    def __init__(self, min_target_wavelength, max_target_wavelength, ignore_spatial_area):
        """
        Args:
            min_target_wavelength(int): the minimum wavelength to keep
            max_target_wavelength(int): the maximum wavelength to keep
            ignore_spatial_area(list): the spatial areas to ignore[[x1,x2,y1,y2],[x3,x4,y3,y4]]
        """
        self.min_target_wavelength = float(min_target_wavelength)
        self.max_target_wavelength = float(max_target_wavelength)
        self.ignore_spatial_area = ignore_spatial_area

    def __call__(self, data, labels, wavelengths_dict):
        float_keys = [float(key) for key in wavelengths_dict.keys()]
        wavelengths = np.array(float_keys)

        band_indices = np.where(
            (wavelengths >= self.min_target_wavelength)
            & (wavelengths <= self.max_target_wavelength)
        )[0]

        compressed_data = data[:, :, band_indices]
        if self.ignore_spatial_area is None:
            return compressed_data, labels
        clipped_data = compressed_data[self.ignore_spatial_area[0][1]:, :, :]
        if labels is None:
            return clipped_data, labels
        clipped_labels = labels[self.ignore_spatial_area[0][1]:, :]

        return clipped_data, clipped_labels

    def __repr__(self):
        return (
            f"ClipTransform({self.min_target_wavelength}, {self.max_target_wavelength})"
        )
