import cv2
from ultralytics import YOLO
import supervision as sv

def reference():

    # model = YOLO('yolov8n.pt')
    img = cv2.imread('images/paper2.jpg')
    # frame = img
    # results = model(frame)[0]
    # detections = sv.Detections.from_yolov8(results)
    # frame = box.annotate(scene=frame, detections=detections)
    # frame = box.annotate(scene=frame)
    cv2.line(img, (124, 365), (832, 382), color=(255, 0, 0), thickness=1)
    cv2.imshow("result", img)
    cv2.waitKey(0)
#     28,5
# 21

reference()