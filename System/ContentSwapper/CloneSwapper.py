'''
Created on Jan 25, 2022

@author: piotr
'''

from ContentSwapper.ContentSwapper import ContentSwapper_AbstCls
from SW_Licensing.SW_License import HostSWLicense_Cls



class CloneSwapper_Cls(ContentSwapper_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Clone swapper"
        
    @staticmethod
    def getClassesServiced():
        return "All"
        
    @staticmethod
    def getDescription():
        return "Swapper that performs replacement by pasting new content with openCV non-AI algorithm"
        
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    def __init__(self):
        ContentSwapper_AbstCls.__init__(self)
    
    
    def _swap(self, srcObjectView, destObjectView):
        
        newContent_rectangle = self._asp.getDetectionViewAsRectangleArray(srcObjectView)
        
        return self._asp.pasteNewContentIntoDestDetectionView(destObjectView, newContent_rectangle, seamlessClone = False)
        

 

class SeamlessCloneSwapper_Cls(CloneSwapper_Cls):
    
    @staticmethod
    def getName(): 
        return "Seamless clone swapper"
    
    @staticmethod
    def getDescription():
        return "Swapper that performs replacement by pasting new content with openCV non-AI algorithm with seamless clone option"
    
    def __init__(self):
        CloneSwapper_Cls.__init__(self)
    
    
    def _swap(self, srcObjectView, destObjectView):
        
        newContent_rectangle = self._asp.getDetectionViewAsRectangleArray(srcObjectView)
        
        return self._asp.pasteNewContentIntoDestDetectionView(destObjectView, newContent_rectangle, seamlessClone = True)








