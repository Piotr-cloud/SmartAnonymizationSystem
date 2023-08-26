'''
Created on 21 sty 2021

@author: piotr
'''


import numpy as np
import cv2
import math
from Anonymizer.Anonymizer import Anonymizer_AbstCls
from SW_Licensing.SW_License import HostSWLicense_Cls



class Anonymizer_Classic_AbstCls(Anonymizer_AbstCls):
        
    @staticmethod
    def getClassesServiced():
        return "All"
    
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    def __init__(self):
        assert type(self) != Anonymizer_Classic_AbstCls
        Anonymizer_AbstCls.__init__(self)
        
    def _black(self, area):
        return np.ones(shape = area.shape, dtype = np.uint8)
    
    
    def _gaussianBlur(self, area, level = 1.0):
        
        factor_pixelsToParam = 10
        
        verticalParam = area.shape[0] * level / factor_pixelsToParam
        horizontalParam = area.shape[1] * level / factor_pixelsToParam
        
        
        verticalParam = int(verticalParam / 2) * 2 + 1
        horizontalParam = int(horizontalParam / 2) * 2 + 1
        
        commonParam = int((horizontalParam + verticalParam) / 2)
            
        return cv2.GaussianBlur(area, (horizontalParam,verticalParam), commonParam)
    
    
    def _blur(self, area, level = 1.0):
        """
        not-in-place operation
        """
        factor_pixelsToParam = 10
        
        verticalParam = int(area.shape[0] * level / factor_pixelsToParam)
        horizontalParam = int(area.shape[1] * level / factor_pixelsToParam)
        
        return cv2.blur(area, (horizontalParam,verticalParam))
        
        
    def _averageColor(self, area):
        return np.ones(shape = area.shape, dtype = np.uint8)*np.uint8(area.mean(axis=0).mean(axis=0))
    
    
    def _whiteNoise(self, area, level=None):
        
        return np.random.randint(255, size=area.shape).astype(np.uint8)
    

    def _resolutionDowngrade(self, area, level = 1.0):
        """
        When relativeLevel_flag is True then:
            Divides in blocks of level x level; in ex. when level = 6 then 6 x 6 cells with equal RBG output is produced
        
        Otherwise:
            Merges every level x level pixels into one RGB value
            
        _ internal x_downgradeFactor and y_downgradeFactor varables represent size of new cells of the same RGB
        
        not-in-place operation
        
        optimal level to anonymize face is: relative, 15
        """
        area = area.copy()
        
        factor_edgeToMaxPixels = 20
        
        if level > 0:
            
            newBoxes_each_axis = math.ceil(factor_edgeToMaxPixels / level)
            
            y_downgradeFactor = math.ceil(area.shape[0] / newBoxes_each_axis)
            x_downgradeFactor = math.ceil(area.shape[1] / newBoxes_each_axis)
                
            for newGrid_y in range(newBoxes_each_axis):
                
                cell_y_Start = newGrid_y * y_downgradeFactor
                cell_y_End = (newGrid_y + 1) * y_downgradeFactor
                
                for newGrid_x in range(newBoxes_each_axis):
                    
                    cell_x_Start = newGrid_x * x_downgradeFactor
                    cell_x_End = (newGrid_x + 1) * x_downgradeFactor
                
                    cellOriginalContents = area[ cell_y_Start : cell_y_End, cell_x_Start : cell_x_End]
                    
                    new_pixel = cv2.mean(cellOriginalContents)
                    
                    cv2.rectangle(area, (cell_x_Start,cell_y_Start), (cell_x_End, cell_y_End), new_pixel , -1)
        
        return area




