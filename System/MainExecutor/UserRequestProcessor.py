'''
Created on Sep 19, 2022

@author: piotr

Loads 
'''
import re
from pathlib import Path
from Configuration.GUI.GUI import GUI_Cls
import os
import mimetypes
from Configuration.ConfigurationObjects.LoadingErrorCodes import Loading_OK
import time
from Configuration.GUI.GUI_cfg import debug
from PolymorphicBases.ABC import Base_AbstCls, abstractmethod
from PerformanceAnalysis.WorkersPerformanceAnalyzer import WorkersPerformanceAnalysisData_Cls
from MainExecutor.MainExecutorWrapper import MainExecutorWrapper_Cls
from Tester.CspcConfigurationGenerator.ConfigurationsGenerator import EachWorkerInRandomScenario_ConfigurationGenerator_Cls
import math
from MainExecutor.Logger import Logger_Cls
from PerformanceAnalysis.FormattingUnits import formatTimestamp
from Space._2D.Array import npArrayAbstractionConfiguration
import json



class UserRequestProcessor_AbstCls(Base_AbstCls):
    """
    An object that is base level caller
    this object is responsible for validation of input data and implement foundamental sequence  
    """
    
    startStatement = "Procedure started!"
    endSleep_s = 0.1
    endStatement = "Procedure completed!"
    
    def __init__(self):
        
        assert type(self) != UserRequestProcessor_AbstCls
        
        from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls
        from Configuration.integrationCfg import workersIncluder
        
        self._cspc_type = ClassesProcessingConfiguration_Cls
        self._workersIncluder = workersIncluder
                    
    

    def _convertArg_intGT_0(self, arg_):
        try:
            arg__ = int(arg_)
            assert arg__ > 0
            return arg__
        except:
            raise TypeError("Argument must be an integer grater than 0. Provided: " + str(arg_))
        
    
    def run(self, *args, **kw_args):
        
        print(self.__class__.startStatement)
        
        npArrayAbstractionConfiguration._cleanDefaultLocationRootFolder()
        
        if debug:
            
            print("Args:")
            print("\n".join(args))
            for key_, val_ in kw_args.items():
                print("{} : {}".format(key_, val_))
        
        self._startHook()
        
        exec_ret = self._run(*args, **kw_args)
        
        self._endHook()
        
        npArrayAbstractionConfiguration._cleanDefaultLocationRootFolder()
        
        time.sleep(self.__class__.endSleep_s)
        
        print(self.__class__.endStatement)
        
        return exec_ret
    
    
    def _startHook(self):
        pass
    
    
    def _endHook(self):
        pass
        
    
    def _getListOfInterestingFilesAtPath(self, path_):
        
        outputFilesPaths_list = []
        
        if path_.is_dir():
            
            for root, _, files in os.walk(path_):
                root = Path(root)
                for file_ in files:
                    filePath = root / file_
                    if self._checkIfFileIsInteresting(filePath):
                        outputFilesPaths_list.append(filePath)

                break # no recursion
            
        elif path_.is_file():
            if self._checkIfFileIsInteresting(path_):
                outputFilesPaths_list.append(path_)
            
        return outputFilesPaths_list
    
    
    def _checkIfImage(self, filePath):
        
        fileType = mimetypes.guess_type(filePath)[0]
        
        if fileType and fileType.startswith('image'):
            return True
        else:
            return False
    
    
    def _checkIfVideo(self, filePath):
        
        fileType = mimetypes.guess_type(filePath)[0]
        
        if fileType and fileType.startswith('video'):
            return True
        else:
            return False
    
    
    def _checkIfFileIsInteresting(self, filePath):
        
        return self._checkIfImage(filePath) or self._checkIfVideo(filePath)   
        
    
    def _filterPathsWithRegexPatterns(self, filesPaths, regexPatterns):
        
        output_list = []
        
        for regexPattern in regexPatterns:
            
            filteredList = list(filter(regexPattern.match, [str(el) for el in filesPaths]))
            
            filesPaths = [filePath for filePath in filesPaths if filePath not in filteredList]
            
            output_list += filteredList
        
        return output_list   
    
    
    def _getListOfPathsOfInputFilesToProcess(self, inputPaths, regexPatterns = None):
        
        nonFiltered_filePaths_list = []
        
        for inputPath in inputPaths:
            for filePath in self._getListOfInterestingFilesAtPath(inputPath):
                if filePath not in nonFiltered_filePaths_list:
                    nonFiltered_filePaths_list.append(filePath)
        
        if regexPatterns:
            output_list = self._filterPathsWithRegexPatterns(nonFiltered_filePaths_list, regexPatterns)
        else:
            output_list = nonFiltered_filePaths_list
        
        return output_list
    
    
    def getListOfPathsOfInputFilesToProcess(self, inputPaths, inputFilters):
        
        # arguments validation
        inputPaths    =  [Path(inputPath) for inputPath in inputPaths]
        
        if inputFilters:
            inputFilters  =  [re.compile(regex_) for regex_ in inputFilters]
        
        inputFilesPaths_list = self._getListOfPathsOfInputFilesToProcess(inputPaths, inputFilters)
        
        return inputFilesPaths_list
    
    
    
    @abstractmethod
    def _run(self):
        pass
    



