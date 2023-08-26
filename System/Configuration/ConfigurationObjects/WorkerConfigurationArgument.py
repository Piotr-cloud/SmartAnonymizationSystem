'''
Created on Jun 4, 2022

@author: piotr
'''
import os
from pathlib import PurePath, Path
from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_Copyable_AbstCls,\
    ConfigurationObject_Named_AbstCls, ConfigurationObject_Activatable_AbstCls,\
    ConfigurationObject_DecisionKeeper_AbstCls
from Configuration.ConfigurationObjects.Choice import Choice_Cls
import inspect
from Configuration.ConfigurationObjects.LoadingErrorCodes import Loading_MissingDecisions,\
    Loading_IgnoredDecisions
from NonPythonFiles import projectRoot_dir



class WorkerConfigurationArgument_AbstCls(ConfigurationObject_Named_AbstCls, ConfigurationObject_Copyable_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls):
    """
    Implements:
      - value
      - value type
      - default value
    """

    allowedValueTypes = [
        int, 
        float,
        str,
        bool,
        PurePath
        ]
    
    def __init__(self, name, description, defaultValueOrType):
        
        assert type(self) != WorkerConfigurationArgument_AbstCls
        
        self._value = None         # Definition ongoing
        self._valueType = None     # Definition ongoing
        self._defaultValue = None  # Definition ongoing
        
        self._invokeName = None # This is name used by constructor as argument name(local symbol)
        
        ConfigurationObject_Named_AbstCls.__init__(self, name, description)
        self._setDefaultValueAndType(defaultValueOrType)
    
    
    def _setDefaultValueAndType(self, defaultValueOrType):
        
        typeOfInput = type(defaultValueOrType)
        
        if typeOfInput is type:
            valueType = defaultValueOrType
            defaultValue = self._valueType()
        
        else:
            valueType = typeOfInput
            defaultValue = defaultValueOrType

        self._setValueType(valueType)
        self._setDefaultValue(defaultValue)
        self._setToDefault()
    
    
    def _setDefaultValue(self, defaultValue):
        self._defaultValue = self._parseInput(defaultValue)
    
    def postSet_Hook(self):
        pass
    
    
    def setInvokeName(self, invokeName):
        assert isinstance(invokeName, str)
        self._invokeName = invokeName
    
    
    def getInvokeName(self):
        assert isinstance(self._invokeName, str)
        return self._invokeName
    
    
    def setValue(self, input_):
            
        ret = False
        
        if input_ != self.getValue():
            valueCandidate = self._parseInput(input_)
            
            if valueCandidate is not None:
                self._value = valueCandidate
                ret = True
        else:
            ret = True
             
        self.postSet_Hook()
        
        return ret
    
    def getValue(self):
        return self._value
    
    def getValueAsString(self):
        return str(self.getValue())
    
    def _setValueType(self, valueType):
        
        valueType_validated = False
        
        for allowedValueType in WorkerConfigurationArgument_AbstCls.allowedValueTypes:
            if issubclass(valueType, allowedValueType):
                valueType_validated = True
                break
        
        assert valueType_validated # Cfg arg value type is not allowed
            
        self._valueType = valueType
        

    def _castInput(self, input_):
        
        try:
            input_ = self._valueType(input_)
        except:
            input_ = None
            raise TypeError("Value \"" + str(input_) + "\" is not convertable to type \"" + str(self._valueType.__name__) + "\"")
        
        assert isinstance(input_, self._valueType)
        
        return input_
    
    
    def _setToDefault(self):
        if self._defaultValue is not None:
            self.setValue(self._defaultValue)
    
    
    def _parseInput(self, input_):
        return self._castInput(input_)
    
    def resolve(self):
        return self._value
    
    def _getCfgDecisionsDict(self):
        self._addCfgDecisionDictElement(name = self.getName(), value = self.getValue())
    
    
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        name = self.getName()
        
        if name in cfgDecisionsDict:
            argumentNewValue = cfgDecisionsDict[name]
            
            if not self.setValue(argumentNewValue):
                self._addLoadingErrorCode(Loading_IgnoredDecisions)
            else:
                del cfgDecisionsDict[name]
        
        else:
            self._addLoadingErrorCode(Loading_MissingDecisions)
    
    def _copy(self):

        return type(self)(
            self._name, 
            self._description,
            self._defaultValue,
            )
    
    def copy(self):
        
        ret_obj = self._copy()
        
