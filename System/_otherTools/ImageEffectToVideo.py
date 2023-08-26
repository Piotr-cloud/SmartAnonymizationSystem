'''
Created on Jun 29, 2023

@author: piotr
'''
import cv2
import numpy as np
from pathlib import Path
import inspect




class ImageEffectToVideo_Cls():
    
    def __init__(self, imageFilePath, outputDir, fps, duration_s):
        
        self.imageFilePath = Path(imageFilePath)
        assert self.imageFilePath.exists()
        assert self.imageFilePath.is_file()
        
        self.originalNpArray = cv2.imread(str(self.imageFilePath))
        assert self.originalNpArray is not None
        
        self.outputDir = Path(outputDir)
        
        if not self.outputDir.exists():
            raise NotADirectoryError("Output directory must exist. Path: \"" + str(self.outputDir) + "\"" )
        
        assert self.outputDir.is_dir()
        
        assert isinstance(fps, float) or isinstance(fps, int)
        self.fps = float(fps)
        
        assert isinstance(duration_s, float) or isinstance(duration_s, int)
        self.duration_s = float(duration_s)
    
    
    def blur(self, endLevel, effectDensity_perc):
        """
        endLevel - blur area
        """
        
        level = endLevel * effectDensity_perc
        
        verticalParam = level#self.originalNpArray.shape[0] * level / 100
        horizontalParam = level#self.originalNpArray.shape[1] * level / 100
        
        
        verticalParam = int(verticalParam / 2) * 2 + 1
        horizontalParam = int(horizontalParam / 2) * 2 + 1
        
        commonParam = int((horizontalParam + verticalParam) / 2)
        
        return cv2.GaussianBlur(self.originalNpArray, (verticalParam, horizontalParam), commonParam)
    
    
    def fade(self, effectDensity_perc):
        
        white = np.array([255, 255, 255], np.uint8)
        vector = white-self.originalNpArray
        
        # fading image
        value = self.originalNpArray + vector * effectDensity_perc
        white = np.array([255, 255, 255], np.uint8)
        
        return np.uint8(value)
    
    
    def revealRight(self, effectDensity_perc):
        
        array = self.originalNpArray.copy()
        h,w = array.shape[:2]
        if effectDensity_perc > 0:
            return cv2.rectangle(array, (0,0), (int(w*effectDensity_perc),h), (255,255,255), -1)
        else:
            return array
    
    
    def revealLeft(self, effectDensity_perc):
        
        array = self.originalNpArray.copy()
        h,w = array.shape[:2]
        if effectDensity_perc > 0:
            return cv2.rectangle(array, (int(w * (1 - effectDensity_perc)),0), (w,h), (255,255,255), -1)
        else:
            return array
        
    
    def revealDown(self, effectDensity_perc):
        
        array = self.originalNpArray.copy()
        h,w = array.shape[:2]
        if effectDensity_perc > 0:
            return cv2.rectangle(array, (0,0), (w, int(h*effectDensity_perc)), (255,255,255), -1)
        else:
            return array
        
    
    def revealUp(self, effectDensity_perc):
        
        array = self.originalNpArray.copy()
        h,w = array.shape[:2]
        if effectDensity_perc > 0:
            return cv2.rectangle(array, (0, int(h * (1 - effectDensity_perc))), (w,h), (255,255,255), -1)
        else:
            return array
        
    
    def generateEffect(self, effectName, endLevel = None):
        
        try:
            method = getattr(self, effectName)
        except:
            raise KeyError("Efect: " + effectName + " not found")
        
        # check mehod args
        inspection = inspect.getfullargspec(method)
        
        assert 'self' in inspection.args
        assert 'effectDensity_perc' in inspection.args
        assert len(inspection.args) in [2,3]
        
        outputFileBaseName = Path(self.outputDir) / self.imageFilePath.stem
        
        if len(inspection.args) == 3:
            assert 'endLevel' in inspection.args
            outputFileBaseNameComponents = [outputFileBaseName, effectName, endLevel]
            endLevel_used = True
        else:
            outputFileBaseNameComponents = [outputFileBaseName, effectName]
            endLevel_used = False
            
        outputFilePath = "_".join([str(el) for el in outputFileBaseNameComponents]) + ".mp4"
        
        totalFrames = int(self.duration_s * self.fps)
        assert totalFrames > 1
        
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        imageHeight, imageWidth = self.originalNpArray.shape[:2]
        outFile = cv2.VideoWriter(str(outputFilePath), fourcc, self.fps, (imageWidth, imageHeight))
        
        for frameIdx in range(totalFrames):
            
            effectDensity_perc = frameIdx / (totalFrames - 1)
            
            if endLevel_used:
                frame = method(endLevel = endLevel, effectDensity_perc = effectDensity_perc)
            else:
                frame = method(effectDensity_perc = effectDensity_perc)
            outFile.write(frame)
        
        outFile.release()


def makeAllEffects(srcImage, outputDir, fps, duration_s, blurLevel):
    effectMaker = ImageEffectToVideo_Cls(srcImage, outputDir, fps, duration_s)
    effectMaker.generateEffect("blur", endLevel = blurLevel)
    effectMaker.generateEffect("fade")
    effectMaker.generateEffect("revealRight")
    effectMaker.generateEffect("revealLeft")
    effectMaker.generateEffect("revealUp")
    effectMaker.generateEffect("revealDown")


if __name__ == "__main__":
    inputPath = r'../../userFiles/inputs/Cars.jpg'
    outputDir = r'ImageEffectToVideo_workspace'
    fps = 30
    duration_s = 5
    
    makeAllEffects(inputPath,
                   outputDir,
                   fps, duration_s,
                   blurLevel = 100)
    

