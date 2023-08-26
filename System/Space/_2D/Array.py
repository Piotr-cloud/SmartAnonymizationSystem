'''
Created on Mar 21, 2021

@author: piotr
'''


import numpy as np
from PolymorphicBases.ABC import Base_AbstCls
import cv2
from pathlib import Path

from PolymorphicBases.Decorators import singleton
from NonPythonFiles import npArraysHDStorage_dir
import os
import shutil



@singleton
class NpArrayAbstractionConfiguration_Cls():
    
    def __init__(self, useHD = True):
        
        self._npArraysHDStorage_defaultDir_root  =  Path(npArraysHDStorage_dir)
        self._processFolderName = "Process: " + str(os.getpid())
        
        self._npArraysHDStorage_defaultDir  =  self._npArraysHDStorage_defaultDir_root  /  self._processFolderName
        
        self._ramOnly = False
    
        self._folderPath_2_id_mappingDict = {}
        
        if self._ramOnly:
            self.useRAM()
        else:
            if useHD:  self.useHD()
            else:      self.useRAM()
    
    
    def isUsingHD_insteadOfRAM(self):
        return self.__HD_insteadOfRAM
    
    def set_RAM_only(self):
        self._ramOnly = True
    
    
    def useHD(self):
        if not self._ramOnly:
            self.__HD_insteadOfRAM = True
    
    
    def useRAM(self):
        self.__HD_insteadOfRAM = False
    
    
    def __cleanDir(self, dir_):
        if dir_.exists() and dir_.is_dir():
            shutil.rmtree(dir_)
    
    
    def _cleanDefaultLocation(self):
        if self.isUsingHD_insteadOfRAM():
            self.__cleanDir(self._npArraysHDStorage_defaultDir)
    
    
    def _cleanDefaultLocationRootFolder(self):
        self.__cleanDir(self._npArraysHDStorage_defaultDir_root)
    
    
    def prepare(self):
        self._cleanDefaultLocation()
    
    
    def finish(self):
        self._cleanDefaultLocation()
    
    
    def getDefaultFileNameForPath(self, folderPath):
        
        if folderPath not in self._folderPath_2_id_mappingDict:
            self._folderPath_2_id_mappingDict[folderPath] = 1
        else:
            self._folderPath_2_id_mappingDict[folderPath] += 1
        
        return str(self._folderPath_2_id_mappingDict[folderPath])
    
    
    def _getVideoNpArrayStorageDir(self, video, storageBaseDir, classifyingRelativePath):
        
        if video not in self._video_2_NpArrayStorageDir_dict:
                
            classifyingAbsolutePath = storageBaseDir / classifyingRelativePath
            
            self._video_2_NpArrayStorageDir_dict[video] = self.getNonExistingPath(
                    classifyingAbsolutePath,
                    Path() / video.getName()
                    )
            
        return self._video_2_NpArrayStorageDir_dict[video]
        
        
    def _getNonExistingFilePath(self, dir_, fileBaseName, extension = ".jpg"):
        """
        increments fileBaseName with prefix until directory does not exist. Apllies the following rule:
        - <directory_>/<prefix><extension>
        - <directory_>/1_<prefix><extension>
        - <directory_>/2_<prefix><extension>
        - <directory_>/3_<prefix><extension>
        ...
        """
        
        if not fileBaseName.endswith(extension):
            fileBaseName += extension
        
        filePath_candidate = dir_ / fileBaseName
        cnt = 0
        while filePath_candidate.exists():
            cnt += 1
            filePath_candidate = dir_ / (str(cnt) + "_" + fileBaseName)    
            if cnt > 10e6: raise EnvironmentError("Endless loop")
        
        return filePath_candidate
    
                
    def getNpArrayStorageFilePath(self, explicit_HD_storageDir, hostObj):
        """
        hostObj is used to define a folder to group np arrays on HD drive, if not provided default folder named "unclassified" is used
        """
        assert isinstance(hostObj, Array_AbstCls)
        
        if self.__HD_insteadOfRAM:
            
            storageBaseDir = Path(self._npArraysHDStorage_defaultDir)
            
            if explicit_HD_storageDir is not None:
                storageDir = Path(explicit_HD_storageDir)
                assert not storageDir.is_file()
                storageDir = storageDir / self._processFolderName
                assert not storageDir.is_file()
            else:
                storageDir = storageBaseDir
                            
            
            if hostObj.__class__.__name__ == "Frame_Cls":
                
                video = hostObj.getVideoRelated()
                
                if video.__class__.__name__ == "InputVideo_Cls":
                    storageDir /= "inputVideos"
                elif video.__class__.__name__ == "OutputVideo_Cls":
                    storageDir /= "outputVideos"
                else:
                    storageDir /= "otherVideos"
            
            else:
            
                if hostObj.__class__.__name__ == "Image_Cls":
                    storageDir /= "Images"
                
                elif hostObj.__class__.__name__ == "ImagePart_Cls":
                    storageDir /= "Images parts"
                
                elif hostObj.__class__.__name__ == "View_Cls":
                    storageDir /= "Views"

            return self._getNonExistingFilePath(storageDir, hostObj.getName(), ".jpg")
                
        
        else:
            return None
        
        
    def prepareDir(self, directory_):
        
        directory_ = Path(directory_)
        
        if not directory_.exists():
            os.makedirs(directory_)
        else:
            if not directory_.is_dir():
                raise NotADirectoryError("Cannot operate on directory: " + str(directory_) + " since it's not a directory")
            


