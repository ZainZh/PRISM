# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/15
# @Address  : clover Lab @ CUHK
# @FileName : spectral_train.py.py

# @Description : Train the Spectral Dataset with optional models

import torch
from torch.utils.data import DataLoader, Dataset
from src.datasets.pad_spectral_dataset import PadDataset
import torch.nn as nn
from datetime import datetime
import os
import time
import random
import src.models.models as models
from torch.utils.tensorboard import SummaryWriter
from torch.nn import functional as F
from src.common import load_omega_config
from src.common import print_info


class SpectralTrain(object):
    def __init__(self, train_dataset, val_dataset, model_name, n_classes, patch_size=5):
        super(SpectralTrain, self).__init__()
        if not isinstance(train_dataset, Dataset):
            raise TypeError("dataset must be a torch.utils.data.Dataset")
        self.cfg = load_omega_config("train")
        self.train_label = self.cfg["train_label"]
        self.class_dict = self.cfg["class_dict"]
        self._train_dataset = train_dataset
        _, _, self.channels = train_dataset[0][0].shape
        self.model_name = model_name
        self.patch_size = patch_size
        self.n_classes = n_classes
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.is_semi_supervised = False
        weights = torch.ones(self.n_classes).to(self.device)
        if model_name == "prism":
            self._model = models.PRISM(input_channels=self.channels, n_classes=self.n_classes)
            cnn_shape = "1D"
            self.loss = nn.CrossEntropyLoss(weight=weights)
        elif model_name == "boulch":
            self._model = models.BoulchEtAl(input_channels=self.channels, n_classes=self.n_classes)
            self.loss = (
                nn.CrossEntropyLoss(weight=weights),
                lambda rec, data: F.mse_loss(rec, data.squeeze()),
            )
            self.is_semi_supervised = True
            cnn_shape = "1D"
        elif model_name == "li":
            self._model = models.LiEtAl(
                input_channels=self.channels, n_classes=self.n_classes, n_planes=16, patch_size=5
            )
            cnn_shape = "3D"
            self.loss = nn.CrossEntropyLoss(weight=weights)
        elif model_name == "mei":
            self.patch_size = 64
            self._model = models.MeiEtAl(
                input_channels=self.channels, n_classes=self.n_classes, patch_size=self.patch_size
            )
            cnn_shape = "3D"
            self.loss = nn.CrossEntropyLoss(weight=weights)

        else:
            raise ValueError("Please specify the model to train.")
        self._val_dataset = val_dataset
        self._test_dataset = None
        self.cnn_shape = cnn_shape

        self.batch_size = self.cfg["batch_size"]

        self._train_dataloader = DataLoader(
            self._train_dataset, batch_size=1, shuffle=True
        )
        self._val_dataloader = DataLoader(self._val_dataset, batch_size=1, shuffle=True)
        self.epoch_num = len(self._train_dataloader) * self.cfg["epoch_times"]
        self._model.to(self.device)
        # self.optimizer = torch.optim.Adam(self._model.parameters(), lr=0.001)
        # li
        self.optimizer = torch.optim.SGD(
            self._model.parameters(), lr=0.001, momentum=0.9, weight_decay=0.0005
        )

        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, factor=0.1, patience=10, verbose=True
        )

        self._sub_dir = (
            f'{datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]}_train_{self.model_name}'
        )
        self.save_dir = os.path.join(
            self.cfg["save_dir"], self._sub_dir
        )
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
        self.model_dir = os.path.join(self.save_dir, "model")
        os.makedirs(self.model_dir)

        self.best_validation_loss = float("inf")

        # Create a SummaryWriter for TensorBoard
        self.writer = SummaryWriter(self.save_dir)
        transform = self.cfg["transform"]
        with open(self.save_dir + "/" + "result.txt", "w") as f:
            f.write(f"model_name: {self.model_name}\n")
            f.write(f"cnn_shape: {self.cnn_shape}\n")
            f.write(f"optimizer: \n{self.optimizer}\n")
            f.write(f"dataset_transform,: \n{str(repr(transform))}\n")

    def __call__(self, *args, **kwargs):
        return self.train(*args, **kwargs)

    def train(self):
        iter_num = 0
        for epoch in range(self.epoch_num):
            epoch_start_time = time.time()
            print(f"Training epoch: {epoch}")
            image_index = epoch % len(self._train_dataloader)
            spectral_data = self._train_dataloader.dataset[image_index]
            spectral_inputs, spectral_labels = spectral_data
            spectral_inputs = torch.from_numpy(spectral_inputs).squeeze(0)
            spectral_labels = torch.from_numpy(spectral_labels).squeeze(0)
            padded_dataset = PadDataset(
                (spectral_inputs, spectral_labels),
                patch_size=self.patch_size,
                cnn_shape=self.cnn_shape,
            )
            padded_dataloader = DataLoader(
                padded_dataset, batch_size=self.batch_size, shuffle=True
            )

            for batch_index, padded_data in enumerate(padded_dataloader):
                start_time = time.time()
                padded_inputs, padded_labels = padded_data

                valid_indices = []
                for idx, label in enumerate(padded_labels):
                    label_value = self.class_dict.get(str(label.item()), None)
                    if label_value in self.train_label:
                        valid_indices.append(idx)

                if len(valid_indices) == 0:
                    continue  # 如果没有有效的标签，则跳过该批次
                padded_inputs = padded_inputs[valid_indices]
                padded_labels = padded_labels[valid_indices]
                # print_info(f"padded_labels: {padded_labels[padded_labels != 0]}")
                padded_inputs = padded_inputs.to(self.device)
                padded_labels = padded_labels.to(self.device)
                self.optimizer.zero_grad()
                if self.is_semi_supervised:
                    outputs, rec = self._model(padded_inputs)
                    loss = self.loss[0](
                        outputs, padded_labels
                    ) + self._model.aux_loss_weight * self.loss[1](rec, padded_inputs)
                else:
                    outputs = self._model(padded_inputs)
                    loss = self.loss(outputs, padded_labels)
                loss.backward()
                self.optimizer.step()

                # Log the loss to TensorBoard
                self.writer.add_scalar(
                    "Loss/train",
                    loss.item(),
                    iter_num,
                )
                iter_num += 1
                # Add code to print training progress
                print(
                    f"Epoch: {epoch}, image: {image_index}, Batch: {batch_index}, Loss: {loss.item()}"
                )
                end_time = time.time()
                print(
                    f"Epoch: {epoch}, image: {image_index}, Batch: {batch_index}, training time: {end_time - start_time} seconds"
                )
            torch.save(
                self._model.state_dict(),
                os.path.join(self.model_dir, f"latest.pth"),
            )
            if image_index == 0:
                val_acc = self.val(iter_num)
                metric = -val_acc
                self.scheduler.step(metric)
            epoch_end_time = time.time()
            print_info(f"Epoch {epoch} finished in {epoch_end_time - epoch_start_time:.2f} seconds")
    def val(self, iter_num):
        print(f"iter_num: {iter_num}")
        self._model.eval()
        with torch.no_grad():
            validation_loss = 0.0
            correct = 0
            total = 0
            # Set the initial best loss to infinity
            image_index = random.randint(0, len(self._val_dataloader) - 1)
            spectral_data = self._val_dataloader.dataset[image_index]
            spectral_inputs, spectral_labels = spectral_data

            spectral_inputs = torch.from_numpy(spectral_inputs).squeeze(0)
            spectral_labels = torch.from_numpy(spectral_labels).squeeze(0)
            padded_dataset = PadDataset(
                (spectral_inputs, spectral_labels),
                patch_size=self.patch_size,
                cnn_shape=self.cnn_shape,
            )
            padded_dataloader = DataLoader(
                padded_dataset, batch_size=self.batch_size, shuffle=True
            )

            for batch_index, padded_data in enumerate(padded_dataloader):
                padded_inputs, padded_labels = padded_data
                padded_inputs = padded_inputs.to(self.device)
                padded_labels = padded_labels.to(self.device)
                if self.is_semi_supervised:
                    outputs, rec = self._model(padded_inputs)
                    loss = self.loss[0](
                        outputs, padded_labels
                    ) + self._model.aux_loss_weight * self.loss[1](rec, padded_inputs)
                else:
                    outputs = self._model(padded_inputs)
                    loss = self.loss(outputs, padded_labels)
                validation_loss += loss.item()

                _, predicted = torch.max(outputs, 1)
                total += padded_labels.size(0)
                correct += (predicted == padded_labels).sum().item()

            validation_accuracy = 100.0 * correct / total
            validation_loss /= len(self._val_dataloader)
            # Log the validation loss and accuracy to TensorBoard
            self.writer.add_scalar("Loss/validation", validation_loss, iter_num)
            self.writer.add_scalar("Accuracy/validation", validation_accuracy, iter_num)

            # Add code to save the model if the validation loss improves
            if validation_loss < self.best_validation_loss:
                self.best_validation_loss = validation_loss
                torch.save(
                    self._model.state_dict(),
                    os.path.join(self.model_dir, "best.pth"),
                )
        self._model.train()
        return validation_accuracy
