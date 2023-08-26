'''
Created on Nov 13, 2021

@author: piotr
'''
from Detector.Detector import Detector_AbstCls


class MultiClassDetector_Cls(Detector_AbstCls):
    
    @staticmethod
    def getJobName():
        return "MultiClassDetection"
    
    
    
