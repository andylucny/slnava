import time
import os
import numpy as np
import cv2
from agentspace import Agent, Space

from motorControl import MotorAgent
from gpsReceiver import GpsAgent
from oak import OakAgent
#from camera import CameraAgent
from qr import QrAgent
from obstacle import ObstacleAgent
from segmentation import SegmentationAgent, visualize
from joystickapiagent import JoystickAgent
from joystickcontrolagent import JoystickControlAgent
from navigator import NavigatorAgent
from osm import OsmAgent, pin
from remeder import RemederAgent
import signal 

def exit():
    os._exit(0)

def signal_handler(signal, frame):
    Space.write('forward',0)
    Space.write('turn',0)
    time.sleep(0.25)
    exit()

signal.signal(signal.SIGINT, signal_handler)

class MonitoringAgent(Agent):

    def __init__(self,rgbName,depthName,annotationName,gpsName):
        self.rgbName = rgbName
        self.depthName = depthName
        self.annotationName = annotationName
        self.gpsName = gpsName
        super().__init__()

    def init(self):
        self.f = open('record/'+self.gpsName+'.txt','w')
        self.last_timestamp = 0
        self.last_position = [-1,-1]
        self.attach_trigger(self.rgbName)
        #self.attach_trigger(self.gpsName)

    def senseSelectAct(self):
        frame_depth = Space.read(self.depthName,None)
        frame_rgb = Space.read(self.rgbName,None)
        frame_annotation = Space.read(self.annotationName,None)
        position = Space.read(self.gpsName,[-1,-1])

        if frame_depth is not None:
            cv2.imshow(self.depthName, frame_depth)
            
        if frame_rgb is not None:
            cv2.imshow(self.rgbName, frame_rgb)

        if frame_annotation is not None:
            cv2.imshow(self.annotationName, visualize(frame_annotation))
        
        if position[0] != self.last_position[0] or position[1] != self.last_position[1]:
            #print('position',position)
        
            for v in position:
                self.f.write(str(v)+' ')
            
            self.f.write('\n')
            self.f.flush()
            
            self.last_position = position

        key = cv2.waitKey(1)
        if key == 27:
            os._exit(0)

        timestamp = round(time.time())
        if timestamp != self.last_timestamp:
        
            if frame_depth is not None:
                cv2.imwrite('record/depth'+str(timestamp)+'.png',frame_depth)
                
            if frame_rgb is not None:
                cv2.imwrite('record/rgb'+str(timestamp)+'.png',frame_rgb)

            if frame_annotation is not None:
                cv2.imwrite('record/annot'+str(timestamp)+'.png',frame_annotation)
                cv2.imwrite('record/disp'+str(timestamp)+'.png',visualize(frame_annotation))
            
            self.last_timestamp = timestamp

GpsAgent('COM7','gps')

MotorAgent('COM6','forward','turn','heading')

OakAgent('rgb','depth')
#CameraAgent(1,'steering-wheel')

QrAgent('rgb','qr')
#img = cv2.imread('record_/rgb1628947271.png') #QR code
#Space.write('rgb',img)

ObstacleAgent('depth','rgb','qr','forward','turn')
RemederAgent('forward','turn') #'obstacle'
#img = cv2.imread('record_/depth1628947143.png',cv2.IMREAD_GRAYSCALE) #obstacle
#img2 = cv2.imread('record_/rgb1628947143.png') #obstacle
#Space.write('depth',img)
#Space.write('rgb',img2)
#Space.write('qr','any')

SegmentationAgent('rgb','annotation')

JoystickAgent('joystick')
JoystickControlAgent('joystick','forward','turn')
NavigatorAgent('gps','goal','heading','forward','turn')
OsmAgent('gps','qr','goal')

MonitoringAgent('rgb','depth','annotation','gps')

#dy = 0.0000275
#dx = -0.0000530
#while True:
#    position = Space.read('gps',[-1,-1])
#    if position[0] != -1:
#        goal = (position[0]-dy,position[1]-dx)
#        Space.write('goal',goal)
#        break
#    time.sleep(1)

#while True:
#    qr = Space.read('qr',None)
#    if qr is not None:
#        print(qr) # geo:48.1491242,17.0737278
#        values = qr[4:].split(',')
#        goal = (float(values[0]),float(values[1]))
#        goal = (48.1491242,17.0737278) # prva nakladka
#        Space.write('goal',goal)
#        print('QR code received')
#        break
#    time.sleep(1)

#print('go!')
#while True:
    #Space.write('forward',1,validity=0.12)
    #Space.write('turn',0,validity=0.12)
#    time.sleep(0.1)
#    gps = Space.read('gps',[-1,-1])
#    goal = Space.read('goal',[-1,-1])
#    if (gps[0] != -1) and (goal[0] != -1):
#        err = abs(goal[0]-gps[0]) + abs(goal[1]-gps[1])
#        print('distance to goal',err)