class UserRequestProcessor_Config_Cls(UserRequestProcessor_AbstCls):
    
    startStatement  = "Configuration started..."
    endStatement    = "Configuration completed"
    
    def _run(self, cfgFilePath):
        
        cspc = self._cspc_type(self._workersIncluder)
        
        self._gui = GUI_Cls(cpc = cspc,
                            noRunButton = True) # initialize gui with default settings
        
        if cfgFilePath is not None:
            self._gui._load(filePath = cfgFilePath) # try to load decisions from file

        self._gui.runGUI()
        



class UserRequestProcessor_WithMainExecutionSequence_AbstCls(UserRequestProcessor_AbstCls):
    
    def __init__(self):
        UserRequestProcessor_AbstCls.__init__(self)
        
        self._logger   = None
        self._txt      = None
        self._json     = None
    
    
    def _endHook(self):
        self._endSessionLogging()
        
    
    def _prepareSessionLogging(self, outputDir, fileBaseName, filesOverwriteWarning_flag, cleanConsoleLogs_flag):
        
        outputDir = Path(outputDir)
        
        paths_list = []
        
        filesToOverwrite_list = []
        errorCause_pathIsDir_list = []
        
        if fileBaseName:
            fileBaseName += "_"
        
        for suffix_ in [
            "ConsoleLogs.log",        # _log
            "WorkersPerformanceStr.txt",  # _txt
            "WorkersPerformance.json"     # _json
            ]:
                
            path_ = outputDir / (fileBaseName + suffix_)
            
            parentPath = path_.parent
            
            if not parentPath.exists():
                os.makedirs(str(parentPath)) 
            
            if path_.exists():
                if path_.is_dir():
                    errorCause_pathIsDir_list.append(path_)
                    raise IsADirectoryError("The follwing path cannot be used as session logs, since it exists and is not a file: " + str(path_))
                if filesOverwriteWarning_flag:
                    filesToOverwrite_list.append(path_)
            
            paths_list.append(path_)
        
        # raise rrrors
        if errorCause_pathIsDir_list:
            raise IsADirectoryError("The following paths are directories: " + "".join(["\n - " + str(el) for el in errorCause_pathIsDir_list]))
        
                    
        if filesToOverwrite_list:
            pathsStatement_str = "".join(["\n - " + str(el) for el in filesToOverwrite_list])
            print("Overwrite Warning! The following files exists and are going to be overwriten: " + pathsStatement_str)
        
        
        _log, self._txt, self._json = paths_list
        
        if cleanConsoleLogs_flag and _log.exists():
            os.remove(str(_log)) # remove console logs file in advance, since it is specially treated
        
        self._logger = Logger_Cls(_log)
        self._logger.redirect()
    
    
    def _dumpSessionLogs(self, wpad):
        
        wpad.dumpToFile(self._json)
        
        wpds = wpad.getWorkersPerformanceDataString()
        
        with open(self._txt, "w") as file:
            file.write(wpds)
        
        return wpds
    
    
    def _endSessionLogging(self):
        
        if self._logger is not None:
            self._logger.revertRedirection()




