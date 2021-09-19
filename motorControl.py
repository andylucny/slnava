import time
import serial
from agentspace import Agent, Space
import cv2

class MotorControl:
    
    def __init__(self,line='COM6'):
        '''Creates an object that you can call to control the robot
        '''
        self.ser = serial.Serial(
            port=line,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1 #nonblock
        )
        if not self.ser.isOpen():
            print('cannot open line '+line)
        else:
            self.ser.write(b'B\x00')
            time.sleep(1)

    def left(self):
        if self.ser.isOpen():
            #self.ser.write(b'C\x01') # only to left
            self.ser.write(b'C\x09') # to left and forward

    def right(self):
        if self.ser.isOpen():
            #self.ser.write(b'C\x02') # only to right
            self.ser.write(b'C\x0A') # to right and forward
        
    def forward(self):
        if self.ser.isOpen():
            self.ser.write(b'C\x08') # forward
        
    def backward(self):
        if self.ser.isOpen():
            self.ser.write(b'C\x04') # backward
        
    def stop(self):
        if self.ser.isOpen():
            self.ser.write(b'C\x00') # stop

    def command(self,value):
        if self.ser.isOpen():
            if value == 0:
                self.ser.write(b'C\x00')
            elif value == 1:
                self.ser.write(b'C\x01')
            elif value == 2:
                self.ser.write(b'C\x02')
            elif value == 3:
                self.ser.write(b'C\x03')
            elif value == 4:
                self.ser.write(b'C\x04')
            elif value == 5:
                self.ser.write(b'C\x05')
            elif value == 6:
                self.ser.write(b'C\x06')
            elif value == 7:
                self.ser.write(b'C\x07')
            elif value == 8:
                self.ser.write(b'C\x08')
            elif value == 9:
                self.ser.write(b'C\x09')
            elif value == 10:
                self.ser.write(b'C\x0A')
            elif value == 11:
                self.ser.write(b'C\x0B')
            elif value == 12:
                self.ser.write(b'C\x0C')
            elif value == 13:
                self.ser.write(b'C\x0D')
            elif value == 14:
                self.ser.write(b'C\x0E')
            elif value == 15:
                self.ser.write(b'C\x0F')

class MotorAgent(Agent):

    def __init__(self,line,forwardName,turnName,headingName):
        self.line = line
        self.forwardName = forwardName
        self.turnName = turnName
        self.headingName = headingName
        super().__init__()

    def init(self):
        self.control = MotorControl(self.line)
        self.attach_trigger(self.forwardName)
        self.attach_trigger(self.turnName)
        
    def senseSelectAct(self):
        forward = Space.read(self.forwardName,0)
        turn = Space.read(self.turnName,0)
        heading = Space.read(self.headingName,0)
        #print('forward',forward,'turn',turn,'heading',heading)
        command = 0
        if turn < 0:
            command += 1
        if turn > 0:
            command += 2
        if forward > 0:
            command += 8
        if forward < 0:
            command += 4
        self.control.command(command)

# Test    
if __name__ == "__main__":
    robot = MotorControl()
#    print('right')
#    robot.right()
#    time.sleep(2)
#    print('left')
#    robot.left()
#    time.sleep(2)
    print('forward')
    robot.forward()
    time.sleep(2)
#    print('backward')
#    robot.backward()
#    time.sleep(2)
    print('stop')
    robot.stop()
