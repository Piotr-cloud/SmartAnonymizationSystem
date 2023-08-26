'''
Created on Jun 25, 2022

@author: piotr
'''
import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk, Image
from Configuration.GUI.GUI_cfg import BULLET, ARROW
import tkinter.font as tkFont
from tkinter.filedialog import Open, Directory
from Pmw import Balloon
from PolymorphicBases.ABC import Base_AbstCls, abstractmethod
from NonPythonFiles import guiCheckboxesFiles_dir


class GUI_element_AbstCls(Base_AbstCls):
    pass



class GUI_FullWidthElement_Cls(GUI_element_AbstCls):

    def __init__(self):
        
        GUI_element_AbstCls.__init__(self)
        
        self._hidden = False
        self._hidden_secondary = False # when super element is hidden anyhow, sub element hides also
        
        self._components = []
        self._staticComponents = []
        self._dynamicComponents = []

    
    def _addComponentStatic(self, component):
        
        assert isinstance(component, GUI_element_AbstCls)
        self._components.append(component)
        self._staticComponents.append(component)
    
    
    def _addComponentDynamic(self, component):
        
        assert isinstance(component, GUI_element_AbstCls)
        self._components.append(component)
        self._dynamicComponents.append(component)
        
    
    def _hide(self):
        
        for component in self._components:
            component.hideSecondary()
        
        assert self.isHidden()
    
    
    def hide(self):
        
        if self._hidden is not True:
            self._hidden = True
            self._hide()
            
    
    def hideSecondary(self):
        
        if self._hidden_secondary is not True:
            self._hidden_secondary = True
            self._hide()
    
        
    def isHidden(self):
        return self._hidden or self._hidden_secondary



class GUI_CellElement_AbstCls(GUI_element_AbstCls):
    
    def __init__(self):
        assert type(self) != GUI_CellElement_AbstCls
        GUI_element_AbstCls.__init__(self)



class Line_AbstCls(GUI_FullWidthElement_Cls):
    
    def __init__(self):
        assert type(self) != Line_AbstCls
        GUI_FullWidthElement_Cls.__init__(self)



class DistanceLine_Cls(Line_AbstCls):
    
    def __init__(self, height = 1):
        
        Line_AbstCls.__init__(self)
        assert isinstance(height, int)
        self.height = height
        

    def pasteOnFrame(self, master):
        
        self.lineFrame = tk.Frame(master)
        self.lineFrame.pack(side = "top", fill ="x")
        
        label = tk.Label(self.lineFrame, text = "\n".join([" "] * self.height))
        label.pack(side = "left", fill = "y")
    


class Line_Cls(Line_AbstCls):
    
    def __init__(self, description = ""):
        
        assert isinstance(description, str)
        
        Line_AbstCls.__init__(self)
        
        self._lineElements = []
        self._description = description
    
    
    def _addDescriptionToFrame(self, decription, masterFrame):
        
        Balloon(masterFrame).bind(masterFrame, decription)
    
    
    def pasteOnFrame(self, master):
        
        self.lineFrame = tk.Frame(master)
        
        if self._description:
            self._addDescriptionToFrame(self._description, self.lineFrame)
        
        for element in self._lineElements:
            element.addToLineFrame(self.lineFrame)
    
        self.lineFrame.pack(side = "left")
        
        rightFillingFrame = tk.Frame(master)
        rightFillingFrame.pack(side = "right", fill ="x")
    
    
    def hide(self):
        self.lineFrame #.hide()
        
    def addElement(self, element):
        assert isinstance(element, LineElement_AbstCls)
        self._lineElements.append(element)
    
    
    def __bool__(self):
        return bool(self._lineElements)



class LineElement_AbstCls(GUI_CellElement_AbstCls):

    def __init__(self):
        
        assert type(self) != LineElement_AbstCls
        GUI_CellElement_AbstCls.__init__(self)
        
        
    @abstractmethod
    def addToLineFrame(self, master):
        pass



class Bullet_Cls(LineElement_AbstCls):

    def addToLineFrame(self, master):
        
        label = tk.Label(master, text = BULLET)
        
        label.pack(side = "left", fill = "y")



class Arrow_Cls(LineElement_AbstCls):

    def addToLineFrame(self, master):
        
        label = tk.Label(master, text = ARROW)
        
        label.pack(side = "left", fill = "y")
   
    


class Space_Cls(LineElement_AbstCls):
    
    "An indent or spacing"
    
    def __init__(self, width):
        
        assert isinstance(width, int)
        
        self._width = width


    def addToLineFrame(self, master):
        
        label = tk.Label(master, text = " " * self._width)
        
        label.pack(side = "left", fill = "y")



class Label_Cls(LineElement_AbstCls):
    
    def __init__(self, text):
        
        assert isinstance(text, str)
        self._text = text


    def addToLineFrame(self, master):
        
        label = tk.Label(master, text = self._text)
        
        label.pack(side = "left", fill = "y")



class LineDecisionElement_AbstCls(LineElement_AbstCls):
    

    def __init__(self, GUI_Bridge):
        
        assert type(self) != LineDecisionElement_AbstCls
        LineElement_AbstCls.__init__(self)
        
        self.GUI_Bridge = GUI_Bridge
    
    
    def handleUserRequest(self):
        
        self.GUI_Bridge.processUserDecision(self)
        
        return True
    
    @abstractmethod
    def getValue(self):
        pass
    
    @abstractmethod
    def setValue(self, value):
        pass



