'''
Created on Apr 21, 2021

@author: piotr
'''
from ObjectsDetectable.Classes import FaceID
from Detector.Detector import Detector_AbstCls
from PolymorphicBases.ABC import final

    

class FacesDetector_AbstCls(Detector_AbstCls):
    
    @staticmethod
    def getJobName():
        return "FaceDetection"
    
    @final
    @staticmethod
    def getClassesServiced():
        return {FaceID}
    

    def __init__(self):
        assert type(self) != FacesDetector_AbstCls
        Detector_AbstCls.__init__(self)
    
    
    
    