import sys
import threading
import time

import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np
import datetime
from threading import Thread
import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from functions import fps_checker, distance_point_to_line, central_point

# reference()

# ---------------------- #
THESHHOLD = 0.5  # Пороговое значение
gateSize = 38500  # ширина створа в см
cameraMatrix = np.array([  # матрица камеры
    [1.65777818, 0.00000000, 8.30442813],
    [0.00000000, 1.65890891, 1.06153195],
    [0.00000000, 0.00000000, 1.00000000]
])
focal = 635  # фокусное расстояние


# ---------------------- #


class BoatTracking:

    def __init__(self, capture_index):
        self.root = tk.Tk()
        self.root.title("Boat Info")
        self.text_widget = tk.Text(self.root)
        self.text_widget.pack()
        save_button = tk.Button(self.root, text='Save', command=self.save_file)
        save_button.pack()

        self.capture_index = capture_index
        self.model = self.yolo_model()
        # test1
        self.line1 = ([566, 233], [842, 321])
        self.line2 = ([-2, 317], [386, 233])

        # test2
        # self.line1 = ([49, 461], [371, 258])
        # self.line2 = ([443, 258], [675, 462])
        # информация о размере изображения
        self.video_info = sv.VideoInfo.from_video_path(self.capture_index)

        self.box = sv.BoxAnnotator(
            color=sv.Color(r=128, g=0, b=0),
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

    def yolo_model(self):  # подгрузка модели yolo
        # model = YOLO('runs/detect/boat_detect3/weights/last.pt')
        model = YOLO('yolov8s.pt')
        model.predict(source="capture_index", show=False, stream=True, classes=8)
        model.fuse()
        return model

    def pixel_coefficient(self, c_point):  # перевод пикселей в cм
        point = distance_point_to_line(c_point, self.line1[0], self.line1[1])
        point2 = distance_point_to_line(c_point, self.line2[0], self.line2[1])
        print("P1", point, "P2", point2)
        print("КОЭФФИЦИЕНТ", gateSize / (point + point2))
        return gateSize / (point + point2)

    def object_real_size(self, pixel_c, boat_width):
        real_size = (pixel_c / 100) * boat_width
        return real_size

    def object_x_y(self, obj_width_p, obj_width_m):
        result = (6350 * obj_width_m) / obj_width_p
        print("РАССТОЯНИЕ", result)
        return result / 100

    def object_deviation(self, c_point, pix_coff):
        point = distance_point_to_line(c_point, self.line1[0], self.line1[1])
        point2 = distance_point_to_line(c_point, self.line2[0], self.line2[1])
        center = (point + point2) / 2
        return abs(center - c_point[0]) * pix_coff / 10000

    def save_file(self):
        file_path = asksaveasfilename(defaultextension='.txt')
        if file_path:
            with open(file_path, 'w') as file:
                text = self.text_widget.get('1.0', tk.END)
                file.write(text)

    def update_text(self, det, y_coord, x_coord):
        self.text_widget.tag_config('tg_red', foreground='red')
        if det:
            self.text_widget.configure(state=tk.NORMAL)
            self.text_widget.insert(tk.END, f"\n{datetime.datetime.now()}")
            self.text_widget.insert(tk.END, f"\nНАЙДЕНО СУДОВ В АКВАТОРИИ:{int(len(det))}")
            for i in range(len(det)):
                self.text_widget.configure(state=tk.NORMAL)
                self.text_widget.insert(tk.END, f"\nСудно {i+1}:\n")
                self.text_widget.insert(tk.END, f"Расстояние до судна: {y_coord[i]}м\n", "red")
                self.text_widget.insert(tk.END, f"Отклонение от центра акватории: {x_coord[i]}м\n", "tg_red")
                self.text_widget.see(tk.END)  # прокрутка виджета до конца
                self.text_widget.configure(state=tk.DISABLED)
                # self.root.after(1000, self.update_text)  # вызов функции через 1000 миллисекунд

    def object_location(self):
        video = cv2.VideoCapture(self.capture_index)  # запуск считывания видеоизображения
        assert video.isOpened()

        video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # ширина видеоизображения
        video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # высота видеоизображения

        while True:
            p_time = datetime.datetime.now()  # старт fps-счетчика
            success, frame = video.read()
            assert success
            results = self.model(frame)[0]
            detections = sv.Detections.from_yolov8(results)
            y_coord = []
            x_coord = []
            # ---------------------- #
            for i in range(len(detections)):  # парсинг найденных объектов для определения координат
                x0 = detections.xyxy[i][0]
                y0 = detections.xyxy[i][1]
                x1 = detections.xyxy[i][2]
                y1 = detections.xyxy[i][3]
                c_point = central_point(x0, y0, x1, y1)  # координаты центра объекта
                p_coefficient = self.pixel_coefficient(c_point)  # коэффициент перевода пикселей в см
                obj_width = self.object_real_size(p_coefficient, (x1 - x0))
                print("ИКС ПЕРВАЯ", x1)
                print("ИКС НУЛЕВАЯ", x0)
                print("В ПИКСЕЛЯХ ", x1 - x0)
                print("В МЕТРАХ", obj_width)
                y_coord.append(self.object_x_y(abs(x1 - x0), obj_width))
                x_coord.append(self.object_deviation(c_point, p_coefficient))
                # cv2.line(frame, [566, 233], [842, 321], color=(255, 0, 0), thickness=1)
                # cv2.line(frame, [-2, 317], [386, 233], color=(255, 0, 0), thickness=1)

            self.update_text(detections, y_coord, x_coord)

            labels = [
                # f"{confidence:0.2f}{class_id}"
                f"{confidence:0.2f}{'|'}{i:0.1f}"
                for confidence, i
                in zip(detections.confidence, y_coord)
            ]
            # ---------------------- #
            # отрисовка боксов и полигона
            frame = self.box.annotate(scene=frame, detections=detections, labels=labels)

            c_time = datetime.datetime.now()  # конец fps-счетчика
            fps = fps_checker(p_time, c_time)  # функция fps-счетчика
            y_coord.clear()
            x_coord.clear()
            cv2.putText(frame, fps, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (250, 235, 215), 2)
            cv2.imshow('Boat Tracking', frame)
            if cv2.waitKey(1) == ord("q"):  # конец выполнения программы в случае нажатии на клавишу q
                break
        video.release()
        cv2.destroyAllWindows()
        self.save_file()

    def __call__(self, *args, **kwargs):
        t1 = Thread(target=self.object_location)
        # t2 = Thread(target=self.update_text)
        t1.start()
        # t2.start()
        self.root.mainloop()


tracking = BoatTracking(capture_index="videos/TEST3.mp4")
tracking()
