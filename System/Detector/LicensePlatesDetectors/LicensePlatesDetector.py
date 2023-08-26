'''
Created on Apr 21, 2021

@author: piotr
'''
from ObjectsDetectable.Classes import LicensePlateID
from Detector.Detector import Detector_AbstCls
from PolymorphicBases.ABC import final



class LicensePlatesDetector_AbstCls(Detector_AbstCls):
    
    @staticmethod
    def getJobName():
        return "LicensePlateDetection"
    
    @final
    @staticmethod
    def getClassesServiced():
        return {LicensePlateID}
        

    def __init__(self):
        assert type(self) != LicensePlatesDetector_AbstCls
        Detector_AbstCls.__init__(self)
    
    
