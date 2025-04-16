# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2024/1/11
# @Address  : clover Lab @ CUHK
# @FileName : specim_to_envi.py
import cv2

# @Description : Convert the hyperspectral image get from the SPECIM camera to envi format.

from src.datasets.utils.load_spectral import LoadSpectralFromSpecim, LoadSpectralFromNumpy
import spectral
import os
import numpy as np
from src.common import click_and_get_pixel, generate_pseudo_rgb_image

ref_block_loc = [[787, 810], [175, 230]]
# material_list = ["polyester", "linen", "silk", "wool", "cotton", "50%Polyester + 50%viscose", "lyocell", "acetate",
#                  "10%acetate + 90%viscose fiber"]
material_list = ["mix7"]


def main():
    root_dir = r"C:\Users\SUN Zheng\OneDrive - The Chinese University of Hong Kong\CUHK学习\研究工作\高光谱相机项目\论文相关\光谱数据\衣物"
    dataset_category = "cloth"
    white_data = np.load(f"{root_dir}/white_reference.npy")
    dark_data = np.load(f"{root_dir}/dark_reference.npy")
    origin_ref = np.load(f"{root_dir}/origin_reference.npy")
    for dataset_name in material_list:
        data_name = f"{root_dir}/{dataset_category}/{dataset_name}/{dataset_name}.npy"
        #
        # pseudo_rgb_image = generate_pseudo_rgb_image(np.load(data_name))
        #
        # cv2.imwrite(fr"C:\Users\SUN Zheng\Downloads\{dataset_name}.png", pseudo_rgb_image)`
        reflectance_file_path = f"{root_dir}/{dataset_category}/{dataset_name}/capture/envi/{dataset_name}_reflectance.hdr"
        if not os.path.exists(data_name) or os.path.exists(reflectance_file_path):
            print(f"{data_name} does not exist.")
            continue
        raw_data = np.load(data_name)
        spectral_data = LoadSpectralFromNumpy(raw_data, white_data, dark_data, origin_ref, ref_block_loc)
        reflectance_file_path = f"{root_dir}/{dataset_category}/{dataset_name}/capture/envi/{dataset_name}_reflectance.hdr"
        raw_file_path = f"{root_dir}/{dataset_category}/{dataset_name}/capture/envi/{dataset_name}_raw.hdr"
        # white_file_path = f"{root_dir}/{dataset_name}/capture/envi/{dataset_name}_white.hdr"
        os.makedirs(f"{root_dir}/{dataset_category}/{dataset_name}/capture/envi", exist_ok=True)

        ## only for the white reference block
        # white_reference = spectral_data.raw_spectral_data[459:493,104:369,:]
        # np.save(f"{root_dir}/{dataset_name}/capture/envi/{dataset_name}_reflectance.npy",white_reference)
        # calibrated
        spectral.envi.save_image(reflectance_file_path, spectral_data.reflectance)
        # # # raw
        # spectral.envi.save_image(raw_file_path, spectral_data.raw_spectral_data)
        # # white
        # spectral.envi.save_image(white_file_path, spectral_data.white_ref_data)
        print("1")

        # cv2.imwrite(rf"C:\Users\SUN Zheng\Desktop/{dataset_name}.png",
        #             generate_pseudo_rgb_image(np.load(f"{root_dir}/{dataset_name}/{dataset_name}.npy")))


if __name__ == "__main__":
    main()
