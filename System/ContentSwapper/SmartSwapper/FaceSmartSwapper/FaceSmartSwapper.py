'''
Created on Mar 5, 2022

@author: piotr
'''
from ContentSwapper.SmartSwapper.SmartSwapper import SmartSwapper_AbstCls
from ObjectsDetectable.Classes import FaceID
from abc import abstractmethod
#from _otherTools.NpArrayViewer import viewer


class FaceSmartSwapper_AbstCls(SmartSwapper_AbstCls):


    @staticmethod
    def getClassesServiced(): 
        return {FaceID}
    
    
    def _swap(self, srcObjectView, destObjectView):
        
        #destArray = destObjectView.getNpArrayCopy()
        
        srcFace = self._asp.getDetectionViewAsRectangleArray(srcObjectView, self._additionalSurroundings_perc)
        #viewer.saveWithID(srcFace, "srcFace")
        destFace = self._asp.getDetectionViewAsRectangleArray(destObjectView, self._additionalSurroundings_perc)
        #viewer.saveWithID(destFace, "destFace")
        
        swappedFace = self._swapFaces(srcFace, destFace)
        #viewer.saveWithID(swappedFace, "swappedFace")
        
        if swappedFace is not None:
            
            return self._asp.pasteNewContentsWithoutSurroundingsIntoRegionWrappingRectangleArea(
                destDetectionView = destObjectView, 
                newContent_rectangle = swappedFace, 
                surroundingsOriginally_perc = self._additionalSurroundings_perc, 
                seamlessClone = False)
            
        else:
            return "Failed"
    
    
    @abstractmethod
    def _swapFaces(self, srcFace, destFace):
        pass



