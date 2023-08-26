'''
Created on Sep 21, 2021

@author: piotr
'''

import mimetypes
import os
from pathlib import Path
from Space.FrameHolder import FrameHolder_AbstCls
from Space._2D.Image import Image_Cls
import json
import hashlib
from abc import abstractmethod
from Space._2D_p_time.Video import InputVideo_Cls



class DataProcessor_AbstCls():
    
    def __init__(self, framesSave_dir):
        
        if framesSave_dir is not None:
            self._framesSave_dir = Path(framesSave_dir)
        else:
            self._framesSave_dir = framesSave_dir
            
        
    def prepare(self):
        pass
    
    def finish(self):
        pass
    
            


class InputDataProcessor_Cls(DataProcessor_AbstCls):
    
    def __init__(self,
                 inputPaths,
                 framesSave_dir,
                 maxFPS,
                 maxHeight,
                 maxWidth,
                 looseProportion):
        
        self._images_paths  =  []
        self._videos        =  []
        self._input_paths   =  []  #  shall combine self._images_paths and self._videos
        
        self.__filesOpened = False
        
        DataProcessor_AbstCls.__init__(self, framesSave_dir)
        
        self._maxFPS = maxFPS
        self._maxHeight = maxHeight
        self._maxWidth = maxWidth
        self._looseProportion = looseProportion
        
        for filePath in inputPaths:
            self._appendFileIfInteresting(filePath)
        
        if not self._input_paths:
            raise IOError("No valid data to process")
        
        self._sortFiles()
    
    
    def _sortFiles(self):
        
        self._images_paths   =  sorted(self._images_paths)
        self._videos         =  sorted(self._videos)
        self._input_paths    =  sorted(self._input_paths)
    
    
    def _appendFileIfInteresting(self, filePath):
        
        filePath = Path(filePath)
        
        if self.checkIfImage(filePath):
            self._images_paths.append(filePath)
            fileAppended_flag = True
        
        elif self.checkIfVideo(filePath):
            
            self._videos.append(
                
                InputVideo_Cls(filePath,
                               self._framesSave_dir,
                               maxFPS = self._maxFPS,
                               maxHeight = self._maxHeight,
                               maxWidth = self._maxWidth,
                               looseProportion = self._looseProportion)
                )
            
            fileAppended_flag = True
        
        else:
            fileAppended_flag = False
        
        if fileAppended_flag:
            self._input_paths.append(filePath)
    
    
    def getFilesPaths(self):
        return self._input_paths[:]
        
    
    
    def getBasicParams(self):
        
        outputParams_list = []
        
        outputParams_list.append(("Input files" , ", ".join([str(el) for el in self._input_paths])))
        outputParams_list.append(("Number of images" , len(self._images_paths)))
        outputParams_list.append(("Number of videos" , len(self._videos)))
        
        return outputParams_list
    
    
    def anyVideos(self):
        return bool(self._videos)
    
    
    def anyImages(self):
        return bool(self._images_paths)
    
    
    def getFrameHolderName(self, filePath, isVideo = False):
        
        isVideo # unused
        
        return os.path.relpath(filePath)
    
    
    
    def getImages(self):
        
        for image_path in self._images_paths:
            image = Image_Cls(image_path)
            yield image
    
    
    def getVideos(self):
        
        for video in self._videos:
            yield video
            
    
    
    def __getitem__(self, key, videoHandle_flag = True):
        
        if videoHandle_flag:
            return self._videoHandles[key]
        else:
            return self._images_paths[key]
        
    
    def checkIfImage(self, filePath):
        
        fileType = mimetypes.guess_type(filePath)[0]
        
        if fileType.startswith('image'):
            return True
        else:
            return False
    
    
    def checkIfVideo(self, filePath):
        
        fileType = mimetypes.guess_type(filePath)[0]
        
        if fileType.startswith('video'):
            return True
        else:
            return False
    
    
    def _getNumberOfImages(self):
        return len(self._images_paths)
    
    
    def _getNumberOfVideos(self):
        return len(self._videos)
    
    
    def _getNumberOfVideoFrames(self):
        return sum([video.getEstimatedNumberOfFrames() for video in self._videos])



