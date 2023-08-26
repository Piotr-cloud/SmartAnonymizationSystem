'''
Created on May 28, 2023

@author: piotr
'''
import math
from Space._2D.Shapes.Polygon import PolygonShape_Cls




class Triangle_Cls(PolygonShape_Cls):
    
    
    def __init__(self, pointA, pointB, pointC):
         
        PolygonShape_Cls.__init__(self, [pointA, pointB, pointC])
    




class LineDirection_Cls():
    
    def __init__(self, pointA, pointB):
        
        self._pointA = pointA
        self._pointB = pointB
        
        A_x, A_y = self._pointA.getCoordinates()
        B_x, B_y = self._pointB.getCoordinates()
        
        dx = B_x - A_x
        dy = B_y - A_y
        
        vectorLen = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        
        if vectorLen > 0:
            self._dir = math.acos(dx / vectorLen)
        
        else:
            self._dir = "undefined"
        
    def __lt__(self, other):
        
        if self._dir != other._dir:
            
            if self._dir == "undefined" or other._dir == "undefined":
                return False
            
            else:
                return self._dir < other._dir
            
        else:
            return False


    def __eq__(self, other):
        return self._dir == other._dir


    
    
    
    