class UserRequestProcessor_Main_Cls(UserRequestProcessor_WithMainExecutionSequence_AbstCls):
    
    startStatement = "Execution started!"
    endSleep_s = 0.1
    endStatement = "Execution completed!"
    
    def _run(self,
             
             inputPaths,
             outputDir,
             
             inputFilters,
             
             cfgFilesPaths,
             noEdit_flag,
        
             streamProcessing_flag,
             ramOnly_flag,
             
             additionalProcessingParams_dict,
             
             inASubprocesses_flag = True,
             plainOutput_flag = False,
             
             printTimeConsumptionTree_flag = True,
             printWorkersPerformanceData_flag = True):

        outputDir = str(Path(outputDir))
        
        self._prepareSessionLogging(outputDir, "", False, cleanConsoleLogs_flag = additionalProcessingParams_dict['cleanFirst_flag'])

        inputFilesPaths = self.getListOfPathsOfInputFilesToProcess(inputPaths, inputFilters)
        
        if not inputFilesPaths:
            print("Warning! No input files found")
            
        assert isinstance(noEdit_flag, bool)
        
        if len(cfgFilesPaths) <= 1:
            
            try:
                cfgFilePath = cfgFilesPaths[0]
            except:
                cfgFilePath = None
                
            cspc = self._cspc_type(self._workersIncluder)
        
            cpcLoad_result = cspc.loadFromFile(cfgFilePath)
        
            if noEdit_flag and cpcLoad_result == Loading_OK:
                pass
            
            else:
                self._gui = GUI_Cls(cpc = cspc,
                                    noRunButton = False)
                
                self._gui.stateResultOfCfgLoading(cpcLoad_result)
                
                cspc = self._gui.runGUI()
        
        
            if cspc: # processing configuration defined and "run" button clicked
                
                wpad = WorkersPerformanceAnalysisData_Cls()
                
                mew = MainExecutorWrapper_Cls(wpad)
                
                mew.execute(cspc = cspc,
                            repetitions = 1,
                            
                            inputFilesPaths = inputFilesPaths,
                            
                            outputDir = outputDir,
                            
                            additionalProcessingParams_dict = additionalProcessingParams_dict,
                            
                            streamProcessing_flag = streamProcessing_flag,
                            ramOnly_flag = ramOnly_flag,
                            
                            startupTests_flag = True,
                            printTimeConsumptionTree_flag = printTimeConsumptionTree_flag,
                            consoleLogFilePath = self._logger.getFilePath())
                
                wpds = self._dumpSessionLogs(wpad)
                
                if printWorkersPerformanceData_flag:
                    print(wpds)
        
        else:
        
            processingData_list = []
            repetitionProtection_set = set()
            
            outputMapping_dict = {}
            
            longestCfgFilePath = ""
            
            for cfgFilePath in sorted(cfgFilesPaths):
                
                if cfgFilePath in repetitionProtection_set: 
                    print("Warning! Cfg file repeated: " + str(cfgFilePath) + "  ==>  SKIPPED")
                    continue
                else:
                    repetitionProtection_set.add(cfgFilePath)
                
                cspc = self._cspc_type(self._workersIncluder)
                cpcLoad_result = cspc.loadFromFile(cfgFilePath)
                
                if cpcLoad_result == Loading_OK:
                    
                    outputDir_forCfg_base = cfgFilePath.stem
                    
                    outputClasificationStr_candidate = outputDir_forCfg_base
                    
                    index = 0
                    
                    while outputClasificationStr_candidate in outputMapping_dict:
                        index += 1
                        outputClasificationStr_candidate = outputDir_forCfg_base + "_" + str(index)
                    
                    outputMapping_dict[outputClasificationStr_candidate] = cfgFilePath
                    
                    if not plainOutput_flag:
                        # candidate is unique - create dir if not existing
                        outputDir_forCfg_candidate = Path(outputDir) / outputClasificationStr_candidate
                        
                        if not outputDir_forCfg_candidate.exists():
                            os.makedirs(outputDir_forCfg_candidate)
                        
                        elif outputDir_forCfg_candidate.is_file():
                            raise IsADirectoryError("The following path cannot be taken as output dir since it refer to a file")
                    
                        outputClasificationStrExtended = outputDir_forCfg_candidate
                        
                    else:
                        outputClasificationStrExtended = outputClasificationStr_candidate
                        
                    processingData_list.append((cspc, cfgFilePath, outputClasificationStrExtended))
                        
                    cfgFilePath = str(cfgFilePath)
                    
                    if cfgFilePath > longestCfgFilePath:
                        longestCfgFilePath = cfgFilePath
                else:
                    print("Warning! The following configuration file is invalid: " + str(cfgFilePath) + "  ==>  SKIPPED")

            
            wpds = ""
        
            if processingData_list: # processing configuration defined and "run" button clicked
                
                printSeparationStatement_flag = len(processingData_list) > 1
                
                # servicing outputFileSuffix
                if "outputFileSuffix" not in additionalProcessingParams_dict: additionalProcessingParams_dict["outputFileSuffix"] = ""
                outputFileSuffix_staticPart = additionalProcessingParams_dict["outputFileSuffix"]
                
                # dump mapping: cfg file to output dir
                outputMappingFilePath = Path(outputDir) / "outputMapping.json" 

                with open(str(outputMappingFilePath), 'w') as f:
                    json.dump({str(val_):str(key_) for key_, val_ in outputMapping_dict.items()}, f, indent=2)
                 
                summarizing_wpad = WorkersPerformanceAnalysisData_Cls()
                
                for cspc, cfgFilePath, outputClasificationStrExtended in processingData_list:
                    
                    if plainOutput_flag:
                        outputDir_forCfg = outputDir
                        if outputFileSuffix_staticPart:
                            additionalProcessingParams_dict["outputFileSuffix"] = outputFileSuffix_staticPart + "_" + outputClasificationStrExtended
                        else:
                            additionalProcessingParams_dict["outputFileSuffix"] = outputClasificationStrExtended
                    else:
                        outputDir_forCfg = outputClasificationStrExtended
                        
                    wpad = WorkersPerformanceAnalysisData_Cls()
                    
                    if inASubprocesses_flag:
                        mew = MainExecutorWrapper_Cls(wpad = wpad, mode = 'To be run in a subprocess')
                    else:
                        mew = MainExecutorWrapper_Cls(wpad = wpad, mode = 'No subprocess use')
                    
                    if printSeparationStatement_flag:
                        separateLine_str = "\n" + "#" *(33 + len(longestCfgFilePath))
                        print(separateLine_str + "\n# Processing configuration: " + str(cfgFilePath) + separateLine_str)
                    
                    mew.execute(cspc = cspc,
                                repetitions = 1,
                                
                                inputFilesPaths = inputFilesPaths,
                                
                                outputDir = str(outputDir_forCfg),
                                
                                additionalProcessingParams_dict = additionalProcessingParams_dict,
                                
                                streamProcessing_flag = streamProcessing_flag,
                                ramOnly_flag = ramOnly_flag,
                                
                                startupTests_flag = True,
                                printTimeConsumptionTree_flag = printTimeConsumptionTree_flag,
                                consoleLogFilePath = self._logger.getFilePath())
                    
                    if printWorkersPerformanceData_flag:
                        print(wpad.getWorkersPerformanceDataString())
                        
                    summarizing_wpad += wpad
                    
                    wpds = self._dumpSessionLogs(summarizing_wpad)
                        
                    additionalProcessingParams_dict["cleanFirst_flag"] = False
    
            if wpds:
                
                print("#" * 150)
                print("#   Summarized workers performance analysis data tables:")
                print("#" * 150)
                
                print(wpds)
            


