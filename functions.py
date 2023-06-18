import cv2
import numpy as np
from ultralytics import YOLO


def fps_checker(p_time, c_time):  # функция fps-счетчика
    fps = (c_time - p_time).total_seconds()
    fps = f"FPS: {1 / fps:.2f}"
    return fps


# def focal_length():  # настройка калибровки
#     # настраиваем калибровку:
#     # 1. матрица камеры; 2.размер видеоизображения;
#     # 3.физическая ширина камеры; 4. физическая высота камеры.
#     focal = cv2.calibrationMatrixValues(cameraMatrix, [1280, 720], 7.01, 5.79)
#     print("ФОКУС", focal[2])
#     return focal[2]


def distance_point_to_line(point, line_start, line_end):  # измерение расстояния от объекта до бортов створа
    # координаты точек на прямой
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end

    # находим коэффициенты уравнения прямой
    coefficients = np.polyfit([x1, x2], [y1, y2], 1)
    slope = coefficients[0]  # наклон прямой
    intercept = coefficients[1]  # пересечение с осью y

    # y_parallel = slope * x0 + intercept  # координата y на параллельной прямой
    x_parallel = (y0 - intercept) / slope  # координата x на параллельной прямой

    #  return int(x_parallel), y0  # точка на прямой, параллельная центру объекта
    return abs(x0 - x_parallel)


def central_point(x0, y0, x1, y1):  # координаты центра объекта
    a = int(x1) - int((x1 - x0) / 2)  # координата x
    b = int(y1) - int((y1 - y0) / 2)  # координата y
    c_point = (a, b)
    return c_point
