'''
Created on Apr 14, 2021

@author: piotr
'''

import numpy as np
import cv2
from Space._2D.Shapes.Polygon import PolygonShape_Cls
from Detections.DetectionsMap import DetectionsMap_Cls
from Space._2D.Array import Array_AbstCls
from Detections.Detection import Detection_AbstCls


class Mask_Cls():
    
    """
    Mask is an array(mask array) that is related to another array that is beeing masked.
        Mask array contains binary data that is related to the original array elements
        Mask array is blank at construction and can only be filled with .addDetection method that adds new ones(binary cells)
    """
    
    def __init__(self, referenceArray, _3d_flag = False, onesThreshold = None):
        
        if isinstance(referenceArray, Array_AbstCls):
            referenceArray_asNpArray = referenceArray.getNpArrayCopy()
            
        elif isinstance(referenceArray, np.ndarray):
            referenceArray_asNpArray = referenceArray
            
        else:
            raise TypeError("Mask cannot be made base on provided reference array data")
        
        maskArray = None
        
        if isinstance(onesThreshold, int):
            if 0 < onesThreshold < 256:
                maskArray = (referenceArray_asNpArray >= onesThreshold).astype(np.uint8) * 255
        
        if maskArray is None:
            maskArray = np.zeros(referenceArray_asNpArray.shape, dtype=np.uint8)
        
        if _3d_flag:
            maskArray = np.repeat(maskArray[..., np.newaxis], 3, axis = 2)
        
        self._array = maskArray
        
    
    def addRegion(self, region):
        
        if len(self._array.shape) > 2:
            mask_color = (255,) * self._array.shape[2]
        else:
            mask_color = (255,)
        
        if isinstance(region, PolygonShape_Cls):
            points = region.getPoints()
            
            points_absoluteCoords = np.array([[point.getAbsoluteCoords(*self._array.shape[:2]) for point in points]], np.int32)
            
            cv2.fillPoly(self._array, points_absoluteCoords, mask_color)
               
        else:
            print("Detection shape(region) class: " + str(type(region).__name__) + " is not supported!")
    
    
    def getMaskArray(self):
        return self._array





class MaskGenerator_Cls():

    def __init__(self):
        '''
        Constructor
        '''
        
    def getBlankMaskArray(self, referenceArray):
        return Mask_Cls(referenceArray)
    

    def getMaskOfDetections(self, referenceArray, detections):
        """
        detections shall be iterable of DetectionsMap_Cls obj
        """
        
        assert isinstance(detections, DetectionsMap_Cls) or all([isinstance(detection, Detection_AbstCls) for detection in detections])
        
        mask = self.getBlankMaskArray(referenceArray)
    
        for detection in detections:
            mask.addRegion(detection.getShape())
        
        return mask

    
    def getClassId_2_MaskDict(self, referenceArray, detectionsMap):
        
        assert isinstance(detectionsMap, DetectionsMap_Cls)
        
        classId_2_detections_dict = detectionsMap.getDetectionsPerClassDict()
        
        output_dict = {}
        
        for classId in classId_2_detections_dict:
            
            output_dict[classId] = self.getMaskOfDetections(referenceArray, classId_2_detections_dict[classId])

        
        return output_dict

    