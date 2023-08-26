'''
Created on May 14, 2022

@author: piotr
'''

from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_AbstCls,\
    ConfigurationObject_Activatable_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls
from ObjectsDetectable.Classes import ClassesOrderProcessing_idsList,\
    ClassName_dict
from Configuration.ConfigurationObjects.WorkerConfiguration import WorkerConfigurationObject_Cls,\
    ChoiceOf_WorkerConfigurationObject_Cls,\
    StaticWorkerConfigurationObjectWrapper_Cls
    
from Detector.Detector import Detector_AbstCls
from Tracker.Tracker import Tracker_AbstCls
from TrackStabilizer.TrackStabilizer import TrackStabilizer_AbstCls
from Anonymizer.Anonymizer import Anonymizer_AbstCls

from Configuration.ConfigurationObjects.Choice import Choice_Cls,\
    ListOfChoices_Cls
from pathlib import Path
from PolymorphicBases.ABC import abstractmethod
import json

from NonPythonFiles import otherDebugFiles_dir
from Configuration.GUI.GUI_cfg import debug
from MainExecutor.ProcessingConfiguration import ProcessingConfiguration_Cls

from Configuration.ConfigurationObjects.WorkerConstruction import WorkerConstructionObject_Cls
import os
from Configuration.ConfigurationObjects.LoadingErrorCodes import Loading_FileDontExist,\
    Loading_PathNotAFile, Loading_WrongFileFormat, Loading_IgnoredDecisions,\
    Loading_NonImported, Loading_NoImportRequested



class StaticWorkersConfigurationManager_AbstCls(ConfigurationObject_AbstCls):
    
    
    def __init__(self, staticWorkersConf_list):
        
        assert type(self) != StaticWorkersConfigurationManager_AbstCls
        assert all([isinstance(staticWorkerConf, StaticWorkerConfigurationObjectWrapper_Cls) for staticWorkerConf in staticWorkersConf_list])
        self.staticWorkersConf_list = staticWorkersConf_list
    
    
    @abstractmethod
    def updateStaticWorkersConfiguration(self):
        pass



