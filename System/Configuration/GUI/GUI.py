
from Configuration.GUI.GUI_frontendBridge import GUI_Bridge_Cls
from pathlib import Path
from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls

import tkinter as tk
import os
basestring = str
import json 

from Configuration.GUI.GUI_cfg import icondata,  _version_, options_fn,\
    defaultOpt
from Configuration.ConfigurationObjects.LoadingErrorCodes import Loading_OK,\
    Loading_NoImportRequested

options_fn, defaultOpt # used by methods as global object


class VerticalScrolledFrame_Cls():
    """
    A vertically scrolled Frame that can be treated like any other Frame
    ie it needs a master and layout and it can be a master.
    keyword arguments are passed to the underlying Canvas (eg width, height)
    
    Class implementation is based on: https://gist.github.com/novel-yet-trivial/3eddfce704db3082e38c84664fc1fdf8 
    """
    def __init__(self, master, **kwargs):
        
        self.outer = tk.Frame(master)

        self.vsb = tk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)
        self.hsb = tk.Scrollbar(self.outer, orient=tk.HORIZONTAL)
        self.hsb.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.canvas = tk.Canvas(self.outer, highlightthickness=0, **kwargs)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vsb.set
        self.canvas['xscrollcommand'] = self.hsb.set
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vsb['command'] = self.canvas.yview
        self.hsb['command'] = self.canvas.xview

        self.inner = tk.Frame(self.canvas)
        # pack the inner Frame into the Canvas with the topleft corner 4 pixels offset
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))
        self.frames = (self.inner, self.outer)

    def __getattr__(self, item):
        """geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
        all other attributes (_w, children, etc) are passed to self.inner"""
        return getattr(self.frames[item in self.outer_attr], item)

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mouse(self, event=None):
        """mouse event bind does not work, so this hack allows the use of bind_all
        Linux uses Buttons, Windows/Mac uses MouseWheel"""
        for ev in ("<Button-4>", "<Button-5>", "<MouseWheel>"):
            self.canvas.bind_all(ev, self._on_mousewheel)

    def _unbind_mouse(self, event=None):
        for ev in ("<Button-4>", "<Button-5>", "<MouseWheel>"):
            self.canvas.unbind_all(ev)

    def _on_mousewheel(self, event):
        """Linux uses event.num; Windows / Mac uses event.delta"""
        if event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units" )



