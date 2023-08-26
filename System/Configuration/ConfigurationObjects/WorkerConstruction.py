'''
Created on Sep 27, 2022

@author: piotr
'''
    
from Detector.Detector import Detector_AbstCls

from Configuration.ConfigurationObjects.WorkerConfiguration import WorkerConfigurationObject_Cls
from ObjectsDetectable.Classes import ClassIDs
import inspect
from PolymorphicBases.Worker import Worker_AbstCls



class WorkerConstructionObject_Cls():
    """
    Object that is ready for construction:
    - Arguments are freezed and prepared for construction
    - This object allows to make worker uniqe where needed
    """
    
    def __init__(self, workerConfigurationObject):
        
        assert isinstance(workerConfigurationObject, WorkerConfigurationObject_Cls)
            
        self._workerCls = workerConfigurationObject.getWorkerClass()
        self._kwArgsDecided = workerConfigurationObject.getKwArgsDecided()
        self._classesServiced = set()
        
        self._addClassesServiced(workerConfigurationObject.getClassesServiced())
        
        self._constructedObject = None
    


    def getWorkerCls(self):
        return self._workerCls
    
    
    def getKwArgsDecided(self):
        return self._kwArgsDecided
    
    
    def _addClassesServiced(self, classIDs):
        
        if classIDs is not None and list(classIDs)[0] is not None:
            assert all([classID in ClassIDs for classID in classIDs])
            
            self._classesServiced.update(classIDs)
    
            
    def __eq__(self, other):
        
        if isinstance(other, WorkerConstructionObject_Cls):
            if self._workerCls == other._workerCls:
                if self._kwArgsDecided == other._kwArgsDecided: # key - key and value - value builtin dict comparison
                    if not self._workerCls.forceSeparateInstanceForEachJob():
                        if self._classesServiced == other._classesServiced:
                            return True
                        
                        else:
                            if self._workerCls.allowOneInstanceServicingMultipleClassesAtATime():
                                self._addClassesServiced(other._classesServiced)
                                other._addClassesServiced(self._classesServiced)
                                return True
                            
        return False
    
    
    def getClassesServiced(self):
        return list(self._classesServiced)
    
    
    def __hash__(self):
        return object.__hash__(self._workerCls)
    
    
    def construct(self, builder):
        
        self._builder = builder
        
    
    # def getConstructed(self):
    #
    #     if self._constructedObject is None:
    #
    #         # construct kw args first
    #         for argInvokeName in self._kw_args_reformatted:
    #             argValue = self._kw_args_reformatted[argInvokeName]
    #
    #             if isinstance(argValue, list):
    #                 raise NotImplementedError("Implementation TBD")
    #
    #             else:
    #                 if isinstance(argValue, WorkerConstructionObject_Cls):
    #                     self._kw_args_reformatted[argInvokeName] = argValue.getConstructed() # In theory infinitive recursion possible when one worker needs itself somewhere during construction of its arguments 
    #
    #         self._constructedObject = self._workerCls(**self._kw_args_reformatted)
    #
    #         self._builder.linkConstructedWorker(self._constructedObject)
    #
    #         self._constructedObject.assignWorkContextParams(self._classesServiced, self._builder.getConstructedWorkersList_ref())
    #
    #     return self._constructedObject
    

    def __repr__(self): return str(self)
    
    def __str__(self):
        
        output_str = self._workerCls.__name__ + "(" + ", ".join([str(name) + "=" + str(self._kwArgsDecided[name]) for name in self._kwArgsDecided]) + ")"
        
        return output_str



