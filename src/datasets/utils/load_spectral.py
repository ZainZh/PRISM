# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/10
# @Address  : clover Lab @ CUHK
# @FileName : load_spectral.py

# @Description : load ENVI spectral image dataset.

from plantcv import plantcv as pcv
import os
import scipy.io as sio
import numpy as np


class LoadSpectralFromSpecim(object):
    def __init__(
            self,
            dataset_name,
            root_dir=None,
    ):
        self.root_dir = root_dir
        self.dataset_name = dataset_name
        self.raw_data_path = os.path.join(
            self.root_dir, f"{dataset_name}/capture"
        )
        self.spectral_data = self.load_spectral_data(self.dataset_name)
        self.spectral_data.array_data = self.spectral_data.array_data[:, 104:369, :]
        white_reference_name = f"WHITEREF_{self.dataset_name}"
        dark_reference_name = f"DARKREF_{self.dataset_name}"
        self.white_ref = self.load_spectral_data(white_reference_name)
        self.white_ref.array_data = np.load(
            f"{root_dir}/white_reference_1/capture/envi/white_reference_1_reflectance.npy")
        self.dark_ref = self.load_spectral_data(dark_reference_name)
        self.dark_ref.array_data = self.dark_ref.array_data[:, 104:369, :]
        self._reflectance = self.calibrate()

    def load_spectral_data(self, image_name):
        spectral_data = pcv.readimage(
            filename=os.path.join(self.raw_data_path, f"{image_name}.raw"), mode="envi"
        )
        return spectral_data

    def calibrate(self):
        reflectance = pcv.hyperspectral.calibrate(
            self.spectral_data, self.white_ref, self.dark_ref
        )
        return reflectance

    @property
    def raw_spectral_data(self):
        return self.spectral_data.array_data

    @property
    def dark_ref_data(self):
        return self.dark_ref.array_data

    @property
    def white_ref_data(self):
        return self.white_ref.array_data

    @property
    def reflectance(self):
        return self._reflectance.array_data

    @property
    def wavelength_dict(self):
        return self.spectral_data.wavelength_dict


class LoadSpectralFromNumpy(object):
    def __init__(
            self,
            raw_image_numpy,
            white_ref_numpy,
            dark_ref_numpy,
            origin_ref_numpy,
            ref_block_loc: [[787, 810], [175, 280]],
    ):
        self.raw_data = raw_image_numpy
        self.white_data = white_ref_numpy
        self.dark_ref = dark_ref_numpy
        self.origin_ref = origin_ref_numpy
        self.ref_block_loc = ref_block_loc
        # self.ref_block_data = self.origin_ref[self.ref_block_loc[0][0]:self.ref_block_loc[0][1],
        #                       self.ref_block_loc[1][0]:self.ref_block_loc[1][1], :]
        # self.raw_ref_block_data = self.raw_data[self.ref_block_loc[0][0]:self.ref_block_loc[0][1],
        #                      self.ref_block_loc[1][0]:self.ref_block_loc[1][1], :]
        # self.lighting_factor_data = self.raw_ref_block_data / self.ref_block_data
        self._reflectance = self.calibrate()


    def calibrate(self):
        """This function allows you calibrate raw hyperspectral image data with white and dark reference data.

        Inputs:
        raw_data        = Raw image 'Spectral_data' class instance
        white_reference = White reference 'Spectral_data' class instance
        dark_reference  = Dark reference 'Spectral_data' class instance

        Returns:
        calibrated      = Calibrated hyperspectral image

        :param raw_data: __main__.Spectral_data
        :param white_reference: __main__.Spectral_data
        :param dark_reference: __main__.Spectral_data
        :return calibrated: __main__.Spectral_data
        """
        # Average dark reference over the first axis (repeated line scans) -> float64
        # Converts the input shape from (y, x, z) to (1, x, z)
        # dark = np.mean(self.dark_ref, axis=0, keepdims=True)

        # Average white reference over the first axis (repeated line scans) -> float64
        # Converts the input shape from (y, x, z) to (1, x, z)
        # white = np.mean(self.white_data, axis=0, keepdims=True)

        # Convert the raw data to float64
        # raw = self.raw_data.astype("float64")/ self.lighting_factor
        raw = self.raw_data.astype("float64")
        dark = self.dark_ref.astype("float64")
        white = self.white_data.astype("float64")
        # white = self.white_data.astype("float64") * self.lighting_factor

        eps = 1e-6
        denominator = white - dark
        denominator[denominator < eps] = 1000000
        # Calibrate using reflectance = (raw data - dark reference) / (white reference - dark reference)
        # Note that dark and white are broadcast over each line (y) in raw
        reflectance = (raw - dark) / denominator

        # Clip the calibrated values to the range 0 - 1
        np.clip(reflectance, a_min=0, a_max=2, out=reflectance)

        return reflectance


    @property
    def lighting_factor(self):
        return np.average(self.lighting_factor_data, axis=(0, 1))
    @property
    def raw_spectral_data(self):
        return self.raw_data

    @property
    def dark_ref_data(self):
        return self.dark_ref

    @property
    def white_ref_data(self):
        return self.white_data

    @property
    def reflectance(self):
        return self._reflectance


if __name__ == "__main__":
    a = LoadSpectralFromSpecim("two_box")
