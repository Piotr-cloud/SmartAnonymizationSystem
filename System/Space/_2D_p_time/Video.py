'''
Created on Mar 20, 2021

@author: piotr
'''

import numpy as np
from Space.FrameHolder import FrameHolder_AbstCls
from Space._2D_p_time.Frame import Frame_Cls
from pathlib import Path
import cv2
import mimetypes
from Space._2D.Array import Array_AbstCls
from math import ceil






class Video_AbstCls(FrameHolder_AbstCls):
    'Term "Video" in this project is identical to "Images Sequence", Video is interpretted as visual data only - no audio'
    
    singleFrameFileNamePrefix = "Frame"
    singleFrameFileNameExtension = "jpg"
    
    _defaultExtension = ".avi"
    _acceptedExtensions = [
        ".avi",
        ".mp4",
        ".mov",
        ".wmv"]
    
    _codec = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    
    
    def __init__(self, originFilePath, fps, frameHeight, frameWidth, HD_storageDir):
        
        FrameHolder_AbstCls.__init__(self, originFilePath)
        
        assert isinstance(fps, float) and fps > 0
        assert isinstance(frameHeight, int) and frameHeight > 0
        assert isinstance(frameWidth, int) and frameWidth > 0
        
        self.fps = fps
        self.frameHeight = frameHeight
        self.frameWidth = frameWidth
        
        
        if HD_storageDir is not None:
            HD_storageDir = Path(HD_storageDir)
        
        self.HD_storageDir = HD_storageDir
        
        self._frames_list = []
    
    
    def __len__(self):
        return len(self._frames_list)
    
    
    def __iter__(self):
        
        for frame in self.iterFrames():
            yield frame
    
    
    def _getFrameName(self, frame_index):

        selfName = self.getName()

        if selfName:
            return selfName + r" (Frame: " + str(frame_index) + r")"

        else:
            return None
    
    
    def addNpArrayAsFrame(self, nparray):
        
        frame = Frame_Cls(nparray, videoRelated = self, frameNumber = len(self._frames_list), HD_storageDir = self.HD_storageDir)
        self._frames_list.append(frame)
        
        return frame
    
    
    def iterFrames(self):
        
        for frame in self._frames_list:
            yield frame

    
    def _getFramePath(self, frameNumber):
        
        return self.workDir / str(self.singleFrameFileNamePrefix + '_' + str(frameNumber) + "." + self.singleFrameFileNameExtension)


    def _validateExtension(self, fileBasename):
        
        guess = mimetypes.guess_type(fileBasename)[0]
        
        if guess is None or not guess.startswith('video'):
            raise TypeError("Video extension is wrong! File name: " + fileBasename)
    
    
    def write(self, filePath):
        
        self._validateExtension(filePath.name)
        
        self.prepareDir(str(filePath.parent))
        
        #filePath = self._formatPathExtension(filePath)
        
        fourcc = Video_AbstCls._codec
        
        outFile = cv2.VideoWriter(str(filePath), fourcc, self.fps, (self.frameWidth, self.frameHeight))
        
        for frame in self.__iter__():
            outFile.write(frame.getNpArrayCopy())
        
        outFile.release()
    
    
    def _setWorkDir_notInUse(self):
        
        videoFolderName_candidate = self.getName()
        
        workDir_candidate = (self.HD_storageDir / self.classFolderName) /videoFolderName_candidate
        
        if workDir_candidate.exists():
            
            workDir_candidate_original = workDir_candidate
            
            cnt = 1
            
            while workDir_candidate.exists():
                
                workDir_candidate = Path(str(workDir_candidate_original) + "_" + str(cnt))
                cnt += 1
        
        self.workDir = workDir_candidate
        
        self.prepareDir(self.workDir)



