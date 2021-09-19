import numpy as np
import cv2
from agentspace import Agent, Space
import random
import time

class ObstacleAgent(Agent):

    def __init__(self,depthName,rgbName,qrName,forwardName,turnName):
        self.depthName = depthName
        self.rgbName = rgbName
        self.qrName = qrName
        self.forwardName = forwardName
        self.turnName = turnName
        super().__init__()

    def init(self):
        self.obstacle = False
        self.attach_trigger(self.depthName)

    def senseSelectAct(self):

        frame_depth = Space.read(self.depthName,None)
        if frame_depth is None:
            return

        frame_rgb = Space.read(self.rgbName,None)
        if frame_rgb is None:
            return

        #qr = Space.read(self.qrName,None)
        #if qr is None:
        #    return

        binary = ((frame_depth > 30)*255).astype(np.uint8)
        rows, cols = binary.shape[:2]
        leftMask = np.zeros((rows,cols),np.uint8)
        cv2.fillConvexPoly(leftMask, np.int32([[0,0],[0,rows-1],[cols//2,0]]), 255)
        rightMask = np.zeros((rows,cols),np.uint8)
        cv2.fillConvexPoly(rightMask, np.int32([[cols//2,0],[cols-1,rows-1],[cols-1,0]]), 255)
        frontMask = np.zeros((rows,cols),np.uint8)
        cv2.fillConvexPoly(frontMask, np.int32([[cols//2,0],[0,rows-1],[cols-1,rows-1]]), 255)
        leftObstacle = cv2.countNonZero(np.bitwise_and(leftMask,binary))/cv2.countNonZero(leftMask)
        rightObstacle = cv2.countNonZero(np.bitwise_and(rightMask,binary))/cv2.countNonZero(rightMask)
        frontObstacle = cv2.countNonZero(np.bitwise_and(frontMask,binary))/cv2.countNonZero(frontMask)

        #print('obstacles',rightObstacle,frontObstacle,leftObstacle)
        remedy = False
        if frontObstacle > 0.2: # or leftObstacle > 0.8 or rightObstacle > 0.8:
            if not self.obstacle:
                print('OBSTACLE!', frontObstacle)
                Space.write('obstacle',True,validity=0.3)    
                remedy = True
            self.obstacle = True
            Space.write(self.forwardName,0,validity=0.3,priority=2)
            Space.write(self.turnName,0,validity=0.3,priority=2)
            #if remedy:
            #    #if leftObstacle > 0.8:
            #    #    dir = 1
            #    #elif rightObstacle > 0.8:
            #    #    dir = -1
            #    #else:
            #    dir = 1 if random.uniform(0,1) > 0.5 else -1
            #    time.sleep(1)
            #    Space.write('Forward',-1,priority=2,validity=2)
            #    Space.write('Turn',dir,priority=2,validity=1)
            #    time.sleep(2)
            #   Space.write('Turn',-dir,priority=2,validity=0.5)
        else:
            if self.obstacle:
                print('FREE')
                Space.write('obstacle',None)
            self.obstacle = False

        

        #    Space.write(self.forwardName,1,validity=0.2)
        #    Space.write(self.turnName,0,validity=0.2)
