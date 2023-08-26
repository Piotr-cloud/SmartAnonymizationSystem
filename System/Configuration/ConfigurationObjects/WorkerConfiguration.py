'''
Created on May 7, 2022

@author: piotr
'''

import inspect

from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_Copyable_AbstCls,\
    ConfigurationObject_Named_AbstCls, ConfigurationObject_Activatable_AbstCls, \
    ConfigurationObject_DecisionKeeper_AbstCls

from ObjectsDetectable.Classes import ClassIDs

from Configuration.ConfigurationObjects.Choice import Option_Cls,\
    Choice_Cls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import Factory_WorkerConfigurationArgument_Cls,\
    WorkerConfigurationArgument_AbstCls
from PolymorphicBases.Worker import Worker_AbstCls




class WorkerConfigurationObject_Cls(ConfigurationObject_Named_AbstCls, ConfigurationObject_Copyable_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls):
    """
    Loads worker class and makes constructors arguments copy
    """
    
    def __init__(self, workerClass):
        
        assert issubclass(workerClass, Worker_AbstCls)
        
        ConfigurationObject_Named_AbstCls.__init__(
            self,
            name = workerClass.getName(), 
            description = workerClass.getDescription()
            )
        
        self._workerClass = workerClass
        self._arguments = WorkerConfigurationArgumentsContainer_Cls()
        
        self._classServiced = None
        
        self.parseArgs()   # fills self._arguments
    
    
    def getWorkerClass(self):
        return self._workerClass
    
    
    def getKwArgsDecided(self):
        return self._arguments.getKwArgsDecided()
    
    
    def _getCfgDecisionsDict(self):
        
        self._addCfgDecisionDictElement(self._workerClass.getName(), self._arguments.getCfgDecisionsDict())
            
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        "Loads {WorkerName: args_dict}"
        
        name = self._workerClass.getName()
        self._passPartOfCfgDecisionsDictToNextDecisionKeeper(name, cfgDecisionsDict, self._arguments)
            
    
    def __repr__(self):
        return str(self)
    
    
    def __str__(self):
        
        output_string = self._workerClass.__name__ + "(" + str(self._arguments) + ")"
        return output_string
    
    
    def checkIfPossibleToCombine(self, other):
        """
        Compares all configuration except _classServiced so objects can be combined into one
        """
        assert isinstance(other, WorkerConfigurationObject_Cls)
        return False
    
    
    def __eq__(self, other):
        
        if isinstance(other, WorkerConfigurationObject_Cls):
            return False
        else:
            return False
    
    
    def __hash__(self):
        return object.__hash__(self)
    
    
    def getClassesServiced(self):
        
        if self._classServiced is None:
            return list(self._workerClass.getClassesServiced_resolved())
        else:
            return [self._classServiced]
    
    
    def setClassServiced(self, classId):
        """
        ! -> can be called once during object life time
        """
        
        assert classId in ClassIDs
        assert self._classServiced is None, "Can be assigned just once" 
        self._classServiced = classId
        
    
    def copy(self):
        return WorkerConfigurationObject_Cls(self._workerClass) # Keeps class reference, and makes copy of argument objects
    
    
    def getWorkerConstructionObj(self):
        return self._workerConstructionObjectClass(self._workerClass, self._arguments.getKwArgsDecided())
    
    
    def getArgumentsObj(self):
        """
        Further operation shall be done on reference
        """
        return self._arguments.getCopy()
    
    
    def parseArgs(self):
        
        parameters_list = list(inspect.signature(self._workerClass.__init__).parameters.values())
        parameters_list = parameters_list[1:] # skip "self"
        
        for parameter in parameters_list:
            
            if hasattr(parameter, "default"):
                
                defaultValue = parameter.default
                
                if isinstance(defaultValue, type) and issubclass(defaultValue, inspect._empty):
                    raise ValueError("All constructor arguments of worker: \"" + self._workerClass.__name__ + "\" shall be defaulted!\nBut parameter named: \"" + parameter.name + "\" is not.")
                else:
                    continue
        
        self.loadCfgArg(parameters_list)
    
    
    def loadCfgArg(self, parameters_list):
        
        factory = Factory_WorkerConfigurationArgument_Cls()
        
        for parameter_index in range(len(parameters_list)):
            
            parameter = parameters_list[parameter_index]
            
            defaultName = parameter.name
            value = parameter.default
            
            defaultDescription = "Argument of constructor of worker: " + str(self._workerClass.__name__) + " at position: " + str(parameter_index) + " (incl. zero)"
            
            userCfg_object = factory(value, defaultName, defaultDescription)
            
            argument = userCfg_object
            
            argument.setInvokeName(parameter.name)
            
            self._arguments.addArgument(argument)


    def constructChoiceOptions(self, workersIncluder):
        "Recursive call to allow construction of sub workers"
        
        for userArg in self._arguments:
            
            if isinstance(userArg, ChoiceOf_WorkerConfigurationObject_Cls):
                userArg.constructOptions(workersIncluder, self._classServiced)