class ClassesProcessingConfiguration_Cls(StaticWorkersConfigurationManager_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls):
    
    def __init__(self, workersIncluder):
        
        self._classesCfg_dict = {}     
        
        self._annotatorCfgWrapper = StaticWorkerConfigurationObjectWrapper_Cls(
            self._convertWorkerTypeIntoWorkerCfg(workersIncluder.getAnnotator()), 
            self)
        
        options_dict = {}
        
        for classId in workersIncluder.getClassesServiced():
            classProcessingConfiguration = ClassProcessingConfiguration_Cls(classId = classId, workersIncluder = workersIncluder)
            self._classesCfg_dict[classId] = classProcessingConfiguration
            options_dict[ClassName_dict[classId]] = classProcessingConfiguration
            
        
        self._classesChoice = Choice_Cls(name = "Classes",
                                         description = "Choose what classes to process",
                                         optionsData_dict = options_dict,
                                         singleChoice_flag = False,
                                         activatable = False)
        
        self._configurationObjects_list = [
            self._classesChoice,
            self._annotatorCfgWrapper
            ]
    
        StaticWorkersConfigurationManager_AbstCls.__init__(self, [self._annotatorCfgWrapper])
        
        self.updateStaticWorkersConfiguration()
        
        self._cfgFilePath = None # cfg last loaded from/saved to this file
    
    def getClassesChoice(self):
        return self._classesChoice
    
    def _getClassesCfgDict(self):
        return self._classesCfg_dict.copy()
    
    
    def _getCfgDecisionsDict(self):
        
        self._addCfgDecisionDictElement(self._classesChoice.getName(), self._classesChoice.getCfgDecisionsDict())
        self._addCfgDecisionDict(self._annotatorCfgWrapper.getWorkerConfigurationObj().getCfgDecisionsDict())
            
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        classesChoice_name = self._classesChoice.getName()
        self._passPartOfCfgDecisionsDictToNextDecisionKeeper(classesChoice_name, cfgDecisionsDict, self._classesChoice)
        
        self._passCfgDecisionsDictToNextDecisionKeeper(cfgDecisionsDict, self._annotatorCfgWrapper.getWorkerConfigurationObj())
        
    
    def saveToFile(self, filePath, silent = False):
        """
        File shall serialize ClassesProcessingConfiguration_Cls object
        """
        filePath = Path(filePath).with_suffix(".json")
        
        if not filePath.parent.exists():
            os.makedirs(filePath.parent)
        
        # Annotator UserCfg_Bool("Color related to object ID") does not work, and Annotator maybe to hide if not needed?
        cfgDecisions_dict = self.getCfgDecisionsDict()
        
        with open(filePath, 'w') as f:
            json.dump(cfgDecisions_dict, f, indent=3)
        
        if not silent:
            print("Saving file: " + str(filePath))
            
        self._cfgFilePath = filePath
        
        if debug:
            with open(filePath, "r") as file_:
                print(file_.read())
    
    
    def loadFromFile(self, filePath):
        """
        File shall reflect ClassesProcessingConfiguration_Cls object
        
        Since ClassesProcessingConfiguration_Cls contains project options loading can be problematic, so:
        
        Returns: error values defined in Configuration.ConfigurationObjects.LoadingErrorCodes
        """
        
        if filePath:
            cfgFilePath = Path(filePath)
            
            if not cfgFilePath.exists():
                return Loading_FileDontExist
            
            elif not cfgFilePath.is_file():
                return Loading_PathNotAFile
            
            else:
                
                try:
                    with open(str(filePath)) as f:
                        cfgDecisions_dict = json.load(f)
                except:
                    return Loading_WrongFileFormat
                
                result = self.loadDecisionsFromCfgDict(cfgDecisions_dict)
                
                if cfgDecisions_dict:
                    self._addLoadingErrorCode(Loading_IgnoredDecisions)
                    print("The following params were not loaded: ", cfgDecisions_dict)
                    
                if result != Loading_NonImported:
                    self._cfgFilePath = cfgFilePath
                else:
                    self._cfgFilePath = None
                
                return result
            
            return Loading_NonImported
        
        else:
            return Loading_NoImportRequested
    
    
    def getConfigurationFilePath(self):
        return self._cfgFilePath
    
    
    def removeConfigurationFilePathReference(self):
        self._cfgFilePath = None
        
    
    def updateStaticWorkersConfiguration(self):
        self._updateAnnotatorCfg()
        
    
    def _updateAnnotatorCfg(self):
        
        annotator_shallActive = False
        
        for classChoiceObj in self._classesChoice:
            
            if classChoiceObj.isActive():
                
                classProcessingConfiguration = classChoiceObj.getValue()
                annonymizerChoice = classProcessingConfiguration.getAnnonymizerChoice()
                
                if not annonymizerChoice.isActive():
                    annotator_shallActive = True
                    break
                
        if annotator_shallActive:
            self._annotatorCfgWrapper.activate()
        else:
            self._annotatorCfgWrapper.deactivate()
    
    
    def getConfigurationObjects(self):
        return self._configurationObjects_list[:]
    
    
    def _convertWorkerTypeIntoWorkerCfg(self, workerType):
        wco = WorkerConfigurationObject_Cls(workerType)
        return wco
    
    
    def resolve(self):
        """
        Shall return ProcessingConfiguration_Cls object
        """
        classesServiced_list = []
        annotatorConstruction = WorkerConstructionObject_Cls(self._annotatorCfgWrapper.getWorkerConfigurationObj())
        
        workerType_constructionDict_dict = {
            Detector_AbstCls :  {},
            Tracker_AbstCls :   {},
            TrackStabilizer_AbstCls : {},
            Anonymizer_AbstCls : {}
            }
        
        for option in self._classesChoice.getActiveOptions():
            classProcessingConfiguration = option.getValue()
            
            classId = classProcessingConfiguration.getClassId()
            classesServiced_list.append(classId)
            
            workerBaseType_2_Choice_dict = classProcessingConfiguration.getWorkerBaseType2ChoiceDict()
            
            for workerBaseType in workerBaseType_2_Choice_dict:
                
                workerBaseTypeRelatedConstructionDict = workerType_constructionDict_dict[workerBaseType]
                
                classWorkerChoice = workerBaseType_2_Choice_dict[workerBaseType]
                
                constructionObj = None
                
                assert classWorkerChoice.isSingleChoiceFlag(), "Only single choice is implemented"
                
                if classWorkerChoice.isActive():
                    constructionObj = WorkerConstructionObject_Cls(classWorkerChoice.resolve())
                
                if constructionObj not in workerBaseTypeRelatedConstructionDict:
                    workerBaseTypeRelatedConstructionDict[constructionObj] = []
                
                workerBaseTypeRelatedConstructionDict[constructionObj].append(classId)
        
        originDecisionsCfgDict = self.getCfgDecisionsDict()
                
        return ProcessingConfiguration_Cls(
            classesServiced_list           = classesServiced_list, 
            detectorsConstruction_dict     = workerType_constructionDict_dict[Detector_AbstCls],
            trackersConstruction_dict      = workerType_constructionDict_dict[Tracker_AbstCls],
            stabilizersConstruction_dict   = workerType_constructionDict_dict[TrackStabilizer_AbstCls],
            anonymizersConstruction_dict   = workerType_constructionDict_dict[Anonymizer_AbstCls],
            annotatorConstruction          = annotatorConstruction,
            originDecisionsCfgDict         = originDecisionsCfgDict
            )
    
    
    def _convertWorkerChoice_2_LinesList(self, workerChoice, indentSize = 10):
        
        output_list = []
        
        assert isinstance(workerChoice, ChoiceOf_WorkerConfigurationObject_Cls)
        
        if isinstance(workerChoice, ClassWorkerChoice_Cls):
            wco = workerChoice.getChosen()
        else:
            wco = workerChoice.resolve()
    
        if wco is not None:
            assert isinstance(wco, WorkerConfigurationObject_Cls)
            
            output_list.append("\n" + " " * indentSize + (workerChoice.getName() + ": ").ljust(25) + wco.getWorkerClass().getName())
        
            for argument in wco._arguments:
                if isinstance(argument, ChoiceOf_WorkerConfigurationObject_Cls):
                    output_list.extend(self._convertWorkerChoice_2_LinesList(argument, indentSize + 5))
            
            
        return output_list
            
    
    def convertWorkerChoice_2_Str(self, workerChoice):
        
        return "".join(self._convertWorkerChoice_2_LinesList(workerChoice))
    
    
    def getStrRepr(self):        
        
        output_str = ""
        
        for option in self._classesChoice._options:
        #for classId, cpc in self._getClassesCfgDict().items():
            
            if option.isActive():
                
                cpc = option.getValue()
                classId = cpc.getClassId()
                className = ClassName_dict[classId]
                
                workerBaseType2ChoiceDict = cpc.getWorkerBaseType2ChoiceDict()
                
                output_str += "\nClass: " + className + " (" + str(classId) + ")\n"
                
                if workerBaseType2ChoiceDict[Detector_AbstCls].isActive():
                    output_str += self.convertWorkerChoice_2_Str(workerBaseType2ChoiceDict[Detector_AbstCls])
                
                if workerBaseType2ChoiceDict[Tracker_AbstCls].isActive():
                    output_str += self.convertWorkerChoice_2_Str(workerBaseType2ChoiceDict[Tracker_AbstCls])
                    
                if workerBaseType2ChoiceDict[TrackStabilizer_AbstCls].isActive():
                    output_str += self.convertWorkerChoice_2_Str(workerBaseType2ChoiceDict[TrackStabilizer_AbstCls])
                    
                if workerBaseType2ChoiceDict[Anonymizer_AbstCls].isActive():
                    output_str += self.convertWorkerChoice_2_Str(workerBaseType2ChoiceDict[Anonymizer_AbstCls])
                
                output_str += "\n"*2
        
        
        if not output_str:
            output_str = "No classes configured!"
            
        return output_str
    
    
    def __str__(self, short = False):
        
        if short:
            return "Configuration of classes: " + ", ".join([ClassName_dict[classId] for classId in self._classesCfg_dict])
        else:
            return self.getStrRepr()
    
    
    def __repr__(self):
        return str(self)

    
    def _viewProcessingGraphvizDiagram(self):
        pass



