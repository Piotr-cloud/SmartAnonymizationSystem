'''
Created on Mar 3, 2023

@author: piotr
'''

from pathlib import Path
import sys

if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))

    
from PerformanceAnalysis.WorkersPerformanceAnalyzer import WorkersPerformanceAnalysisData_Cls
import json
from Configuration.integrationCfg import workersIncluder
from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls
from MainExecutor.ProcessingData import InputDataProcessor_Cls,\
    OutputDataProcessor_Cls, OutputDataProcessor_Stub_Cls
from MainExecutor.MainExecutor_ import MainExecutor_Cls
from NonPythonFiles import mainExecutorWrapperFiles_temp_dir
import os
from subprocess import Popen
from MainExecutor.Logger import Logger_Cls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj




class MainExecutorWrapper_Cls():
    """
    Provides subprocess abstraction while calling .execute() 
    .execute() returns WorkersPerformanceAnalysisData_Cls
    """
    
    def __init__(self, wpad = None, mode = 'No subprocess use'):
        
        assert mode in ['No subprocess use', 'To be run in a subprocess', 'Is ran as a subprocess']
        
        self.mode = mode
        
        # wpad - start
        if self.mode == 'Is ran as a subprocess':
            assert wpad is None
            wpad = WorkersPerformanceAnalysisData_Cls()
            
        else:
            assert isinstance(wpad, WorkersPerformanceAnalysisData_Cls)
        
        self.wpad = wpad
        
        self.current_wpad_filePath = None
        # wpad - end
        
        self.temp_dir = Path(str(mainExecutorWrapperFiles_temp_dir))
    
    
    def _cleanTempFileAndGetFilePath(self, fileBaseName):
        
        filePath = self.temp_dir / fileBaseName
        
        if filePath.is_dir(): 
            raise IsADirectoryError("Temp file cannot be used since the folowing path is a directory: " + str(filePath))
        
        if filePath.exists():
            os.remove(str(filePath))
            
        filePath_dir = filePath.parent
        
        if not filePath_dir.exists():
            os.makedirs(str(filePath_dir))
        
        return str(filePath)
    
        
    def _args_dump(self, args_filePath, cspc_filePath, wpad_filePath, args):
        
        dumpTuple = cspc_filePath, wpad_filePath, args
    
        with open(str(args_filePath), 'w') as f:
            json.dump(dumpTuple, f, indent=2)
    
    
    def _args_load(self, filePath):
        
        with open(filePath) as f:
            cspc_filePath, wpad_filePath, args = json.load(f)
            
        return cspc_filePath, wpad_filePath, args
    
    
    def _executeFromFile(self, args_filePath):
        
        assert self.mode == 'Is ran as a subprocess'
        
        cspc_filePath, wpad_filePath, args = self._args_load(args_filePath)
        
        cspc = ClassesProcessingConfiguration_Cls(workersIncluder)
        cspc.loadFromFile(cspc_filePath)
        
        self.current_wpad_filePath = wpad_filePath
        
        self.execute(cspc, *args)
    
    
    def _runSubprocessExecution(self, args_filePath, wpad_filePath):
        
        args = [sys.executable, __file__, str(args_filePath)]
        
        p = Popen(args)
        
        p.communicate()
        
        if  p.returncode != 0:
            print(" -> Warning!! Could not process further due to subprocess termination with error. See above error")
            
            wpad_filePath = Path(wpad_filePath)
            
            if wpad_filePath.exists() and wpad_filePath.is_file():
                self.wpad.importFromFile(wpad_filePath)
                
        else:
            self.wpad.importFromFile(wpad_filePath)
    
    
    
    def execute(self,
                cspc,
                repetitions,
                
                inputFilesPaths,
                outputDir,
                
                additionalProcessingParams_dict = {},
                        
                streamProcessing_flag = False,
                ramOnly_flag = False,
                
                startupTests_flag = True,
                printTimeConsumptionTree_flag = True,
                consoleLogFilePath = None):
        
        assert isinstance(repetitions, int) and repetitions > 0
        
            
        if self.mode == 'To be run in a subprocess':
            cspc_filePath = self._cleanTempFileAndGetFilePath("cspc.json")
            args_filePath = self._cleanTempFileAndGetFilePath("args.json")
            wpad_filePath = self._cleanTempFileAndGetFilePath("wpad.json")
            
            cspc.saveToFile(cspc_filePath, silent = True)
            
            dump_args_list = [ # list here all arguments of .execute except cspc(that is saved in another file)
                
                repetitions,
                [str(path_) for path_ in inputFilesPaths],
                outputDir,
                        
                additionalProcessingParams_dict,
                        
                streamProcessing_flag,
                ramOnly_flag,
                
                startupTests_flag,
                printTimeConsumptionTree_flag,
                consoleLogFilePath
                ]
            
            
            self._args_dump(
                args_filePath,
                cspc_filePath,
                wpad_filePath,
                
                dump_args_list
                
                )
            
            self._runSubprocessExecution(args_filePath, wpad_filePath)
        
        
        elif self.mode in ['Is ran as a subprocess', 'No subprocess use']:
            
            if consoleLogFilePath is not None:
                logger = Logger_Cls(consoleLogFilePath)
                logger.redirect()
                consoleLogFilePath = logger.getFilePath()
            
            for repetitionIdx in range(repetitions):
                
                if repetitions > 1:
                    
                    print("="*100)
                    print("\n\tRepetition: {}/{}\n".format(str(repetitionIdx + 1), str(repetitions)))
                    print("="*100)
                
                
                framesSave_dir      =  additionalProcessingParams_dict.get("framesSave_dir", None)
                maxFPS              =  additionalProcessingParams_dict.get("maxFPS", None)
                maxHeight           =  additionalProcessingParams_dict.get("maxHeight", None)
                maxWidth            =  additionalProcessingParams_dict.get("maxWidth", None)
                looseProportion     =  additionalProcessingParams_dict.get("looseProportion", False)
                
                outFilePrefix       =  additionalProcessingParams_dict.get("outFilePrefix", "")
                outputFileSuffix    =  additionalProcessingParams_dict.get("outputFileSuffix", "")
                cleanFirst_flag     =  additionalProcessingParams_dict.get("cleanFirst_flag", False)
                
                no_cuda             =  additionalProcessingParams_dict.get("no_cuda", False)
                
                if no_cuda:
                    os.environ["CUDA_VISIBLE_DEVICES"] = "" # force to disable torch GPU support
                
                inputDataProcessor = InputDataProcessor_Cls(inputFilesPaths,
                                                            framesSave_dir,
                                                            maxFPS,
                                                            maxHeight,
                                                            maxWidth,
                                                            looseProportion)
                
                
                if outputDir is not None:
                    outputDataProcessor = OutputDataProcessor_Cls(outputDir = outputDir,
                                                                  cleanFirst_flag = cleanFirst_flag,
                                                                  outFilePrefix = outFilePrefix,
                                                                  outputFileSuffix = outputFileSuffix,
                                                                  framesSave_dir = framesSave_dir,
                                                                  consoleLogFilePath = consoleLogFilePath)
                else:
                    outputDataProcessor = OutputDataProcessor_Stub_Cls()
                
                
                processingContiguration = cspc.resolve()
                
                self._printUserRequest(processingContiguration, inputDataProcessor, outputDataProcessor, streamProcessing_flag)
                
                mainExecutor = MainExecutor_Cls(
                    processingConfiguration  =  processingContiguration
                    )
            
                mainExecutor.execute(
                    inputDataProcessor      =  inputDataProcessor,
                    outputDataProcessor     =  outputDataProcessor,
                    
                    streamProcessing_flag   =  streamProcessing_flag,
                    ramOnly_flag            =  ramOnly_flag
                    )
                
                self.wpad.importFromLogger(workersPerformanceLoggerObj)
                
                if self.current_wpad_filePath is not None:
                    self.wpad.dumpToFile(self.current_wpad_filePath)
                
                if printTimeConsumptionTree_flag:
                    stepsLogs = mainExecutor.getStepsLogs()
                    print(stepsLogs.getTimeConsumptionTreeString())
        
        
            if consoleLogFilePath is not None:
                logger.revertRedirection()
                
                
        else:
            raise RuntimeError("MainExecutorWrapper_Cls: Mode is corrupted")


    def _printUserRequest(self, processingContiguration, inputDataProcessor, outputDataProcessor, streamProcessing_flag):
        
        def getStatementStringOfPairs(paramsParis_list):
            
            if paramsParis_list:
                
                longestLeft_len = 0
                
                for specificParam in paramsParis_list:
                    longestLeft_len = max([len(specificParam[0]), longestLeft_len])
                 
                longestLeft_len += 5
                 
                specificParamLines = []
                 
                for specificParam in paramsParis_list:
                    specificParamLines.append((specificParam[0] + ": ").ljust(longestLeft_len) + str(specificParam[1]))
                
                output_str = "".join([str(el) + "\n" for el in specificParamLines])
                    
                return output_str
            
            else:
                return ""
        
        
        statement = ""
        
        # Details
        
        statement += "Processing method: "
        if streamProcessing_flag:   statement += "STREAM"
        else:                       statement += "SEQUANTIAL"
        statement += "\n\n"
            
        statement += "\nSpecific params:\n\n"
        statement += getStatementStringOfPairs(inputDataProcessor.getBasicParams())
        statement += getStatementStringOfPairs(outputDataProcessor.getBasicParams())
        
        statement += "\nWorkers chosen by user:\n\n"
        statement += getStatementStringOfPairs(processingContiguration.getBasicParams())
        
        if statement:
            print(statement)
        




if __name__ == "__main__":
    
    
    mew = MainExecutorWrapper_Cls(mode='Is ran as a subprocess')
    mew._executeFromFile(sys.argv[1])
    
    
    
    