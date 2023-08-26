'''
Created on Mar 15, 2021

@author: piotr
'''
from Space._2D.Array import Array_AbstCls
from Space.FrameHolder import FrameHolder_AbstCls
from Space._2D.ImageParts import ImagePart_Cls
import cv2
import numpy as np
from pathlib import Path



class Image_Cls(Array_AbstCls, FrameHolder_AbstCls):
    """
    """
    
    def __init__(self, originFilePath):
        
        FrameHolder_AbstCls.__init__(self, originFilePath)
        
        originFilePath = Path(originFilePath)
        
        if not originFilePath.exists():
            raise OSError("The following path odes not exist: " + str(originFilePath))
            
        if not originFilePath.is_file():
            raise IsADirectoryError("The following path is not a file, but drectory: " + str(originFilePath))
        
        npArray = cv2.imread(str(originFilePath))
        
        assert isinstance(npArray, np.ndarray)
        
        Array_AbstCls.__init__(self, npArray, isOnHdAlready_filePath = originFilePath)
    

    def getPart(self, left, top, right, bottom):
        """
        Relative values shall be provided: all arguments shall be in range (0.0, 1.0)
        """
        
        left_abs   = left * self._array.shape[1]
        right_abs  = right * self._array.shape[1]
        
        top_abs     = top * self._array.shape[0]
        bottom_abs  = bottom * self._array.shape[0]
        
        return ImagePart_Cls(numpyArray = self._array[left_abs:right_abs, top_abs:bottom_abs])
    
    
    def copy(self):
        return RAM_Image_Cls(self.getNpArrayCopy(), self.getOriginFilePath())
     


        
   
        

class RAM_Image_Cls(Image_Cls):
    
    def __init__(self, numpyArray, originFilePath = None):
        FrameHolder_AbstCls.__init__(self, originFilePath)
        Array_AbstCls.__init__(self, numpyArray, forceRAM=True)
        












