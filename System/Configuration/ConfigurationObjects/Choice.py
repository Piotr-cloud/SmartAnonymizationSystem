'''
Created on Jun 4, 2022

@author: piotr
'''
from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_Copyable_AbstCls,\
    ConfigurationObject_Activatable_AbstCls, ConfigurationObject_AbstCls,\
    ConfigurationObject_Named_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls
from Configuration.ConfigurationObjects.LoadingErrorCodes import Loading_MissingDecisions



class Option_Cls(ConfigurationObject_Copyable_AbstCls, ConfigurationObject_Activatable_AbstCls, ConfigurationObject_Named_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls):
    
    def __init__(self, value, name = None, description = ""):
        """
        When value is instance of ConfigurationObject_Named_AbstCls then name is overwritten with value.getName()
        """
        
        if isinstance(value, ConfigurationObject_Named_AbstCls):
            name = value.getName()
            description = value.getDescription()
        
        assert isinstance(name, str)
        ConfigurationObject_Named_AbstCls.__init__(self, name, description)
        
        self._value = value
        self._hostChoice = None
        
        ConfigurationObject_Activatable_AbstCls.__init__(self, True)
    
    
    def _getCfgDecisionsDict(self):
        
        optionValue = self.getValue()
        
        if isinstance(optionValue, ConfigurationObject_DecisionKeeper_AbstCls):
            
            if isinstance(optionValue, ConfigurationObject_Named_AbstCls):
                self._addCfgDecisionDict(optionValue.getCfgDecisionsDict())
            else:
                self._addCfgDecisionDictElement(self.getName(), optionValue.getCfgDecisionsDict())
            
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        optionValue = self.getValue()
        
        if isinstance(optionValue, ConfigurationObject_DecisionKeeper_AbstCls):
            
            if isinstance(optionValue, ConfigurationObject_Named_AbstCls):
                self._passCfgDecisionsDictToNextDecisionKeeper(currentCfgDecisionsDict = cfgDecisionsDict,
                                                               nextDecisionKeeper = optionValue)
                
            else:
                self._passPartOfCfgDecisionsDictToNextDecisionKeeper(
                    dictPartKey = self.getName(), 
                    currentCfgDecisionsDict = cfgDecisionsDict,
                    nextDecisionKeeper = optionValue)
            
        else:
            pass # option then is non-configurable cannot load any param. Input dict is left non-changed
    
    
    def activate(self):
        
        ret = self._activate()
        self._hostChoice._checkOption_Event(self)
    
        return ret
    
    
    def deactivate(self):
        
        ret = False
        
        if self._hostChoice.checkIfOptionCanBeUnchecked():
            ret = self._deactivate()
            self._hostChoice._uncheckOption_Event(self)
        
        return ret
    
    
    def getValue(self):
        return self._value
    
    
    def getOptionsSimpleFormatFlag(self):
        
        return self._hostChoice._optionsSimpleFormat_flag
    
    
    def sentNonUserActivationWiseSignalToGUI(self):
        
        if self.GUI_checkBox is not None:
            self.GUI_checkBox.synchronizeGuiActivationToCfgObj()
    

    def assignChoiceObject(self, choice):
        
        assert isinstance(choice, Choice_Cls)
        assert self._hostChoice is None
        
        self._hostChoice = choice
    
    

    def copy(self):
        
        value = self._value
        
        try:
            value_original = value
            value = value.copy()
            assert type(value) == type(value_original)
            
        except:
            pass # do not make a copy of value
        
        return Option_Cls(value = value, name = self._name, description = self._description)

        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        output_str = self._name + " : " + str(self._value)
        
        if self.isActive():
            output_str += "  -> Checked <-"
        
        return output_str