class FileSystemBrowser_AbstCls(LineDecisionElement_AbstCls):
    
    def __init__(self, GUI_Bridge):
        
        assert type(self) != FileSystemBrowser_AbstCls
        LineDecisionElement_AbstCls.__init__(self, GUI_Bridge)
        

    def addToLineFrame(self, master):
        self.button = ttk.Button(master, text="...", width=3, command=self.handleUserRequest)
        self.button.pack(side = "left", fill = "y")


    def getValue(self, referenceFolder = None): 
        
        options = {}
        
        if referenceFolder:
            options['initialdir'] = referenceFolder
            
        ret = type(self).browseExecutor(**options).show()
            
        return ret
        
    def setValue(self, value):pass
        


class DirectoryBrowse_Cls(FileSystemBrowser_AbstCls):
    browseExecutor = Directory



class FileBrowse_Cls(FileSystemBrowser_AbstCls):
    browseExecutor = Open



class Entry_Cls(LineDecisionElement_AbstCls):
    
    min_width = 20
    
    entryFontIndex = 21
    
    entryFontsAvailable = [
        "Consolas", #0
        "Courier", #1
        "Cutive Mono", #2
        "DejaVu Sans Mono", #3
        "Droid Sans Mono", #4
        "Everson Mono", #5
        "Fira Mono", #6
        "Fixed", #7
        "Fixedsys", #8
        "FreeMono", #9
        "Go Mono", #10
        "HyperFont", #11
        "IBM Plex Mono", #12
        "Inconsolata", #13
        "Iosevka", #14
        "Letter Gothic", #15
        "Liberation Mono", #16
        "Lucida Console", #17
        "Menlo", #18
        "Monaco", #19
        "monofur", #20
        "Monospace", #21
        "Nimbus Mono L", #22
        "Noto Mono", #23
        "OCR-A", #24
        "OCR-B", #25
        "Overpass Mono", #26
        "Oxygen Mono", #27
        "PragmataPro", #28
        "Prestige Elite", #29
        "ProFont", #30
        "PT Mono", #31
        "Roboto Mono", #32
        "Source Code Pro", #33
        "Terminus", #34
        "Tex Gyre Cursor", #35
        "UM Typewriter", #36
        ]
    
    entries = []
    
    def __init__(self, GUI_Bridge):
        
        LineDecisionElement_AbstCls.__init__(self, GUI_Bridge)
        
        self.entries.append(self)
        
    
    def setWidth(self, numberOfSigns):
        
        assert isinstance(numberOfSigns, int)
        width = max([numberOfSigns, Entry_Cls.min_width])
        self.entry['width'] = width
        
        
    
    def setValue(self, value):
        
        if value is not None:
            text = str(value)
        else:
            text = ""
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.setWidth(self.getTextWidthExpected())


    def getTextWidthExpected(self):
        return len(self.entry.get()) + 5

    
    def getValue(self):
        
        return str(self.entry.get())
    
    
    def changeFont(self, index):
        font = tkFont.Font(family = Entry_Cls.entryFontsAvailable[index],
                            size = 12,
                            #weight = "bold"
                            )
        self.entry['font'] = font
        
    def addToLineFrame(self, master):
        
        #font = (Entry_Cls.entryFontsAvailable[], 12)
        
        self.entry = tk.Entry(master, validate="focusout", validatecommand = self.handleUserRequest)
        
        self.changeFont(Entry_Cls.entryFontIndex)
        
        self.entry.pack(side = "left", fill = "y")



        

class CheckBox_Cls(LineDecisionElement_AbstCls):
    
    checkbox_size = (15,15)
    
    
    def __init__(self, GUI_Bridge):
        
        LineDecisionElement_AbstCls.__init__(self, GUI_Bridge)
        
        self._active = False
        
    
    def _prepareImagesAndStyle(self):
        
        if "style" not in CheckBox_Cls.__dict__:
            
            CheckBox_Cls.style = ttk.Style()
            CheckBox_Cls.style.layout('no_indicatoron.TCheckbutton',
                         [('Checkbutton.padding', {'sticky': 'nswe', 'children': [
                             # ('Checkbutton.indicator', {'side': 'left', 'sticky': ''}),
                             ('Checkbutton.focus', {'side': 'left', 'sticky': 'w',
                                                    'children':
                                                    [('Checkbutton.label', {'sticky': 'nswe'})]})]})]
                         )

            CheckBox_Cls.checked_image    =  ImageTk.PhotoImage(Image.open(guiCheckboxesFiles_dir / "CheckBox_checked.png").resize(CheckBox_Cls.checkbox_size))
            CheckBox_Cls.unchecked_image  =  ImageTk.PhotoImage(Image.open(guiCheckboxesFiles_dir / "CheckBox_unchecked.png").resize(CheckBox_Cls.checkbox_size))
        
    
    
    def addToLineFrame(self, master):
        
        self._prepareImagesAndStyle()
        
        self.var = tk.BooleanVar(value = int(not self._active))
        
        self.checkBox = ttk.Checkbutton(master,
                                           variable = self.var, style='no_indicatoron.TCheckbutton',
                                           command=self.handleUserRequest)
        
        self.checkBox.pack(side = "left", fill = "y")
    
        self._synchronizeActivationState()
        
    
    def _synchronizeActivationState(self):
        
        if self._active:
            self.checkBox["image"] = CheckBox_Cls.checked_image
            
        else:
            self.checkBox["image"] = CheckBox_Cls.unchecked_image
            
        self.var.set(self._active)
            
    
    def getValue(self):
        return bool(self.var.get())
    
    
    def setValue(self, value):
        
        value = bool(value)
        
        if value != self._active:
            self._active = value
        
        self._synchronizeActivationState()
     
     
    def enable(self):
        "Published to and usable only by: GUI_Bridge"
        self.checkBox.config(state=tk.NORMAL)
     
     
    def disable(self):
        "Published to and usable only by: GUI_Bridge"
        self.checkBox.config(state=tk.DISABLED)
















