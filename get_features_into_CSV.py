# return_128d_features()          获取某张图像的 128D 特征
# write_into_csv()                获取某个路径下所有图像的特征，并写入 CSV
# compute_the_mean()              从 CSV　中读取　128D 特征，并计算特征均值

import cv2
import os
import dlib
from skimage import io
import csv
import numpy as np
import pandas as pd
import shutil

path_faces_uncalculated = "data_faces_from_camera/Uncalculated/" #存放每个人未经过计算的脸
path_faces_calculated="D:/face recognition 2/data_faces_from_camera/calculated/"
path_csv = "data_csvs_from_camera/"  #存放每个人的人脸的csv

# Dlib 正向人脸检测器
detector = dlib.get_frontal_face_detector()

# Dlib 人脸预测器
predictor = dlib.shape_predictor("data_dlib/shape_predictor_68_face_landmarks.dat")

# Dlib 人脸识别模型
# Face recognition model, the object maps human faces into 128D vectors
facerec = dlib.face_recognition_model_v1("data_dlib/dlib_face_recognition_resnet_model_v1.dat")


# 返回单张图像的 128D 特征
def return_128d_features(path_img):
    img = io.imread(path_img)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = detector(img_gray, 1)

    print("检测的人脸图像：", path_img, "\n")

    # 因为有可能截下来的人脸再去检测，检测不出来人脸了
    # 所以要确保是 检测到人脸的人脸图像 拿去算特征
    if len(faces) != 0:
        shape = predictor(img_gray, faces[0])
        face_descriptor = facerec.compute_face_descriptor(img_gray, shape)
    else:
        face_descriptor = 0
        print("no face")

    # print(face_descriptor)
    return face_descriptor


# 将Uncalculated文件夹中每个人的照片特征提取出来，写入 CSV
#   path_faces_personX:     每个人的人脸图像路径
#   path_csv:               存放每个人的人脸的csv
def write_into_csv(path_faces_personX, path_csv):
    dir_pics = os.listdir(path_faces_personX)
    with open(path_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(dir_pics)):
            # 调用return_128d_features()得到128d特征
            print("正在读的人脸图像：", path_faces_personX + "/" + dir_pics[i])
            features_128d = return_128d_features(path_faces_personX + "/" + dir_pics[i])
            #  print(features_128d)
            # 遇到没有检测出人脸的图片跳过
            if features_128d == 0:
                i += 1
            else:
                writer.writerow(features_128d)

# 读取某人所有的人脸图像的数据，写入 person_X.csv
faces = os.listdir(path_faces_uncalculated)
if len(faces)>0:
    for person in faces:
        print(path_csv + person + ".csv")
        write_into_csv(path_faces_uncalculated + person, path_csv + person + ".csv")
        shutil.move(path_faces_uncalculated+person,path_faces_calculated)
else:
    print("没有人脸可计算")


# 从 CSV 中读取数据，计算 128D 特征的均值
def compute_the_mean(path_csv_rd):
    column_names = []

    # 128列特征
    for feature_num in range(128):
        column_names.append("features_" + str(feature_num + 1))

    # 利用pandas读取csv
    f=open(path_csv_rd)
    rd = pd.read_csv(f, names=column_names)

    # 存放128维特征的均值
    feature_mean = []
    # 在每行的第一列存放人的姓名
    name = path_csv_rd.split('/')[1].split('.')[0]
    feature_mean.append(name)
    for feature_num in range(128):
        tmp_arr = rd["features_" + str(feature_num + 1)]
        tmp_arr = np.array(tmp_arr)

        # 计算某一个特征的均值
        tmp_mean = np.mean(tmp_arr)
        feature_mean.append(tmp_mean)
    return feature_mean


# 存放所有特征均值的 CSV 的路径
path_csv_feature_all = "features_all.csv"

# 存放每个人人脸特征的 CSV 的路径
path_csv = "data_csvs_from_camera/"

with open(path_csv_feature_all, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    csv_rd = os.listdir(path_csv)
    print("得到的特征均值 / The generated average values of features stored in: ")

    for i in range(len(csv_rd)):
        feature_mean = compute_the_mean((path_csv + csv_rd[i]))
        print(path_csv + csv_rd[i])
        writer.writerow(feature_mean)