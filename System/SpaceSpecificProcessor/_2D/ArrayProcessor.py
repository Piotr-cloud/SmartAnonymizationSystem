'''
Created on Mar 20, 2021

@author: piotr
'''

import numpy as np
import cv2
from Space._2D.Shapes.Box import BoxShape_Cls
from SpaceSpecificProcessor._2D.Mask import MaskGenerator_Cls
from View.View import View_Cls
from Annotator.Annotator import Annotator_Cls
#from _otherTools.NpArrayViewer import viewer


class ArraySpecificProcessor_Cls(object):
    '''
    stateless class
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    def _valArr(self, array_):
        """
        validate array type
        """            
        assert isinstance(array_, np.ndarray)
        
     
    def getInnerRectangle(self, array, left_ind, top_ind, right_ind, bottom_ind):
        
        self._valArr(array)
        
        return array[top_ind : bottom_ind, left_ind : right_ind].copy()
    
    
    def replaceRegions(self, destArray, srcArray, regionsMask):
        
        return self.replaceSingleRegion(destArray, srcArray, regionsMask, False)
        
    
    def replaceSingleRegion(self, destArray, srcArray, regionMask, seamlessClone = False):
        """
        not-in-place operation
        TBD: This changed! Check it (in-place -> not-in-place)
        """
        
        maskArray = regionMask.getMaskArray()
        
        self._valArr(destArray)
        self._valArr(srcArray)
        self._valArr(maskArray)
        
        #destArray = destArray[:]
        
        assert destArray.shape == srcArray.shape == maskArray.shape
            
        if seamlessClone:
            maskArray = maskArray[:,:,-1]
            _, maskArray = cv2.threshold(maskArray,127,255,cv2.THRESH_BINARY)
            maskBoundingBox = cv2.boundingRect(maskArray)
            
            center = (
                (maskBoundingBox[0] + int(maskBoundingBox[2] / 2), 
                 maskBoundingBox[1] + int(maskBoundingBox[3] / 2)
                 )
                ) # TODO: is it correct ?? 
            
            final_array = cv2.seamlessClone(srcArray, destArray, maskArray, center, cv2.NORMAL_CLONE)

        else:
            
            destRegionsMask = np.ones(maskArray.shape).astype(np.uint8)*255 - maskArray
    
            final_array = cv2.bitwise_and(srcArray, maskArray) + cv2.bitwise_and(destArray, destRegionsMask)  
        
        #destArray[:] = final_array[:]
        
        return final_array
    
    
    def resize(self, npArray, height_2_width_ratio, enhance=True):
        
        height, width = npArray.shape[:2]
        
        new_height = height
        new_width = height / height_2_width_ratio
        
        if (new_width > width) ^ (enhance):
            new_width = width
            new_height = width * height_2_width_ratio
        
        return cv2.resize(npArray, (int(new_width), int(new_height)), interpolation = cv2.INTER_AREA)
    
    
    
    def getDetectionViewAsRectangleArray(self, srcDetectionView, additionalSurroundings_perc = 0, returnNewAbsCoordsToo = False):
        
        """
        Loads detection view and transforms it into rectangle (if irregular shape)
        additional surroundings can be added as percetage of base rectangle edge
        
        
        Step 1 - shape transormation:
        
              x---x      +---+
             /   /       |   |
            /   /   ->   |   |
           /   /         |   |
          x---x          +---+
        
        
        
        Step 2 - additional surroundings addition:
        

                       +-------+      +-------+
           +---+       | +---+ |      |       |
           |   |       | |   | |      |       |
           |   |   ->  | |   | |  ->  |       |
           |   |       | |   | |      |       |
           +---+       | +---+ |      |       |
                       +-------+      +-------+
        
        """
        
        assert isinstance(srcDetectionView, View_Cls)
        
        
        region = srcDetectionView.getDetection().getShape()
        array = srcDetectionView.getNpArrayCopy()
        
        self._valArr(array)
        
        assert region.getNumberOfSides() == 4
        
        (left_addS, top_addS, right_addS, bottom_addS), (left, top, right, bottom) = region.getExtremumCoordinatesAbsolute(*array.shape[:2], additionalSurroundings_perc)
        
        detectionArea = self.getInnerRectangle(array, left_addS, top_addS, right_addS, bottom_addS)

        if isinstance(region, BoxShape_Cls):
            transformedArray = detectionArea
        
        else:
            # make transformation
            
            area_h, area_w = detectionArea.shape[:2]
            
            TL_absCoordinates, TR_absCoordinates, BR_absCoordinates,  BL_absCoordinates = region.getPointsAbsoluteCoords(*array.shape[:2])
            
            # print(TL_absCoordinates, TR_absCoordinates, BR_absCoordinates,  BL_absCoordinates)
            
            TL_areaAbsCoordinates = [TL_absCoordinates[0] - left_addS, TL_absCoordinates[1] - top_addS]
            TR_areaAbsCoordinates = [TR_absCoordinates[0] - left_addS, TR_absCoordinates[1] - top_addS]
            BR_areaAbsCoordinates = [BR_absCoordinates[0] - left_addS, BR_absCoordinates[1] - top_addS]
            BL_areaAbsCoordinates = [BL_absCoordinates[0] - left_addS, BL_absCoordinates[1] - top_addS]
            
            
            pts1 = np.float32([ TL_areaAbsCoordinates,  TR_areaAbsCoordinates,  BR_areaAbsCoordinates,  BL_areaAbsCoordinates])
            pts2 = np.float32([ [0,0],                  [area_w, 0],            [area_w, area_h],       [0, area_h] ])
 
            perspectiveTransform = cv2.getPerspectiveTransform(pts1, pts2)
             
            transformedArray = cv2.warpPerspective(detectionArea, perspectiveTransform, (area_w, area_h))
        
        
        if returnNewAbsCoordsToo:
            relativeCoordsInImagePart = (left - left_addS, top - top_addS, right - left_addS, bottom - top_addS)
            
            return transformedArray, relativeCoordsInImagePart
            
        else:
            return transformedArray


    def cutArrayMiddleOutOfTheSurroundings(self, array, surroundingsSize_perc = 0):
        """
        Just limits array to get it's middle;
        Example:
        input:   When surroundingsSize_perc == 5
        output:  array[5% : 95%, 5% : 95%]   but converts x% into int accordingly
        """
        
        self._valArr(array)
        
        if not surroundingsSize_perc:
            return array
        
        assert isinstance(surroundingsSize_perc, int)
        assert surroundingsSize_perc > 0
        
        array_h, array_w = array.shape[:2]
        
        new_array_w = int(array_w / (1. + 2. * (surroundingsSize_perc/100.)))
        new_array_h = int(array_h / (1. + 2. * (surroundingsSize_perc/100.)))
        
        width_halfDifference   =  int((array_w - new_array_w) / 2)
        height_halfDifference  =  int((array_h - new_array_h) / 2)
        
        new_array = array[height_halfDifference : height_halfDifference + new_array_h, width_halfDifference : width_halfDifference + new_array_w]
        
        return new_array

    
    def pasteNewContentsWithoutSurroundingsIntoRegionWrappingRectangleArea(self, destDetectionView, newContent_rectangle, surroundingsOriginally_perc = 0, seamlessClone = True):
        """
        not-in-place operation
        """
        
        array = destDetectionView.getNpArrayCopy()
        region = destDetectionView.getDetection().getShape()
        
        self._valArr(array)
        self._valArr(newContent_rectangle)
        
        left_abs, top_abs, right_abs, bottom_abs = region.getExtremumCoordinatesAbsolute(*array.shape[:2], surroundingsOriginally_perc)[0]
        
        target_w = right_abs - left_abs
        target_h = bottom_abs - top_abs
        
        if not (target_h == newContent_rectangle.shape[0]) or \
           not (target_w == newContent_rectangle.shape[1]):
            # Resize newContent_rectangle to fit target place
            newContent_rectangle = cv2.resize(newContent_rectangle, (target_w, target_h), interpolation = cv2.INTER_AREA)
        
        assert target_h == newContent_rectangle.shape[0]
        assert target_w == newContent_rectangle.shape[1]
        
        if not seamlessClone:
            array[top_abs:bottom_abs, left_abs:right_abs] = newContent_rectangle
            
        else:
            maskArray = np.zeros(newContent_rectangle.shape, newContent_rectangle.dtype)
            maskArray.fill(255)
            
            center = int((right_abs + left_abs) / 2), int((bottom_abs + top_abs) / 2)

            final_array = cv2.seamlessClone(newContent_rectangle, array, maskArray, center, cv2.NORMAL_CLONE)
            
            array[:] = final_array[:]
        
        return array
    
    
    def pasteSrcPolygonDataIntoDestPolygonData(self, srcArray, srcShape, destArray, destShape, seamlessClone_flag = False):
        
        """
        not-in-place operation; from any polygon to another;
        Performs swap by division of polygon by swapping triangles defined by Delaunay triangulation
        """
        
        self._valArr(srcArray)
        self._valArr(destArray)
        
        srcShapePointsLen = srcShape.getNumberOfVertexes()
        destShapePointsLen = destShape.getNumberOfVertexes()
        
        seamlessClone_flag = bool(seamlessClone_flag)
        
        assert srcShapePointsLen == destShapePointsLen, "Cannot paste into shape of the same number of vertexes"
        
        triangulars = destShape.triangulate()
        
        srcTriangles = srcShape.splitIntoTriangles(triangulars)
        destTriangles = destShape.splitIntoTriangles(triangulars)
        
        numberOfTriangles = len(srcTriangles)
        
        assert numberOfTriangles == len(destTriangles), "Different number of triangles! Triangulation do not match"
        
        newFaceInPlaceArray = np.zeros(destArray.shape, dtype=np.uint8) # create black image to paste to it new face
        cloneMask = MaskGenerator_Cls().getBlankMaskArray(destArray)
        
        anotator = Annotator_Cls()
        
        srcArrayWithTriangles = srcArray.copy()
        destArrayWithTriangles = destArray.copy()
        
        for triangleIdx in range(numberOfTriangles):
            
            srcTriangle = srcTriangles[triangleIdx]
            destTriangle = destTriangles[triangleIdx]
            
            newFaceInPlaceArray = self.pasteSrcTriangleDataIntoDestTriangleData(srcArray, srcTriangle, newFaceInPlaceArray, destTriangle, drawDebug = ( triangleIdx in [0, 9, 19, 29, 49] ))
        
            cloneMask.addRegion(destTriangle)
            
            anotator._annotateShapeWithColor(srcArrayWithTriangles, srcTriangle, color = (0,255,0), thickness = 6)
            anotator._annotateShapeWithColor(destArrayWithTriangles, destTriangle, color = (0,0,255), thickness = 6)
            
        # viewer.saveWithID(newFaceInPlaceArray, "beforeResize")
        # viewer.saveWithID(srcArrayWithTriangles, "srcArrayWithTriangles")
        # viewer.saveWithID(destArrayWithTriangles, "destArrayWithTriangles")
        
        # viewer.saveWithID(destArray, "destArray")
        # viewer.saveWithID(newFaceInPlaceArray, "newFaceInPlaceArray")
        
        # viewer.saveWithID(cloneMask.getMaskArray(), "Whole Clone mask")
        
        finalArray = self.replaceSingleRegion(destArray, newFaceInPlaceArray, cloneMask, seamlessClone = seamlessClone_flag)
        
        # viewer.saveWithID(finalArray, "result_noSeamless")
        # viewer.saveWithID(finalArray, "result_seamless")
        
        
        return finalArray
    
    
    def pasteSrcTriangleDataIntoDestTriangleData(self, srcArray, srcTriangle, destArray, destTriangle, drawDebug = False):
        
        # if drawDebug:
        #     viewer.saveWithID(
        #         viewer.drawVertexes(
        #             viewer.drawVertexes(srcArray,
        #                                 srcTriangle, 
        #                                 addNumbers = True),
        #             destTriangle,
        #             color = (0,255,0),
        #             addNumbers = True), 
        #         "affineTransform")
        
        affineTransform = cv2.getAffineTransform(
            np.array([point.getAbsoluteCoords(*srcArray.shape[:2]) for point in srcTriangle.getPoints()]).astype(np.float32),
            np.array([point.getAbsoluteCoords(*srcArray.shape[:2]) for point in destTriangle.getPoints()]).astype(np.float32)
            )
        
        # if drawDebug: viewer.saveWithID(srcArray, "beforeWrapping")
            
        modifiedArray = cv2.warpAffine(srcArray, affineTransform, srcArray.shape[:2][::-1])
        # if drawDebug: viewer.saveWithID(modifiedArray, "wrapped")
        
        modifiedArray = cv2.resize(modifiedArray, destArray.shape[:2][::-1])
        # if drawDebug: viewer.saveWithID(modifiedArray, "wrapped resized")
        
        cloneMask = MaskGenerator_Cls().getBlankMaskArray(destArray)
        cloneMask.addRegion(destTriangle)
        
        # if drawDebug: viewer.saveWithID(cloneMask.getMaskArray(), "Clone mask")
        
        finalArray = self.replaceSingleRegion(destArray, modifiedArray, cloneMask, seamlessClone = False)
        
        # if drawDebug: viewer.saveWithID(finalArray, "replaced")
                
        return finalArray
    

    def pasteNewContentIntoDestDetectionView(self, destDetectionView, newContent_rectangle, surroundingsOriginally_perc = None, seamlessClone = False):
        """
        not-in-place operation
        
        When shapes do not match transformation is done so newContent fits detection zone
        """
        
        assert isinstance(destDetectionView, View_Cls)
        assert isinstance(newContent_rectangle, np.ndarray)
        
        if surroundingsOriginally_perc:
            newContent_rectangle = self.cutArrayMiddleOutOfTheSurroundings(newContent_rectangle, surroundingsOriginally_perc)
        
        region = destDetectionView.getDetection().getShape()
        destArray = destDetectionView.getNpArrayCopy()
        
        assert region.getNumberOfSides() == 4 # only tetragon is supported
        
        array_h, array_w = destArray.shape[:2]
        
        newContent_h, newContent_w = newContent_rectangle.shape[:2]
        
        transformBorderReplicateSize = int(array_h / newContent_h + array_w / newContent_w) + 1  # " + 1" - since transformation algorithm might input noice on borders, borders are enchanged temporarily with + 1
        tbrs = transformBorderReplicateSize # trbs is a border added to newContent_rectangle image to add surrounding bytes 
        
        replacementMask = MaskGenerator_Cls().getBlankMaskArray(destArray)
        
        replacementMask.addRegion(region)
            
        TL_absCoordinates, TR_absCoordinates, BR_absCoordinates,  BL_absCoordinates = region.getPointsAbsoluteCoords(array_h, array_w)
        
        #print(TL_absCoordinates, TR_absCoordinates, BR_absCoordinates,  BL_absCoordinates)
        
        if tbrs > 0:
            newContent = cv2.copyMakeBorder(newContent_rectangle, tbrs, tbrs, tbrs, tbrs, cv2.BORDER_REPLICATE)
        
        pts1 = np.float32([ [tbrs, tbrs],         [tbrs + newContent_w, tbrs],   [tbrs + newContent_w, tbrs + newContent_h],   [tbrs, tbrs + newContent_h] ])
        pts2 = np.float32([ TL_absCoordinates,    TR_absCoordinates,             BR_absCoordinates,                            BL_absCoordinates])
        
        perspectiveTransform = cv2.getPerspectiveTransform(pts1, pts2)
         
        newViewArray = cv2.warpPerspective(newContent, perspectiveTransform, (array_w, array_h))
        
        finalArray = self.replaceSingleRegion(destArray, newViewArray, replacementMask, seamlessClone)
        
# TODO: remove debug stuff        
#         viewer.saveWithID(destArray, id_ = "destArray")
#         viewer.saveWithID(replacementMask.getNpArrayCopy(), id_ = "ReplacementMask")
#         viewer.saveWithID(newContent_rectangle, id_ = "newContent_rectangle")
#         viewer.saveWithID(newViewArray, id_ = "newViewArray")
#         viewer.saveWithID(newContent, id_ = "newContent")
#         viewer.saveWithID(finalArray, id_ = "finalArray")
        
        return finalArray


    def flip(self, array):
        return cv2.flip(array, 0)
    
    



# TODO: remove debug stuff      
# if __name__ == "__main__":
#
#     from Detections.Detection import Tetragon_Cls
#
#     imageFilePath = r"/home/piotr/ProjektMagisterski/BazaDanych/Images/Other/XxY.jpeg"
#     newViewSaveFileDir = r"/home/piotr/ProjektMagisterski/_Outputs/PartsTesting"
#     newViewSaveFileBaseName = r"View_3"
#
#     vertexesAbsoluteCoords = [[1381,713], [3615,846], [3414,2577], [737,2079]]
#
#     image = cv2.imread(imageFilePath)
#
#     asp = ArraySpecificProcessor_Cls()
#
#     image_h, image_w = image.shape[:2]
#
#     vertexes = [ Point_Cls(vertexAbsoluteCoords[0] / image_w, 
#                            vertexAbsoluteCoords[1] / image_h) 
#                            for vertexAbsoluteCoords in vertexesAbsoluteCoords ]
#
#     detection = Tetragon_Cls(0, vertexes)
#
#
#     newView = asp.getDetectionViewAsRectangleArray(View_Cls(image, detection))
#
#     newView = asp.flip(newView)
#
#     newImage = asp.pasteNewContentIntoDestDetectionView(View_Cls(image, detection), newView, True)












