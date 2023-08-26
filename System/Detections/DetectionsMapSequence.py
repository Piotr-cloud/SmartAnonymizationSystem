'''
Created on Sep 8, 2021

@author: piotr
'''
from Detections.DetectionsMap import DetectionsMap_Cls
from Space._2D_p_time.Video import Video_AbstCls




class DetectionsMapSequence_Cls():
    """
    Shall keep tracks and single detections for each frame 
    """
    
    def __init__(self, init_detectionMaps_list = None, imagesSequenceRelated = None):
        
        self.currentDetectionMap_list = []
        
        self.detectionsMaps_list = []
        
        self._classesDetected_set = set()
        
        if hasattr(init_detectionMaps_list, "__iter__"):
            for detectionMap in init_detectionMaps_list:
                self.addFrameDetectionMap(detectionMap)
        
        assert isinstance(imagesSequenceRelated, Video_AbstCls) or imagesSequenceRelated is None
        
        self._imagesSequenceRelated = imagesSequenceRelated
    
    
    def getObjects(self):
        """
        Returns objects that are assigned to detections
        """
        objects_set = set()
        
        for detectionMap in self.detectionsMaps_list:
            objects_set.update(detectionMap.getObjects())
        
        return objects_set
    
    
    def getObjectsOfSpecificClasses(self, classesIds):
        
        objects_set = set()
        
        for detectionMap in self.detectionsMaps_list:
            objects_set.update( detectionMap.getDetectionsMapOfSpecificClasses(classesIds).getObjects() )
        
        return objects_set
    
    
    def __iter__(self):
        
        for detectionMap in self.detectionsMaps_list.copy():
            yield detectionMap
    
    
    def __len__(self):
        return len(self.detectionsMaps_list)
    
    
    def __getitem__(self, index):
        
        if index >= len(self):
            raise IndexError("Index out of range")
        
        return self.detectionsMaps_list[index]
    
    
    def getClassesDetected(self):
        return list(self._classesDetected_set)
    
    
    def addFrameDetectionMap(self, detectionsMap):
        
        assert detectionsMap is None or isinstance(detectionsMap, DetectionsMap_Cls)
        self.detectionsMaps_list.append(detectionsMap)
    
        self._classesDetected_set.update(detectionsMap.getClassesDetected())


    def getDetectionMapSequenceOfSpecificClasses(self, classesIds):
        return self
        raise





