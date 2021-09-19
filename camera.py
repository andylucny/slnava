import numpy as np
import cv2
from agentspace import Agent, Space

class CameraAgent(Agent):

    def __init__(self,id,name):
        self.id = id
        self.name = name
        super().__init__()

    def init(self):
        this.camera = cv2.VideoCapture(1,cv2.CAP_DSHOW) 
        while True:
            hasFrame, frame = camera.read()
            if not hasFrame:
                break
            Space.write(name,frame)
        
    def senseSelectAct(self):
        pass
