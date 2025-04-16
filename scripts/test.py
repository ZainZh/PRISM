# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/15
# @Address  : clover Lab @ CUHK
# @FileName : train.py

# @Description : Test the model on the test dataset.
from src.tools.image_interfence import ImageInterference
from src.common import load_omega_config
import src.models.models as models
import argparse
from src.datasets.spectral_dataset import SpectralDataset
from src.datasets.transforms import ClipTransform, MNFTransform




cfg = load_omega_config("train")
model_name = cfg["model_type"]
if cfg["transform"] == "ClipTransform":
    transform = ClipTransform(530, 1100, None)
train_dataset = SpectralDataset(root_dir=cfg["train_dir"], transform=transform)
height, width, channels = train_dataset[0][0].shape
test_dataset = SpectralDataset(root_dir=cfg["test_dir"], transform=transform)
model_path = cfg["test_model_path"]
if model_name == "hu":
    """
    Deep Convolutional Neural Networks for Hyperspectral Image Classification

    Wei Hu, Yangyu Huang, Li Wei, Fan Zhang and Hengchao Li
    Journal of Sensors, Volume 2015 (2015)
    https://www.hindawi.com/journals/js/2015/258619/
    """
    model_type = models.PRISM(input_channels=channels, n_classes=len(cfg["class_dict"]))
    cnn_shape = "1D"
elif model_name == "boulch":
    model_type = models.BoulchEtAl(input_channels=channels, n_classes=len(cfg["class_dict"]))
    cnn_shape = "1D"
elif model_name == "li":
    model_type = models.LiEtAl(
        input_channels=channels, n_classes=len(cfg["class_dict"]), n_planes=16, patch_size=5
    )
    cnn_shape = "3D"
elif model_name == "sharma":
    model_type = models.MeiEtAl(
        input_channels=channels, n_classes=len(cfg["class_dict"]), patch_size=64
    )
    cnn_shape = "3D"
else:
    raise ValueError("Please specify the model to train.")


def interference():
    model = ImageInterference(
        model_type=model_type,
        model_path=model_path,
        cnn_shape=cnn_shape,
        model_name=model_name,
    )
    if model_name == "li":
        model.interference(test_dataset[0], n_classes=len(cfg["class_dict"]), patch_size=5)
    else:
        model.interference(test_dataset[0],n_classes=len(cfg["class_dict"]), patch_size=64)


if __name__ == "__main__":

    interference()
