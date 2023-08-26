'''
Created on Jun 25, 2022

@author: piotr
'''

import tkinter as tk
from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls,\
    StaticWorkersConfigurationManager_AbstCls
from Configuration.ConfigurationObjects.Choice import ListOfChoices_Cls,\
    Choice_Cls, Option_Cls
from Configuration.GUI.GUI_relatedAdditionalClasses import Line_Cls,\
    Label_Cls, CheckBox_Cls, Bullet_Cls, DistanceLine_Cls, Line_AbstCls,\
    Entry_Cls, FileBrowse_Cls, LineDecisionElement_AbstCls,\
    FileSystemBrowser_AbstCls, Space_Cls
from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_AbstCls,\
    ConfigurationObject_Activatable_AbstCls, ConfigurationObject_Named_AbstCls
from Configuration.ConfigurationObjects.WorkerConfiguration import WorkerConfigurationObject_Cls,\
    StaticWorkerConfigurationObjectWrapper_Cls,\
    WorkerConfigurationArgumentsContainer_Cls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import WorkerConfigurationArgument_AbstCls,\
    UserCfg_Path, UserCfg_Int, UserCfg_Float,\
    WorkerConfigurationArgument_Limited_AbstCls, UserCfg_Bool, UserCfg_String


from Configuration.GUI.GUI_cfg import debug

if debug:
    _tkinterFramesClassUsed = tk.LabelFrame
else:
    _tkinterFramesClassUsed = tk.Frame



