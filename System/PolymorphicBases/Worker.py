'''
Created on Apr 21, 2021

@author: piotr
'''

from ObjectsDetectable.Classes import ClassIDs
from pathlib import Path
import inspect
from PolymorphicBases.ABC import Base_AbstCls, abstractmethod, final
from Configuration.ConfigurationObjects.Choice import Choice_Cls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj
from SW_Licensing.SW_License import License_Cls



# secondary global variables creation

def _getWorkerBuilder():
    
    global _workerBuilder
    try:
        return _workerBuilder
    
    except:
        from Configuration.ConfigurationObjects.WorkerConstruction import WorkerBuilder_Cls
        _workerBuilder = WorkerBuilder_Cls() # here unique instance of WorkerBuilder is created
        return _workerBuilder


def _getWorkerConfigurationArgument_AbstCls():
    
    global _WorkerConfigurationArgument_AbstCls
    
    try:
        return _WorkerConfigurationArgument_AbstCls
    
    except:
        from Configuration.ConfigurationObjects.WorkerConfigurationArgument import WorkerConfigurationArgument_AbstCls
        _WorkerConfigurationArgument_AbstCls = WorkerConfigurationArgument_AbstCls
        return _WorkerConfigurationArgument_AbstCls  



class Worker_AbstCls(Base_AbstCls):
    
    allWorkersConstructed_list = []
    namesUsed_dict = {}
    
    """
    The generic class of any logical component that performs predefined role in stream processing
    
    Is an abstract base class to any specification class implementing particular and 
    consistent part of stream processing(processing sequence part). Intermediate 
    abstract base classes are for example:
     - Annotator
     - Detector
     - Tracker
     - TrackStabilizer
     - Recognizer
     - Generator
     - Swapper
     - Anonymizer
    """
    
    @staticmethod
    @abstractmethod
    def getName(): 
        """
        Static method: instance - "self" shall not be used. Method shall output string, for ex:
         - "UniversalImageAnnotator"
         - "Haar"
         - "DeepPrivacy"
        
        Returned param has no processing impact changes display statements and namings
        """
        raise NotImplementedError("This is an abstract method that is missing and shall be implemented by integrator engineer!")
    
    @staticmethod
    @abstractmethod
    def getWorkerGenericName():
        """
        Static method: instance - "self" shall not be used. Method shall output string, for ex:
         - Annotator"
         - "Detector"
         - "Tracker"
         - "TrackStabilizer"
         - "Recognizer"
         - "Generator"
         - "Swapper"
         - "Anonymizer"
         - ...
         
        Returned param has no processing impact changes display statements and namings
        """ 
        raise NotImplementedError("This is an abstract method that is missing and shall be implemented by integrator engineer!")
    
    @staticmethod
    @abstractmethod
    def getJobName():  
        """
        Static method: instance - "self" shall not be used. Method shall output string, for ex:
         - "Annotation"
         - "Detection"
         - "Tracking"
         - "Stabilization"
         - "Generation"
         - "Swapping"
         - "Anonymizing"
         - ...
         
        Returned param has no processing impact changes display statements and namings
        """ 
        raise NotImplementedError("This is an abstract method that is missing and shall be implemented by integrator engineer!")
    
    @staticmethod
    @abstractmethod
    def getDescription():
        """
        Static method: instance - "self" shall not be used. Method shall output string, for ex:
         - "Non-AI anonymizer based on gausian blur"
         - "AI-based detector origin: www.github.com/detector"
         
        Returned param has no processing impact changes display statements and namings
        """
        raise NotImplementedError("This is an abstract method that is missing and shall be implemented by integrator engineer!")

    @staticmethod
    @abstractmethod
    def getClassesServiced():
        """
        Static method: instance - "self" shall not be used. Method shall output set of ints representing 
        classes serviced. Also it is possible to define for all known classes( by returning string: "All". For ex:
         - {0, 1}
         - {0}
         - {1}
         - "All"
        
        Set of classes shall define all possible classes to process. Due to user configuration some of them might 
        not be processable, but it is due to user choice and not the case here 
        
        Note: All ints provided shall represent known classes what means shall be in a list: from ObjectsDetectable.Classes import ClassIDs
        
        This param have processing impact since defines what classes can be processed with a worker
        """
        raise NotImplementedError("This is an abstract method that is missing and shall be implemented by integrator engineer!")
    
    
    @classmethod
    def forceSeparateInstanceForEachJob(cls):
        """
        Set to True to disable optimization in case when worker instance do not perform it's job in stateless manner
        """
        return False
    
    
    @classmethod
    def allowOneInstanceServicingMultipleClassesAtATime(cls):
        """
        Set to False to disable optimization in case when worker instance can process more than one class at a time
        This reuse applies only to instances that are configured the exact same way
        Whenever .forceSeparateInstanceForEachJob() returns True, this method outcome does not matter 
        """
        return True
    
    
    @final
    @staticmethod
    def clearAllWorkersConstructedContainer():
        Worker_AbstCls.allWorkersConstructed_list = []


    @final
    @staticmethod
    def getAllWorkersConstructed():
        return Worker_AbstCls.allWorkersConstructed_list[:]


    @final
    @staticmethod
    def getWorkerConstructedObject(workerConstructionData):
        
        workerBuilder = _getWorkerBuilder()
        
        if workerBuilder.isWorkerRelatedData(workerConstructionData):
            
            return workerBuilder.getWorkerConstructedObject(workerConstructionData)
        
        if isinstance(workerConstructionData, Worker_AbstCls):
            return workerConstructionData
    
    
    @staticmethod
    @abstractmethod
    def getLicense():
        pass
    
    
    def __new__(cls, *_, **__):
        
        # Additional checks on class .getName return
        clsName = cls.getName()
        
        if clsName in Worker_AbstCls.namesUsed_dict:
            knownCls = Worker_AbstCls.namesUsed_dict[clsName]
            if not cls is knownCls:
                raise NameError("The following worker: " + cls.__name__ + " name: \"" + clsName + "\" is not unique. It is used also by the worker: " + knownCls.__name__ )
        else:
            Worker_AbstCls.namesUsed_dict[clsName] = cls
        
        # Validate SW License
        if not isinstance(cls.getLicense(), License_Cls):
            raise PermissionError("You cannot use this SW since license has not been defined\nWorker: " + cls.__name__ + " name: \"" + clsName)
        
        
        with workersPerformanceLoggerObj.startContext_construction(cls):
            instance_ = Base_AbstCls.__new__(cls, *_, **__)
        
        Worker_AbstCls.allWorkersConstructed_list.append(instance_)
        
        return instance_
    
    
    def __init__(self):
        """
        Worker_AbstCls.__init__ shall be called each time any subclass object is created
        """
        assert type(self) != Worker_AbstCls
        self._classesProcessedByInstance = self.getClassesServiced_resolved()
    
    
    def __repr__(self):
        
        return \
            "Name:               " + self.getName()                  + "\n" + \
            "Worker class:       " + self.getWorkerGenericName()     + "\n" + \
            "Job name:           " + self.getJobName()               + "\n" + \
            "Description:        " + self.getDescription()           + "\n" + \
            "Classes serviced:   " + str(self.getClassesServiced())
    
    
    def _setLogFirstUseFlag(self):
        
        varName = "First execution log flag set"
        
        if varName not in self.__dict__:
            
            self.__dict__[varName] = True
            return True
        
        else:
            return False
        
    
    def _getApplicableClassIds(self, workerType, typeAttrName):
        
        applicableClassIds = getattr(workerType, typeAttrName)
        
        if isinstance(applicableClassIds, int):
            applicableClasses_output = {applicableClassIds}
            
        elif hasattr(applicableClassIds, "__iter__") and all([isinstance(applicableClass, int) for applicableClass in applicableClassIds]):
            applicableClasses_output = set(applicableClassIds)
        
        elif applicableClassIds is None:
            applicableClasses_output = set()
            
        else:
            raise TypeError(str(workerType) + " classes applicable type is incorrect: " + str(applicableClassIds) + "\n Accepts only int or list of ints" )
        
        unknownClassIds = []
        
        for applicableClassId in applicableClasses_output:
            if applicableClassId not in ClassIDs:
                unknownClassIds.append(applicableClassId)
        
        if unknownClassIds:
            raise ValueError("Applicable classes: " + str(unknownClassIds) + " are unknown. \nKnown class ids are: " + list(ClassIDs))
        
        return applicableClasses_output

    
    def getFilePathReferenced(self, refereeFile, referencePath):
        return str((Path(refereeFile).parent / referencePath).absolute())

    
    def limitFloatFrom0To1(self, floatVal):
        return min(max(floatVal, 0.0), 1.0)
    
    
    @final
    @classmethod
    def getClassesServiced_resolved(cls):
        """
        Accepts forms:
         - "All"
         - set of ints
        
        All ints prvided shall be in ClassIDs
        """
        classesServiced = cls.getClassesServiced()
        
        if classesServiced == 'All':
            classesServiced = set(ClassIDs)
            
        elif isinstance(classesServiced, set):
            classesServiced = classesServiced.copy()
        else:
            raise TypeError("Classes serviced shall be defined as instance of set or string \"All\"")
                
        if not all([classServiced in ClassIDs for classServiced in classesServiced]):
            raise ValueError("Some classes serviced are unknown. \nProvided: " + ", ".join(classesServiced) + "\nKnown: " + ", " .join(ClassIDs))
        
        return classesServiced
    
    
    def limitClassesProcessedByInstance(self, classOrClassesProcessed_limitation):
        
        if hasattr(classOrClassesProcessed_limitation, "__iter__"):
            classesProcessed_limitation = list(classOrClassesProcessed_limitation)
        else:
            classesProcessed_limitation = [classOrClassesProcessed_limitation]
        
        classesProcessed = self.getClassesProcessedByInstance()
        
        self._classesProcessedByInstance = []
        
        for classProcessed_limitation in classesProcessed_limitation:
            if classProcessed_limitation in classesProcessed:
                self._classesProcessedByInstance.append(classProcessed_limitation)
    

    def resolveArgument(self, argumentObj):
        
        if isinstance(argumentObj, Choice_Cls):
            argumentObj = argumentObj.resolve()
            
            if isinstance(argumentObj, list):
                argumentObj = [self.resolveArgument(argumentObj_listElement) for argumentObj_listElement in argumentObj]
                return argumentObj

        if isinstance(argumentObj, _getWorkerConfigurationArgument_AbstCls()):
            return argumentObj.resolve()
        
        else:
            
            workerConstructed = Worker_AbstCls.getWorkerConstructedObject(argumentObj)
            
            if workerConstructed is not None:
                workerConstructed.limitClassesProcessedByInstance(self.getClassesProcessedByInstance())
                # modify classes serviced where needed
                return workerConstructed
            
        return argumentObj
        
        
    def assignWorkContextParams(self, classesProcessedByInstance):
            
        assert "_workContextParamsAssigned_flag" not in self.__dict__
        self._workContextParamsAssigned_flag = True
        
        assert all([classServiced in ClassIDs for classServiced in classesProcessedByInstance])
        assert all([classServiced in self.getClassesServiced_resolved() for classServiced in classesProcessedByInstance])        

        if not self.allowOneInstanceServicingMultipleClassesAtATime():
            assert len(classesProcessedByInstance) == 1, "Implementation error, case shall not be possible"
            
        self._classesProcessedByInstance = list(classesProcessedByInstance)
        
    
    def getClassesProcessedByInstance(self):
        
        if not "_classesProcessedByInstance" in self.__dict__:
            self._classesProcessedByInstance = self.getClassesServiced_resolved()
            
        return list(self._classesProcessedByInstance)
    
    
    @final
    def anythingToPrepare(self):
        return id(type(self)._prepare) != id(Worker_AbstCls._prepare) # check whether method had been overwritten
    
    
    @final
    def prepare(self):
        varName = "is prepared"
        
        if varName not in self.__dict__:
            if self.anythingToPrepare():
                with workersPerformanceLoggerObj.startContext_preparation(self): 
                    self._prepare()
                
            self.__dict__[varName] = True 

    
    def _prepare(self):
        """
        Implementation of __init__ continuation due to final definition of classes processed; if needed 
        In short: __init__2()
        """
        pass


        