class ClassWorkerChoice_Cls(ChoiceOf_WorkerConfigurationObject_Cls, ConfigurationObject_Activatable_AbstCls):
    
    def __init__(self, 
                 name, 
                 description,
                 workersBaseType,
                 activatable):
        
        ChoiceOf_WorkerConfigurationObject_Cls.__init__(self, name, description, workersBaseType, singleChoice_flag = True)
        ConfigurationObject_Activatable_AbstCls.__init__(self, activatable)
    
    
    def getChosen(self):
        activeOptionInList = self.getActiveOptions()
        
        if not activeOptionInList:
            chosen = None
        else:
            assert len(activeOptionInList) == 1
            chosen = activeOptionInList[0].getValue()
            
        return chosen
            
    def __str__(self):
        return ConfigurationObject_Activatable_AbstCls.__str__(self) + ChoiceOf_WorkerConfigurationObject_Cls.__str__(self)



class ClassProcessingConfiguration_Cls(ListOfChoices_Cls, ConfigurationObject_AbstCls):
    
    def __init__(self, classId, workersIncluder):
        
        self._classId = classId
        
        className = ClassName_dict[self._classId]
        self._className = className
        
        if className[0].isupper():
            className = className[0].lower() + className[1:]
        
        self._detectorChoice      =   ClassWorkerChoice_Cls(name = "Detector", 
                                                            description = "Worker performing detections of " + className + " objects on frame",
                                                            workersBaseType = Detector_AbstCls,
                                                            activatable = False)
        
        self._trackerChoice       =   ClassWorkerChoice_Cls(name = "Tracker", 
                                                            description = "Worker performing tracking of " + className + " objects when detected in images sequence",
                                                            workersBaseType = Tracker_AbstCls,
                                                            activatable = True)
        
        self._stabilizerChoice    =   ClassWorkerChoice_Cls(name = "Stabilizer", 
                                                            description = "Worker performing track stabilization of " + className + " objects when detected in images sequence",
                                                            workersBaseType = TrackStabilizer_AbstCls,
                                                            activatable = True)
        
        self._annonymizerChoice   =   ClassWorkerChoice_Cls(name = "Anonymizer", 
                                                            description = "Worker performing anonymization of detected " + className + " objects on target frame",
                                                            workersBaseType = Anonymizer_AbstCls,
                                                            activatable = True)
        
        self._workerBaseType_2_choice_dict = {
            Detector_AbstCls : self._detectorChoice,
            Tracker_AbstCls : self._trackerChoice,
            TrackStabilizer_AbstCls : self._stabilizerChoice,
            Anonymizer_AbstCls : self._annonymizerChoice
            }
        
        self._detectorChoice.constructOptions(workersIncluder, classId)
        self._trackerChoice.constructOptions(workersIncluder, classId)
        self._stabilizerChoice.constructOptions(workersIncluder, classId)
        self._annonymizerChoice.constructOptions(workersIncluder, classId)
        
        ListOfChoices_Cls.__init__(self, [
            self._detectorChoice,
            self._trackerChoice,
            self._stabilizerChoice,
            self._annonymizerChoice
            ])
    
    
    def getWorkerBaseType2ChoiceDict(self):
        return self._workerBaseType_2_choice_dict.copy()
    
    
    def getClassId(self):
        return self._classId
    
    def __repr__(self): return str(self)
    
    def __str__(self):
        return "Configuration of processing the class: " + ClassName_dict[self._classId]
    
    def __lt__(self, other):   return ClassesOrderProcessing_idsList.index(self._classId) < ClassesOrderProcessing_idsList.index(other._classId)
    def __gt__(self, other):   return ClassesOrderProcessing_idsList.index(self._classId) > ClassesOrderProcessing_idsList.index(other._classId)
    
        
    def getAnnonymizerChoice(self):
        return self._annonymizerChoice



if __name__ == "__main__":
    
    from Configuration.integrationCfg import workersIncluder
    cpc = ClassesProcessingConfiguration_Cls(workersIncluder)
    
    filePath = otherDebugFiles_dir / "cpcDump.json"
    
    cpc.saveToFile(filePath)
    
    cpc._viewProcessingGraphvizDiagram()
    
        
    
    
    

