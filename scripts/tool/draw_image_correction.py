import cv2
import numpy as np
import os

# 加载图片
file_path = 'C:/Users/SUN Zheng/Desktop/tools.png'
if not os.path.exists(file_path):
    print("File does not exist!")
else:
    image = cv2.imread(file_path)

# 图像的高度和宽度
height, width, _ = image.shape


# 定义鱼眼变换函数
def fisheye_transform(x, y, center_x, center_y, k=0.00001):
    # 计算距离图像中心的距离
    # r = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    r = np.sqrt((y - center_y) ** 2)

    # 进行径向畸变
    r_prime = r * (1 + k * r ** 2)

    # 计算新的x和y坐标
    x_prime = center_x + (x - center_x) * r_prime / r if r != 0 else x
    # y_prime = center_y + (y - center_y) * r_prime / r if r != 0 else y

    return int(x_prime), y


# 中心点坐标


# border_size = 30
# output_image = cv2.copyMakeBorder(image, 0, 0, border_size, border_size, cv2.BORDER_CONSTANT, value=(0, 0, 0))

# 获取新的图像尺寸

center_x, center_y = width // 2,height // 2
# 创建一个新的图像，用于存储鱼眼效果
fisheye_image = np.zeros_like(image)

# 对每个像素应用鱼眼变换
for i in range(height):
    for j in range(width):
        new_x, new_y = fisheye_transform(j, i, center_x, center_y, k=-0.000001)  # 这里可以调整 k 值
        if 0 <= new_x < width and 0 <= new_y < height:
            fisheye_image[new_y, new_x] = image[i, j]

# 扩展图像，在图像外增加黑色边框（例如边框宽度为30像素）

# 在整个图像上均匀分布点
rows = 50  # 总行数
cols = 40  # 每行的点数

# 设置点的坐标
x_values = np.linspace(0, width - 1, cols, dtype=int)
y_values = np.linspace(0, height - 1, rows, dtype=int)
cross_size =3
# 绘制均匀分布的点
for y in y_values:
    for x in x_values:
        # cv2.circle(fisheye_image, (x, y), radius=2, color=(255, 255, 0), thickness=-1)
        # 绘制水平线（横线）
        cv2.line(fisheye_image, (x - cross_size, y), (x + cross_size, y), (0,255,255), thickness=2)
        # 绘制垂直线（竖线）
        cv2.line(fisheye_image, (x, y - cross_size), (x, y + cross_size), (0,255,255), thickness=2)
# 显示输出图像
cv2.imshow('Fisheye Image with Uniform Points', fisheye_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 保存输出图像
cv2.imwrite('fisheye_image_with_uniform_points.jpg', fisheye_image)