class InputVideo_Cls(Video_AbstCls):
    
    def __init__(self, originFilePath, HD_storageDir = None, maxFPS = None, maxHeight = None, maxWidth = None, looseProportion = False):
        """
        provide HD_storageDir to use HD instead of RAM
        """
            
        if maxFPS is not None:
            assert isinstance(maxFPS, float)
            assert maxFPS >= 1.
        
        self.maxFPS = maxFPS
        
        
        if maxHeight is not None:
            assert isinstance(maxHeight, int)
            assert maxHeight > 0
            
        self.maxHeight = maxHeight
        
        
        if maxWidth is not None:
            assert isinstance(maxWidth, int)
            assert maxWidth > 0
            
        self.maxWidth = maxWidth
        
        
        assert isinstance(looseProportion, bool)
        self.looseProportion = looseProportion
        
        
        originFilePath = Path(originFilePath)
        assert originFilePath.exists() and originFilePath.is_file()
        
        
        self._cap = cv2.VideoCapture(str(originFilePath))
        
        self.originalFPS = self._cap.get(cv2.CAP_PROP_FPS)
        
        self.frameCount = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if self.maxFPS and (self.originalFPS > self.maxFPS):
            self.estimatedNumberOfFrames = ceil(self.frameCount * self.maxFPS / self.originalFPS)
        else:  
            self.estimatedNumberOfFrames = self.frameCount
        
        original_frameHeight  =  int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        original_frameWidth   =  int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        frameHeight, frameWidth = self._calculateNewResolution(original_frameHeight, original_frameWidth)
        
        if frameHeight != original_frameHeight or frameWidth != original_frameWidth: # any change?
            self.resizeNeeded = True
        else: 
            self.resizeNeeded = False
        
        if self.maxFPS is not None:    fps = min([self.originalFPS, self.maxFPS])
        else:                          fps = self.originalFPS
        
        
        Video_AbstCls.__init__(self, originFilePath, fps, frameHeight, frameWidth, HD_storageDir)
        
        self._firstInteration_flag = True
    
    
    def __lt__(self, other):
        return self._originFilePath < other._originFilePath
    
    
    def getEstimatedNumberOfFrames(self):
        return self.estimatedNumberOfFrames
    
    
    def _calculateNewResolution(self, original_frameHeight, original_frameWidth):
        
        frameHeight = original_frameHeight
        frameWidth  = original_frameWidth
        
        if self.maxHeight is not None and self.maxWidth is not None:
                
            if self.looseProportion:
                    
                frameHeight = min([self.maxHeight, frameHeight])
                
                frameWidth = min([self.maxWidth, frameWidth])
            
            else:
                original_ratio = frameWidth / frameHeight
                
                frameHeight = min([self.maxHeight, frameHeight])
                frameWidth = min([self.maxWidth, frameWidth])
                
                new_ratio = frameWidth / frameHeight
                
                if new_ratio > original_ratio:
                    frameWidth = int(frameWidth / new_ratio * original_ratio)
                else:
                    frameHeight = int(frameHeight / original_ratio * new_ratio)
                
        
        return frameHeight, frameWidth
    
    
    
    def getOutputVideoObj(self):
            
        return OutputVideo_Cls(self.getOriginFilePath(), self.fps, self.frameHeight, self.frameWidth, self.HD_storageDir)
    
    
    def _shallFrameBeTaken(self, fps, fps_limit, framesRead_number):
        
        if self.maxFPS is None:
            return True
        
        else:
            timeElapsed_s = framesRead_number / fps
            timeToNextFrame_s = len(self) / fps_limit
            
            if timeElapsed_s >= timeToNextFrame_s:
                return True
            else:
                return False
        
    
    
    def _resizeFrame(self, frame):
        
        return cv2.resize(frame, (self.frameWidth, self.frameHeight))
    
            
    def _firstIteration(self):
        
        framesRead_number = 0
        
        while(self._cap.isOpened()) and \
                (framesRead_number < self.frameCount):
            flag, nparray = self._cap.read()
            
            if flag:
                
                framesRead_number += 1
                
                if self._shallFrameBeTaken(self.originalFPS, self.fps, framesRead_number):
                    
                    if self.resizeNeeded:
                        nparray = self._resizeFrame(nparray)
                    
                    yield self.addNpArrayAsFrame(nparray)
    
    
    def iterFrames(self):
        
        if self._firstInteration_flag:
            yield from self._firstIteration()
            
            self._firstInteration_flag = False
            
        else:
            yield from Video_AbstCls.iterFrames(self)




class OutputVideo_Cls(Video_AbstCls):
    
    def __init__(self, originFilePath, fps, frameHeight, frameWidth, HD_storageDir = None):
        
        Video_AbstCls.__init__(self, originFilePath, fps, frameHeight, frameWidth, HD_storageDir)
        
        # self._highestFrameClass = Frame_Cls
        # self._frameClassToVideoClass_dict = self._getFrameClassToVideoClassDict()
        
    

    def append(self, frameData):
        """
        Accepts frame and np.array
        but the size must match
        """
        assert isinstance(frameData, Array_AbstCls) or isinstance(frameData, np.ndarray)
        
        if isinstance(frameData, Array_AbstCls):
            numpyArray = frameData.getNpArrayCopy()
            
        else:
            numpyArray = frameData
            
        nparrayShape = numpyArray.shape[:2]
        
        if not (self.frameHeight, self.frameWidth) == nparrayShape:
            raise ValueError("Provided frame does not fit required size")
        
        self.addNpArrayAsFrame(numpyArray)





