'''
Created on 9 sty 2021

@author: piotr
'''

from ObjectsDetectable.Classes import ClassIDs
from PolymorphicBases.Worker import Worker_AbstCls
from PolymorphicBases.ABC import abstractmethod, final
from ObjectsDetectable.ClassesCfg import ClassName_dict
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj
from Detections.DetectionsMap import DetectionsMap_Cls


class Detector_AbstCls(Worker_AbstCls):
    
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Detector"
    
    
    def __init__(self):
        
        assert type(self) != Detector_AbstCls
        self._detectableClasses = self.getClassesServiced_resolved()
    
    
    @final
    def detectClass(self, img, classId):
        """
        This function shall return DetectionMap_Cls
        This is a specific case of detect method checking 
        """
            
        if classId not in self._detectableClasses:
            raise RuntimeError("Detector does not detect class: " + str(ClassIDs[classId]))
        
        detections = self.detect(img)
        
        if {classId} != detections.getClassesDetected(): # Filter results ?
            detections = detections.getDetectionsMapOfSpecificClass(classId)
            
        
        return detections
    
    
    @final
    def detectClasses(self, img, classIds):
        
        for classId in classIds:
            if classId not in self._detectableClasses:
                raise RuntimeError("Detector does not detect class: " + str(ClassName_dict[classId]))
        
        with workersPerformanceLoggerObj.startContext_executuion(self):
            npArray = img.getNpArrayCopy()
            detections = self._detectClasses(npArray, classIds)
            del npArray
            
        return detections
        
        
        
    def _detectClasses(self, nparray, classIds):
        """
        This function can be overwritten if detection algorithm differs when detecting specific classes in ex. reduce number of computations when some classes are not needed
        """
        
        detectionsMap = self._detect(nparray)
        
        assert isinstance(detectionsMap, DetectionsMap_Cls), "return object of <detector>._detect() shall be and instance of DetectionsMap_Cls"
        
        if any([detectedClass not in self._detectableClasses for detectedClass in detectionsMap.getClassesDetected()]): # Filter results ?
            detectionsMap = detectionsMap.getDetectionsMapOfSpecificClasses(classIds)
        
        return detectionsMap
    
    @final
    def detect(self, img):
        
        with workersPerformanceLoggerObj.startContext_executuion(self):
            detections = self._detect(img.getNpArrayCopy())
        
        return detections


    @abstractmethod
    def _detect(self, nparray):
        """
        This function shall implement detection of classes and return DetectionMap_Cls obj
        """
        raise NotImplementedError()


    def getJobName(self):
        return "Detection"
    