class Choice_Cls(ConfigurationObject_Copyable_AbstCls, ConfigurationObject_Activatable_AbstCls, ConfigurationObject_Named_AbstCls, ConfigurationObject_DecisionKeeper_AbstCls):
    
    def __init__(self, name, description, optionsData_dict = None, singleChoice_flag = True, activatable = False):
        """
        optionsData_dict of pairs 
            name : value
        
        name - shall be string, or convertable to string
        value - any object 
        
        Options are going to be constructed within object constructor. Order is defined by name
        
        At least one option must match so first one is taken as default choice
        
        """
        ConfigurationObject_Named_AbstCls.__init__(self, name, description)
        ConfigurationObject_Activatable_AbstCls.__init__(self, activatable)
                
        self._singleChoice_flag = bool(singleChoice_flag)
        
        self._options = []
        
        self._optionsSimpleFormat_flag = True
        
        if bool(optionsData_dict): 
            options_list = []
            
            names = []
            optionsData_new_dict = {}
            
            for optionKey in optionsData_dict.keys():
                optionName = str(optionKey)
                names.append(optionName)
                
                assert optionName not in optionsData_new_dict
                optionsData_new_dict[optionName] = optionsData_dict[optionKey]
                
            namesOrdered = sorted(names)
            optionsData_dict = optionsData_new_dict
            
            for name in namesOrdered:
                
                value = optionsData_dict[name]
                
                if isinstance(value, ConfigurationObject_AbstCls):
                    self._optionsSimpleFormat_flag = False
                
                options_list.append(Option_Cls(value = value, name = name))
                
            self._setOptions(options_list)
        
        self._GUI_radiobutton_var = None
    
    
    def _getCfgDecisionsDict(self):
        
        for optionChecked in self.getOptionsChecked():
            self._addCfgDecisionDict(optionChecked.getCfgDecisionsDict())
            
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        if self.isActivatable():
            self.activate()
            
        optionActivated_flag = False
        
        optionsToDeativate_list = []
        
        for option in self:
            optionName = option.getName()
            
            if optionName in cfgDecisionsDict:
                if not self._singleChoice_flag or not optionActivated_flag: 
                    option.activate()
                    optionActivated_flag = True
                    self._passCfgDecisionsDictToNextDecisionKeeper(cfgDecisionsDict, option)
            
            else:
                optionsToDeativate_list.append(option)
                
        for option in optionsToDeativate_list:
            option.deactivate()
        
        if self._singleChoice_flag and not optionActivated_flag:
            self._addLoadingErrorCode(Loading_MissingDecisions)
                
    
    def isSingleChoiceFlag(self):
        return self._singleChoice_flag

    
    def setRadiobuttonVar(self, GUI_radiobutton_var):
        assert self._GUI_radiobutton_var is None
        self._GUI_radiobutton_var = GUI_radiobutton_var
    
    def getActiveOptions(self):
        output_list = []
        
        for option in self:
            if option.isActive():
                output_list.append(option)
        
        return output_list
    
    def getRadiobuttonVar(self):
        return self._GUI_radiobutton_var
    
        
    def _setOptions(self, options_list):
        
        assert isinstance(options_list, list) and all([isinstance(option, Option_Cls) for option in options_list])
        assert not self._options, "Cannot redefine options"
            
        for option in options_list:
            option.assignChoiceObject(self)
            self._options.append(option)
    
        self._assertIntegrity()
        
        if self._options:
            self._options[0].activate() # activate first option as default
    
    
    def getOptions(self):
        return self._options[:]
    
    
    def getOptionsStartingFromFirstActive(self):
        
        headList = []
        tailList = []
        
        started_flag = False
        
        for option in self:
            
            if option.isActive() and started_flag is False:
                started_flag = True
            
            if started_flag:
                headList.append(option)
            else:
                tailList.append(option)
        
        return headList + tailList
    
    
    def _checkOption_Event(self, optionChecked):
        
        if self._singleChoice_flag:
            for option in self._options:
                if option is not optionChecked:
                    option._deactivate()
    
        self._assertIntegrity()
    
    
    def _uncheckOption_Event(self, optionUnchecked):
        
        self._assertIntegrity()
    
    
    def checkIfOptionCanBeUnchecked(self):
        
        if self._singleChoice_flag:
            return False
        
        else:
            return self.getNumberOfOptionsChecked() > 1
            
    
    def getNumberOfOptionsChecked(self):
        return [option.isActive() for option in self._options].count(True)
    
    
    def _assertIntegrity(self):
        
        if self._singleChoice_flag: 
            assert 0 <= self.getNumberOfOptionsChecked() <= 1
    
    def getOptionsChecked(self):
        
        if self._singleChoice_flag:
            for option in self._options:
                if option.isActive():
                    return [option]
            
            return []
        
        else:
            options = []
            
            for option in self._options:
                if option.isActive():
                    options.append(option)
                    
            return options
        
    
    def resolve(self):
        """
        Resolve of Choice_Cls shall return option values
        """
        
        if self.isActive():
            
            optionsChecked = self.getOptionsChecked()
            assert isinstance(optionsChecked, list)
            
            valuesChecked = [option.getValue() for option in optionsChecked]
            
            if self.isSingleChoiceFlag():
                assert len(valuesChecked) == 1, "No options available for the choice, so choce cannot be resolved"
                return valuesChecked[0]
            
            else:
                return valuesChecked
            
        return None
    
    
    def copy(self):
        return Choice_Cls({option._name: option._value for option in self._options}, self._singleChoice_flag)
    
    
    def __bool__(self):
        return bool(self._options)
    
    
    def __iter__(self):
        
        for option in self._options:
            yield option
            
    
    def __repr__(self):
        return str(self)
    
    
    def __str__(self):
        if self._options:
            return "Choice named:" + str(self._name) + "".join(["\n - " + str(option) for option in self._options])
        else:
            return "Empty choice"  
    