class WorkerBuilder_Cls():
    """
    Performs worker construction implementing worker uniqueness mechanism where needed. Whenever instance is used uniqueness is applied(if worker is configured so)
    """
    
    workersBaseClassesForUniqness_list = [
        Detector_AbstCls
        ]
        
    def __init__(self):
        
        self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict = {}
        
        # self._workersConstructionObjects_list = []
        # self._workersConstructedObjects_list = []
        
    
    def _getWorkerConstructedObject_of_WorkerConstructionObj(self, workerConstructionObj):
        """
        Does:
            WorkerConstructionObject_Cls -> unique worker object
        """
        assert isinstance(workerConstructionObj, WorkerConstructionObject_Cls)
        
        workerConstructionObj = self.getUniqueWorkerConstructionObject(workerConstructionObj)
        
        if self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict[workerConstructionObj] is None:
            workerCls = workerConstructionObj.getWorkerCls()
            kwArgsResolved = self._getWorkerConstructionArgumentsResolved(workerConstructionObj)
            
            if self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict[workerConstructionObj] is not None: # double construction case
                raise RuntimeError("Double construction case is not supported")
            
            workerInstance = workerCls(**kwArgsResolved)
            workerInstance.assignWorkContextParams(workerConstructionObj.getClassesServiced())
            
            self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict[workerConstructionObj] = workerInstance
        
        return self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict[workerConstructionObj]
    
    
    def getWorkerConstructionObject(self, workerConfigurationObj):
        """
        Does:
            WorkerConfigurationObject_Cls -> WorkerConstructionObject_Cls
        """
        assert isinstance(workerConfigurationObj, WorkerConfigurationObject_Cls)
        
        return WorkerConstructionObject_Cls(workerConfigurationObj)
    
    
    def getUniqueWorkerConstructionObject(self, workerConstructionObj):
        
        for workerConstructionObject_known in self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict.keys():
            if workerConstructionObject_known == workerConstructionObj:
                return workerConstructionObject_known
        
        self._workerConstructionObject_2_uniqueWorkerConstructionObj_dict[workerConstructionObj] = None
        
        return workerConstructionObj
    
    
    def isWorkerRelatedData(self, workerConstructionData):
        
        if (inspect.isclass(workerConstructionData) and issubclass(workerConstructionData, Worker_AbstCls)) or \
            isinstance(workerConstructionData, WorkerConfigurationObject_Cls) or \
            isinstance(workerConstructionData, WorkerConstructionObject_Cls):
            
            return True
        
        else:
            return False
        
    
    def getWorkerConstructedObject(self, workerConstructionData):
        
        if isinstance(workerConstructionData, Worker_AbstCls):
            print("Warning! Do not use this API for already created instances of Worker_AbstCls")
            return workerConstructionData
        
        if inspect.isclass(workerConstructionData) and issubclass(workerConstructionData, Worker_AbstCls):
            workerConstructionData = WorkerConfigurationObject_Cls(workerConstructionData)
        
        if isinstance(workerConstructionData, WorkerConfigurationObject_Cls):
            workerConstructionData = self.getWorkerConstructionObject(workerConstructionData)
            
        assert isinstance(workerConstructionData, WorkerConstructionObject_Cls)
        
        return self._getWorkerConstructedObject_of_WorkerConstructionObj(workerConstructionData)
    
    
    def _getWorkerConstructionArgumentsResolved(self, workerConstructionObj):
        """
        Searches for nested WorkerConstructionObject_Cls and transforms them into unique worker constructed objects
        """
        assert isinstance(workerConstructionObj, WorkerConstructionObject_Cls)
        
        kwArgsDecided_dict = workerConstructionObj.getKwArgsDecided()
        
        kwArgsResolved_dict = {}
        
        for argInvokeName, argValue in kwArgsDecided_dict.items():
    
            if isinstance(argValue, WorkerConstructionObject_Cls):
                argValue = self.getWorkerConstructedObject(argValue)
                
            elif (isinstance(argValue, list) and argValue and isinstance(argValue[0], WorkerConfigurationObject_Cls)):
                argValue_new = []
                for workerConfigurationObj in argValue:
                    argValue_new.append(self.getWorkerConstructedObject(workerConfigurationObj))
                argValue = argValue_new
    
            kwArgsResolved_dict[argInvokeName] = argValue
        
        return kwArgsResolved_dict
    