#         if self._name is not None:
#             ret_obj._setName(self._name)
        
        return ret_obj


    def _getReprStrings(self):
        
        return super()._getReprStrings() + [
            "Default value: " + str(self._defaultValue),
            "Value type: " + str(self._valueType.__name__)]






class WorkerConfigurationArgument_Limited_AbstCls(WorkerConfigurationArgument_AbstCls):
    
    def __init__(self, name, description, lower_limit, defaultValue, upper_limit):
        
        assert type(self) != WorkerConfigurationArgument_Limited_AbstCls
        assert type(defaultValue) is not type, "Starting from this class definition only value is accepted as default value data"
        
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValue)
        
        self._setLimits(lower_limit, upper_limit)
        
    
    def _copy(self):
        
        return type(self)(self._name,
                          self._description,
                          self._lowerLimit,
                          self._defaultValue,
                          self._upperLimit)
    
    
    def _setLimits(self, lower_limit, upper_limit):
        
        lower_limit = self._castInput(lower_limit)
        upper_limit = self._castInput(upper_limit)
        
        assert lower_limit <= self._value <= upper_limit, "Cannot set limits -> see condition"
        
        self._lowerLimit = lower_limit
        self._upperLimit = upper_limit
    
    
    def getLowerLimitStr(self):
        return str(self._lowerLimit)
    
    
    def getUpperLimitStr(self):
        return str(self._upperLimit)


    def _limitInput(self, input_):
        
        if "_upperLimit" not in self.__dict__:
            self._upperLimit = input_
        if "_lowerLimit" not in self.__dict__:
            self._lowerLimit = input_
            
        if input_ > self._upperLimit:
            return self._upperLimit
        
        elif input_ < self._lowerLimit:
            return self._lowerLimit
        
        else:
            return input_
    
    
    def _parseInput(self, input_):
        
        valueCandidate = self._castInput(input_)
        
        if valueCandidate is not None:
            return self._limitInput(valueCandidate)
        else:
            return valueCandidate 
        


    def _getReprStrings(self):
        
        return super()._getReprStrings() + [
            "Range <" + str(self._lowerLimit) + ", " + str(self._upperLimit) + ">"]





class UserCfg_Int(WorkerConfigurationArgument_AbstCls):

    def __init__(self, name, description, defaultValue = int):
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValue)
        

class UserCfg_Float(WorkerConfigurationArgument_AbstCls):

    def __init__(self, name, description, defaultValue = float):
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValue)


class UserCfg_Bool(WorkerConfigurationArgument_AbstCls, ConfigurationObject_Activatable_AbstCls):

    def __init__(self, name, description, defaultValue = bool):
        
        ConfigurationObject_Activatable_AbstCls.__init__(self, activatable = True)
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValue)
        
    
    def setValue(self, input_):
        
        ret = WorkerConfigurationArgument_AbstCls.setValue(self, input_)
        
        if self._value:
            self._activate()
        else:
            self._deactivate()
        
        return ret
    
      
    def activate(self):
        "Action - frontend signal"
        WorkerConfigurationArgument_AbstCls.setValue(self, True)
        return self._activate()
      
    def deactivate(self):
        "Action - frontend signal"
        WorkerConfigurationArgument_AbstCls.setValue(self, False)
        return self._deactivate()
    
    

class UserCfg_String(WorkerConfigurationArgument_AbstCls):

    def __init__(self, name, description, defaultValue = str):
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValue)




