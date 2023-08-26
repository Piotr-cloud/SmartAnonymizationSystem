'''
Created on 19 gru 2020

@author: piotr
'''
import os
from Detections.Detection import Detection_AbstCls, BoundingBox_Cls,\
    detectionClasses_IDs


class DetectionsMap_Cls():
    
    detectionsFileExtension = "txt"
    
    _Dump_DetectionsSplitSign = "\n"
    _Dump_ValuesSplitSign = " "
    
    def __init__(self, initDetectionsList = None, detectionsFilePath = None):
        
        self._classId2DetectionsList_dict = {}
        self._detections_list = []
        self._onlyBoundingBoxes = True
    
        self._classesDetected_set = set()
        
        if detectionsFilePath is not None:
            self.deserializeFromFile(detectionsFilePath)
        
        if initDetectionsList is not None:
            for initDetection in initDetectionsList:
                self.addDetection(initDetection)


    def __iter__(self):
        
        for detection in self._detections_list:
            yield detection
    

    def __getitem__(self, key_):
        return self._detections_list[key_]
    
    
    def __len__(self):
        return len(self._detections_list)
    
    
    def __bool__(self):
        return bool(self._detections_list)
    
    
    def __add__(self, other):
        
        if isinstance(other, DetectionsMap_Cls):
            detectionsList = other.getDetections()
        
        elif isinstance(other, Detection_AbstCls):
            detectionsList = [other]
        
        else:
            raise TypeError("Unsupported type")
        
        detectionsList = self.getDetections() + detectionsList
        
        return DetectionsMap_Cls(initDetectionsList = detectionsList)
    
    
    def containsOnlyBoundingBoxes(self):
        return self._onlyBoundingBoxes
    
    
    def getLongestEdgeExposition(self):
        greatestExposition = 0.0
        
        for detection in self._detections_list:
            detectionGreatestExposition = detection.getLongestEdgeExposition()
            greatestExposition = max([detectionGreatestExposition, greatestExposition])
        
        return greatestExposition
    
    
    def getClassesDetected(self):
        return self._classesDetected_set.copy()
    
    
    def getNonTrackedDetectionsMap(self):
        
        detections_list = []
        
        for detection in self._detections_list:
            if detection.isObjectNotAssigned():
                detections_list.append(detection)
        
        return DetectionsMap_Cls(initDetectionsList = detections_list)
        
    
    def getDetectionsMapOfSpecificClass(self, classID):
        
        if classID in self._classId2DetectionsList_dict:
            return DetectionsMap_Cls(initDetectionsList = self._classId2DetectionsList_dict[classID])
        else:
            return DetectionsMap_Cls(initDetectionsList = [])
    
    def getDetectionsMapOfSpecificClasses(self, classIDs):
        
        initDetectionsList = []
        
        for classID in classIDs:
            if classID in self._classId2DetectionsList_dict:
                initDetectionsList.extend(self._classId2DetectionsList_dict[classID])
        
        return DetectionsMap_Cls(initDetectionsList = initDetectionsList)
        
    
    
    def getDetections(self):
        return self._detections_list.copy()
    
    
    def getDetectionsPerClassDict(self):
        return {classId: detections.copy() for classId, detections in self._classId2DetectionsList_dict.items()}
    
    
    def addDetection(self, detection):
        
        assert isinstance(detection, Detection_AbstCls)
        
        detectionClassId = detection.class_
        
        if detectionClassId not in self._classId2DetectionsList_dict: 
            self._classId2DetectionsList_dict[detectionClassId] = []
            self._classesDetected_set.add(detectionClassId)
            
        if detection not in self._classId2DetectionsList_dict[detectionClassId]:
            
            if not isinstance(detection, BoundingBox_Cls):
                self._onlyBoundingBoxes = False
                
            self._classId2DetectionsList_dict[detectionClassId].append(detection)
            self._detections_list.append(detection)
    
    
    def getPair_anonymizationWithSwapDetections_and_restOfDetections(self):
        
        swapAnonymization_detectionsList = []
        nonSwapAnonymization_detectionsList = []
        
        for detection in self._detections_list:
             
            assignedObject = detection.getObject()
             
            if assignedObject and assignedObject.isAtAnonymizedState():
                swapAnonymization_detectionsList.append(detection)
            else:
                nonSwapAnonymization_detectionsList.append(detection)
        
        return DetectionsMap_Cls(swapAnonymization_detectionsList), DetectionsMap_Cls(nonSwapAnonymization_detectionsList)
    

    def getObjects(self):
        
        objects_set = set()
        
        for detection in self._detections_list:
            detection_object = detection.getObject()
            
            if detection_object is not None:
                objects_set.add(detection_object)
        
        return objects_set
    
    
    def _getIfInt(self, value):
        
        try:
            return int(value)
        except:
            raise ValueError("Int rounding issue")
    
    
    def _getIfFloatsList(self, values):
        
        output_list = []
        
        for val in values:
            output_list.append(float(val))
        
        return output_list
    
    
    def deserialize(self, inputString):
        
        assert isinstance(inputString, str)
        
        detectionsRepr_list = inputString.split(DetectionsMap_Cls._Dump_DetectionsSplitSign)
        
        for detectionRepr in detectionsRepr_list:
            
            if detectionRepr:
                detectionValues = detectionRepr.split(DetectionsMap_Cls._Dump_ValuesSplitSign)
                
                classID = self._getIfInt(detectionValues[0])
                detectionID = self._getIfInt(detectionValues[1])
                shapeRawParams = self._getIfFloatsList(detectionValues[2:])
            
                if detectionID in detectionClasses_IDs:
                    
                    detectionClass = detectionClasses_IDs[detectionID]
                    
                    shapeParams = detectionClass.detectionShape.unpackShapeParams(1, shapeRawParams) # reformat data before passing to constructor
                    detection = detectionClass(classID, *shapeParams)
                    
                    self.addDetection(detection)
        
    
    def deserializeFromFile(self, filePath):
        
        assert isinstance(filePath, str)
        assert os.path.exists(filePath)
        
        output_ = None
        
        extension = os.path.splitext(filePath)[1][1:]
        
        if extension == DetectionsMap_Cls.detectionsFileExtension:
            
            with open(filePath, "r") as file:
                fileContents = file.read()
            
            output_ = self.deserialize(fileContents)
                        
        return output_
    
    
    def serialize(self):
        
        detectionsRepr_list = []
    
        if self._classId2DetectionsList_dict:
            
            for detectionClassID in self._classId2DetectionsList_dict:
                
                for detection in self._classId2DetectionsList_dict[detectionClassID]:
                    detectionsRepr_list.append(DetectionsMap_Cls._Dump_ValuesSplitSign.join([str(el) for el in detection.getDetectionParams()]))
            
            return DetectionsMap_Cls._Dump_DetectionsSplitSign.join(detectionsRepr_list)
        
        return None
    
    
    def serializeToFile(self, directory, fileBaseName):
        
        directory = str(directory)
        
        if not os.path.exists(directory):
            raise NotADirectoryError("Dirrectory does not exist: " + directory)
        
        
        fileContents = self.serialize()
        
        if fileContents is not None:    
            newFilePath = os.path.join(directory, fileBaseName + "." + DetectionsMap_Cls.detectionsFileExtension)
             
            with open(newFilePath, "w") as newFile:
                newFile.write(fileContents)
        

if __name__ == "__main__":
    
    from NonPythonFiles import otherDebugFiles_dir
    
    directory_ = otherDebugFiles_dir
    
    if not directory_.exists():
        os.makedirs(str(directory_))
     
    detection = BoundingBox_Cls(class_ = 0, left = 0.1, top = 0.2, right = 0.3, bottom = 0.4)
      
    detections = DetectionsMap_Cls(initDetectionsList = [detection])
      
    detections.serializeToFile(directory_, "DetectionsMap_1")


    detections = DetectionsMap_Cls(detectionsFilePath = os.path.join(directory_, "DetectionsMap_1.txt"))

    detections.addDetection(detection)
    detections.serializeToFile(directory_, "DetectionsMap_2")




