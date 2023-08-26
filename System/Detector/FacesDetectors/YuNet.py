'''
Created on May 13, 2023

@author: piotr
'''
from Detector.FacesDetectors.FacesDetector import FacesDetector_AbstCls
from SW_Licensing.SW_License import License_Cls

import cv2
import numpy as np

from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path,\
    UserCfg_Float_Limited, UserCfg_Int_Limited
from NonPythonFiles.WorkersFiles.Detectors.YuNet import YuNet_defaultModel_path
from Detections.DetectionsMap import DetectionsMap_Cls
from Detections.Detection import BoundingBox_Cls
from ObjectsDetectable.ClassesCfg import FaceID



class YuNet_Cls(FacesDetector_AbstCls):
    
    @staticmethod
    def getName(): 
        return "YuNet"
        
    @staticmethod
    def getDescription():
        return "Deep neural network detector. YuNet: A Fast and Accurate CNN-based Face Detector (https://github.com/ShiqiYu/libfacedetection)."
    
    @staticmethod
    def getLicense():
        return License_Cls(
            type_ = "MIT License",
            srcCodeLocation = "https://github.com/opencv/opencv_zoo/tree/master/models/face_detection_yunet",
            fullStatement = """MIT License

Copyright (c) 2020 Shiqi Yu <shiqi.yu@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")
        
    def __init__(self, 
            modelPath = UserCfg_Path(
                name = "Model file",
                description = "Path to requested model",
                path = YuNet_defaultModel_path),
            
            confThreshold = UserCfg_Float_Limited(
                name="Confidence threshold",
                description = "The threshold to filter out bounding boxes of score smaller than the given value ",
                lower_limit = 0.0001,
                defaultValue = 0.8,
                upper_limit = 1.0),
                  
            nmsThreshold = UserCfg_Float_Limited(
                name="Non-max suppression threshold",
                description = "The threshold to suppress bounding boxes of IoU bigger than the given value ",
                lower_limit = 0.0001,
                defaultValue = 0.3,
                upper_limit = 1.0),
                  
            topK = UserCfg_Int_Limited(
                name = "Max detections",
                description = "Keep top K bboxes before NMS",
                lower_limit = 1,
                defaultValue = 5000,
                upper_limit = 20000)):
        
        
        self._modelPath = self.resolveArgument(modelPath)
        self._confThreshold = self.resolveArgument(confThreshold)
        self._nmsThreshold = self.resolveArgument(nmsThreshold)
        self._topK = self.resolveArgument(topK)
        
        self._inputSize = [320, 320] # DNN model input size
        self._backendId = 0
        self._targetId = 0
        
        
        self._model = cv2.FaceDetectorYN.create(
            model=str(self._modelPath),
            config="",
            input_size=self._inputSize,
            score_threshold=self._confThreshold,
            nms_threshold=self._nmsThreshold,
            top_k=self._topK,
            backend_id=self._backendId,
            target_id=self._targetId)
        
        FacesDetector_AbstCls.__init__(self)
        

    def _detect(self, nparray):
        
        detections = DetectionsMap_Cls()
        
        h, w, _ = nparray.shape

        # Inference
        self._model.setInputSize([w, h])
        results = self._model.detect(nparray)[1]
        
        for det in (results if results is not None else []):
            
            bbox = det[0:4].astype(np.int32)
            
            left = bbox[0] / w
            right = (bbox[0]+bbox[2]) / w
            
            top = bbox[1] / h
            bottom = (bbox[1]+bbox[3]) / h
            
            left = self.limitFloatFrom0To1(left)
            right = self.limitFloatFrom0To1(right)
            top = self.limitFloatFrom0To1(top)
            bottom = self.limitFloatFrom0To1(bottom)
            
            detections.addDetection(
                BoundingBox_Cls(
                    class_ = FaceID,
                    left = left,
                    top = top,
                    right = right,
                    bottom=bottom
                    )
                )
            
    
        return detections