class ListOfChoices_Cls(ConfigurationObject_DecisionKeeper_AbstCls):
    """
    Used as base workers choices
    """

    def __init__(self, choicesList):
        
        assert all([isinstance(choice, Choice_Cls) for choice in choicesList])
        
        self._choicesList = choicesList


    def _getCfgDecisionsDict(self):
        
        for choice_ in self._choicesList:
            if choice_.isActive():
                self._addCfgDecisionDict({choice_.getName(): choice_.getCfgDecisionsDict()})
            
            
    def _loadDecisionsFromCfgDict(self, cfgDecisionsDict):
        
        for choice_ in self._choicesList:
            choiceName = choice_.getName()
            if choiceName in cfgDecisionsDict:
                if choice_.isActivatable():
                    choice_.activate()
                self._passPartOfCfgDecisionsDictToNextDecisionKeeper(dictPartKey = choiceName,
                                                                     currentCfgDecisionsDict = cfgDecisionsDict,
                                                                     nextDecisionKeeper = choice_)
            else:
                if choice_.isActivatable():
                    choice_.deactivate()
                else:
                    self._addLoadingErrorCode(Loading_MissingDecisions)
    
    
    def __iter__(self):
        for choice in self._choicesList:
            yield choice
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        if self._choicesList:
            return "Choices:" + "".join(["\n - " + str(choice) for choice in self._choicesList])
        else:
            return "Empty list of choices"  



if __name__ == "__main__":
    
    from Configuration.ConfigurationObjects.WorkerConfigurationArgument import Factory_WorkerConfigurationArgument_Cls
    
    factory = Factory_WorkerConfigurationArgument_Cls()
    
    
    choice_ = factory([1,2,3,4])
    
    
    for option in choice_:
        option.activate()
        print(choice_)
    print(choice_.resolve())
        
        
    choice_ = Choice_Cls("name", "desc", 
                         optionsData_dict = 
                             {
                                 "1" : 1,
                                 "2" : 2,
                                 "3" : 3,
                                 "4" : 4,
                             }, 
                         singleChoice_flag = True) 
    
    
    for option in choice_:
        option.activate()
        print(choice_)
        
    print(choice_.resolve())