class UserCfg_Path(WorkerConfigurationArgument_AbstCls):
    
    projectRoot_dir = projectRoot_dir
    
    def __init__(self, name, description, path, referenceFolder = "@caller_dir"):
            
        #What if default file does not exist - then entry shall be empty waiting for the input. Reference folder remains
        if referenceFolder == "@caller_dir" or referenceFolder == ".":
            
            referenceFolder_set = False
            
            if path and (isinstance(path, str) or isinstance(path, Path)):
                
                path_ = Path(path)
                
                if path_.is_absolute() and path_.exists():
                    if path_.is_file():
                        path_ = path_.parent
                        
                    referenceFolder = path_
                    referenceFolder_set = True
            
            if not referenceFolder_set:
                referenceFolder = self._getSecondCallerDirectory()
        
        elif referenceFolder == "..":
            referenceFolder = self._getSecondCallerDirectory().parent
            
        else:
            referenceFolder = Path(referenceFolder).expanduser().absolute()
            
        if not path:
            path = ""
        
        self._referenceFolder = referenceFolder
        
        absolutePath = self._getAbsolutePath(path)
        assert absolutePath.exists(), "default path must exists"
        
        path = self._getProjectRelativePath(absolutePath)
        
        WorkerConfigurationArgument_AbstCls.__init__(self, name, description, defaultValueOrType= path)
    
    
    def getReferenceFolder(self):
        return self._referenceFolder
    
    
    def _getSecondCallerDirectory(self):
        return Path(inspect.stack()[2][1]).parent
            
    
    def _castInput(self, input_):
        return Path(input_) 
    
    
    def _getAbsolutePath(self, input_):
        
        input_ = Path(input_)
        
        if not input_.is_absolute():
            input_ = (UserCfg_Path.projectRoot_dir / input_).absolute()
            
        return input_
    
    
    def _getProjectRelativePath(self, input_):
        absPath = self._getAbsolutePath(input_)
        assert absPath.exists() and absPath.is_file()
        projectRelativePath = os.path.relpath(str(absPath), str(UserCfg_Path.projectRoot_dir))
        return projectRelativePath
    
    
    def _validateInput(self, input_):
        absPath = self._getAbsolutePath(input_) 
        return absPath.exists() and absPath.is_file()
    
    
    def resolve(self):
        projectRelativePath = self._getAbsolutePath(self.getValue())
        return projectRelativePath
    
    
    def _parseInput(self, input_):
        
        valueCandidate = self._castInput(input_)
        
        if self._validateInput(valueCandidate):
            return self._getProjectRelativePath(valueCandidate)
        else:
            return None
    
    def _getCfgDecisionsDict(self):
        
        valueToDump = self.getValue()
        if valueToDump is not None:
            valueToDump = str(valueToDump)
            
        self._addCfgDecisionDictElement(name = self.getName(), value = valueToDump)
        
        
    def _copy(self):
        
        return UserCfg_Path(self._name,
                            self._description, 
                            self._defaultValue,
                            self._referenceFolder)
    
    
    def _checkIfPathExists(self, input_):
        pass



# class UserCfg_Choice_Cls(Paste here Choice_Cls and Implement the factory then make choice to be produced when user provides dict {str: value}):
#     pass



class UserCfg_Int_Limited(WorkerConfigurationArgument_Limited_AbstCls, UserCfg_Int):
    pass


class UserCfg_Float_Limited(WorkerConfigurationArgument_Limited_AbstCls, UserCfg_Float):
    pass



# def classlookup(cls):
#     c = list(cls.__bases__)
#     for base in c:
#         c.extend(classlookup(base))
#     return c


class Factory_WorkerConfigurationArgument_Cls():
    
    "Stateless class"

    def __call__(self, inputData, defaultName = "No name", defaultDescription = "Not descripted"):

        if isinstance(inputData, ConfigurationObject_Copyable_AbstCls):
            return inputData.copy()
        
        elif isinstance(inputData, list) or \
            isinstance(inputData, dict):
            
            if isinstance(inputData, list):
                input_dict = {str(el): el for el in inputData}
            
            else:
                input_dict = inputData
                
            return Choice_Cls(name = defaultName, description = defaultDescription, optionsData_dict = input_dict)
             
            
        else:
            
            CfgArgClass = None
            
            if isinstance(inputData, bool):
                CfgArgClass = UserCfg_Bool
                
            elif isinstance(inputData, int):
                CfgArgClass = UserCfg_Int
                
            elif isinstance(inputData, float):
                CfgArgClass = UserCfg_Float
                
            elif isinstance(inputData, str):
                CfgArgClass = UserCfg_String
                
            else:
                raise TypeError("Unkown constructor argument type: " + str(type(inputData).__name__))
        
            output_object = CfgArgClass(defaultName, defaultDescription, inputData)

            return output_object





if __name__ == "__main__":

    
    # Factory tests
    
    factory = Factory_WorkerConfigurationArgument_Cls() 
    
    testData_list = [
        1,
        "dsad",
        UserCfg_Int_Limited(name = "A",
                            description = "description of A",
                            lower_limit = 1,
                            defaultValue = 10,
                            upper_limit = 100),
        UserCfg_Int_Limited(name = "X",
                                description = "description",
                                lower_limit = 1,
                                defaultValue = 1,
                                upper_limit = 100),
        [1,2,3,4,5],
        {1:1,2:2,3:3}
        ]
   
   
    for testData in testData_list:
        
        userCfg_object = factory(testData)
        
        print(userCfg_object)
    
    
    
    
    
    







