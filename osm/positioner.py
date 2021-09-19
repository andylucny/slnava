import numpy as np
import cv2
from bs4 import BeautifulSoup
import time
import serial
import re

class GpsReceiver:
    
    def __init__(self,line='COM7'):
        '''Creates an object that you can call to control the robot
        '''
        self.ser = serial.Serial(
            port=line,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0 #block
        )
        if not self.ser.isOpen():
            print('cannot open line '+line)
        else:
            self.buffer = ''

    def receive(self):
        if self.ser.isOpen():
            while self.buffer.find('\n')==-1:
                self.buffer += self.ser.read(1024).decode()
            result = re.sub('[\r\n].*','',self.buffer)
            self.buffer = self.buffer[self.buffer.find('\n')+1:]
        else:
            result = ''
        return result

    def recalc(self,bulg):
        dg = int(bulg/100)
        min = bulg-100*dg
        return dg + min/60

    def getPosition(self):
        while True:
            line = self.receive()
            #print(line)
            if line.find('$GPGLL') != -1:
                if ',,' in line:
                    return [-1,-1]
                else:
                    values = re.findall(r'[\d\.]+(?:,[\d\.]+)?',line)
                    return [self.recalc(float(v)) for v in values[:2]]

map = cv2.imread('../map.png')

with open('../map.osm', 'r', encoding="utf-8") as f:
    data = f.read()

bs = BeautifulSoup(data, "xml")

maxlat = float(bs.bounds['maxlat'])
minlat = float(bs.bounds['minlat'])
maxlon = float(bs.bounds['maxlon'])
minlon = float(bs.bounds['minlon'])

def pin(point):
    lat, lon = point
    y = (map.shape[0]-1) - map.shape[0]*(lat-minlat)/(maxlat-minlat)
    x = map.shape[1]*(lon-minlon)/(maxlon-minlon)
    return (int(x), int(y))
    
def unpin(pixel):
    x, y = pixel
    lat = (maxlat-minlat)*((map.shape[0]-1) - y)/map.shape[0] + minlat
    lon = x*(maxlon-minlon)/map.shape[1] + minlon
    return lat, lon

def mouseHandler(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(unpin((x,y)))
    elif event == cv2.EVENT_LBUTTONUP:
        pass
        
cv2.namedWindow("map")
cv2.setMouseCallback("map", mouseHandler)

gps = GpsReceiver(line='COM7') #12
while True:
    pos = gps.getPosition()
    print(pos)
    if pos[0] == -1:
        continue
    map2 = np.copy(map)
    p = pin(pos)
    print(p)
    cv2.circle(map2,p,3,(0,0,255),cv2.FILLED)
    cv2.imshow("map",map2)
    if cv2.waitKey(1) == 27:
        break
        