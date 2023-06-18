from ultralytics import YOLO

model = YOLO('yolov8s.pt')  # подгрузка модели

results = model.train(
    data="dataset2/projectdata.yaml",
    imgsz=640,
    epochs=2,
    batch=16,
    name='boat_detect',
    save=True)
# model performance on the val set
# model.val()
# export pt to onnx
# model.export(format="onnx")
