'''
Created on 23 lis 2020

@author: piotr
'''

from Space._2D.Shapes.Polygon import PolygonShape_Cls
from Space.Point import Point_Cls


class BoxShape_Cls(PolygonShape_Cls):
    
    def __init__(self, left, top, right, bottom):
        """
        Coordinates from 0.0 to 1.0
        
        Rectangle takes coordinates of extreme points: (left, top) and (right, bottom) 
            unless flag: yoloFormat == True then right and top means difference from  
        
        Internally kept is as follows:
            (left, top) x (right, bottom)
        
        """
        
        self.TL_point = Point_Cls(left, top)
        self.BR_point = Point_Cls(right, bottom)
        
        
        if left == right:
            raise ValueError("Rectangle cannot be a vertical line")
        
        if top == bottom:
            raise ValueError("Rectangle cannot be a horizontal line")
        
        
        if left != min([left,  right]):
            raise ValueError("Rectangle left coord is greater than right:\nLeft: " + str(left) + "\nRight: " + str(right))
        
        if top != min([top, bottom]):
            raise ValueError("Rectangle top coord is greater than bottom:\nTop: " + str(left) + "\nBottom: " + str(right))
        
        
        TR_point = Point_Cls(x_coord = self.BR_point.x, y_coord = self.TL_point.y)
        BL_point = Point_Cls(x_coord = self.TL_point.x, y_coord = self.BR_point.y)
        
        points = [self.TL_point, TR_point, self.BR_point, BL_point]
        
        PolygonShape_Cls.__init__(self, points)
    
    
    def _getArea(self):
        
        x_side = self.BR_point.x - self.TL_point.x
        y_side = self.BR_point.y - self.TL_point.y
        
        return x_side * y_side
    
    
    def __str__(self):
        return "Rectangle: " + str(self.TL_point) + " x " + str(self.BR_point)
    
    
    def getShapeParamsPacked(self):
        
        left, top       =  self.TL_point.getCoords()
        right, bottom   =  self.BR_point.getCoords()
        
        return left, top, right, bottom
    
    
    def unpackShapeParams(self, rawParamsData):
        
        assert len(rawParamsData) == 4
        
        left = float(rawParamsData[0])
        top = float(rawParamsData[1])
        right = float(rawParamsData[2])
        bottom = float(rawParamsData[3])
        
        return left, top, right, bottom
    
    



