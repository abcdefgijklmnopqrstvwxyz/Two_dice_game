from ultralytics import YOLO
import torch
from os.path import exists


class PredictionModel():
    def __init__(self):
        if exists('E:\\2\\2\\best.pt'):
            self.model = YOLO('E:\\2\\2\\best.pt')
        else:
            self.model = YOLO('yolov8s.pt')
            self.model.train(data='data.yaml', epochs=100,imgsz=200)
            torch.save('best.pt')

    def predict(self,img):
        res = self.model.predict(source=img)[0]
        return res.boxes.cls
        