class GUI_Bridge_Cls():
    """
    Is an interface between beckend objects/actions and frontend objects/actions
    
    Frontend <----> Bridge <----> Backend
    
    """
    
    def __init__(self):
        
        self.backendConfObjs_list = []
        self.backendConfObj_2_frontendConfObj_dict = {}
        
        self.frontendConfObj_2_upperFrontendConfObj_dict = {}
        
        self.frontendConfObj_2_decisionElementsDict_dict = {} # {frontendObj : {decisionElement class : [active elements] } }
        self.decisionElement_2_frontendConfObj_dict = {}
        
        
    
        self._loopFullyRunning = False
        self._staticWorkersManagers_list = []
    
    
    def _isManagedByStaticWorkerManager(self, backendConfObj):
        return any([backendConfObj in staticWorkerManager.staticWorkersConf_list for staticWorkerManager in self._staticWorkersManagers_list])
    
    
    def _isDisapperableDueToUserChoice(self, backendConfObj):
        frontendConfObj = self.backendConfObj_2_frontendConfObj_dict[backendConfObj]
        return self._getCheckBoxes(frontendConfObj) or self._isManagedByStaticWorkerManager(backendConfObj)
    
    
    def synchronizeFrontendToBackend(self):
        "Backend leads" 
        
        for backendConfObj in self.backendConfObjs_list:
            
            frontendConfObj = self.backendConfObj_2_frontendConfObj_dict[backendConfObj]
            
            if isinstance(backendConfObj, ConfigurationObject_Activatable_AbstCls) and backendConfObj.isActivatable():
            
                checkBoxes = self._getCheckBoxes(frontendConfObj)
                
                backendIsActive = backendConfObj.isActive()
                
                if self._isDisapperableDueToUserChoice(backendConfObj):
                    if backendIsActive:
                        frontendConfObj.show()
                    else:
                        frontendConfObj.hide()
                
                for checkbox in checkBoxes:
                    checkbox.setValue(backendIsActive)
                
                
            for decisionElementsType in self.frontendConfObj_2_decisionElementsDict_dict[frontendConfObj]:
                
                decisionElements = self.frontendConfObj_2_decisionElementsDict_dict[frontendConfObj][decisionElementsType]
                
                if not issubclass(decisionElementsType, CheckBox_Cls):
                    
                    for decisionElement in decisionElements:
                        decisionElement.setValue(backendConfObj.getValue())
                    
                
                
    
    
    
    def performCrossInteraction(self):
        
        for staticWorkerManager in self._staticWorkersManagers_list:
            staticWorkerManager.updateStaticWorkersConfiguration()
    
    
    def fullSynchronize(self):
        "Backend leads" 
        self.performCrossInteraction()   
        self.synchronizeFrontendToBackend()
        
    
    def frontEndAction_endHook(self):
        
        self.fullSynchronize()
    
    
    def processUserDecision(self, guiDecisionElement):
        
        "Called by frontend"
        
        doEndHook = True
        
        backendConfObj = self._getBackendConfObj_OfGuiDecisionElement(guiDecisionElement)
        
        if isinstance(guiDecisionElement, Entry_Cls):
            
            entry = guiDecisionElement
            
            try:
                backendConfObj.setValue(entry.getValue())
                
            except TypeError as e:
                print(e)
    
    
        elif isinstance(guiDecisionElement, CheckBox_Cls):
            
            checkBox = guiDecisionElement
            
            if checkBox.getValue():
                backend_result = backendConfObj.activate()
            
            else:
                backend_result = backendConfObj.deactivate()
        
            if not backend_result:
                doEndHook = False
    
    
        elif isinstance(guiDecisionElement, FileSystemBrowser_AbstCls):
            
            browser = guiDecisionElement
            
            referenceFolder = backendConfObj.getReferenceFolder()
            
            newPath = browser.getValue(referenceFolder)
            
            if newPath:
                backendConfObj.setValue(newPath)
        
        if doEndHook:
            self.frontEndAction_endHook()
    
    
    def _getBackendConfObj_OfGuiDecisionElement(self, guiDecisionElement):
        assert isinstance(guiDecisionElement, LineDecisionElement_AbstCls)
        
        return self._getBackendConfObj_OfFrontendConfObj(
                self._getFrontendConfObj_OfGuiDecisionElement(guiDecisionElement)
                )
    
    def _getFrontendConfObj_OfGuiDecisionElement(self, guiDecisionElement):
        assert isinstance(guiDecisionElement, LineDecisionElement_AbstCls)
        return self.decisionElement_2_frontendConfObj_dict[guiDecisionElement]
    
    
    def _getBackendConfObj_OfFrontendConfObj(self, frontend_confObj):
        return frontend_confObj.getBackendConfObj()
    
    
    def _getFrontendConfObj_OfBackendConfObj(self, backend_confObj):
        return self.backendConfObj_2_frontendConfObj_dict[backend_confObj]
    
    
    def _getGuiDecisionElements_OfFrontendConfObj(self, frontend_confObj, decisionElementsType):
        
        if frontend_confObj in self.frontendConfObj_2_decisionElementsDict_dict:
            if decisionElementsType in self.frontendConfObj_2_decisionElementsDict_dict[frontend_confObj]:
                return self.frontendConfObj_2_decisionElementsDict_dict[frontend_confObj][decisionElementsType]
        
        return []
    
    
    def _getCheckBoxes(self, frontend_confObj):
        
        return self._getGuiDecisionElements_OfFrontendConfObj(frontend_confObj, CheckBox_Cls)
    
         
    
    
    def _constructDecisionElement(self, frontend_configurationObj, decisionElementType):
        
        assert isinstance(frontend_configurationObj, Frontend_ConfigurationObj_Cls)
        
        if frontend_configurationObj not in self.frontendConfObj_2_decisionElementsDict_dict:
            self.frontendConfObj_2_decisionElementsDict_dict[frontend_configurationObj] = {}
            
        if not decisionElementType in self.frontendConfObj_2_decisionElementsDict_dict[frontend_configurationObj]:
            self.frontendConfObj_2_decisionElementsDict_dict[frontend_configurationObj][decisionElementType] = []
        
        newDecisionElement = decisionElementType(self)
        self.frontendConfObj_2_decisionElementsDict_dict[frontend_configurationObj][decisionElementType].append(newDecisionElement)
        self.decisionElement_2_frontendConfObj_dict[newDecisionElement] = frontend_configurationObj
        
        return newDecisionElement
            
            
    
    
    def construct_frontendConfigurationObject(self, backend_confObj, upperFrontend_confObj, master, noBaseLinePastingDueToUpperElement_flag = False, tableRow = None):
        "upperFrontendConfigurationObj can be None"
        
        assert isinstance(upperFrontend_confObj, Frontend_ConfigurationObj_Cls) or upperFrontend_confObj is None
        
        if isinstance(backend_confObj, StaticWorkersConfigurationManager_AbstCls):
            assert backend_confObj not in self._staticWorkersManagers_list
            self._staticWorkersManagers_list.append(backend_confObj)
        
        frontend_confObj = Frontend_ConfigurationObj_Cls(master, backend_confObj, self, noBaseLinePastingDueToUpperElement_flag, tableRow)
        
        self.backendConfObjs_list.insert(1, backend_confObj)
        self.backendConfObj_2_frontendConfObj_dict[backend_confObj] = frontend_confObj
        self.frontendConfObj_2_upperFrontendConfObj_dict[frontend_confObj] = upperFrontend_confObj
        
        if frontend_confObj not in self.frontendConfObj_2_decisionElementsDict_dict:
            self.frontendConfObj_2_decisionElementsDict_dict[frontend_confObj] = {}
            
        return frontend_confObj
            
        
        
    
    def construct_Entry(self, frontend_configurationObj):
        
        return self._constructDecisionElement(frontend_configurationObj, Entry_Cls)
        
    
    def construct_FileBrowse(self, frontend_configurationObj):
        
        return self._constructDecisionElement(frontend_configurationObj, FileBrowse_Cls)
    
    
    def construct_CheckBox(self, frontend_configurationObj):
        
        checkBox = self._constructDecisionElement(frontend_configurationObj, CheckBox_Cls)
        
        backend_confObj = self._getBackendConfObj_OfFrontendConfObj(frontend_configurationObj)
        assert isinstance(backend_confObj, ConfigurationObject_Activatable_AbstCls)
        assert backend_confObj.isActivatable()
        
        return checkBox



