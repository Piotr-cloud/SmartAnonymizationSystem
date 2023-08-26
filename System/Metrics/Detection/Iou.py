'''
Created on Apr 9, 2021

@author: piotr
'''
from Metrics.Detection.Area import Area_Cls
from Space._2D.Shapes.Box import BoxShape_Cls
from Space._2D.Shapes.ShapeSimplifier import ShapeSimplifier_Cls



class IOU_Computer_Cls():
    
    
    def getIouAndUnionSizeOfShapes(self, firstOperand_shapesList, secondOperand_shapesList):
        
        if len(firstOperand_shapesList) == 1 and len(secondOperand_shapesList) == 1:
            shapesSimplifier = ShapeSimplifier_Cls()
            
            firstOperand_shapesList   = [shapesSimplifier.simplify(firstOperand_shapesList[0])]
            secondOperand_shapesList  = [shapesSimplifier.simplify(secondOperand_shapesList[0])] 
            
            if isinstance(firstOperand_shapesList[0], BoxShape_Cls) and isinstance(secondOperand_shapesList[0], BoxShape_Cls):
                
                firstBox   =  firstOperand_shapesList[0]
                secondBox  =  secondOperand_shapesList[0] 
                
                # intersection calculation
                
                middle_x_points = sorted([firstBox.TL_point.x, firstBox.BR_point.x, secondBox.TL_point.x, secondBox.BR_point.x])[1:3]
                middle_y_points = sorted([firstBox.TL_point.y, firstBox.BR_point.y, secondBox.TL_point.y, secondBox.BR_point.y])[1:3]
                
                intersection_size = (middle_x_points[1] - middle_x_points[0]) * (middle_y_points[1] - middle_y_points[0])
                
                # union calculation
                firstBox_size   =  (firstBox.BR_point.x - firstBox.TL_point.x) * (firstBox.BR_point.y - firstBox.TL_point.y)
                secondBox_size  =  (secondBox.BR_point.x - secondBox.TL_point.x) * (secondBox.BR_point.y - secondBox.TL_point.y)
                
                union_size = firstBox_size + secondBox_size - intersection_size
                
                if intersection_size > 0 and union_size > 0:
                    iou = intersection_size / union_size
                    
                else:
                    iou = 0.0
                
                return iou, union_size
                
        
        # if not calculated by now use Area_Cls
        
        firstArea = Area_Cls()
        secondArea = Area_Cls()
        
        for firstAreaShape in firstOperand_shapesList:
            firstArea.addShape(firstAreaShape)
            
        for secondAreaShape in secondOperand_shapesList:
            secondArea.addShape(secondAreaShape)
            
        intersection = firstArea * secondArea
        union = firstArea + secondArea
        
        intersection_size = intersection.size()
        union_size = union.size()
        
        if intersection_size > 0 and union_size > 0:
            iou = intersection_size / union_size
            
        else:
            iou = 0.0
        
        return iou, union_size
    
    
    def getIouOfShapes(self, firstOperand_shapesList, secondOperand_shapesList):
        
        iou, _ = self.getIouAndUnionSizeOfShapes(firstOperand_shapesList, secondOperand_shapesList)
        
        return iou
        
        
    def getIouOfDetectionsMapOfClassId(self, classId, firstDetectionsMap, secondDetectionsMap):
        """
        Returns single float: iou
        """
        
        firstDetectionsMap_classId2Detections   = firstDetectionsMap.getDetectionsPerClassDict()
        secondDetectionsMap_classId2Detections  = secondDetectionsMap.getDetectionsPerClassDict()
        
        if classId in firstDetectionsMap_classId2Detections and classId in secondDetectionsMap_classId2Detections:
            return self.getIouOfDetections(firstDetectionsMap_classId2Detections[classId], secondDetectionsMap_classId2Detections[classId])
        
        else:
            return 0.0
    
    
    def getIouOfDetections(self, firstDetection_list, secondDetections_list):
        """
        classId is not checked so different classIds detections are combined
        Returns single float: iou
        """
        
        firstDetections_shapesList = []
        secondDetections_shapesList = []
        
        for detection in firstDetection_list:
            firstDetections_shapesList.append(detection.shape)
        
        for detection in secondDetections_list:
            secondDetections_shapesList.append(detection.shape)
        
        iou = self.getIouOfShapes(firstDetections_shapesList, secondDetections_shapesList)
        
        return iou
        
        
    def getIouPerClassIdOfDetectionsMap(self, firstDetectionsMap, secondDetectionsMap):
        """
        http://www.cs.umd.edu/~ozdemir/papers/prl_evaluation.pdf
        Chapter 4.1.3
        
        Returns dict:
        - classId(int) : iou(float)
        
        """
        
        classId_2_iou_dict = {}
        
        firstDetectionsMap_classId2Detections   = firstDetectionsMap.getDetectionsPerClassDict()
        secondDetectionsMap_classId2Detections  = secondDetectionsMap.getDetectionsPerClassDict()
        
        secondDetectionsMap_classIdsLeft = set(secondDetectionsMap_classId2Detections.keys())
        
        for classId in firstDetectionsMap_classId2Detections:
            
            if classId in secondDetectionsMap_classId2Detections:
                
                classId_2_iou_dict[classId] = self.getIouOfDetections(
                    firstDetectionsMap_classId2Detections[classId], 
                    secondDetectionsMap_classId2Detections[classId]
                    )
                
                secondDetectionsMap_classIdsLeft.remove(classId)
            
            else:
                classId_2_iou_dict[classId] = 0.0
        
        
        for classId in list(secondDetectionsMap_classIdsLeft):
            classId_2_iou_dict[classId] = 0.0
        
        
        return classId_2_iou_dict




if __name__ == "__main__":
    
    rect = BoxShape_Cls(0., 0., 1., 1.)
    rect2 = BoxShape_Cls(0., 0.5, 1., 1.)
    
    import time
    
    start_time = time.time()
    iou = IOU_Computer_Cls().getIouOfShapes([rect], [rect2])
    
    print("Time consumed[s]: ", time.time() - start_time)
    
    print("Iou = " + str(iou))




