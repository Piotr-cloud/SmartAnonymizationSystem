'''
Created on Nov 5, 2021

@author: piotr
'''

from Space.FrameHolder import FrameHolder_AbstCls
from Space._2D.Array import Array_AbstCls


class Frame_Cls(Array_AbstCls, FrameHolder_AbstCls):
    '''
    classdocs
    '''

    def __init__(self, nparray, videoRelated, frameNumber, HD_storageDir = None):
        '''
        Constructor
        '''
        name = videoRelated._getFrameName(frameNumber)
        
        self._frameNumber   =  frameNumber
        self._videoRelated  =  videoRelated
        
        FrameHolder_AbstCls.__init__(self, videoRelated.getOriginFilePath(), name)
        Array_AbstCls.__init__(self, nparray, explicit_HD_storageDir=HD_storageDir)
    

    def getVideoRelated(self):
        return self._videoRelated
    
    
    def getIndex(self):
        return self._frameNumber
    






