#! /usr/bin/python3
# -*- coding:utf-8 -*-
# @Time: 2023-07-10 15:13
# @Author: Rangers
# @Site: 
# @File: test.py


import cv2
import numpy as np

def correct_skew(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像转换为灰度
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 对图像进行边缘检测
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 检测图像中的直线
    lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=100)

    # 计算直线的平均角度
    angles = []
    for line in lines:
        for rho, theta in line:
            angles.append(theta)
    mean_angle = np.mean(angles)

    # 计算旋转角度
    rotation_angle = np.degrees(mean_angle) - 90

    # 对图像进行旋转纠正
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), rotation_angle, 1)
    corrected_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))

    return corrected_image

# 调用纠正函数并显示结果
image_path = '../data/id_card/反面（周伊皓）_1.jpg'
corrected_image = correct_skew(image_path)
cv2.imshow('Corrected Image', corrected_image)
cv2.waitKey(0)
cv2.destroyAllWindows()