def validateStaticMethodsDefinition(worker):
    
    def isStillAbstractMethod(class_, methodName):
        return methodName in class_.__abstractmethods__
    
    def isStaticMethod(class_, methodName):
        return isinstance(inspect.getattr_static(class_, methodName), staticmethod)
    
    def isNullaryMethod(class_, methodName):
        "If takes no arguments"
        return inspect.getattr_static(class_, methodName).__func__.__code__.co_argcount == 0
        
    if not inspect.isclass(worker):
        workerType = type(worker) # convert to class
    else:
        workerType = worker
    
    assert issubclass(workerType, Worker_AbstCls)
    
    for methodName in ["getName", "getWorkerGenericName", "getJobName", "getDescription", "getClassesServiced"]:
    
        if isStillAbstractMethod(workerType, methodName):
            raise NotImplementedError("Method:  >> " + workerType.__name__ + "." + methodName + "() <<  is still abstract!\n  -> Overwrite abstract method with a nullary static method")
        
        elif not isStaticMethod(workerType, methodName):
            raise NotImplementedError("Method:  >> " + workerType.__name__ + "." + methodName + "() << is not static!\n  -> Use @staticmethod decorator")
        
        elif not isNullaryMethod(workerType, methodName):
            raise NotImplementedError("Method:  >> " + workerType.__name__ + "." + methodName + "() << is not nullary!\n  -> This method by design shall take no arguments")






if __name__ == "__main__":
    
    from Annotator.Annotator import Annotator_Cls
    a = Annotator_Cls()
    
    print(a)








