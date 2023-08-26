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

    # TODO: remove commented code
    #
    # def _getFrameClassToVideoClassDict(self):
    #
    #     if OutputVideo_Cls.frameClassToVideoClass_dict is None:
    #
    #         globals_cpy = globals().copy()
    #         frameClassToVideoClass_dict = {}
    #         baseClass = Frame_Cls
    #
    #         for var_name in globals_cpy:
    #
    #             var = globals_cpy[var_name]
    #
    #             if inspect.isclass(var):
    #                 if issubclass(var, Video_AbstCls):
    #                     _framesType = var.framesType
    #
    #                     if _framesType:
    #                         if issubclass(_framesType, baseClass):
    #                             if _framesType in frameClassToVideoClass_dict:
    #                                 if var is not frameClassToVideoClass_dict[_framesType]:
    #                                     raise KeyError("Frame class: " + str(_framesType) + " already indicates the following video class in class degradation mechanism: " + str(frameClassToVideoClass_dict[_framesType]) + "\n so the following new video class cannot be added: " + str(var))
    #                                 else:
    #                                     continue
    #
    #                             frameClassToVideoClass_dict[_framesType] = var
    #
    #         OutputVideo_Cls.frameClassToVideoClass_dict = frameClassToVideoClass_dict
    #
    #     return OutputVideo_Cls.frameClassToVideoClass_dict
    #
    #
    # def getOutputVideoClass(self):
    #     return self._frameClassToVideoClass_dict[self._highestFrameClass]








