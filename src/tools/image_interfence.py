# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/25
# @Address  : clover Lab @ CUHK
# @FileName : image_interfence.py
import numpy as np
import torch
import spectral as spy
from spectral import spy_colors
import os
from datetime import datetime
from time import time
from src.utils import grouper, sliding_window, count_sliding_window
from tqdm import tqdm
from sklearn import metrics
from src.common import print_info, load_omega_config
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import seaborn as sns


class ImageInterference(object):
    def __init__(self, model_type, model_path=None, cnn_shape="3D", model_name=None):
        super(ImageInterference, self).__init__()
        self.cfg = load_omega_config("train")
        self.class_dict = self.cfg["class_dict"]
        self.class_dict_inverse = {v: k for k, v in self.class_dict.items()}
        self._model = model_type
        self.model_path = model_path
        self.cnn_shape = cnn_shape
        self.save_dir = os.path.join(
            r"/home/clover/test_result",
            f'{datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]}_test_{model_name}',
        )
        os.makedirs(self.save_dir)
        self._model.load_state_dict(torch.load(self.model_path))
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self._model.to(self.device)
        self._model.eval()

    def __call__(self, *args, **kwargs):
        return self.interference(**kwargs)

    def interference(
            self, test_data, n_classes=3, patch_size=5, batch_size=1024, center_pixel=True
    ):
        image = test_data[0]
        label = test_data[1]
        probs = np.zeros(image.shape[:2] + (n_classes,))
        if self.cnn_shape == "1D":
            patch_size = 1

        iterations = (
                count_sliding_window(image, step=1, window_size=(patch_size, patch_size))
                // 1024
        )

        # initialize a matplotlib figure
        plt.ion()
        fig, ax = plt.subplots(figsize=(8, 6))

        cmap = cm.get_cmap('jet', n_classes)
        img_display = ax.imshow(
            np.zeros(image.shape[:2] + (3,)), cmap="jet", vmin=0, vmax=n_classes
        )

        iterations_count = 0
        time1 = datetime.now()
        print_info("Interference at time", time1.strftime("%Y-%m-%d %H:%M:%S"))
        for batch in tqdm(
                grouper(
                    batch_size,
                    sliding_window(image, step=1, window_size=(patch_size, patch_size)),
                ),
                total=(iterations),
                desc="Inference on the image",
        ):
            start_time = time()
            with torch.no_grad():
                if patch_size == 1:
                    data = [b[0][0, 0] for b in batch]
                    data = np.copy(data)
                    data = torch.from_numpy(data)
                else:
                    data = [b[0] for b in batch]
                    data = np.copy(data)
                    data = data.transpose(0, 3, 1, 2)
                    data = torch.from_numpy(data)
                    data = data.unsqueeze(1)

                indices = [b[1:] for b in batch]
                data = data.to(self.device).to(torch.float32)
                output = self._model(data)
                if isinstance(output, tuple):
                    output = output[0]
                output = output.to("cpu")

                if patch_size == 1 or center_pixel:
                    output = output.numpy()
                else:
                    output = np.transpose(output.numpy(), (0, 2, 3, 1))
                for (x, y, w, h), out in zip(indices, output):
                    if center_pixel:
                        probs[x + w // 2, y + h // 2] += out
                    else:
                        probs[x: x + w, y: y + h] += out

                predicted_results = np.argmax(probs, axis=-1)
                rgb_predicted = cmap(predicted_results / n_classes)[:, :, :3]  # 使用 jet colormap 映射颜色
                img_display.set_data(rgb_predicted)
                ax.set_title(f"Iteration: {iterations_count}")
                fig.canvas.draw()
                plt.pause(0.001)
                iterations_count += 1
            end_time = time()
            single_inference_time = end_time - start_time
            print(f"Time elapsed: {single_inference_time:.2f} s")

        time2 = datetime.now()
        print_info("Interference at time", time2.strftime("%Y-%m-%d %H:%M:%S"))
        print_info("Total time elapsed", time2 - time1)
        predicted_test = np.reshape(predicted_results, (-1))

        # 保存带有颜色的预测结果图像
        plt.figure()
        plt.imshow(rgb_predicted)  # 显示映射后的 RGB 图像

        # 生成图例，确保只包含实际存在的类别
        unique_labels = np.unique(predicted_results)
        print(f"Unique labels in the predicted results: {unique_labels}")  # Debug: 输出唯一的标签
        legend_patches = [
            mpatches.Patch(color=cmap(i)[:3], label=f"{self.class_dict_inverse[i]}")
            for i in unique_labels if i in self.class_dict_inverse
        ]
        labels = [self.class_dict[f"{i}"] for i in unique_labels]
        ax.legend(handles=legend_patches, bbox_to_anchor=(1.25, 1), loc='upper left', borderaxespad=0.)

        plt.axis('off')  # 隐藏坐标轴
        plt.savefig(self.save_dir + "/" + "pre.png", bbox_inches='tight', pad_inches=0)

        plt.savefig(
            self.save_dir + "/" + "pre.svg",
            bbox_inches='tight', pad_inches=0,
            format='svg'  # 指定保存格式为 SVG
        )
        plt.close()
        plt.close()

        gt_test = np.reshape(label, (-1))
        accuracy_score = metrics.accuracy_score(gt_test, predicted_test)
        confusion_matrix = metrics.confusion_matrix(gt_test, predicted_test)
        confusion_matrix_percent = confusion_matrix / np.sum(confusion_matrix, axis=1)[:, np.newaxis]
        print_info(
            f"accuracy_score: \n{accuracy_score}\n"
            f"confusion_matrix: \n{confusion_matrix}\n"
        )
        plt.figure(figsize=(10, 8))
        sns.heatmap(confusion_matrix_percent, annot=True, fmt=".2%", cmap="YlOrBr",  xticklabels=labels,
                    yticklabels=labels, annot_kws={"fontfamily": "Times New Roman", "fontsize": 10})
        plt.rc('font', family='Times New Roman')
        plt.title("Confusion Matrix (Percentage Form)")
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.savefig(self.save_dir + "/" + "matrix.png", bbox_inches='tight', pad_inches=0)

        plt.ioff()
        plt.show()

        # 将测试时间、准确率和混淆矩阵等信息记录在一个txt文件中
        test_info = []
        test_info.append("Test Results")
        test_info.append("=" * 50)
        test_info.append("Test start time: " + time1.strftime("%Y-%m-%d %H:%M:%S"))
        test_info.append("Test end time: " + time2.strftime("%Y-%m-%d %H:%M:%S"))
        test_info.append("Total time elapsed: " + str(time2 - time1))
        test_info.append("Accuracy Score: " + str(accuracy_score))
        test_info.append("Confusion Matrix:\n" + np.array2string(confusion_matrix))
        test_info.append("Confusion Matrix (Percentage):\n" + np.array2string(confusion_matrix_percent))

        # 拼接各行信息，形成一个字符串
        test_info_str = "\n".join(test_info)

        # 写入到文件
        with open(self.save_dir + "/" + "test_info.txt", "w") as f:
            f.write(test_info_str)
