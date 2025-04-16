# -*- coding: utf-8 -*-
# @Auther   : Zheng SUN (ZainZh)
# @Time     : 2023/11/10
# @Address  : clover Lab @ CUHK
# @FileName : coco_to_mat.py
import numpy as np

# @Description: load annotation data from coco format dataset and convert to spectral annotation data in '.mat' format.

from pycocotools.coco import COCO
from pycocotools.mask import decode
import os
import scipy.io as sio
from tqdm import tqdm
import spectral as spy
from spectral import spy_colors
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as mpatches

class_dict = {"background": 0, "white_polyester": 1, "white_linen": 2, "white_silk": 3, "white_wool": 4, "white_cotton": 5,
              "white_0.5poly+0.5vis": 6,
              "white_lyocell": 7, "white_acetate": 8,
              "white_0.1ac+0.9vis": 9, "black_polyester": 10, "black_linen": 11, "black_silk": 12, "black_wool": 13,
              "black_cotton": 14,
              "black_0.5poly+0.5vis": 15, "black_lyocell": 16, "black_acetate": 17}
# class_dict = { "black_linen": 1, "black_silk": 2, "black_wool": 3,"black_acetate": 4}


class COCO2MAT(object):
    def __init__(self, coco_file_path):
        self.root_path = os.path.dirname(coco_file_path)
        self.coco = COCO(coco_file_path)
        self.dataset_name = os.path.basename(coco_file_path).split(".")[0]
        self.coco_info = self.coco.dataset
        self.coco_categories = self.coco_info["categories"]
        self.image_index_list = self.coco.getImgIds()
        self.coco_categories_dict = self.get_categories_dict()

    def get_categories_dict(self):
        coco_categories_dict = {}
        for category in self.coco_categories:
            category_dic = {category["id"]: category["name"]}
            coco_categories_dict.update(category_dic)
        return coco_categories_dict

    def get_ground_truth_label_mat(self):
        ground_truth_dict = self.get_ground_truth()
        self.save_mat(ground_truth_dict)

    def get_ground_truth(self):
        ground_truth_dict = {}

        # 获取类别对应的颜色
        category_colors = {v: k for k, v in class_dict.items()}

        # convert coco annotation to ground truth labels [0, n_classes] in '.mat' format.
        for image_index in tqdm(self.image_index_list, desc="Converting COCO to MAT"):
            coco_anns = self.coco.loadAnns(self.coco.getAnnIds(imgIds=image_index))
            ground_truth = np.zeros(
                (int(coco_anns[0]["height"]), int(coco_anns[0]["width"]))
            )
            legend_patches = []
            for coco_anno in coco_anns:
                category_id = class_dict[
                    self.coco_categories_dict[coco_anno["category_id"]]
                ]
                mask = (
                    decode(coco_anno["segmentation"])
                    if isinstance(coco_anno["segmentation"], dict)
                    else self.coco.annToMask(coco_anno)
                )
                ground_truth[mask == 1] = category_id
                legend_patches.append(
                    mpatches.Patch(
                        color=np.array(spy_colors[category_id]) / 255.0,
                        label=f"{category_colors[category_id]}",
                    )
                )

            # 使用 jet colormap 渲染 ground truth
            cmap = cm.get_cmap('jet', len(class_dict))  # 使用 jet colormap
            rgb_image = cmap(ground_truth / len(class_dict))[:, :, :3]  # 将标签映射到 RGB
            bgr_image = rgb_image[:, :, ::-1]  # 将 RGB 转换为 BGR
            plt.figure()
            plt.imshow(bgr_image)  # 显示使用 jet colormap 渲染的图像

            # # 创建图例标签，并确保图例颜色与 jet colormap 一致
            # legend_patches = []
            # for label in np.unique(ground_truth):
            #     if label in category_colors:
            #         color = cmap(label / len(class_dict))[:3]  # 获取对应标签的颜色
            #         legend_patches.append(
            #             mpatches.Patch(color=color, label=f"{category_colors[label]}")
            #         )

            # if legend_patches:  # 仅在存在实际标签时添加图例
            #     plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

            plt.axis('off')  # 隐藏坐标轴
            # 保存带图例的图片
            plt.savefig(
                os.path.join(
                    self.root_path,
                    f"{image_index}_gt_with_legend.png",
                ),
                bbox_inches='tight', pad_inches=0
            )
            # 保存 SVG 图像
            plt.savefig(
                os.path.join(
                    self.root_path,
                    f"{image_index}_gt_with_legend.svg",
                ),
                bbox_inches='tight', pad_inches=0,
                format='svg'  # 指定保存格式为 SVG
            )
            plt.close()

            filename = self.coco.loadImgs(ids=image_index)[0]["file_name"]
            if filename.endswith(".png"):
                filename = filename[:-4]
            ground_truth_dict.update(
                {
                    filename: ground_truth
                }
            )
        return ground_truth_dict

    def save_mat(self, mat):
        sio.savemat(
            os.path.join(
                self.root_path,
                f"spectral_gt.mat",
            ),
            mat,
        )


if __name__ == "__main__":
    parser = ArgumentParser(description="COCO to MAT tool")
    parser.add_argument(
        "--coco_file_path",
        default=r"C:/Users/SUN Zheng/Downloads/for_diagram.json",
        help="The path to the coco annotation file.",
    )
    args = parser.parse_args()
    a = COCO2MAT(args.coco_file_path)
    a.get_ground_truth_label_mat()
