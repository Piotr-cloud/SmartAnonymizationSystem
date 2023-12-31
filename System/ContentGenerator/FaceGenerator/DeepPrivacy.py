'''
Created on 24 sty 2021

@author: piotr
'''

from ContentGenerator.FaceGenerator.FaceGenerator import FaceGenerator_AbstCls
import numpy as np
import logging
from View.View import View_Cls
from SW_Licensing.SW_License import License_Cls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Int_Limited
from SpaceSpecificProcessor._2D.ArrayProcessor import ArraySpecificProcessor_Cls


class DeepPrivacy_Cls(FaceGenerator_AbstCls):
    
    @staticmethod
    def getName(): 
        return "DeepPrivacy"
        
    @staticmethod
    def getDescription():
        return "DNN based face generator, trained with GAN"
    
    @staticmethod
    def getLicense():
    
        return License_Cls(
            type_ = "MIT",
            srcCodeLocation = "https://github.com/hukkelas/DeepPrivacy",
            fullStatement = """MIT License

Copyright (c) 2019 Håkon Hukkelås

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")
    
    def __init__(self,
                 additionalSurroundings_perc = UserCfg_Int_Limited(
                     name = "Additional context of area [%]",
                     description = "Detection area is enhanced to give more context to the swapper",
                     lower_limit = 0,
                     defaultValue = 100,
                     upper_limit = 10000),):
        
        
        FaceGenerator_AbstCls.__init__(self)
        
        from deep_privacy.build import build_anonymizer
        from deep_privacy.logger import rootLogger
        
        rootLogger.setLevel(logging.ERROR)
        
        self._asp = ArraySpecificProcessor_Cls()
        self._additionalSurroundings_perc = self.resolveArgument(additionalSurroundings_perc)
        self.generator = build_anonymizer()
    
    
    def _generateMultiple(self, views):
        
        npArraysOfDetectedAreas = []
        
        for view in views:
            npArraysOfDetectedAreas.append(self._asp.getDetectionViewAsRectangleArray(view, self._additionalSurroundings_perc, returnNewAbsCoordsToo = False))
        
        assert all([isinstance(npArray, np.ndarray) for npArray in npArraysOfDetectedAreas])
            
        newNpArraysOfDetectedAreas = self.generator.detect_and_anonymize_images(images = npArraysOfDetectedAreas)
        
        assert len(newNpArraysOfDetectedAreas) == len(views)
        
        newViews =[]
        
        for idx, view in enumerate(views):
            
            newViewNpArray = self._asp.pasteNewContentsWithoutSurroundingsIntoRegionWrappingRectangleArea(
                destDetectionView = view, 
                newContent_rectangle = newNpArraysOfDetectedAreas[idx], 
                surroundingsOriginally_perc = self._additionalSurroundings_perc, 
                seamlessClone = True)
            
            newViews.append(View_Cls(newViewNpArray, view.getDetection()))
            
        return newViews
    
    
    def _generate(self, view):
        return self._generateMultiple([view])[0]
    

    def _defineStaticAnonymizedViewReferenceForEachObject(self, objectFound, contentSwapperValidating):
        
        self._dSAVRFEO_byAnonymizingBestView(objectFound, contentSwapperValidating)
        


if __name__ == "__main__":
    
    deepPrivacy = DeepPrivacy_Cls()