class UserRequestProcessor_Eval_Cls(UserRequestProcessor_WithMainExecutionSequence_AbstCls):
        
    def _run(self, 
             
             inputPaths,
             outputDir,
             
             inputFilters,
             
             streamProcessing_flag,
             
             repeatEachWorker_times, 
             repetitionsInARow_times,
             
             additionalProcessingParams_dict,
             
             inASubprocesses_flag = True
             ):  
        
            
        outputDir = Path(outputDir)
        sessionName = formatTimestamp(time.time())
        
        additionalProcessingParams_dict["framesSave_dir"] = None # overwriting just in case, others are defaulted
        
        self._prepareSessionLogging(outputDir, sessionName, True, cleanConsoleLogs = True)

        
        repeatEachWorker_times   =  self._convertArg_intGT_0(repeatEachWorker_times)
        repetitionsInARow_times  =  self._convertArg_intGT_0(repetitionsInARow_times)
        
        inputFilesPaths = self.getListOfPathsOfInputFilesToProcess(inputPaths, inputFilters)
        
        generatorSide_repeatEachWorker_times = math.ceil(repeatEachWorker_times / repetitionsInARow_times)
        
        cfgGenerator = EachWorkerInRandomScenario_ConfigurationGenerator_Cls(workersIncluder = self._workersIncluder)
        
        summarizing_wpad = WorkersPerformanceAnalysisData_Cls()
        
        # countdown = 2
        
        wpds = "" # just an initialization of WorkersPerformanceDataString placeholder
        
        for cspc in cfgGenerator.generate(generatorSide_repeatEachWorker_times):
            
            wpad = WorkersPerformanceAnalysisData_Cls()
            
            if inASubprocesses_flag:
                mew = MainExecutorWrapper_Cls(wpad = wpad, mode = 'To be run in a subprocess')
            else:
                mew = MainExecutorWrapper_Cls(wpad = wpad, mode = 'No subprocess use')
            
            mew.execute(cspc = cspc,
                        repetitions = repetitionsInARow_times,
                        inputFilesPaths = inputFilesPaths,
                        outputDir = None,
                        
                        additionalProcessingParams_dict = additionalProcessingParams_dict,
                        
                        streamProcessing_flag = streamProcessing_flag,
                        ramOnly_flag = False,
                        
                        startupTests_flag = False,
                        printTimeConsumptionTree_flag = True,
                        consoleLogFilePath = self._logger.getFilePath())
            
            print(wpad.getWorkersPerformanceDataString())
            summarizing_wpad += wpad
            
            wpds = self._dumpSessionLogs(summarizing_wpad)
            
            # countdown -= 1
            #
            # if countdown == 0:
            #     break
            
        if wpds:
            
            print("#" * 150)
            print("#   Summarized workers performance analysis data tables:")
            print("#" * 150)
            
            print(wpds)
            














