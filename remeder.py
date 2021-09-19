import numpy as np
import cv2
from agentspace import Agent, Space
import random
import time

class RemederAgent(Agent):

    def __init__(self,forwardName,turnName):
        self.forwardName = forwardName
        self.turnName = turnName
        super().__init__()

    def init(self):
        self.attach_trigger('obstacle')

    def senseSelectAct(self):
        obstacle = Space.read('obstacle',False)
        if obstacle:
            time.sleep(1.5)
            dir = 1 if random.uniform(0,1) > 0.5 else -1
            Space.write('Turn',dir,priority=3,validity=0.8)
            time.sleep(0.5)
            Space.write('Forward',-1,priority=3,validity=1)
