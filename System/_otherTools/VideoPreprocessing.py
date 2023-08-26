'''
Created on Jun 28, 2023

@author: piotr
'''
import cv2
from pathlib import Path


class VideoPreprocesser_Cls():
    
    def __init__(self):
        self._videoParts = []
    
    def addPart(self, videoFilePath, startTime_s, endTime_s):
        self._addPart(_VideoPart_Cls(videoFilePath, startTime_s, endTime_s))
    
    def _addPart(self, videoPart):
        self._videoParts.append(videoPart)
    
    def render(self, outputFilePath, fps = None, frameWidth = None, frameHeight = None):
        "When fps or resolution is None then params are taken from first added video part"
        
        if len(self._videoParts) == 0:
            raise ValueError("No videos added")
        
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        
        if frameWidth is None or frameHeight == None is None or fps is None:
            
            originalFPS, _, (original_frameWidth, original_frameHeight) = self._videoParts[0]._openAndGetParams()
            
            if frameHeight is None: frameHeight = original_frameHeight
            if frameWidth is None: frameWidth = original_frameWidth
            if fps is None: fps = originalFPS
                
        outFile = cv2.VideoWriter(str(outputFilePath), fourcc, fps, (frameWidth, frameHeight))
        
        for videoPart in self._videoParts:
            for frame in videoPart.getFrames(fps, frameWidth, frameHeight):
                outFile.write(frame)

        outFile.release()

 
        

class _VideoPart_Cls():
    
    def __init__(self, videoFilePath, startTime_s, endTime_s):
        
        startTime_s = float(startTime_s)
        endTime_s = float(endTime_s)
        assert endTime_s > startTime_s, "End time shall be grater than start time"
        
        videoFilePath = Path(videoFilePath) 
        assert videoFilePath.exists()
        
        self._videoFilePath = str(videoFilePath)
        self._startTime_s = startTime_s
        self._endTime_s = endTime_s
        
        self._cap = None
    
    
    def _openAndGetParams(self):
        
        if self._cap is None:
            
            self._cap = cv2.VideoCapture(str(self._videoFilePath))
            
            self._original_frameWidth   =  int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self._original_frameHeight  =  int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self._originalFPS = self._cap.get(cv2.CAP_PROP_FPS)
            self._frameCount = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        return self._originalFPS, self._frameCount, (self._original_frameWidth, self._original_frameHeight)
        
        
    def getFrames(self, requestedFPS = None, frameWidth = None, frameHeight = None):
        
        originalFPS, frameCount, (original_frameWidth, original_frameHeight) = self._openAndGetParams()
        
        resizeNeeded_flag = False
        
        if requestedFPS is None:
            requestedFPS = originalFPS
        
        if frameWidth is None:
            frameWidth = original_frameWidth
        
        if frameHeight is None:
            frameHeight = original_frameHeight
        
        if (original_frameWidth != frameWidth) or (original_frameHeight != frameHeight):
            resizeNeeded_flag = True
        
        framesToTake_list = self._getInterestingFramesIndexes(originalFPS, requestedFPS, self._startTime_s, self._endTime_s)
        
        frameIndex = 0
        
        while(self._cap.isOpened()) and \
                (frameIndex < frameCount):
            flag, nparray = self._cap.read()
            
            if flag:
                
                if frameIndex in framesToTake_list:
                    
                    if resizeNeeded_flag:
                        nparray = self._resizeFrame(nparray, frameWidth, frameHeight)
                    
                    yield nparray
                
                frameIndex += 1
                
        self._cap.release()
        
        self._cap = None
    
    
    def _getInterestingFramesIndexes(self, originalFPS, requestedFPS, startTime_s, endTime_s):
        
        originalNumberOfFramesTillEndTime = int(originalFPS * endTime_s + 1)
        
        if requestedFPS and originalFPS > requestedFPS:
            framesRelativeDistance = originalFPS / requestedFPS
        else:
            framesRelativeDistance = 1
        
        timeFromBegining_s = 0.
        
        output_list = []
        
        nextFrameIndexThreshold = 0.
        
        for frameIdx in range(originalNumberOfFramesTillEndTime):
            
            timeFromBegining_s = frameIdx / originalFPS
            
            if frameIdx >= nextFrameIndexThreshold:
                nextFrameIndexThreshold += framesRelativeDistance
                
                if timeFromBegining_s >= startTime_s:
                    output_list.append(frameIdx)
        
        return output_list
        
    
    def _isInInterestingTime(self, time_s):
        return self._startTime_s <= time_s <= self._endTime_s
    
    
    def _resizeFrame(self, frame, frameWidth, frameHeight):
        
        return cv2.resize(frame, (frameWidth, frameHeight))
    
    
    
    def _shallFrameBeTaken(self, originalFPS, newFPS, framesRead_number):
        
        if self.maxFPS is None:
            return True
        
        else:
            
            timeElapsed_s = framesRead_number / originalFPS
            timeToNextFrame_s = len(self) / newFPS
            
            if timeElapsed_s >= timeToNextFrame_s:
                return True
            else:
                return False




def cutVideo(videoFilePath, outputFilePath, startTime_s, endTime_s, fps = None, frameWidth = None, frameHeight = None):
    
    prepr = VideoPreprocesser_Cls()
    prepr.addPart(videoFilePath, startTime_s, endTime_s)
    prepr.render(outputFilePath, fps, frameWidth, frameHeight)





if __name__ == "__main__":
    inputFilePath   =  r"People.mp4"
    outputFilePath  =  r"People1.mp4"
    
    cutVideo(inputFilePath, outputFilePath, startTime_s = 0.3, endTime_s = 1.3, fps = 8)







