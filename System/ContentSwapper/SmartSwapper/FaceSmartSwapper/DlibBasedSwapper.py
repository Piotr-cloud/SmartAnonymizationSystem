'''
Created on May 27, 2023

@author: piotr
'''
from SW_Licensing.SW_License import HostSWLicense_Cls
from ContentSwapper.SmartSwapper.FaceSmartSwapper.FaceSmartSwapper import FaceSmartSwapper_AbstCls
import dlib
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path,\
    UserCfg_Int_Limited
from NonPythonFiles.WorkersFiles.ContentSwappers.DlibBasedSwapper import DlibBasedSwapper_defaultModel_path
from Space.Point import Point_Cls
from Space._2D.Shapes.Polygon import PolygonShape_Cls
#from _otherTools.NpArrayViewer import viewer



class DlibBasedSwapper_Cls(FaceSmartSwapper_AbstCls):
    
    @staticmethod
    def getName(): 
        return "DlibBasedSwapper"
        
    @staticmethod
    def getDescription():
        return "Based on dlib.shape_predictor and using openCV for seamlessClone"
    
    
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    
    def __init__(self,
                 
                 additionalSurroundings_perc = UserCfg_Int_Limited(
                     name = "Additional context of area [%]",
                     description = "Detection area is enhanced by provided value to give more context to the swapper",
                     lower_limit = 0,
                     defaultValue = 10,
                     upper_limit = 50), # TODO: delete this
                 
                 keyPointsLimit = UserCfg_Int_Limited(
                     name = "Keypoints number limit",
                     description = "The might be no need reasonable quality reasons to use all available face landmark keypoints and on the other hand limiting them might speed up swap process",
                     lower_limit = 3,
                     defaultValue = 68,
                     upper_limit = 1000),
                 
                 modelFile = UserCfg_Path(name = "Model file",
                                         description = "Dlib face shape predictor model file - can be downloaded from  http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
                                         path = DlibBasedSwapper_defaultModel_path)):
        
        
        self._additionalSurroundings_perc = self.resolveArgument(additionalSurroundings_perc)
        self._keyPointsLimit = self.resolveArgument(keyPointsLimit)
            
        self._modelFile = self.resolveArgument(modelFile)
        
        self._predictor = dlib.shape_predictor(str(self._modelFile))
        
        FaceSmartSwapper_AbstCls.__init__(self)

    
    def _limitFloatFrom0To1(self, floatVal):
        return min(max(floatVal, 0.0), 1.0)
        

    def _convertKeyPointsIntoPointObjects(self, keyPoints, h, w):
        
        return [Point_Cls(self._limitFloatFrom0To1(part.x / w), self._limitFloatFrom0To1(part.y / h)) for part in keyPoints.parts()[:self._keyPointsLimit]]
    
        
    def _swapFaces(self, srcFace, srcFace_coords, destFace, destFace_coords):
        
        #viewer.saveWithID(srcFace, "srcFace")
        #viewer.saveWithID(destFace, "destFace")
        
        srcFaceKeyPoints = self._predictor(srcFace, dlib.rectangle(*srcFace_coords))
        destFaceKeyPoints = self._predictor(destFace, dlib.rectangle(*destFace_coords))
        
        srcShape    =  PolygonShape_Cls( points = self._convertKeyPointsIntoPointObjects(srcFaceKeyPoints,   *srcFace.shape[:2]) )
        destShape   =  PolygonShape_Cls( points = self._convertKeyPointsIntoPointObjects(destFaceKeyPoints,  *destFace.shape[:2]) )
        
        #viewer.saveWithID(viewer.drawVertexes(srcFace, srcShape, color = (0,255,0), addNumbers=False), "srcFacePoints")
        #viewer.saveWithID(viewer.drawVertexes(destFace, destShape, addNumbers=False), "destFacePoints")
        
        #viewer.saveWithID(viewer.drawVertexes(srcFace, srcShape, color = (0,255,0), addNumbers=True), "srcFacePoints_withNumbers")
        #viewer.saveWithID(viewer.drawVertexes(destFace, destShape, addNumbers=True), "destFacePoints_withNumbers")
                
        modifiedDestFace = self._asp.pasteSrcPolygonDataIntoDestPolygonData(srcFace, srcShape, destFace, destShape, seamlessClone_flag = True)
        
        return modifiedDestFace
        
    
    
    def _swap(self, srcObjectView, destObjectView):
        
        #destArray = destObjectView.getNpArrayCopy()
        
        srcFace, srcFace_newCoords   =  self._asp.getDetectionViewAsRectangleArray(srcObjectView, self._additionalSurroundings_perc, returnNewAbsCoordsToo = True)
        
        destFace, destFace_newCoords  =  self._asp.getDetectionViewAsRectangleArray(destObjectView, self._additionalSurroundings_perc, returnNewAbsCoordsToo = True)
        
        swappedFace = self._swapFaces(srcFace, srcFace_newCoords, destFace, destFace_newCoords)
                
        if swappedFace is not None:
            
            result = self._asp.pasteNewContentsWithoutSurroundingsIntoRegionWrappingRectangleArea(
                destDetectionView = destObjectView, 
                newContent_rectangle = swappedFace, 
                surroundingsOriginally_perc = self._additionalSurroundings_perc, 
                seamlessClone = False)
            
            #viewer.saveWithID(result, "result")
            
            return result
            
        else:
            return "Failed"
        




