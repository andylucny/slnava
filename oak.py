import cv2
import depthai as dai
import numpy as np
import time
from agentspace import Agent, Space

class OakAgent(Agent):

    def __init__(self,rgbName,depthName):
        self.rgbName = rgbName
        self.depthName = depthName
        super().__init__()

    def init(self):
        
        while True:
            # Start defining a pipeline
            pipeline = dai.Pipeline()

            # Define a source - two mono (grayscale) cameras
            left = pipeline.createMonoCamera()
            left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
            left.setBoardSocket(dai.CameraBoardSocket.LEFT)

            right = pipeline.createMonoCamera()
            right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
            right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

            # Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
            depth = pipeline.createStereoDepth()
            depth.setConfidenceThreshold(200)
            left.out.link(depth.left)
            right.out.link(depth.right)

            # Create output
            xout = pipeline.createXLinkOut()
            xout.setStreamName("disparity")
            depth.disparity.link(xout.input)

            # Define a source - color camera
            cam_rgb = pipeline.createColorCamera()
            cam_rgb.setPreviewSize(300,300) # 300,300  # 1920, 1080
            cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)
            cam_rgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
            cam_rgb.setInterleaved(False)
            cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

            # Create output
            xout_rgb = pipeline.createXLinkOut()
            xout_rgb.setStreamName("rgb")
            cam_rgb.preview.link(xout_rgb.input)

            # Pipeline defined, now the device is connected to
            with dai.Device(pipeline) as device:
                # Start pipeline
                device.startPipeline()

                # Output queue will be used to get the disparity frames from the outputs defined above
                q_disparity = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)
                q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

                while True:
                    restart = False
                    try:
                        in_depth = q_disparity.get()  # blocking call, will wait until a new data has arrived
                        # data is originally represented as a flat 1D array, it needs to be converted into HxW form
                        frame_depth = in_depth.getData().reshape((in_depth.getHeight(), in_depth.getWidth())).astype(np.uint8)
                        frame_depth = np.ascontiguousarray(frame_depth)
                        
                        Space.write(self.depthName,frame_depth,validity=0.25)
                    
                    except:
                        restart = True 

                    try:
                        in_rgb = q_rgb.get()
                        frame_rgb = in_rgb.getCvFrame()
                    
                        Space.write(self.rgbName,frame_rgb,validity=0.25)
                    
                    except:
                        restart = True
            
                    if restart:
                        break
                
    def senseSelectAct(self):
        pass
        