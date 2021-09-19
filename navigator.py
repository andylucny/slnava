import numpy as np
import cv2
from agentspace import Agent, Space

class NavigatorAgent(Agent):

    def __init__(self,gpsName,goalName,headingName,forwardName,turnName):
        self.gpsName = gpsName
        self.goalName = goalName
        self.headingName = headingName
        self.forwardName = forwardName
        self.turnName = turnName
        super().__init__()

    def init(self):
        self.state = 0
        self.last_position = None
        self.attach_trigger(self.gpsName)

    def senseSelectAct(self):
        
        position = Space.read(self.gpsName,None)
        if position is None:
            return
            
        if self.last_position is not None:
            heading = (position[0] - self.last_position[0], position[1] - self.last_position[1])
            Space.write(self.headingName,heading,validity=1.5)
        else:
            heading = None
            
        self.last_position = position
        
        if heading is None:
            return

        goal = Space.read(self.goalName,None)
        if goal is None:
            return
            
        if self.state == 0:
            self.state = 1
            print('goal',goal,'accepted')

        vis = Space.read('visual',None)
        if vis is not None:
            limit = 5
            angle = -vis
            print('vis',angle)
            if angle < -limit:
                Space.write(self.turnName,-1,validity=0.3)
                Space.write(self.forwardName,1,validity=0.3)
            elif angle > limit:
                Space.write(self.turnName,1,validity=0.3)
                Space.write(self.forwardName,1,validity=0.3)
            else:
                Space.write(self.turnName,0,validity=0.3)
                Space.write(self.forwardName,1,validity=0.3)
            
            return
        
        eps = 0.000005
        if (position[0] - goal[0])**2 + (position[1] - goal[1])**2 < eps**2:
            Space.write(self.forwardName,0,validity=1.5)
            Space.write(self.turnName,0,validity=1.5)
            if self.state == 1:
                self.state = 0
                print('goal',goal,'achieved')
                Space.write(self.goalName,None)
        else:
            goal_heading = (goal[0] - position[0], goal[1] - position[1])
            angle = -np.arctan2(heading[0]*goal_heading[1]-heading[1]*goal_heading[0],heading[0]*goal_heading[0]+goal_heading[1]*heading[1])
            angle *= 180 / np.pi
            #print('angle',angle)
            limit = 5
            if angle < -limit:
                Space.write(self.forwardName,1,validity=1.5)
                Space.write(self.turnName,-1,validity=0.8)
            elif angle > limit:
                Space.write(self.forwardName,1,validity=1.5)
                Space.write(self.turnName,1,validity=0.8)
            else:
                Space.write(self.forwardName,1,validity=1.5)
                Space.write(self.turnName,0,validity=1.5)
