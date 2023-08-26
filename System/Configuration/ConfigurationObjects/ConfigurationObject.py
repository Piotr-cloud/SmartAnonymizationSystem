'''
Created on May 7, 2022

@author: piotr
'''
from Configuration.GUI.GUI_cfg import SQUARE_EMPTY, SQUARE_FILLED
from PolymorphicBases.ABC import final, abstractmethod
from Configuration.ConfigurationObjects.LoadingErrorCodes import mergeLoadingErrorCodes,\
    Loading_IgnoredDecisions, Loading_NonImported,\
    Loading_MissingAndIgnoredDecisions, Loading_MissingDecisions, Loading_OK


from Configuration.GUI.GUI_cfg import debug
from PolymorphicBases.ABC import Base_AbstCls



class ConfigurationObject_AbstCls(Base_AbstCls):
    
    def __init__(self):
        assert type(self) != ConfigurationObject_AbstCls



class ConfigurationObject_Activatable_AbstCls(ConfigurationObject_AbstCls):
    
    def __init__(self, activatable = False):
        
        assert type(self) != ConfigurationObject_Activatable_AbstCls
        self._activatable = bool(activatable)
          
        if self._activatable:
            self._active = False
        else:
            self._active = True
    
        self.GUI_checkBox = None
    
    
    def __str__(self):
        
        output_string = ""
        
        if self._activatable:
            if self._active:
                output_string += SQUARE_FILLED
            else:
                output_string += SQUARE_EMPTY
            
            output_string += " "
        
        return output_string
    
    
    def assignGUICheckBox(self, GUI_checkBox):
        
        assert self.GUI_checkBox is None
        self.GUI_checkBox = GUI_checkBox
    
    
    def isActive(self):
        return self._active 
    
    def isActivatable(self):
        return self._activatable
      
    def activate(self):
        "Action - frontend signal"
        return self._activate()
      
    def deactivate(self):
        "Action - frontend signal"
        return self._deactivate()
    
    def _activate(self):
        "Activation universal self response"
        assert self._activatable
        self._active = True
        
        return True # successfull activation
        
    def _deactivate(self):
        "Activation universal self response"
        assert self._activatable
        self._active = False
        
        return True # successfull deactivation
    
    
#     def activate_backend(self):
#         "Reaction to backend signal"
#         return self._activate()
#     
#     def deactivate_backend(self):
#         "Reaction to backend signal"
#         return self._deactivate()
#           



class ConfigurationObject_Copyable_AbstCls(ConfigurationObject_AbstCls):
    @abstractmethod
    def copy(self):
        pass



class ConfigurationObject_Named_AbstCls(ConfigurationObject_AbstCls):
    """
    This class object is used as a base class for user-configuration object like:
     - WorkerConfiguration 
     - WorkerConfigurationArgument
     - ConfigurationObject_Choice
     - ClassProcessingConfiguration
     - ClassesProcessingConfiguration 
    """
    
    def __init__(self, name, description):
        '''
        Constructor
        '''
        assert type(self) != ConfigurationObject_Named_AbstCls
        
        if name is not None:   self._setName(name)
        else:                  self._name = None
        
        if description is not None:   self._setDescription(description)
        else:                         self._description = None
            
    
    def _setName(self, name):
        name = self._parseString(name)
        assert name, "Empty"
        self._name  = name
    
    
    def _setDescription(self, description):
        self._description  =  self._parseString(description)
    
    
    def getName(self):
        return self._name
    
    def getDescription(self):
        return self._description
    
    
    def _parseString(self, input_):
        
        assert isinstance(input_, str)
        
        return input_


    def getReprStrings(self):

        return self._getReprStrings()
    
    
    def _getReprStrings(self):
        
        output_list = []
        
        if self._name is not None:
            output_list.append("Name: \"" + self._name + "\"")
            
        output_list.append("Description: \"" + str(self._description) + "\"")
        
        return output_list


    def __str__(self):
        return "; ".join(self.getReprStrings())
        
        
    def __repr__(self):
        return str(self)

    