class Frontend_ConfigurationObj_Cls():
    
    def __init__(self, master, backend_confObj, GUI_Bridge, noBaseLinePastingDueToUpperElement_flag, tableRow = None):
        
        assert isinstance(GUI_Bridge, GUI_Bridge_Cls)
        assert isinstance(noBaseLinePastingDueToUpperElement_flag, bool)
        assert tableRow is None or (isinstance(tableRow, int) and tableRow >= 0)
        
        self.GUI_Bridge = GUI_Bridge
        self.noBaseLinePastingDueToUpperElement_flag = noBaseLinePastingDueToUpperElement_flag or tableRow is not None
        
        self.backend_confObj = backend_confObj
        
        self.constructMainFiveFrames(master)
        
        if isinstance(self.backend_confObj, ConfigurationObject_Named_AbstCls):
            self._description = self.backend_confObj.getDescription()
        else:
            self._description = ""
            
        self.baseLine = Line_Cls(self._description)
        self.subElements = []
        self.tableSubElements = []
        
        self._separatorLine = None
        self._isUsingTable = False
        self._tableRow = tableRow
        
        self._shown = True
        
        self.constructElements()
        
        if not self.noBaseLinePastingDueToUpperElement_flag:
            self.baseLine.pasteOnFrame(self.baseLineFrame) # base line elements collected
        
            if bool(self):
                self.indentFrame.config( width = 26 )
    
    
    def isReprInTable(self):
        return self._tableRow is not None
    
    
    def defineSeparatorLine(self, height):
        assert self._separatorLine is None, "Cannot reassign"
        self._separatorLine = DistanceLine_Cls(height)
    
    
    def __str__(self):
        return "Frontend of " + str(self.backend_confObj)
    
    def __repr__(self):
        return str(self)
    
    
    def getBackendConfObj(self):
        return self.backend_confObj
    
    
    def __bool__(self):
        return bool(self.baseLine)
    

    def haveSubElementsAnyGraphicalRepr(self):
        
        for subElement in self.subElements:
            if (subElement.baseLine and not subElement.noBaseLinePastingDueToUpperElement_flag) or subElement.haveSubElementsAnyGraphicalRepr() or subElement.isReprInTable():
                return True
                
        return False
    

    def constructMainFiveFrames(self, master):
        
        global _tkinterFramesClassUsed
        
        if not self.noBaseLinePastingDueToUpperElement_flag:
            self.frame = _tkinterFramesClassUsed(master)
            self.frame.pack(side = "top", fill = "both")
            
            self.baseLineFrame = _tkinterFramesClassUsed(self.frame)
            self.baseLineFrame.pack(side = "top", fill = "x")
            
            self.subElementsFrame = _tkinterFramesClassUsed(self.frame)
            self.subElementsFrame.pack(side = "bottom", fill = "x")
            
            self.indentFrame = _tkinterFramesClassUsed(self.subElementsFrame)
            self.indentFrame.pack(side = "left", fill = "y")
            
            self.plottableFrame = _tkinterFramesClassUsed(self.subElementsFrame)
            self.plottableFrame.pack(fill = "x")
        
        else:
