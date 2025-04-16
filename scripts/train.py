# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/15
# @Address  : clover Lab @ CUHK
# @FileName : train.py  b n

# @Description : TODO
from src.tools.spectral_train import SpectralTrain
import argparse
from src.common import load_omega_config
from src.datasets.spectral_dataset import SpectralDataset
from src.datasets.transforms import ClipTransform, MNFTransform
import os


def train():
    cfg = load_omega_config("train")
    model = cfg["model_type"]
    if cfg["transform"] == "ClipTransform":
        transform = ClipTransform(530, 1100, None)
    train_dataset = SpectralDataset(root_dir=cfg["train_dir"], transform=transform)
    val_dataset = SpectralDataset(root_dir=cfg["val_dir"], transform=transform)

    model = SpectralTrain(train_dataset, val_dataset, model_name=model,
                          n_classes=len(cfg["class_dict"]))
    model.train()


if __name__ == "__main__":
    train()
