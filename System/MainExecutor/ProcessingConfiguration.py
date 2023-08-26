'''
Created on Nov 2, 2021

@author: piotr
'''
from ObjectsDetectable.Classes import ClassIDs, ClassName_dict
from Detector.Detector import Detector_AbstCls
from Tracker.Tracker import Tracker_AbstCls
from TrackStabilizer.TrackStabilizer import TrackStabilizer_AbstCls
from Anonymizer.Anonymizer import Anonymizer_AbstCls
import time




class ProcessingConfiguration_Cls():

    def __init__(self, 
            classesServiced_list, 
            detectorsConstruction_dict,
            trackersConstruction_dict,
            stabilizersConstruction_dict,
            anonymizersConstruction_dict,
            annotatorConstruction,
            originDecisionsCfgDict = None):
        
        """
        construction dicts are the form of {workerConstructionObject/None : [classesIds]} 
        """
        
        self._classesServiced_list = []
        
        for classId in classesServiced_list:
            assert classId in ClassIDs
            assert classId not in self._classesServiced_list #just in case
            self._classesServiced_list.append(classId)
        
        
        self._constructionsDicts_dict = {
            
            Detector_AbstCls          : detectorsConstruction_dict,
            Tracker_AbstCls           : trackersConstruction_dict,
            TrackStabilizer_AbstCls   : stabilizersConstruction_dict,
            Anonymizer_AbstCls        : anonymizersConstruction_dict
            
            }
        
        self.validateConstructionsDict()
        
        self._processingFlags_dict   =  self._defineProcessingFlags()
        
        self._annotatorConstruction      =  annotatorConstruction
        self._annotatorProcessing_flag   =  any([anonymizer  is     None for anonymizer  in  self._constructionsDicts_dict[Anonymizer_AbstCls]])
        
        
        assert originDecisionsCfgDict is None or isinstance(originDecisionsCfgDict, dict)
        
        self._originDecisionsCfgDict = originDecisionsCfgDict
        self._processingID = str(int(time.time()))
    
    
    def validateConstructionsDict(self):
        
        if all([workerCls is None for workerCls in self._constructionsDicts_dict[Detector_AbstCls]]):
            raise ValueError("Nothing to detect! Choose at least one detector!")
        
        for workerGenericClass, constructionDict in self._constructionsDicts_dict.items():
            
            for constructionObj, classesIds in constructionDict.items():
                
                assert all([classId in ClassIDs for classId in classesIds]), "Classes to process are undefined"
                
                if constructionObj is not None:
                    assert issubclass(constructionObj.getWorkerCls(), workerGenericClass), "Provided worker class is not in a subclass of group parent class"
    
    
    def _defineProcessingFlags(self):
        
        output_dict = {}
        
        for workerGenericClass, constructionDict in self._constructionsDicts_dict.items():
            output_dict[workerGenericClass] = any([workerCls is not None for workerCls in constructionDict])
            
        
        return output_dict
    
    
    
    def getProcessingID(self):
        return self._processingID

    def getOriginDecisionsCfgDict(self):
        return self._originDecisionsCfgDict
    
    
    def getDetectorsConstructionDict(self):
        return self._constructionsDicts_dict[Detector_AbstCls].copy()

    def getTrackersConstructionDict(self):
        return self._constructionsDicts_dict[Tracker_AbstCls].copy()

    def getStabilizersConstructionDict(self):
        return self._constructionsDicts_dict[TrackStabilizer_AbstCls].copy()
    
    def getAnonymizersConstructionDict(self):
        return self._constructionsDicts_dict[Anonymizer_AbstCls].copy()
    
    def getAnnotatorConstruction(self):
        return self._annotatorConstruction
    
    
    def getBasicParams(self, video_flag = True):
        
        def getBasicParamsOfWorkerClass(workerBaseClass):
            
            outputParams_list = []
            
            classId_2_processingParamsList_dict = {}
            
            if self._processingFlags_dict[workerBaseClass]:
            
                workerGenericName = workerBaseClass.getWorkerGenericName()
                
                for constructionObj, classIds in self._constructionsDicts_dict[workerBaseClass].items():
                    for classId in classIds:
                        if classId not in classId_2_processingParamsList_dict:
                            classId_2_processingParamsList_dict[classId] = []
                        
                        classId_2_processingParamsList_dict[classId].append(
                            (ClassName_dict[classId] + " " + workerGenericName, str(constructionObj) if constructionObj is not None else "-")
                            ) 
            
            for outputParamsPart in classId_2_processingParamsList_dict.values():
                outputParams_list.extend(outputParamsPart)
                
            return outputParams_list
            
            
        outputParams_list = []
        
        outputParams_list.extend(getBasicParamsOfWorkerClass(Detector_AbstCls))
        
        if video_flag:
            outputParams_list.extend(getBasicParamsOfWorkerClass(Tracker_AbstCls))
            outputParams_list.extend(getBasicParamsOfWorkerClass(TrackStabilizer_AbstCls))
            
        outputParams_list.extend(getBasicParamsOfWorkerClass(Anonymizer_AbstCls))
        
        
        return outputParams_list
    
    
    def getDetectionFlag(self):
        return self._processingFlags_dict[Detector_AbstCls]
    
    def getTrackingFlag(self):
        return self._processingFlags_dict[Tracker_AbstCls]
    
    def getStabilizationFlag(self):
        return self._processingFlags_dict[TrackStabilizer_AbstCls]
    
    def getAnonymizationFlag(self):
        return self._processingFlags_dict[Anonymizer_AbstCls]
    
    def getAnnotationFlag(self):
        return self._annotatorProcessing_flag
    
    
    def getClassesServiced(self):
        return self._classesServiced_list.copy()
    
    def defineClasses(self):
        return [ classId for classId in self._classId2Detector_dict if self._classId2Detector_dict[classId] is not None]
    
    def loadDetectors(self, classId2Detector_dict):
        
        for classId in classId2Detector_dict:
            assert classId in ClassIDs
            
            detector = classId2Detector_dict[classId]
            
            if detector is not None:
                self._validateDetector(detector, classId)
                
        return classId2Detector_dict
    
    
    def _reverseDictOfWorkersMapping(self, workers_dict):
        """
        Reversing is done to force input format where only one worker per class is possible 
        """
        
        new_dict = {}
        
        for classId in workers_dict:
            worker = workers_dict[classId]
            
            if worker not in new_dict:
                new_dict[worker] = []
            
            new_dict[worker].append(classId)
        
        return new_dict
    
    
    def _validateDetector(self, detector, classId):
        
        assert issubclass(detector, Detector_AbstCls)
        
    
    def loadAnonymizers(self, classId2Anonymizer_dict):
        
        anonymizers_dict_new = {}
        
        for classId in classId2Anonymizer_dict:
            
            assert classId in ClassIDs
            
            if classId not in self._classId2Detector_dict: # class is not under detection so no need to process it anyhow 
                continue
            
            anonymizer = classId2Anonymizer_dict[classId]
            detector = self._classId2Detector_dict[classId]
            
            className = ClassIDs[classId]
            
            if anonymizer is not None and detector is None:
                
                print("Warning: Anonymizer of " + className + " (\"" + anonymizer.getName(None) + "\") is ignored due to missing detector")
                
            else:
                if anonymizer is not None:
                    self._validateAnonymizer(anonymizer, classId)
                    
                    anonymizers_dict_new[classId] = anonymizer
        
        for classId in self._classId2Detector_dict:
            if classId not in anonymizers_dict_new:
                anonymizers_dict_new[classId] = None
                
        return anonymizers_dict_new
    
    
    def _validateAnonymizer(self, anonymizer, classId):
        
        classId # unused
        assert issubclass(anonymizer, Anonymizer_AbstCls)


    
    def _validateTracker(self, tracker):
        
        if tracker is not None:
            if not issubclass(tracker, Tracker_AbstCls):
                raise TypeError("Tracker " + str(tracker) + " is not recognized")
            
        return tracker