class OutputDataProcessor_Base_AbstCls(DataProcessor_AbstCls):
    
    @abstractmethod
    def setProcessingID(self, *args, **kw_args): pass
    
    @abstractmethod
    def setConfigurationDataDict(self, *args, **kw_args): pass
    
    @abstractmethod
    def write(self, imageOrVideo): pass
    
    @abstractmethod
    def getOutputDir(self): pass
    
    @abstractmethod
    def getBasicParams(self): pass
    


class OutputDataProcessor_Stub_Cls(OutputDataProcessor_Base_AbstCls):
    
    def __init__(self): pass
    def write(self, imageOrVideo): pass
    def setProcessingID(self, *args, **kw_args): pass
    def setConfigurationDataDict(self, *args, **kw_args): pass
    def getOutputDir(self): return None
    def getBasicParams(self): return []



class OutputDataProcessor_Cls(OutputDataProcessor_Base_AbstCls):
    
    logFileBaseName = "outputData.json"
    
    def __init__(self, outputDir, cleanFirst_flag, outFilePrefix, outputFileSuffix, framesSave_dir, consoleLogFilePath):
        """
        cleanFirst_flag indicates if to remove all the files that might be interpreted as output files
        """
        
        DataProcessor_AbstCls.__init__(self, framesSave_dir)
                
        self._outputDir = self.validateOutputDir(outputDir)
        self._outputPrefix_str = self.validateOutputPrefixOrSuffix(outFilePrefix)
        self._outputSuffix_str = self.validateOutputPrefixOrSuffix(outputFileSuffix)
        
        assert isinstance(cleanFirst_flag, bool)
        
        self._cleanFirst_flag = cleanFirst_flag
        
        self._consoleLogFilePath = consoleLogFilePath
        self._logFilePath = self._outputDir / OutputDataProcessor_Cls.logFileBaseName
        
        self._processingConfigurationString = ""
        self._processingConfigurationId = None
        
        self._processingId = None
        
        self._processingDataAdded_flag = False
        
    
    def prepare(self):
        
        "If configured so: Deletes all the files that might be interpreted as output files"
        
        def removeAllTheFilesInDir(directory_):
            if directory_.exists():
                for root,_,filesPaths in os.walk(directory_):
                    for filePath in filesPaths:
                        filePath = os.path.join(root, filePath)
                        if Path(filePath).is_file():
                            if str(filePath) != str(self._consoleLogFilePath):
                                os.remove(filePath)
                    break
        
        if self._cleanFirst_flag:
            
            removeAllTheFilesInDir(self._outputDir)
            
            if self._logFilePath.exists():               os.remove(self._logFilePath)
    
    
    def setProcessingID(self, processingId):
        assert isinstance(processingId, str) and processingId
        self._processingId = processingId
        
    
    def setConfigurationDataDict(self, configurationDict):
        
        if configurationDict is not None:
            assert isinstance(configurationDict, dict)
            self._processingConfigurationDict = configurationDict
            ProcessingConfigurationString = str(json.dumps(self._processingConfigurationDict, indent=2))
            self._processingConfigurationId = hashlib.sha1(ProcessingConfigurationString.encode('utf-8')).hexdigest()[-15:].upper()
            
    
    def getLogFileDict(self):
        
        output_dict = {}
        
        if self._logFilePath.exists():
            with open(self._logFilePath, "r") as logFile:
                output_dict.update(json.load(logFile))
        
        return output_dict
    
    
    def dumpLogFileDict(self, output_dict):
        
        with open(self._logFilePath, 'w') as f:
            json.dump(output_dict, f, indent=2)
        
    
    def appendToLogWrittenFile(self, originFilePath, newCurrentFilePath):
        
        outputFileDetails_slotKey = "Output file details in form of { Output file : (origin file, processing ID, <optional> processing configuration ID) }"
    
        output_dict = self.getLogFileDict()
        
        if outputFileDetails_slotKey not in output_dict:
            output_dict[outputFileDetails_slotKey] = {}

        outputFileDetails_dict = output_dict[outputFileDetails_slotKey]
        
        key_   =  str(newCurrentFilePath)
        
        word_  =  [str(originFilePath)]
        
        if self._processingId: 
            word_.append(self._processingId)
        
        if self._processingConfigurationId:
            word_.append(self._processingConfigurationId)
            
        word_ = tuple(word_)
        
        outputFileDetails_dict[key_] = word_
        
        
        if self._processingDataAdded_flag is False:
            
            if self._processingConfigurationId:
                
                processingConfigurationsDetails_slotKey = "{ Processing configuration ID : Processing configuration details }"
                
                if processingConfigurationsDetails_slotKey not in output_dict:
                    output_dict[processingConfigurationsDetails_slotKey] = {}
                    
                processingConfigurationsDetails_dict = output_dict[processingConfigurationsDetails_slotKey]
                
                processingConfigurationsDetails_dict[self._processingConfigurationId] = self._processingConfigurationDict
                
                
            self._processingDataAdded_flag = True
        
        
        self.dumpLogFileDict(output_dict)
        
        
    
    def getBasicParams(self):
        
        outputParams_list = []
        
        outputParams_list.append(("Output directory" ,  self._outputDir))
        
        if self._outputPrefix_str:
            outputParams_list.append(("Output prefix" , self._outputPrefix_str))
        
        if self._outputSuffix_str:
            outputParams_list.append(("Output suffix" , self._outputSuffix_str))
        
        return outputParams_list
    
    
    def write(self, imageOrVideo):
        
        if not(isinstance(imageOrVideo, FrameHolder_AbstCls)):
            raise TypeError("Frame holder type: " + str(type(imageOrVideo)) + " is unknown")
        
        outputDir = self._outputDir
        
        
        objectOriginFilePath = imageOrVideo.getOriginFilePath()
        
        baseName = objectOriginFilePath.name
        
        if self._outputPrefix_str:
            baseName = self._outputPrefix_str + "_" + baseName
        
        if self._outputSuffix_str:
            baseName = Path(baseName)
            baseName = baseName.stem + "_" + self._outputSuffix_str + baseName.suffix
        
        newFilePath = self.getNextNonExistingPath(
            directory = outputDir,
            basename = baseName
            )
        
        imageOrVideo.write(newFilePath)
        
        # if isinstance(imageOrVideo, Image_Cls):
        #     dataWriter = self._imageWriter 
        # else:
        #     dataWriter = self._videoWriter
        #
        #
        # dataWriter.write(
        #     imageOrVideo,
        #     fileBasename = newFilePath.name,
        #     directory = newFilePath.parent,
        #     createDir = True
        #     )
        #
        # self.appendToLogWrittenFile(
        #     objectOriginFilePath,
        #     newFilePath
        #     )
        
        
    
    def getNextNonExistingPath(self, directory, basename):
        
        "Modifies path by indexing basename"
        
        path_candidate = directory / basename
        
        if path_candidate.exists():
            index = 1
            path_noExtension = path_candidate.parent / path_candidate.stem
            extension = path_candidate.suffix
            
            path_candidate = Path(str(path_noExtension) + "_" + str(index) + str(extension))
        
            while path_candidate.exists():
                index += 1
                path_candidate = Path(str(path_noExtension) + "_" + str(index) + extension)
        
        return path_candidate
        
        
    def validateOutputPrefixOrSuffix(self, outputPrefixOrSuffix_str):
        
        assert isinstance(outputPrefixOrSuffix_str, str)
        return outputPrefixOrSuffix_str
    
    
    def validateOutputDir(self, outputDir):
        
        outputDir = Path(outputDir)
        
        if not outputDir.is_dir():
            raise FileNotFoundError("Directory: " + str(outputDir.absolute()) + " does not exist")
        
        return outputDir.absolute()
    
    
    def getOutputDir(self):
        return self._outputDir



