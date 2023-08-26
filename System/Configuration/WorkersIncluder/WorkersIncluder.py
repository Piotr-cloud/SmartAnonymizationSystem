'''
Created on May 7, 2022

@author: piotr
'''
from builtins import issubclass
import inspect
from PolymorphicBases.Worker import validateStaticMethodsDefinition
from PolymorphicBases.Decorators import singleton
from ObjectsDetectable.Classes import ClassName_dict


@singleton
class _WorkersIncluder_Cls(object):
    '''
    classdocs
    '''
    alreadyConstructed = False

    def __init__(self):
        '''
        Constructor
        '''        

        from PolymorphicBases.Worker import Worker_AbstCls
        from Annotator.Annotator import Annotator_Cls

        self._workerBaseClass = Worker_AbstCls
        self._annotator = Annotator_Cls # annotator although worker but non-derivable
        
        from Detector.Detector import Detector_AbstCls
        from Tracker.Tracker import Tracker_AbstCls
        from TrackStabilizer.TrackStabilizer import TrackStabilizer_AbstCls
        from Anonymizer.Anonymizer import Anonymizer_AbstCls
        
        from ContentGenerator.ContentGenerator import ContentGenerator_AbstCls
        from ContentSwapper.ContentSwapper import ContentSwapper_AbstCls
        from ContentRecognizer.ContentRecognizer import ContentRecognizer_AbstCls
        
        # Some workers do no make sense when others are missing, so here is the rule:
        self._rule_dependantWorker_2_dependeesWorkers_dict = {                          # Says what key worker makes possible to work others indicated by word - list
            Detector_AbstCls :         [Tracker_AbstCls, Anonymizer_AbstCls],                # No detection is made(no base input) so nothing to do
            Tracker_AbstCls :          [TrackStabilizer_AbstCls],                            # No track so no track stabilization possible
            Anonymizer_AbstCls:        [ContentGenerator_AbstCls, ContentSwapper_AbstCls],   # Contents generators and swappers work as a part of anonymizers
            ContentGenerator_AbstCls:  [ContentRecognizer_AbstCls],                          # Content recognizer works as a part of content generator
            }
        
        self._specializedWorkerBasesClasses_list = [
            Detector_AbstCls,
            Tracker_AbstCls,
            TrackStabilizer_AbstCls,
            Anonymizer_AbstCls,
            ContentGenerator_AbstCls,
            ContentRecognizer_AbstCls,
            ContentSwapper_AbstCls
            ]

        
        self._baseClass_2_aggregatingList_dict = {}
        
        for specializedWorkerBaseType in self._specializedWorkerBasesClasses_list:
            
            self._baseClass_2_aggregatingList_dict[specializedWorkerBaseType] = []
        
        self._classServicedIds_2_workerBaseClass_2_worksersClassesList = {}
        
        self._classesServiced = set()
        
        self._includingProcessOpened_flag = True
    
    
    def getSpecializedWorkerBaseClasses(self):
        return self._specializedWorkerBasesClasses_list[::]
    
    
    def _extendListWithUnique(self, listTo, listFrom):
        for el in listFrom:
            if el not in listTo:
                listTo.append(el)
    
    def endIncludingProcess(self):
        
        if self._includingProcessOpened_flag is not False:
            self._includingProcessOpened_flag = True
            
            classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict = {}
            
            # extend self._rule_dependantWorker_2_dependeesWorkers_dict due to obvious facts
            for dependantWorker in self._rule_dependantWorker_2_dependeesWorkers_dict:
                dependeeWorkers_list = self._rule_dependantWorker_2_dependeesWorkers_dict[dependantWorker]
                
                for dependeWorker in dependeeWorkers_list[:]:
                    if dependeWorker in self._rule_dependantWorker_2_dependeesWorkers_dict:
                        
                        self._extendListWithUnique(dependeeWorkers_list, self._rule_dependantWorker_2_dependeesWorkers_dict[dependeWorker])
        
            for classId in self._classServicedIds_2_workerBaseClass_2_worksersClassesList:
                workerBaseClass_2_worksersClassesList_dict = self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId]
                
                for workerBaseClass in list(workerBaseClass_2_worksersClassesList_dict.keys()):
                    
                    if workerBaseClass in workerBaseClass_2_worksersClassesList_dict:
                        
                        if not workerBaseClass_2_worksersClassesList_dict[workerBaseClass]:
                            if workerBaseClass in self._rule_dependantWorker_2_dependeesWorkers_dict:
                                for dependeeWorkerBaseClass in self._rule_dependantWorker_2_dependeesWorkers_dict[workerBaseClass]:
                                    if dependeeWorkerBaseClass in workerBaseClass_2_worksersClassesList_dict and workerBaseClass_2_worksersClassesList_dict[dependeeWorkerBaseClass]:
                                        
                                        if classId not in classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict:
                                            classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict[classId] = []
                                        
                                        self._extendListWithUnique(classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict[classId],
                                                                   [workerClassRemoved.getWorkerGenericName() + ": \"" + workerClassRemoved.getName() + "\" due to missing " + workerBaseClass.getWorkerGenericName() + "" 
                                                                     for workerClassRemoved in workerBaseClass_2_worksersClassesList_dict[dependeeWorkerBaseClass]] 
                                                                   )
                                        del workerBaseClass_2_worksersClassesList_dict[dependeeWorkerBaseClass] # delete workers what cannot do any job due to other workers missing
            
            
            # Reduce number of classes serviced
            for classId in list(self._classServicedIds_2_workerBaseClass_2_worksersClassesList.keys()):
                anyWorkerUsed = False
                
                for workerBaseClass in self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId]:
                    if self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId][workerBaseClass]:
                        anyWorkerUsed = True
                        break
                
                if anyWorkerUsed is False:
                    del self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId]
                    
            if classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict:
                print("\nWARNING: The following workers are not usable due to missing dependant workers(for ex. no detector to use tracker):")
                
                for classId in classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict:
                    
                    print("  Class: " + ClassName_dict[classId] + " (id: " + str(classId) + ")")
                    
                    for removalStatement in classId_2_removedWorkersStatementsDueToNoPossibilityToUseList_dict[classId]:
                        print("   - " + str(removalStatement))
                
                print()
    
    def getClassesServiced(self):
        
        self.endIncludingProcess()
        
        return list(self._classServicedIds_2_workerBaseClass_2_worksersClassesList.keys())
    
    
    def getAnnotator(self):
        
        self.endIncludingProcess()
        
        return self._annotator
    
    
    def _validateIncludedWorkerType(self, workerType):
        validateStaticMethodsDefinition(workerType) 
        
    
    def getWorkersThatServiceTheClass(self, workersBaseType, classId):
        
        self.endIncludingProcess()
        
        output_list = []
        
        if classId in self._classServicedIds_2_workerBaseClass_2_worksersClassesList:
            if workersBaseType in self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId]:
                output_list = self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classId][workersBaseType][:]
        
        return output_list
    
    
    def _addClassServiced(self, classServiced):
        
        # declare class serviced
        self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classServiced] = {}
        
        for specializedWorkerBaseType in self._specializedWorkerBasesClasses_list:
            self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classServiced][specializedWorkerBaseType] = []
    
    
    def include(self, workerType):
        
        assert self._includingProcessOpened_flag, "Including process must be opened"
        
        if not issubclass(workerType, self._workerBaseClass):
            raise TypeError("Cannot include class that is not a child class of " + str(self._workerBaseClass.__name__))
        
        included = False
        
        for specializedWorkerBaseType in self._specializedWorkerBasesClasses_list:
            if issubclass(workerType, specializedWorkerBaseType):
                
                for classServiced in workerType.getClassesServiced_resolved():
                    
                    if classServiced not in self._classServicedIds_2_workerBaseClass_2_worksersClassesList:
                        self._addClassServiced(classServiced)
                            
                    targetList = self._classServicedIds_2_workerBaseClass_2_worksersClassesList[classServiced][specializedWorkerBaseType]
                    
                    if not workerType in targetList:
        
                        self._validateIncludedWorkerType(workerType)                        
                        targetList.append(workerType)
                        
                included = True
                break
        
        if not included:
            raise LookupError("Worker: " + workerType.__name__ + " class bases tree is not supported: " + ", ".join([el.__name__ for el in inspect.getmro(workerType)]))
    
    
    def _getStatementOfContentsAsWorkersGroup(self, specializedWorkerBaseClass): #groupName, workersList):
        
        output_statement = ""
        
        workerGenericName = specializedWorkerBaseClass.getWorkerGenericName()
        workersList = self._baseClass_2_aggregatingList_dict[specializedWorkerBaseClass]
        
        if workersList:
            output_statement = workerGenericName + ":\n"
            
            for classId in self._classesServiced:
                
                classWorkersList = self.getWorkersThatServiceTheClass(specializedWorkerBaseClass, classId)
                output_statement += "  Class " + str(classId) + ":  "
                
                if classWorkersList: 
                    output_statement += ", ".join([worker.getName() for worker in classWorkersList]) + "\n"
                else:
                    output_statement += "None workers"
                
                
        return output_statement

    
    def __str__(self):
        return repr(self)
    
    
    def __repr__(self):
        
        output_statement = ""
        
        for specializedWorkerBaseClass in self._specializedWorkerBasesClasses_list:
            output_statement += self._getStatementOfContentsAsWorkersGroup(specializedWorkerBaseClass)
        
        return output_statement
    
    
    def printContents(self):
        print(str(self))
    
    #
    # def completeChoiceDefinition(self, choice, classId):
    #
    #     choice.fillListOfOptions(self._workersList)
    #
    #     choice.constructFinalOptionsObjects()
    #
    #     subChoices = choice.getSubChoices()
    #
    #     for subChoice in subChoices:
    #
    #         self.completeChoiceDefinition(subChoice, classId)
        
        
        



