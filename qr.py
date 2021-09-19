import numpy as np
import cv2
from agentspace import Agent, Space

class QrAgent(Agent):

    def __init__(self,imageName,qrName):
        self.imageName = imageName
        self.qrName = qrName
        super().__init__()

    def init(self):
        self.decoder = cv2.wechat_qrcode_WeChatQRCode("models/detect.prototxt", "models/detect.caffemodel", "models/sr.prototxt", "models/sr.caffemodel")
        self.attach_timer(1)
        
    def senseSelectAct(self):
        rgb = Space.read(self.imageName,None)
        if not rgb is None:
            res, points = self.decoder.detectAndDecode(rgb)
            res = None if len(res) == 0 else res[0]
            #print(res) # 'geo:48.8016394,16.8011145'
            if res is not None:
                Space.write(self.qrName,res)
