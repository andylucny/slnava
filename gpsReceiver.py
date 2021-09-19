import time
import serial
import re
from agentspace import Agent, Space

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
                
class GpsAgent(Agent):

    def __init__(self,line,gpsName):
        self.line = line
        self.gpsName = gpsName
        super().__init__()

    def init(self):
        gps = GpsReceiver(self.line)
        while True:
            position = gps.getPosition()
            Space.write(self.gpsName,position)
        
    def senseSelectAct(self):
        pass

# Test    
if __name__ == "__main__":
    gps = GpsReceiver(line='COM12')
    while True:
        print(gps.getPosition())