# class VideoData_AbstCls(FrameHolder_AbstCls):
#
#     def __init__(self, fps, frameCount, frameShape, nparrays_list, originFilePath):
#
#         assert type(self) != VideoData_AbstCls
#         assert isinstance(fps, float) or isinstance(fps, int)
#         assert isinstance(frameCount, int)
#         assert hasattr(frameShape, "__iter__") 
#         assert len(frameShape) >= 2
#
#         if len(frameShape) > 2: frameShape = frameShape[:2]
#
#         assert isinstance(nparrays_list, list)
#
#         self._fps = float(fps)
#         self._frameCount = frameCount
#         self._nparrays_list = nparrays_list
#         self._frameShape = frameShape
#
#         FrameHolder_AbstCls.__init__(self, originFilePath)
#
#
#     def _getBaseParams(self):
#         return self._fps, self._frameCount, self._nparrays_list, self._frameShape
#
#
#     def __len__(self):
#         return self._frameCount
#
#
#     def getFPS(self):
#         return self._fps
#
#
#     def getShape(self):
#         return self._frameShape
#
#
#     def getNumpyArraysList(self):
#         return self._nparrays_list
#
#     def _loadFramesToNpArrayList(self, frames_list):
#         "Returns np arrays list and frame shape used"
#
#         nparrays_list = []
#
#         frameShape = None
#
#         for frame in frames_list:
#
#             if isinstance(frame, Array_AbstCls):
#                 numpyArray = frame.getArray()
#
#             elif isinstance(frame, np.ndarray):
#                 numpyArray = frame
#
#             else:
#                 raise TypeError("Video frame type is wrong")
#
#             if not frameShape == numpyArray.shape:
#
#                 if frameShape is None:
#                     frameShape = numpyArray.shape
#
#                 else:
#                     raise ValueError("Frames shape differs.  Expected: " + str(frameShape) + "  Issue frame shape: " + str(numpyArray.shape))
#
#             nparrays_list.append(numpyArray)
#
#         return nparrays_list, frameShape
#
#
#     def __iter__(self, getCopies = False, justNumpyArr = False):
#
#         if justNumpyArr:
#
#             nparrays_list = self._nparrays_list.copy()
#
#             if getCopies:
#                 for array in nparrays_list:
#                     yield array.copy()
#             else:
#                 for array in nparrays_list:
#                     yield array
#
#         else:
#
#             for frame_index in range(len(self._nparrays_list)):
#                 yield self._getFrame(frame_index)
#
#
#     def _getFrame(self, frame_index):
#
#         return type(self).framesType(self._nparrays_list[frame_index], self, frame_index)
#
#
#     def getFrame(self, frame_index):
#
#         self._validateFrameIndex(frame_index)
#
#         return self._getFrame(frame_index)
#
#
#     def _validateFrameIndex(self, frame_index):
#         assert isinstance(frame_index, int)
#
#         if frame_index >= len(self):
#             raise IndexError("Video is not long enough(" + str(len(self)) + ") to obtain frame number: " + str(frame_index))
#
#
#
#
#
#
#
# class Video_Cls(VideoData_AbstCls):
#
#     imagesType = Image_Cls
#     framesType = Frame_Cls
#
#     def __init__(self, frames_list, fps, originFilePath = None, HD_based = False):
#
#         assert isinstance(frames_list, list) # cannot be a set or dict since order matters
#
#         if not frames_list:
#             raise ValueError("Video is empty!")
#
#         nparrays_list, frameShape = self._loadFramesToNpArrayList(frames_list)
#
#         # nparrays_list = []
#         #
#         # frameShape = None
#         #
#         # for frame in frames_list:
#         #
#         #     if isinstance(frame, Array_AbstCls):
#         #         numpyArray = frame.getArray()
#         #
#         #     elif isinstance(frame, np.ndarray):
#         #         numpyArray = frame
#         #
#         #     else:
#         #         raise TypeError("Video frame type is wrong")
#         #
#         #     if not frameShape == numpyArray.shape:
#         #
#         #         if frameShape is None:
#         #             frameShape = numpyArray.shape
#         #
#         #         else:
#         #             raise ValueError("Frames shape differs.  Expected: " + str(frameShape) + "  Issue frame shape: " + str(numpyArray.shape))
#         #
#         #     nparrays_list.append(numpyArray)
#
#         VideoData_AbstCls.__init__(self, fps, len(nparrays_list), frameShape, nparrays_list, originFilePath)
#
#
#     def getImage(self, frame_index):
#
#         self._validateFrameIndex(frame_index)
#
#         image = type(self).imagesType(self._getFrame(frame_index), self._getFrameName(frame_index))
#
#         return image
#
#
#     def _getFrameName(self, frame_index):
#
#         selfName = self.getName()
#
#         if selfName:
#             return selfName + r"//" + str(frame_index)
#
#         else:
#             return None
#
#
#     def __getitem__(self, index):
#
#         return self.getFrame(index)
#
#
#
# Video_Cls = Video_Cls #alias
#
# RAM_Video_Cls
# class RAM_Video_Cls(FrameHolder_AbstCls):
#
#     framesType = Frame_Cls
#
#     def __init__(self, nparrays_list, fps):
#
#         assert isinstance(nparrays_list, list)
#
#         nparrays_list, frameShape = self._loadFramesToNpArrayList(nparrays_list)
#
#         assert isinstance(fps, float) or isinstance(fps, int)
#         assert len(frameShape) >= 2
#
#         if len(frameShape) > 2: frameShape = frameShape[:2]
#
#         self._frameShape = frameShape
#         self._fps = fps
#         self._nparrays_list = nparrays_list
#
#
#
# class SecondaryVideo_Cls(OutputVideo_Cls):
#
#     imagesType = SecondaryImage_Cls
#     framesType = SecondaryFrame_Cls
#
#
# class AnnotatedVideo_Cls(AnnotatedFrameHolder_AbstCls, SecondaryVideo_Cls):
#
#     imagesType = AnnotatedImage_Cls
#     framesType = AnnotatedFrame_Cls
#
#
#
# class AnonymizedVideo_Cls(AnonymizedFrameHolder_AbstCls, SecondaryVideo_Cls):
#
#     imagesType = AnonymizedImage_Cls
#     framesType = AnonymizedFrame_Cls
#
#
#
# class AnonymizedAndAnnotatedVideo_Cls(AnonymizedAndAnnotatedFrameHolder_AbstCls, SecondaryVideo_Cls):
#
#     imagesType = AnonymizedAndAnnotatedImage_Cls
#     framesType = AnonymizedAndAnnotatedFrame_Cls
#
#
#
#
# class VideoBuilder_Cls():
#
#     """
#     This class construts video of specific class in regards to video frames added
#     Frames one by one are added and then video of specific class is constructed
#     Performs class degradation
#     """
#
#     frameClassToVideoClass_dict = None
#
#
#     def __init__(self, fps, originFilePath, HD_use_flag = True):
#
#         assert isinstance(HD_use_flag, bool)
#
#         if HD_use_flag:
#
#             if HD_folderName_str is None:
#                 HD_folderName_str = time.time()
#
#             self._HD_file_path = videosHDSupport_dir / str(HD_folderName_str)
#
#         self._frames_list = []
#
#         self._highestFrameClass = Frame_Cls
#
#         self._frameClassToVideoClass_dict = self._getFrameClassToVideoClassDict()
#
#
#     def append(self, frameData):
#         """
#         Accepts frame and np.array
#         but the size must match
#         """
#         assert isinstance(frameData, Frame_Cls) or isinstance(frameData, np.ndarray)
#
#         if isinstance(frameData, Frame_Cls):
#
#             frameClass = type(frameData)
#
#             if issubclass(frameClass, self._highestFrameClass):
#                 self._highestFrameClass = frameClass              # TODO check if degradation works
#
#             numpyArray = frameData.getArray()
#
#         else:
#             numpyArray = frameData
#
#         nparrayAbstraction = NpArrayAbstraction_Cls(numpyArray, self._HD_file_path)
#
#         self._frames_list.append(nparrayAbstraction)
#
#
#     def getVideo(self, fps, originFilePath = None):
#         """
#         Outputs video of specific class
#         """
#         videoClass = self._frameClassToVideoClass_dict[self._highestFrameClass]
#
#         return videoClass(
#             frames_list = self._frames_list,
#             fps = fps,
#             originFilePath = originFilePath
#             )
#
#
#     def _getFrameClassToVideoClassDict(self):
#
#         if VideoBuilder_Cls.frameClassToVideoClass_dict is None:
#
#             globals_cpy = globals().copy()
#             frameClassToVideoClass_dict = {}
#             baseClass = Frame_Cls
#
#             for var_name in globals_cpy:
#
#                 if "Video_Cls" in var_name:
#                     debug = 1
#
#                 var = globals_cpy[var_name]
#
#                 if inspect.isclass(var):
#                     if issubclass(var, Video_Cls):
#                         _framesType = var.framesType
#
#                         if _framesType:
#                             if issubclass(_framesType, baseClass):
#                                 if _framesType in frameClassToVideoClass_dict:
#                                     if var is not frameClassToVideoClass_dict[_framesType]:
#                                         raise KeyError("Frame class: " + str(_framesType) + " already indicates the following video class in class degradation mechanism: " + str(frameClassToVideoClass_dict[_framesType]) + "\n so the following new video class cannot be added: " + str(var))
#                                     else:
#                                         continue
#
#                                 frameClassToVideoClass_dict[_framesType] = var
#
#             VideoBuilder_Cls.frameClassToVideoClass_dict = frameClassToVideoClass_dict
#
#         return VideoBuilder_Cls.frameClassToVideoClass_dict







