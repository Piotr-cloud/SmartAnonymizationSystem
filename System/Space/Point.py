'''
Created on 9 sty 2021

@author: piotr
'''

import math


class Point_Cls():

    def __init__(self, x_coord, y_coord):
        
        """
        Relative coordinates shall be provided - in range from 0 to 1
        """
        
        self._setNewCoords(x_coord, y_coord)


    def _setNewCoords(self, x_coord, y_coord):
        
        assert isinstance(x_coord, float)
        assert isinstance(y_coord, float)
        
        if not 0.0 <= x_coord <= 1.0:
            raise ValueError("Point out of the image. x = " + str(x_coord))
         
        if not 0.0 <= y_coord <= 1.0:
            raise ValueError("Point out of the image. y = " + str(y_coord))

        self.x = x_coord
        self.y = y_coord
        
        

    def getCoords(self):
        return self.x, self.y


    def getAbsoluteCoords(self, image_h, image_w):
        return int(self.x * image_w), int(self.y * image_h)
    
    
    def getDistanceToReferencePoint(self, referencePoint):
        return math.sqrt( (self.x - referencePoint.x) ** 2 + (self.y - referencePoint.y) ** 2 )
    
    
    def __eq__(self, other):
        if type(other) == Point_Cls:
            return (self.x == other.x) and (self.y == other.y)
        else:
            raise TypeError("Cannot compare Point_Cls to non Point_Cls object")
    
    
    def copy(self):
        return Point_Cls(self.x, self.y)
    
    
    def __lt__(self, other):
        """
        Ordering as RTL scripting 
        """
        return (self.y, self.x) < (other.y, other.x)


    def __hash__(self):
        return object.__hash__(self)


    def __str__(self):
        return "(%.4f, %.4f)" % (self.x, self.y)




