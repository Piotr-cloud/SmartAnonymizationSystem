'''
Created on Mar 17, 2022

@author: piotr
'''
import numpy as np
from Detections.Detection import Detection_AbstCls
from ContentRecognizer.Recognition import Recognition_AbstCls
from Space._2D.Array import Array_AbstCls


class View_Cls(Array_AbstCls):
    """
    Is a pair of np array and single detection(shape + details)
    """
    
    def __init__(self, array, detection, forceRAM = False):
        
        assert isinstance(detection, Detection_AbstCls)
        
        self._detection = detection
        
        if isinstance(array, np.ndarray):
            self._constructedWithNpArray_flag = True
            Array_AbstCls.__init__(self, array, forceRAM = forceRAM)
        
        elif isinstance(array, Array_AbstCls):
            self._constructedWithNpArray_flag = False
            self.dataSrc = array.dataSrc
        
        else:
            raise TypeError("Provided array data type is not valid")
        
        self._recognition = None
    
    
    def getName(self):
        return "View: " + str(self.getDetection())
    
    
    def setRecognition(self, recognition):
        
        assert self._recognition is None
        assert isinstance(recognition, Recognition_AbstCls)
        
        self._recognition = recognition
    
    
    def getRecognition(self):
        return self._recognition
    
    
    def isRecognized(self):
        return self._recognition is not None
    

    def getDetection(self):
        return self._detection




class ObjectView_Cls(View_Cls):
    pass




class StubView_Cls(View_Cls):
    # This class is used to create View_Cls instance that is just a dummy instance used to stub interfaces against assertions
    def __init__(self):
        pass








