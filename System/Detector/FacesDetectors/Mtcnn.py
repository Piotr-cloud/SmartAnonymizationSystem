'''
Created on 25 lis 2020

@author: piotr
'''

from Detections.Detection import BoundingBox_Cls
from Detections.DetectionsMap import DetectionsMap_Cls

from ObjectsDetectable.Classes import FaceID

import logging
import numpy as np

from Detector.FacesDetectors.FacesDetector import FacesDetector_AbstCls
from CommonTools.ContextManagers import PrintingDisabler_Cls
from SW_Licensing.SW_License import License_Cls



class MTCNN_Cls(FacesDetector_AbstCls):
    
    @staticmethod
    def getName(): 
        return "MTCNN"
        
    @staticmethod
    def getDescription():
        return "Cascaded convolutional neurla networks system consist of prosposal(P-Net), refinement(R-Net) and output (O-Net) networks"
    
    @staticmethod
    def getLicense():
        return License_Cls(
            type_ = "MIT",
            srcCodeLocation = "https://pypi.org/project/mtcnn/",
            fullStatement = """MIT License

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
SOFTWARE.
""")
        
            
    def __init__(self):
        
        from mtcnn.mtcnn import MTCNN # long loading time
        import tensorflow as tf
        
        FacesDetector_AbstCls.__init__(self)
        
        tf.get_logger().setLevel(logging.ERROR)
        self.classifier = MTCNN()
    
    
    def _detect(self, nparray):
        
        detections = DetectionsMap_Cls()
        
        with PrintingDisabler_Cls():
            results = self.classifier.detect_faces(nparray)
        
        for result in results:
            
            left    = result['box'][0] / nparray.shape[1]
            top     = result['box'][1] / nparray.shape[0]
            right   = (result['box'][0] + result['box'][2]) / nparray.shape[1]
            bottom  = (result['box'][1] + result['box'][3]) / nparray.shape[0]
            
            left, top, right, bottom = np.clip((left, top, right, bottom), 0.0, 1.0)
            
            detections.addDetection(BoundingBox_Cls(class_ = FaceID,
                                                    left = left,
                                                    top = top,
                                                    right = right,
                                                    bottom = bottom))
        
        return detections
    
    



