from agentspace import Agent,Space
import joystickapi
import time

class JoystickControlAgent(Agent):

    def __init__(self,name,nameForward,nameTurn):
        self.name = name
        self.nameForward = nameForward
        self.nameTurn = nameTurn
        super().__init__()

    def init(self):
        self.attach_trigger(self.name)
        
    def valueOf(self,value):
        if value < -25000:
            return -1
        elif value > 25000:
            return 1
        else:
            return 0

    def senseSelectAct(self):
        axisXYZ = Space.read(self.name,[[],[0,0,0],[]])[1]
        turn = self.valueOf(axisXYZ[0])
        forward = -self.valueOf(axisXYZ[1])
        #print('joystick','turn',turn,'forward',forward)
        Space.write("forward",forward,validity=0.4)
        Space.write("turn",turn,validity=0.4)
