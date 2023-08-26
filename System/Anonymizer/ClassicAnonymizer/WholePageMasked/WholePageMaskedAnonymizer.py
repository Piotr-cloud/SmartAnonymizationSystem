'''
Created on 20 sty 2021

@author: piotr
'''
from Anonymizer.ClassicAnonymizer.ClassicAnonymizer import Anonymizer_Classic_AbstCls
from SpaceSpecificProcessor._2D.Mask import MaskGenerator_Cls


class Anonymizer_Classic_SameMethodWholePage_AbstCls(Anonymizer_Classic_AbstCls):
    """
    Whole page means appling the method whole alternate image and merge two images by masked area 
    """

    def _anonymize(self, nparray, detections):
        
        blurredImage = self._anonymizeWholePage(nparray, detections.getLongestEdgeExposition())
        blurMask = MaskGenerator_Cls().getMaskOfDetections(nparray, detections)
        
        nparray = self._asp.replaceRegions(nparray, blurredImage, blurMask)
        
        return nparray


class Blur_MaskedPage_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Blur"
        
    @staticmethod
    def getDescription():
        return "Applying blur to the area"
    
    def _anonymizeWholePage(self, area, level):
        return self._blur(area, level)
    
    


class GaussianBlur_MaskedPage_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "GausBlur"
        
    @staticmethod
    def getDescription():
        return "Applying gaussian blur to the area"
    
    def _anonymizeWholePage(self, area, level):
        return self._gaussianBlur(area, level)
        
        


class ResolutionDowngrade_MaskedPage_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "ResDown"
        
    @staticmethod
    def getDescription():
        return "Resolution downgrade in the area"
    
    def _anonymizeWholePage(self, area, level):
        return self._resolutionDowngrade(area, level)




class Black_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Black"
        
    @staticmethod
    def getDescription():
        return "Black the area"
    
    def _anonymizeWholePage(self, area, level):
        level # unused
        return self._black(area)




class AverageColor_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "AverageColor"
        
    @staticmethod
    def getDescription():
        return "Fill the area with image average color"
    
    def _anonymizeWholePage(self, area, level):
        level # unused
        return self._averageColor(area)




class WhiteNoise_Anonymizer_Cls(Anonymizer_Classic_SameMethodWholePage_AbstCls):
    
    @staticmethod
    def getName(): 
        return "WhiteNoise"
        
    @staticmethod
    def getDescription():
        return "Fill the area with white noise"
    
    def _anonymizeWholePage(self, area, level):
        level # unused
        return self._whiteNoise(area)






    
    
