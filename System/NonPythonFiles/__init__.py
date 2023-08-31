

from pathlib import Path
import os



nonPythonFiles_dir   =  Path(__file__).parent

temporaryFiles_dir   =  nonPythonFiles_dir / "temp"


editorOptions_dir              =  temporaryFiles_dir / "EditorOptions"
mainExecutorWrapperFiles_dir   =  temporaryFiles_dir / "MainExecutorWrapper"
memoryMonitorWorkspace_dir     =  temporaryFiles_dir / "MemoryMonitorWorkspace"
processingCfgFiles_dir         =  temporaryFiles_dir / "ProcessingConfigurationFiles"
testData_dir                   =  temporaryFiles_dir / "TestData"

npArraysHDStorage_dir          =  temporaryFiles_dir / "NpArrayHardDriveRuntimeStorage"
npArrayDebugDisplay_dir        =  temporaryFiles_dir / "NpArrayDebugDisplay"
otherDebugFiles_dir            =  temporaryFiles_dir / "OtherDebugFiles"

workersFiles_dir               =  nonPythonFiles_dir / "WorkersFiles"
guiFiles_dir                   =  nonPythonFiles_dir / "GUI"


npArrayDebugDisplay_defaultOutputFile       =  npArrayDebugDisplay_dir / "nparrays"
npArrayDebugDisplay_defaultBulkDumpFolder   =  npArrayDebugDisplay_dir / "BulkDump"


workspaces_dir          =  temporaryFiles_dir / "Workspaces"
graphvizWorkspace_dir   =  workspaces_dir / "Graphviz"
EasyOcrWorskapce_dir    =  workspaces_dir / "EasyOCR"

guiCheckboxesFiles_dir  =  guiFiles_dir / "CheckBoxes"


mainExecutorWrapperFiles_temp_dir  =  mainExecutorWrapperFiles_dir / "temp"
memoryMonitorWorkspace_Logs_dir    =  memoryMonitorWorkspace_dir / "Logs"


# The following two shall not be in this file, but there is no dedicated file for them
pythonEntryPointExpected_dir   =  nonPythonFiles_dir.parent
projectRoot_dir                =  pythonEntryPointExpected_dir.parent



def getUserDecision_memoryMonitoring():
    return True  # change to True to turn on Memory monitor logging

        
if not memoryMonitorWorkspace_Logs_dir.exists():
    os.makedirs(str(memoryMonitorWorkspace_Logs_dir))








if __name__ == "__main__":
    
    from NonPythonFiles.WorkersFiles.Detectors.WpodNet import *
    from NonPythonFiles.WorkersFiles.Detectors.UnderstandAI import *
    from NonPythonFiles.WorkersFiles.ContentSwappers.WuHukaiFaceSwapper import *
    from NonPythonFiles.WorkersFiles.Detectors.Haar import *
    from NonPythonFiles.WorkersFiles.Detectors.Dnn import *
    from NonPythonFiles.WorkersFiles.Trackers.DeepSort import *
    
    
    def validatePathsExistance(variablesDict):
        indent_ = 35
        for var_name, var_val in list(variablesDict.items()):
            if isinstance(var_val, Path):
                if not temporaryFiles_dir in var_val.parents:
                    if not var_val.exists():
                        raise FileNotFoundError("The following path does not exist: " + str(var_val))
                    indent_ = max([len(str(var_name)), indent_])
                    print((str(var_name) + ": ").ljust(indent_ + 5) + str(var_val))
    
    
    validatePathsExistance(globals())
    