class DuplicateKeyError(ValueError): pass
#
#
# class SerilizationTriple_Cls():
#     """
#     Three elements used for efficient dump-load: 
#     - name
#     - getMethod  (used during dump; when dump dict is constructed name insicates whatever outcome of this method)
#     - setMethod  (used during load; when loading what is indicated name indicates goes to this method and when execution is finished is removed from load dict)
#     """
#
#     def __init__(self, name, getMethod, setMethod):
#         self._name = name
#         self._getMethod = getMethod
    

class ConfigurationObject_DecisionKeeper_AbstCls(ConfigurationObject_AbstCls):
    
    @final
    def getCfgDecisionsDict(self):
        self._cfgDecisionsDict = {}
        ret = self._getCfgDecisionsDict()
        assert ret is None, "Mehod shall produce cfgDecisionsDict no by return, but by calling methods: ._addCfgDecisionDictElement() ._addCfgDecisionDict()"
        return self._cfgDecisionsDict

    @final
    def _addCfgDecisionDictElement(self, name, value):
        
        if name in self._cfgDecisionsDict:
            raise DuplicateKeyError("Key: \"" + str(name) + "\" is duplicated!")
        
        self._cfgDecisionsDict[name] = value

    @final
    def _addCfgDecisionDict(self, dict_):
        for name in dict_:
            self._addCfgDecisionDictElement(name, dict_[name])


    @abstractmethod
    def _getCfgDecisionsDict(self):
        """
        Shall fill self._cfgDecisionsDict by using two methods: 
          - _addCfgDecisionDictElement
          - _addCfgDecisionDict
        """
        pass


    @final
    def loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        self._loading_ErrorCode_ret = Loading_OK
        
        if debug:
            print()
            print("Before: ", cfgDecisionsDict)
            
        self._loadDecisionsFromCfgDict(cfgDecisionsDict)
        self.validateErrorCodeInRange(self._loading_ErrorCode_ret)
        
        if debug:
            print("After: ", cfgDecisionsDict)
            print("\t -> Error code: " + self._loading_ErrorCode_ret)
            print()
        
        return self._loading_ErrorCode_ret
    
    
    def validateErrorCodeInRange(self, loading_ErrorCode):
        
        assert loading_ErrorCode in [
            Loading_OK,
            Loading_MissingDecisions,
            Loading_IgnoredDecisions,
            Loading_MissingAndIgnoredDecisions,
            Loading_NonImported
            ], "Error code is not as expected"
            
        
    def _addLoadingErrorCode(self, loading_ErrorCode):
        before_ = self._loading_ErrorCode_ret
        self._loading_ErrorCode_ret = mergeLoadingErrorCodes(self._loading_ErrorCode_ret, loading_ErrorCode)
        
        if debug:
            if before_ != self._loading_ErrorCode_ret:
                print("-> Error code change to: " + str(self._loading_ErrorCode_ret))
                if self._loading_ErrorCode_ret == Loading_MissingDecisions:
                    _breakpoint = 1
    
    
    def _passPartOfCfgDecisionsDictToNextDecisionKeeper(self, dictPartKey, currentCfgDecisionsDict, nextDecisionKeeper):
        
        if  dictPartKey in currentCfgDecisionsDict:
            cfgDictPart = currentCfgDecisionsDict[dictPartKey]
            
            self._addLoadingErrorCode(
                nextDecisionKeeper.loadDecisionsFromCfgDict(cfgDictPart)
                )
            if not currentCfgDecisionsDict[dictPartKey]:
                del currentCfgDecisionsDict[dictPartKey]
        else:
            self._addLoadingErrorCode(Loading_MissingDecisions)
    
    
    def _passCfgDecisionsDictToNextDecisionKeeper(self, currentCfgDecisionsDict, nextDecisionKeeper):
        
        self._addLoadingErrorCode(
            nextDecisionKeeper.loadDecisionsFromCfgDict(currentCfgDecisionsDict)
            )

        
    @abstractmethod
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        pass
















