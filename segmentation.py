import numpy as np
import cv2
from agentspace import Agent, Space

model_name = "models/road-segmentation-adas-0001"
model_xml = model_name+".xml"
model_bin = model_name+".bin"
net = cv2.dnn.readNet(model_bin,model_xml,'DLDT') 
print('segmentation model loaded')

def segment(img):
    rows, cols = img.shape[:2]
    height, width = 512, 896
    offset = (width - height) // 2
    blob = np.zeros((height,width,3),np.uint8)
    blob[0:height,offset:offset+height] = cv2.resize(img,(height,height))
    blob = np.array([cv2.split(blob)])

    net.setInput(blob)
    outs = net.forward()

    annotation = np.argmax(outs[0],axis=0)
    annotation = annotation[0:height,offset:offset+height]
    annotation = cv2.resize(annotation,(cols,rows),interpolation=cv2.INTER_NEAREST_EXACT)
    return annotation

def visualize(annotation):
    classes = ['BG', 'road', 'curb', 'mark']
    colors = np.array([(0,0,0),(0,255,0),(255,255,0),(0,0,255)],np.uint8)
    disp = colors[annotation]
    return disp
    
class SegmentationAgent(Agent):

    def __init__(self,rgbName,annotationName):
        self.rgbName = rgbName
        self.annotationName = annotationName
        super().__init__()

    def init(self):
        self.attach_trigger(self.rgbName)

    def senseSelectAct(self):
        frame = Space.read(self.rgbName,None)
        if frame is not None:
            annotation = segment(frame)
            Space.write(self.annotationName,annotation,validity=1.0)
            try:
                indices = np.where(annotation == 1)
                if len(indices) > 0:
                    x,y = int(np.average(indices[1])),int(np.average(indices[0]))
                    angle = np.arctan2(x,annotation.shape[0]-y)
                    angle *= 180/np.pi
                    Space.write('visual',angle,validity=0.5)
            except:
                pass

# Test    
if __name__ == "__main__":
    image = cv2.imread('walkway.png')
    annotation = segment(image)
    cv2.imwrite('annotation.png',annotation)
    cv2.imwrite('annotated.png',visualize(annotation))
    