class GUI_Cls():
    
    def __init__(self, cpc, noRunButton = False):
        
        assert isinstance(cpc, ClassesProcessingConfiguration_Cls)
        assert isinstance(noRunButton, bool)
        
        self._noRunButton = noRunButton
        
        self.master = tk.Tk()
        #print("Using tkinter version:", self.master.tk.call("info", "patchlevel"))
        #self.master.option_add("*Font", "lucida")
        
        global options_fn
        
        self.options_fn = options_fn
        self.opt = self.loadOptions()
        
        self.cpc = cpc
        
        self.fn = None
        self.bs = None
        
        self.master.title("Processing Configuration Editor")
        icon = tk.PhotoImage(data=icondata)
        self.master.tk.call('wm', 'iconphoto', self.master._w, icon)
        self.master.geometry(self.opt.get('geometry'))
        self.master.protocol("WM_DELETE_WINDOW", self._quit)
        self.master.bind("<Control - S>", self._saveShortcut)
        self.master.bind("<Control - s>", self._saveShortcut)

        self.constructHeaderFrame(self.master)
        
        self.data_frame = tk.Frame(self.master)
                
        self.display = VerticalScrolledFrame_Cls(self.data_frame)
        self.display.pack(fill=tk.BOTH, expand=True)
        self.data_frame.pack(fill=tk.BOTH, expand=True)
         
        self.status = tk.StringVar(self.master, "Version: "+".".join(map(str,_version_)))
        lbl = tk.ttk.Label(self.master, textvariable=self.status)
        lbl.pack(fill=tk.X)
        

        #self.pack(fill=tk.BOTH, expand=True)
        
        self.quitToStartProcessing = False
        
        self.constructCfgFrame(self.cpc, self.display)
        
        self.updateConfigurationFilePath()
        
    
    def updateConfigurationFilePath(self):
        
        filePath = self.cpc.getConfigurationFilePath()
        
        try:
            filePath = Path(filePath)
            #assert filePath.exists()
        except: 
            filePath = None
            
        if filePath is None:
            textToSet = "< No file reference >"
        else:
            textToSet =  str(filePath)
        
        self.filePath_label["text"] = textToSet
        self.filePath = filePath
                                           
        return bool(filePath)
    
    
    def removeConfigurationFilePathReference(self):
        
        self.cpc.removeConfigurationFilePathReference()
        self.updateConfigurationFilePath()
        
    
    def constructHeaderFrame(self, master):
        
        self.headerFrame = tk.LabelFrame(master)
        
        fileInfo_frame = tk.Frame(self.headerFrame, pady = 5)
        fileInfo_frame.pack(side = "top", fill = tk.X)
        
        
        introPath_label = tk.Label(fileInfo_frame, text = "Config file:")
        introPath_label.pack(side = "left", padx = 20)
        
        
        self.filePath_frame = tk.Frame(fileInfo_frame)
        self.filePath_frame.pack(side = "left", fill = tk.X, expand=True) # This frame is not needed
        self.filePath_frame.bind('<Configure>', lambda _: self.filePath_label.config(wraplength=max([100,self.filePath_frame.winfo_width()])))
        
        
        self.filePath_label = tk.Label(self.filePath_frame, text = "Initial value"*20, justify="center")
        self.filePath_label.pack(side = "left")

        fileOperationButtonsWrapping_frame = tk.Frame(self.headerFrame)
        fileOperationButtonsWrapping_frame.pack(side = "top", fill=tk.X)
        
        leftButtons_frame = tk.Frame(fileOperationButtonsWrapping_frame)
        leftButtons_frame.pack(side = "left")
        
        
        rightButtons_frame = tk.Frame(fileOperationButtonsWrapping_frame)
        rightButtons_frame.pack(side = "right", fill = tk.X)
        
        removeFileRef_button = tk.Button(leftButtons_frame, text = "Remove file reference", command = self.removeConfigurationFilePathReference)
        removeFileRef_button.pack(side = "left")
        
        self.load_button = tk.Button(rightButtons_frame, text = "Reload", command=self.reload, height = 1, width = 15)
        self.load_button.grid(column = 1, row = 1, padx = 20)
        
        self.load_button = tk.Button(rightButtons_frame, text = "Load from...", command=self.loadFrom, height = 1, width = 15)
        self.load_button.grid(column = 2, row = 1, padx = 20)
        
        self.saveAs_button = tk.Button(rightButtons_frame, text = "Save as...", command=self.saveAs, height = 1, width = 15)
        self.saveAs_button.grid(column = 3, row = 1, padx = 20)
        
        self.save_button = tk.Button(rightButtons_frame, text = "Save", command=self.save, height = 1, width = 15)
        self.save_button.grid(column = 4, row = 1, padx = 20)
        
        exitGuiButtonFrame = tk.Frame(self.headerFrame)
        
        if self._noRunButton:
            exitGuiButton = tk.Button(rightButtons_frame, text = "Exit", height = 1, width = 15,command=self._quit)
        else:
            exitGuiButton = tk.Button(rightButtons_frame, text = "Exit & RUN processing", height = 2, width = 30,command=self.quitToStartProcessing)
        
        exitGuiButton.grid(column = 5, row = 1, padx = 20)
        
        exitGuiButtonFrame.pack(side = "top", fill = "x")
        
        self.headerFrame.pack(side = "top", fill = "x")
    
    
    def _getFilePath(self):
        return None
    
    
    def stateResultOfCfgLoading(self, loadingErrorCode):
        
        if loadingErrorCode != Loading_OK and loadingErrorCode != Loading_NoImportRequested:
            self.stateWarning("Cfg file loading result: \n\n\"" + str(loadingErrorCode) + "\"\n\nPlease review the configuration before processing!")
    
        
    def stateError(self, errorStatement):
        tk.messagebox.showerror('Error', errorStatement)
        print("Error: " + str(errorStatement))

    
    def stateWarning(self, warningStatement):
        tk.messagebox.showwarning('Warning', warningStatement)
        print("Warning: " + str(warningStatement))
    
    
    def _save(self, filePath):
        
        if filePath:
            
            self.cpc.saveToFile(filePath)
            
            self.updateConfigurationFilePath()
        
        else:
            self.saveAs()

        self.saveOptions()
    
    
    def _saveShortcut(self, *args):
        self.save()
    
    
    def save(self):
        
        self._save(self.filePath)
            
        
    def saveAs(self):
        
        filePath = tk.filedialog.SaveAs(initialdir= self.opt.get('dir')).show()
        
        if filePath:
            self._save(filePath)
        
    
    def _load(self, filePath):
        
        result = self.cpc.loadFromFile(filePath)
        
        self.updateConfigurationFilePath()
        
        self.guiBridge.fullSynchronize()
        
        self.stateResultOfCfgLoading(result)
        
        self.saveOptions()
        
        return result


    def loadFrom(self):
        
        filePath = tk.filedialog.Open(initialdir= self.opt.get('dir')).show()
        
        if filePath:
            
            filePath = Path(filePath)
            
            if filePath.exists():
                
                dir_ = filePath.parent
                    
                self.opt['dir'] = str(dir_)
                
                self._load(filePath)
        

        
    def reload(self):
        
        if self.filePath:
            self._load(self.filePath)
        
        else:
            print("Cannot load! No file reference!")
            
    
    def constructCfgFrame(self, configurationObj, master):
        
        self.guiBridge = GUI_Bridge_Cls()
        
        self._configurationObjGUI = self.guiBridge.construct_frontendConfigurationObject(configurationObj, None, master, False)
        
        self.guiBridge.fullSynchronize()
    
    
    def runGUI(self):
        
        self.master.mainloop()
        
        if self.quitToStartProcessing:
            return self.cpc
        else:
            return None
        
    
    def saveOptions(self):
        
        options_fn_dir = self.options_fn.parent
        
        if not options_fn_dir.exists():
            os.mkdir(str(options_fn_dir))
            
        with open(self.options_fn, 'w') as f:
            json.dump(self.opt, f, indent=2)
    
    
    def loadOptions(self):
        
        global defaultOpt
        
        defaultOpt = defaultOpt.copy()
        
        try:
            with open(self.options_fn) as f:
                defaultOpt.update(json.load(f))
        except Exception as e:
            print("default options used due to", e)
        
        return defaultOpt
    
    
    def quitToStartProcessing(self):
        self.quitToStartProcessing = True
        self._quit()
    
        
    def _quit(self):
        if self.opt.get('save_position'):
            self.opt['geometry'] = self.master.geometry()
        else:
            # strip the position information; keep only the size information
            self.opt['geometry'] = self.master.geometry().split('+')[0]
        self.master.quit()
        self.master.destroy()
        self.saveOptions()
        

    


if __name__ == "__main__":
    
    from Configuration.integrationCfg import workersIncluder
        
    def main():
    
        cpc = ClassesProcessingConfiguration_Cls(workersIncluder)
        gui = GUI_Cls(cpc)
        #gui.top.load_path(" ".join(sys.argv[1:]))
        result = gui.runGUI()
        print("Result: " + str(result))
        
    try:
        main()
        
    except Exception as e:
        tk.messagebox.showerror("Fatal error!", "Config Editor crashed.\n\n" + str(e))
        raise