#             self.frame = master
#             self.indentFrame = master
#             self.baseLineFrame = master
            
            self.subElementsFrame = master
            self.plottableFrame = master
            
    
    
    def constructElements(self):
        
        backend_confObj = self.backend_confObj

        
        if isinstance(backend_confObj, ClassesProcessingConfiguration_Cls):
            
            self.defineSeparatorLine(1)
            
            self.addSubElement(backend_confObj._classesChoice)
            self.addSubElement(backend_confObj._annotatorCfgWrapper)
       
        
        elif isinstance(backend_confObj, ListOfChoices_Cls):
            
            self.defineSeparatorLine(1)
            
            for choice in backend_confObj:
                self.addSubElement(choice)
        
        
        elif isinstance(backend_confObj, Choice_Cls):
            
            if backend_confObj:
                # Checkbox
                if backend_confObj._activatable:
                    self.addSelfCheckBoxToLine(self.baseLine)
                # Checkbox
                
                self.addBaseLineElement(Label_Cls(text = backend_confObj.getName() + ":"))
                    
                for option in backend_confObj:
                    self.addSubElement(option)
        
        
        elif isinstance(backend_confObj, Option_Cls):
            
            self.addSelfCheckBoxToLine(self.baseLine)
            
            self.addBaseLineElement(Label_Cls(text = backend_confObj.getName()))
            
            self.addSubElement(backend_confObj._value, True)
        
        
        elif isinstance(backend_confObj, StaticWorkerConfigurationObjectWrapper_Cls):
            
            self.addSubElement(backend_confObj.getWorkerConfigurationObj())
        
        
        elif isinstance(backend_confObj, WorkerConfigurationObject_Cls):
                
            text = backend_confObj._workerClass.getWorkerGenericName() + ": " + backend_confObj.getName()
            
            self.addBaseLineElement(Label_Cls(text = text))
            
            self.addSubElement(backend_confObj.getArgumentsObj(), True)
        
        
        elif isinstance(backend_confObj, WorkerConfigurationArgumentsContainer_Cls):
            
            oneLineUserCfgObjs_list = []
            otherUserCfgObjs_list = []
            
            for argument in backend_confObj:
                
                if isinstance(argument, WorkerConfigurationArgument_AbstCls):
                    oneLineUserCfgObjs_list.append(argument)
                else:
                    otherUserCfgObjs_list.append(argument)
            
            if oneLineUserCfgObjs_list: 
                
                for oneLineUserCfgObj in oneLineUserCfgObjs_list:
                    self.addSubElement(oneLineUserCfgObj)
            
            for subElement in otherUserCfgObjs_list:
                self.addSubElement(subElement)
        
        
        else:
            assert isinstance(backend_confObj, WorkerConfigurationArgument_AbstCls)
            
            if self.isReprInTable():
                leftPart = Line_Cls(self._description)
                rightPart = Line_Cls()
            
            else:
                leftPart = self.baseLine
                rightPart = self.baseLine

            
            leftPart.addElement(Bullet_Cls())
            leftPart.addElement(Label_Cls(text = backend_confObj.getName()))
            
    
            if isinstance(backend_confObj, UserCfg_Bool):
                checkBox = self.GUI_Bridge.construct_CheckBox(self)
                rightPart.addElement(checkBox)
            
            
            elif isinstance(backend_confObj, UserCfg_Path):
                fileBrowse = self.GUI_Bridge.construct_FileBrowse(self)
                rightPart.addElement(fileBrowse)
                rightPart.addElement(Space_Cls(1))
                self.addSelfEntryToLine(rightPart)
                
            
            
            elif isinstance(backend_confObj, UserCfg_Int) or isinstance(backend_confObj, UserCfg_Float) or isinstance(backend_confObj, UserCfg_String):
                self.addSelfEntryToLine(rightPart)
            
            
            if isinstance(backend_confObj, WorkerConfigurationArgument_Limited_AbstCls):
                rightPart.addElement(Label_Cls(text = " " * 5 + "Limited:  " + backend_confObj.getLowerLimitStr() + "  <=  x  <=  " + backend_confObj.getUpperLimitStr()))
            
            
            if self.isReprInTable():
                
                self.pasteIntoTheTable(leftPart, rightPart)
                
    
    def pasteIntoTheTable(self, leftPart, rightPart):
                
        leftFrame = _tkinterFramesClassUsed(self.plottableFrame)
        
        leftFrame.grid(row = self._tableRow, column = 1, sticky="W")
        
        distanceFrame =  _tkinterFramesClassUsed(self.plottableFrame)
        distanceFrame.grid(row = self._tableRow, column = 2)
        
        rightFrame = _tkinterFramesClassUsed(self.plottableFrame)
        rightFrame.grid(row = self._tableRow, column = 3, sticky="W")
        
        leftPart.pasteOnFrame(leftFrame)
        rightPart.pasteOnFrame(rightFrame)
    
    
    def addSelfEntryToLine(self, line):
        
        entry = self.GUI_Bridge.construct_Entry(self)
        line.addElement(entry)
        
        
    def addSelfCheckBoxToLine(self, line):
        
        checkBox = self.GUI_Bridge.construct_CheckBox(self)
            
        line.addElement(checkBox)
        
    
    def addBaseLineElement(self, element):
        self.baseLine.addElement(element)
    
    
    def getTableFrame(self):
        
        if self._isUsingTable is False:
            
            self._isUsingTable = True
            
            self._tableFrame = _tkinterFramesClassUsed(self.subElementsFrame)
            self._tableFrame.pack(side = "top", fill ="x")
            self._tableFrame.grid_columnconfigure(2, minsize = 20)
        
        return self._tableFrame
        
    
    def addSubElement(self, subElement, noBaseLinePastingDueToUpperElement_flag = False):
        
        # Add separator line
        if self._separatorLine and not self.subElements:
            self._separatorLine.pasteOnFrame(self.plottableFrame)
        
        
        if isinstance(subElement, WorkerConfigurationArgument_AbstCls):
            
            subElement_toAdd = self.GUI_Bridge.construct_frontendConfigurationObject(backend_confObj = subElement,
                                                                                     upperFrontend_confObj = self,
                                                                                     master = self.getTableFrame(),
                                                                                     noBaseLinePastingDueToUpperElement_flag = noBaseLinePastingDueToUpperElement_flag,
                                                                                     tableRow = len(self.tableSubElements) + 1)
            
            self.tableSubElements.append(subElement_toAdd)
            
        
        elif isinstance(subElement, ConfigurationObject_AbstCls):
            subElement_toAdd = self.GUI_Bridge.construct_frontendConfigurationObject(backend_confObj = subElement,
                                                                                     upperFrontend_confObj = self,
                                                                                     master = self.plottableFrame,
                                                                                     noBaseLinePastingDueToUpperElement_flag = noBaseLinePastingDueToUpperElement_flag)
        
        elif isinstance(subElement, Line_AbstCls):
            subElement_toAdd = subElement.pasteOnFrame(self.plottableFrame)
        
        else:
            raise TypeError()
            
        # Add separator line
        if self._separatorLine and subElement_toAdd.haveSubElementsAnyGraphicalRepr():
            self._separatorLine.pasteOnFrame(self.plottableFrame)
            
        self.subElements.append(subElement_toAdd)

    
    def isSubElementsFrameEmpty(self):
        return not self.subElements or (isinstance(self.backend_confObj, Option_Cls) and not self.subElements[0].subElements)
        
    
    def hide(self):
        self._shown = False
        #if self.haveSubElementsAnyGraphicalRepr():
        if not isinstance(self.backend_confObj, WorkerConfigurationArgument_AbstCls):
            self.subElementsFrame.pack_forget() # .hide()
    
    
    def show(self):
        self._shown = True
        if self.haveSubElementsAnyGraphicalRepr():
            self.subElementsFrame.pack(side = "left", fill = "x") # .show()
        