class StaticWorkerConfigurationObjectWrapper_Cls(ConfigurationObject_Activatable_AbstCls):
    

    def __init__(self, workerConfigurationObj, managing_confObj):
        
        assert isinstance(workerConfigurationObj, WorkerConfigurationObject_Cls)
        
        self._workerConfigurationObj = workerConfigurationObj
        self._managing_confObj = managing_confObj
        
        ConfigurationObject_Activatable_AbstCls.__init__(self, True)
    
    
    def getWorkerConfigurationObj(self):
        return self._workerConfigurationObj
    


class WorkerConfigurationArgumentsContainer_Cls(ConfigurationObject_DecisionKeeper_AbstCls):
    
    def __init__(self, arguments_list = None):
        
        self._arguments_list = []
        
        if arguments_list:
            
            assert isinstance(arguments_list, list)
            
            for argument in arguments_list:
                self.addArgument(argument)
                
            self._arguments_list = arguments_list
    
    
    def _getCfgDecisionsDict(self):
        
        for argument in self._arguments_list:
            
            if isinstance(argument, Choice_Cls):
                self._addCfgDecisionDictElement(argument.getName(), argument.getCfgDecisionsDict())
            else:
                self._addCfgDecisionDict(argument.getCfgDecisionsDict())
        
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        for argument in self._arguments_list:
            
            if isinstance(argument, Choice_Cls):
                
                self._passPartOfCfgDecisionsDictToNextDecisionKeeper(
                    dictPartKey = argument.getName(),
                    currentCfgDecisionsDict = cfgDecisionsDict, 
                    nextDecisionKeeper = argument)
                
            else:
                
                self._passCfgDecisionsDictToNextDecisionKeeper(
                    currentCfgDecisionsDict = cfgDecisionsDict, 
                    nextDecisionKeeper = argument)
                
    
    def __str__(self):
        return ", ".join([el.getName() for el in self._arguments_list])
    
    def __bool__(self):
        return bool(self._arguments_list)
    
    def getCopy(self):
        return WorkerConfigurationArgumentsContainer_Cls(self._arguments_list)
    
    def getArgs(self):
        return self._arguments_list[:]
    
    def addArgument(self, argument):
        assert isinstance(argument, WorkerConfigurationArgument_AbstCls) or isinstance(argument, ChoiceOf_WorkerConfigurationObject_Cls)
        self._arguments_list.append(argument)
    
    
    def getKwArgsDecided(self):
        
        output_dict = {}
        
        for argument in self._arguments_list:
            if isinstance(argument, ChoiceOf_WorkerConfigurationObject_Cls):
                argumentValue = argument.resolve()
            else:
                argumentValue = argument
            argumentName = argument.getInvokeName()
            
            # if hasattr(argumentValue, "resolve"):
            #     argumentValue = argumentValue.resolve()
                
            output_dict[argumentName] = argumentValue
        
        return output_dict
    
    
    def __iter__(self):
        for argument in self._arguments_list:
            yield argument





