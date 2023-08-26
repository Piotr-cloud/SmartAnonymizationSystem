'''
Created on Mar 5, 2022

@author: piotr
'''
from ContentSwapper.SmartSwapper.FaceSmartSwapper.FaceSmartSwapper import FaceSmartSwapper_AbstCls
from ContentSwapper.SmartSwapper.FaceSmartSwapper._FaceSmartSwapper_WuHuikai.face_detection import select_face
from ContentSwapper.SmartSwapper.FaceSmartSwapper._FaceSmartSwapper_WuHuikai.face_swap import warp_image_3d
import cv2
import numpy as np
from SpaceSpecificProcessor._2D.Mask import Mask_Cls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Int_Limited
from SW_Licensing.SW_License import License_Cls



class FaceSmartSwapper_Wuhuikai_Cls(FaceSmartSwapper_AbstCls):
    
    @staticmethod
    def getName(): 
        return "WuHukaiFaceSwapper"
        
    @staticmethod
    def getDescription():
        return "Based on dlib and using openCV, origin: https://github.com/wuhuikai/FaceSwap"
    
    @staticmethod
    def getLicense():
        return License_Cls(type_ = "\"Feel free to use it\"",
                           srcCodeLocation = "https://github.com/wuhuikai/FaceSwap",
                           fullStatement = "\"Feel free to use it\" as of: https://github.com/wuhuikai/FaceSwap/issues/46")
    
    
    def __init__(self,
                 additionalSurroundings_perc = UserCfg_Int_Limited(
                     name = "Additional context of area [%]",
                     description = "Detection area is enhanced by provided value to give more context to the swapper",
                     lower_limit = 0,
                     defaultValue = 10,
                     upper_limit = 10000)):
        
        # Resolve worker arguments in case of direct use(skipping dynamic configuration mechanism)
        self._additionalSurroundings_perc = self.resolveArgument(additionalSurroundings_perc)
        
        FaceSmartSwapper_AbstCls.__init__(self)
    
    
    def _validateSrcObjectView(self, srcObjectView):
        srcFace = self._asp.getDetectionViewAsRectangleArray(srcObjectView, self._additionalSurroundings_perc)
        _, _, src_face = select_face(srcFace)
        return src_face is not None
    
    
    def _getWrappedSrcFace(self, src_face, src_points, dst_points, destImageShape):
        
        h, w = destImageShape
        
        return warp_image_3d(src_face, src_points, dst_points, (h, w))
    
    
    def _getDestFaceMask(self, destPoints, destImageShape):
        
        h, w = destImageShape
        
        mask = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(mask, cv2.convexHull(destPoints), 255)
        
        return Mask_Cls(mask, True, 255)
    
    
    def _swapFaces_2(self, src_face, dst_face, src_points, dst_points, dst_shape, dst_img, start = 0, end=48):
        
        destImageShape = dst_face.shape[:2]
        
        warped_src_face = self._getWrappedSrcFace(src_face, src_points[start:end], dst_points[start:end], destImageShape)
        
        mask = self._getDestFaceMask(dst_points, destImageShape)
        
        output = self._asp.replaceSingleRegion(dst_face.copy(), warped_src_face, mask, True)
        
        ##Poisson Blending
        #r = cv2.boundingRect(mask)
        #center = ((r[0] + int(r[2] / 2), r[1] + int(r[3] / 2))) # is it correct ??    
        #output = cv2.seamlessClone(warped_src_face, dst_face, mask, center, cv2.NORMAL_CLONE)

        x, y, w, h = dst_shape
        dst_img_cp = dst_img.copy()
        dst_img_cp[y:y + h, x:x + w] = output
    
        return dst_img_cp
        
    
    def _swapFaces(self, srcFace, destFace):
        
        # Select src face
        src_points, _, src_face = select_face(srcFace, choose = False)
        
        if src_face is not None:
            # Select dst face
            dst_points, dst_shape, dst_face = select_face(destFace, choose = False)
            
            if dst_face is not None:
                
                return self._swapFaces_2(src_face, dst_face, src_points, dst_points, dst_shape, destFace)



