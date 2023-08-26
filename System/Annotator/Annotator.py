'''
Created on 16 sty 2021

This file contains annotator implementation.

@author: piotr
'''
import random
import numpy as np
import cv2

from Detections.Detection import Detection_AbstCls
from Space._2D.Shapes.Box import BoxShape_Cls
from Space._2D.Shapes.Polygon import PolygonShape_Cls
from ObjectsDetectable.Classes import ClassIDs
from PolymorphicBases.Worker import Worker_AbstCls

from Space._2D.Image import Image_Cls, RAM_Image_Cls
import binascii
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Int_Limited,\
    UserCfg_Bool, UserCfg_Int
from PolymorphicBases.ABC import final
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj
from SW_Licensing.SW_License import HostSWLicense_Cls
import math




class Annotator_Cls(Worker_AbstCls):
    """
    Annotator is the worker that takes image and detections and writes detections on the image then new image is produced
    """   
    @staticmethod
    def getName():
        return "UniversalImageAnnotator"
        
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Annotator"
        
    @staticmethod
    def getJobName():
        return "Annotation"
        
    @staticmethod
    def getDescription():
        return "Annotates detections on images by drawing colored area border. Non AI. Open-cv based"
        
    @staticmethod
    def getClassesServiced():
        return "All"
    
    @final
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    
    def __init__(self,
                 
                 blackColorSaturationLimit  =  UserCfg_Int_Limited(
                     lower_limit = 0,
                     defaultValue = 100,
                     upper_limit = 100,
                     name = "Black color saturation limit",
                     description = "Black color saturation limit"),
                 
                 blackColorValueLimit  =  UserCfg_Int_Limited(
                     lower_limit = 0,
                     defaultValue = 100,
                     upper_limit = 100,
                     name = "Black color value limit",
                     description = "Black color value limit"),
                 
                 blackColor_R  =  UserCfg_Int_Limited(
                     lower_limit = 0,
                     defaultValue = 0,
                     upper_limit = 255,
                     name = "Black color comp. RED",
                     description = "Black color red component value"),
                 
                 blackColor_G  =  UserCfg_Int_Limited(
                     lower_limit = 0,
                     defaultValue = 0,
                     upper_limit = 255,
                     name = "Black color comp. GREEN",
                     description = "Black color green component value"),
                 
                 blackColor_B = UserCfg_Int_Limited(
                     lower_limit = 0,
                     defaultValue = 0,
                     upper_limit = 255,
                     name = "Black color comp. BLUE",
                     description = "Black color blue component value"),
                 
                 borderThickness = UserCfg_Int_Limited(
                     lower_limit = 1,
                     defaultValue = 2,
                     upper_limit = 255,
                     name = "Line thickness",
                     description = "Tkickness of lines that surround the detection area"),
                 
                 colorBasedOnObjIdVal_flag = UserCfg_Bool(
                     name = "Color related to object ID",
                     description = "Flag whether color is assigned based on color ID",
                     defaultValue = True),
                 
                 hashSeed = UserCfg_Int(
                     name = "Color random seed", 
                     description = "random set of colors mapping can be chosen here", 
                     defaultValue = 6) 
                 ):
        
        # Resolve worker arguments in case of direct use(skipping dynamic configuration mechanism)
        
        Worker_AbstCls.__init__(self)
        
        self._blackColorSaturationLimit = self.resolveArgument(blackColorSaturationLimit)
        self._blackColorValueLimit = self.resolveArgument(blackColorValueLimit)
        self._blackColor_R = self.resolveArgument(blackColor_R)
        self._blackColor_G = self.resolveArgument(blackColor_G)
        self._blackColor_B = self.resolveArgument(blackColor_B)
        self._borderThickness = self.resolveArgument(borderThickness)
        self._colorBasedOnObjIdVal_flag = self.resolveArgument(colorBasedOnObjIdVal_flag)
        self._hashSeed = self.resolveArgument(hashSeed)
        
        self.__classIDsKnown = list(ClassIDs)
        
        self._requestedLabelsColor_RGB = None
        self._colors_objectsIdsCache = {classID: {} for classID in self.__classIDsKnown}
        self._colors_classesRanges = {} # classId : ( range_start, range_end, middle )
        self._calculateDefaultColorsAndRanges()
    
    
    
    def _addClassIDColor(self, classId, hue_start, hue_end):
        
        hue_middle = (hue_end + hue_start) / 2
        
        self._colors_classesRanges[classId] = (hue_start, hue_end, hue_middle)
        
        
    def _calculateDefaultColorsAndRanges(self):
        
        angleMax = 180.0
        
        hue_step = angleMax / len(self.__classIDsKnown)
        
        rangeStart = 0.0
        rangeEnd = 0.0
        
        for classId in self.__classIDsKnown:
            rangeEnd += hue_step * 2 / 3 # to keep boundary hue :  2/3  |=1/3=|  2/3  |=1/3=|
            
            self._addClassIDColor(classId, hue_start = int(rangeStart), hue_end = int(rangeEnd))
            
            rangeStart += hue_step
     
    
    def setConstantColorOfLabels(self, labelsColor_RGB = None):
        
        assert labelsColor_RGB is None or (len(labelsColor_RGB) == 3 and hasattr(labelsColor_RGB, "__iter__"))
        
        self._requestedLabelsColor_RGB = labelsColor_RGB
    
    
    def getHashValOfInt(self, intVal, lowerLimit, upperLimit, seed = 0):
                                
        intVal_limited = intVal % 65535
        hash_val = binascii.crc32(intVal_limited.to_bytes(2, 'big'), seed + self._hashSeed)
        
        hash_limited_val = int(lowerLimit + hash_val % (upperLimit - lowerLimit))
        
        return hash_limited_val
    
    
    def getRGBColorOfDetection(self, detection):
        
        if self._requestedLabelsColor_RGB is None:
            
            detectionClassId = detection.class_
            
            if detectionClassId in ClassIDs:
                
                objId = detection.getObjectID() # take color from the middle
                
                if objId not in self._colors_objectsIdsCache[detectionClassId]:
                    
                    if objId is None:
                        
                        saturation = 255
                        value = 255
                        hue = self._colors_classesRanges[detectionClassId][2]
                        
                    else:
                        
                        if self._colorBasedOnObjIdVal_flag:
                            
                            hue_fromVal  =  self._colors_classesRanges[detectionClassId][0]
                            hue_toVal    =  self._colors_classesRanges[detectionClassId][1]
                            
                            hue         =  self.getHashValOfInt(objId, hue_fromVal, hue_toVal, seed = 0)
                            saturation  =  self.getHashValOfInt(objId, self._blackColorSaturationLimit, 256, seed = 1)
                            value       =  self.getHashValOfInt(objId, self._blackColorValueLimit, 256, seed = 2)
                            
                        else:
                        
                            saturation  =  random.randint(self._blackColorSaturationLimit, 256)
                            value       =  random.randint(self._blackColorValueLimit, 256)
                            
                            hue = random.randint(
                                self._colors_classesRanges[detectionClassId][0],
                                self._colors_classesRanges[detectionClassId][1]
                                )
                        
                    self._colors_objectsIdsCache[detectionClassId][objId] = [int(val) for val in cv2.cvtColor(np.uint8([[[hue, saturation, value]]]), cv2.COLOR_HSV2RGB)[0][0]]
                
                return self._colors_objectsIdsCache[detectionClassId][objId]
                
            else:
                return self._blackColor_RGB  # Black
            
        else:
            return self._requestedLabelsColor_RGB
    
    
    def _drawVertexes(self, image, shape, color = (0, 0, 255), addNumbers = True):
        
        nparray = image.getNpArrayCopy()
        
        points = shape.getPoints()
        
        radius = math.ceil(sum(nparray.shape[:2]) / 300)
        
        for idx, point in enumerate(points):
            
            x_rel, y_rel = point.getCoords()
            
            coords = (int(x_rel * nparray.shape[1]), int(y_rel * nparray.shape[0]))
            cv2.circle(nparray, coords, radius, color, thickness = -1)
            
            if addNumbers:
                thickness = int(radius / 4)
                self._drawTextToImage(nparray, text = str(idx), left = coords[0] + int(thickness / 2), top = coords[1], color = color, thickness = thickness)
        
        return RAM_Image_Cls(nparray, image.getOriginFilePath())
        

    @final
    def annotate(self, image, detections):
        
        if detections:
            
            with workersPerformanceLoggerObj.startContext_executuion(self):
            
                nparray = image.getNpArrayCopy()
                
                nparray_new = self._annotate(nparray, detections)
                
                return RAM_Image_Cls(nparray_new, image.getOriginFilePath())

        else:
            
            assert isinstance(image, Image_Cls)
            
            return image


    def _annotate(self, nparray, detections):
        """
        In-place operation
        """
        
        for detection in detections:
            
            assert isinstance(detection, Detection_AbstCls)
            
            labelColor = self.getRGBColorOfDetection(detection)
            
            self._annotateWithColor(nparray, detection, labelColor)
            
        return nparray
    
    
    def _drawTextToImage(self, nparray, text, left, top, color, thickness):
            
        pt1 = (left, top)
        
        text_size = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_PLAIN, thickness, 1)

        center = pt1[0] + 5, pt1[1] + 5 + text_size[0][1]
        pt2 = pt1[0] + 10 + text_size[0][0], pt1[1] + 10 + \
            text_size[0][1]
        cv2.rectangle(nparray, pt1, pt2, color, -1)
        cv2.putText(nparray, text, center, cv2.FONT_HERSHEY_PLAIN,
                    thickness, (255, 255, 255), thickness)
    
    
    def _annotateShapeWithColor(self, nparray, shape, color, thickness):
            
        if isinstance(shape, BoxShape_Cls):
            
            left, top      =  shape.TL_point.getAbsoluteCoords(*nparray.shape[:2])
            right, bottom  =  shape.BR_point.getAbsoluteCoords(*nparray.shape[:2])
            
            cv2.rectangle(nparray, (left, top), (right, bottom), color, thickness)
            
        elif isinstance(shape, PolygonShape_Cls):
            points = shape.getPoints()
            vertexes = np.array([list(point.getAbsoluteCoords(*nparray.shape[:2])) for point in points])
            
            cv2.polylines(nparray, [vertexes], True, color, thickness)
        
        else:
            print("Shape class: " + str(type(shape).__name__) + " is not supported!")
        
    
    def _annotateWithColor(self, nparray, detection, color):
        
        shape = detection.shape
        
        self._annotateShapeWithColor(nparray, shape, color, self._borderThickness)
        
        # Draw object id rectangle
        objId = detection.getObjectID()
        
        if objId is not None:
            
            objId_str = "id: " + str(objId)
            left, top, _, _ = detection.shape.getExtremumCoordinatesAbsolute(*nparray.shape[:2])[0]
            
            #cv2.putText(nparray, "id: " + str(objId), (left, top), fontFace = cv2.FONT_HERSHEY_COMPLEX, fontScale = 1.5, color = labelColor)

            text_thickness = max([int(self._borderThickness / 3), 1])
            
            self._drawTextToImage(nparray, text = objId_str, left = left, top = top, color = color, thickness = text_thickness)