class ChoiceOf_WorkerConfigurationObject_Cls(Choice_Cls):
    
    """
    Named and described choice of from the objects of class WorkerConfigurationObject_Cls
    """
    
    def __init__(self,
                 name,
                 description,
                 workersBaseType,
                 subsetOfWorkersTypes = None,
                 activatable = False,
                 singleChoice_flag = True):
        """
        name - param name displayed in configuration panel(no processing param)
        description - description displayed in configuration panel(no processing param)
        workersBaseType - defines workers set by indicating common base type
        subsetOfWorkersTypes - additional limitation of workers(see argument above) to provided set
        singleChoice_flag - flag telling whether one worker shall be returned, otherwise returning a list of workers is possible
        """
        Choice_Cls.__init__(self, name, description, singleChoice_flag = singleChoice_flag, activatable = activatable)
        
        self._optionsConstructed = False
        
        self._workersBaseType = Worker_AbstCls
        
        if workersBaseType is not None:
            self.narrowWorkersBaseType(workersBaseType)
        
        self._subsetOfWorkersTypes = subsetOfWorkersTypes
        
        self._options_workerClasses = self._process_subsetOfWorkersTypes(subsetOfWorkersTypes)
        
        self._classServiced = None
        self._invokeName = None
    
    
        
    def narrowWorkersBaseType(self, workersBaseType):
        
        assert issubclass(workersBaseType, self._workersBaseType), "Cannot narrow since new type is not a subclass of current worker base type"
        self._workersBaseType = workersBaseType
    

    def _process_subsetOfWorkersTypes(self, subsetOfWorkersTypes):
        
        new_subsetOfWorkersTypes = []
        
        if subsetOfWorkersTypes is not None:
            
            assert hasattr(subsetOfWorkersTypes, "__iter__")
            
            disqualifiedWorkerTypes = []
            
            for workerType in subsetOfWorkersTypes:
                if not issubclass(workerType, self._workersBaseType):
                    disqualifiedWorkerTypes.append(workerType)
                else:
                    if workerType not in new_subsetOfWorkersTypes: # make new list unique
                        new_subsetOfWorkersTypes.append(workerType)
            
            raise TypeError("The following workers are not subclasses of base class: " + str(self._workersBaseType.__name__) + ":" + ["\n -" + str(el.__name__) for el in disqualifiedWorkerTypes])
        
        return new_subsetOfWorkersTypes
    
    
    def constructOptions(self, workersIncluder, classServiced):
        """
        Recursion construction
        Integrator is used to get all the suboptions
        
        ! -> can be called once during object life time
        
        """

        assert classServiced in ClassIDs
        assert self._optionsConstructed is False
        
        self._optionsConstructed = True
        
        self._classServiced = classServiced
        
        self._filterWorkersDueToClassServiced(classServiced)
        
        intergratorKnownOptions_raw = workersIncluder.getWorkersThatServiceTheClass(self._workersBaseType, classServiced)
        
        if not bool(self._options_workerClasses):
            optionsTaken = intergratorKnownOptions_raw
        else:
            optionsTaken = []
            optionsRemoved = []
            
            for workerClass in self._options_workerClasses:
                if workerClass in intergratorKnownOptions_raw:
                    optionsTaken.append(workerClass)
                
                else:
                    optionsRemoved.append(workerClass)
            
            if optionsRemoved:
                print("Warning! Some options were removed")
        
        self._options_workerClasses = optionsTaken
        
        options = []
        
        for workerClass in self._options_workerClasses:
            
            workerConfigurationObj_option = WorkerConfigurationObject_Cls(workerClass)
            workerConfigurationObj_option.setClassServiced(classServiced)
            workerConfigurationObj_option.constructChoiceOptions(workersIncluder)
            
            options.append( Option_Cls(workerConfigurationObj_option) )
        
        self._setOptions(options)


    def _filterWorkersDueToClassServiced(self, classServiced):
        """
        Filter in terms of class serviced
        
        -> Reduces self._options_workerClasses
        """
        
        if classServiced is not None:
            
            for option_ in self._options_workerClasses:
                if classServiced not in option_.getClassesServiced_resolved():
                    self._options_workerClasses.remove(option_)
    
    
    def setInvokeName(self, invokeName):
        assert isinstance(invokeName, str)
        self._invokeName = invokeName
    
    
    def getInvokeName(self):
        assert isinstance(self._invokeName, str)
        return self._invokeName
    
    
    def copy(self):
        
        assert self._optionsConstructed is False
        
        newObj = ChoiceOf_WorkerConfigurationObject_Cls(
            name = self._name,
            description = self._description,
            workersBaseType = self._workersBaseType,
            subsetOfWorkersTypes = self._subsetOfWorkersTypes,
            activatable = self._activatable,
            singleChoice_flag = self._singleChoice_flag)

        return newObj

    def __repr__(self): return str(self)
    
    def __str__(self):
        return ConfigurationObject_Named_AbstCls.__str__(self) + "\n" + Choice_Cls.__str__(self)













