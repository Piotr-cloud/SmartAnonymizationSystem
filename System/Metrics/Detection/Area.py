'''
Created on 19 gru 2020

@author: piotr
'''
import numpy as np
import cv2


class Area_Cls():
    
    """
    Non optimal but tough and universal area computer class
    
    This class is used to define IOU whenever computation of IOU is complicated because of complexed areas comparison due to irregular polygons or multiple shapes.
    
    This class constructs logical matrice of predefined constant size (see method: ._getMatrixSize) that becomes digital map for areas comparison.
    """
    
    def __init__(self, initializationArray = None):
        
        arrayShape = (self._getMatrixSize(), self._getMatrixSize())
        
        if initializationArray is None:
            
            self._area = np.zeros(arrayShape, dtype = np.bool)
        
        else:
            assert isinstance(initializationArray, np.ndarray)
            assert initializationArray.shape == arrayShape
            self._area = initializationArray
        
    
    def _getMatrixSize(self):
        # Of course, it cannot be lower than 1
        return 2000
    
    
    def addShape(self, shape):
        
        if type(shape).__name__ == "BoxShape_Cls":
            self._addBox(shape)
    
        elif type(shape).__name__ == "PolygonShape_Cls":
            self._addPolygon(shape)
        
        else:
            raise TypeError("Unknown shape type, cannot add")
        
    
    def _addBox(self, boxShape):
        
        matrixSize_m1 = self._getMatrixSize() - 1
        
        x_start, y_start = boxShape.TL_point.getCoords()
        x_end, y_end = boxShape.BR_point.getCoords()
        
        
        x_start = int(x_start * matrixSize_m1)
        y_start = int(y_start * matrixSize_m1)
        
        x_end = int(x_end * matrixSize_m1)
        y_end = int(y_end * matrixSize_m1)
        
        area_uint8 = np.uint8(self._area)
        
        self._area = cv2.rectangle(area_uint8, (x_start, y_start), (x_end, y_end), color = 1, thickness = -1).astype(np.bool)
        
        return self._area
    
    
    def _addPolygon(self, polygonShape):
        
        matrixSize_m1 = self._getMatrixSize() - 1
        
        vertexes_absolute = []
        
        for vertex in polygonShape.getPoints():
            vertex_x, vertex_y = vertex.getCoords()
            
            new_vertexData = [int(vertex_x * matrixSize_m1), int(vertex_y * matrixSize_m1)]
            
            vertexes_absolute.append(new_vertexData)
            
        vertexes_formatted = np.array(vertexes_absolute, np.int32).reshape((-1,1,2))
                
        area_uint8 = np.uint8(self._area)
        
        self._area = cv2.fillPoly(area_uint8, [vertexes_formatted], color = 1).astype(np.bool)
                
        
    def __add__(self, other):
        return Area_Cls(self._area + other._area)


    def __mul__(self, other):
        return Area_Cls(self._area * other._area)

    
    def __sub__(self, other):
        return self.__add__(other.__neg__())


    def __neg__(self):
        return Area_Cls(~self._area)
    
    
    def size(self, absolute = False):
        
        sizeAbs = np.count_nonzero(self._area)
        
        if absolute: 
            return sizeAbs
        
        else:
            return sizeAbs / (self._getMatrixSize() ** 2)