npArrayAbstractionConfiguration = NpArrayAbstractionConfiguration_Cls()



class Array_AbstCls(Base_AbstCls):
    """
    Just a numpy array wrapper
    """
    
    def __init__(self, nparray, explicit_HD_storageDir = None, forceRAM = False, isOnHdAlready_filePath = None):
        """
        explicit_HD_file_path if provided forces to use this path instead of internally defined. It also allows frames to be not deleted when program terminates
        forceRAM flag makes HD usage impossible
        """
        
        self.dataSrc = None # RAM by default
        donotSaveToHD_flag = False
        
        if not forceRAM:
            if isOnHdAlready_filePath is not None:
                isOnHdAlready_filePath = Path(isOnHdAlready_filePath)
                if isOnHdAlready_filePath.is_file():
                    self.dataSrc = isOnHdAlready_filePath
                    donotSaveToHD_flag = True
                    
            if self.dataSrc is None:
                self.dataSrc = npArrayAbstractionConfiguration.getNpArrayStorageFilePath(explicit_HD_storageDir, self)
        
        self.updateArray(nparray, donotSaveToHD_flag = donotSaveToHD_flag)
        
    
    def getShape(self):
        return self._shape
    
    
    def updateArray(self, nparray, donotSaveToHD_flag = False):
        
        assert isinstance(nparray, np.ndarray)
        
        self._shape = nparray.shape
        
        if isinstance(self.dataSrc, Path):
            
            if not donotSaveToHD_flag:
                self._write(str(self.dataSrc), nparray)
            
        else:
            self.dataSrc = nparray
    
    
    def getNpArray(self):
        
        raise NotImplementedError("This method is unavailable by design. getNpArrayCopy shall be used instead")
    

    def getNpArrayCopy(self, grayScale = False): # this function can probably be optimzed
        
        if isinstance(self.dataSrc, Path):
            
            if not self.dataSrc.exists():
                raise FileNotFoundError("Np array related file does not exist: " + str(self.dataSrc))
            
            nparray = cv2.imread(str(self.dataSrc))
                
        else:
            nparray = self.dataSrc.copy()
        
        
        if grayScale:
            return cv2.cvtColor(nparray, cv2.COLOR_BGR2GRAY)
        else:
            return nparray


    def copy_notInUse(self):
        return type(self)(self._array.copy())
        

    def write(self, filePath, createDir = False):
        filePath = Path(filePath)
        
        if createDir:
            dir_= filePath.parent
            if not dir_.exists():
                os.makedirs(dir_)
                
        self._write(filePath, self.getNpArrayCopy())
        

    def _write(self, filePath, nparray):
        
        filePath = Path(filePath)
        
        dir_ = filePath.parent
        
        if not dir_.exists():
            os.makedirs(dir_)
            
        cv2.imwrite(str(filePath), nparray)






