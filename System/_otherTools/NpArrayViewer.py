'''
Created on Feb 11, 2022

@author: piotr
'''
import cv2
import numpy as np
from pathlib import Path
import os
import shutil
from Annotator.Annotator import Annotator_Cls
from PolymorphicBases.Decorators import singleton
from NonPythonFiles import npArrayDebugDisplay_defaultOutputFile,\
    npArrayDebugDisplay_defaultBulkDumpFolder
from Space._2D.Image import RAM_Image_Cls



@singleton
class __NpArrayOperator_Cls():
    
    def __init__(self):
        
        self._annotator = Annotator_Cls()
        self._defaultOutputFile = npArrayDebugDisplay_defaultOutputFile
        self._defaultBulkDumpFolder = npArrayDebugDisplay_defaultBulkDumpFolder
        
        self._saveIndex = 0
        
    
    def clearWindows(self):
        cv2.destroyAllWindows()
    
    
    def save(self, nparray):
        
        self.saveWithID(nparray, "saved")
    
    
    def saveWithID(self, nparray, id_, addIdx = True):
        
        id_ = str(id_)
        
        if addIdx:
            self._saveIndex += 1
            id_ = str(self._saveIndex) + "_" + id_
            
        self._save(nparray, str(self._defaultOutputFile / id_))
    
    
    def dumpAllNpArraysOfDict(self, variables_dict):
        
        directory_ = Path(__file__).parent / self._defaultDumpFolder
        
        if directory_.exists():
            shutil.rmtree(directory_)
            
        os.mkdir(directory_)
        
        for attr_name in variables_dict:
            attr = variables_dict[attr_name]
            
            if isinstance(attr, np.ndarray):
                try:
                    self._save(attr, self._defaultDumpFolder + "/" + str(attr_name))
                except:
                    pass
    
    
    def _getRegion(self, detectionView, additionalSurroundings_perc = None):
        
        from SpaceSpecificProcessor._2D.ArrayProcessor import ArraySpecificProcessor_Cls
        return ArraySpecificProcessor_Cls().getDetectionViewAsRectangleArray(detectionView, additionalSurroundings_perc)
    
    
    def _save(self, nparray, filePath):
        
        filePath = Path(filePath)
        
        if not filePath.is_absolute():
            filePath = Path(__file__).parent / filePath
        
        dir_ = filePath.parent
        
        if not dir_.exists():
            os.makedirs(str(dir_))
        
        filePath = str(filePath)
        
        if not filePath.endswith(".jpg"):
            filePath += ".jpg"
        
        cv2.imwrite(filePath, nparray)
        
        print("Saved to: " + filePath)
        
    
    def view(self, nparray):
        """
        Not recommended
        """
        
        cv2.imshow("Numpy array ", nparray)
        cv2.waitKey(0) # why this is needed ? I don't know. Setting argument to 0 causes no frame display window show
    
    
    def drawVertexes(self, nparray, shape, color = (0,0,255), addNumbers = False):
        
        return self._annotator._drawVertexes(RAM_Image_Cls(nparray[:], "None"), shape, color = color, addNumbers = addNumbers).getNpArrayCopy()
        
        
        
    def annotateDetection(self, view):
        
        return self._annotator._annotate(view.getArrayCopy(), [view.getDetection()])
        


viewer = __NpArrayOperator_Cls()



