'''
Created on Apr 10, 2021

@author: piotr
'''
from math import sqrt, pow, acos, pi
from PolymorphicBases.ABC import Base_AbstCls, abstractmethod



class Shape_AbstCls(Base_AbstCls):
    
    
    def __init__(self):
        assert type(self) != Shape_AbstCls
        self._area = None
    
        
    @abstractmethod
    def getShapeParamsPacked(self):
        '''
        Returns shape defining params(minimalisic way)
        '''
        raise NotImplementedError()
    
    
    @abstractmethod
    def unpackShapeParams(self, rawParamsData):
        """
        This method formats raw params(got with .getShapeParamsPacked to store data for example)
        """
        raise NotImplementedError()


    @abstractmethod
    def getLongestEdge(self):
        raise NotImplementedError()
    
    
    def getArea(self):

        if self._area is None:
            self._area = self._getArea()
        
        return self._area

        
    @abstractmethod
    def _getArea(self):
        raise NotImplementedError()
    

    @abstractmethod
    def getExtremumCoordinates(self):
        """
        Coordinates that defines box that shape is inscribed in 
        """
        raise NotImplementedError()
        
    
    
    def getExtremumCoordinatesAbsolute(self, image_h, image_w, additionalSurroundings_perc = None):
        """
        Returns absolute coords
        
        additionalSurroundings_perc enhance extremum coordinates
        """
        (left_addS, top_addS, right_addS, bottom_addS), (left, top, right, bottom) = self.getExtremumCoordinates(additionalSurroundings_perc)
        
        # Circumscribing rectangle
        left_abs    = int(left * image_w)
        right_abs   = int(right * image_w)
        
        top_abs     = int(top * image_h)
        bottom_abs  = int(bottom * image_h)
        
        # Plus surroundings 
        left_addS_abs    = int(left_addS * image_w)
        right_addS_abs   = int(right_addS * image_w)
        
        top_addS_abs     = int(top_addS * image_h)
        bottom_addS_abs  = int(bottom_addS * image_h)
            
        return (left_addS_abs, top_addS_abs, right_addS_abs, bottom_addS_abs), (left_abs, top_abs, right_abs, bottom_abs)
    
    
    def getDistanceBetweenPoints(self, firstPoint, secondPoint):
        """
        Pythagorean theorem
        """
        
        x_distance = abs(firstPoint.x - secondPoint.x)
        y_distance = abs(firstPoint.y - secondPoint.y)
        
        distance = sqrt(pow(x_distance, 2) + pow(y_distance, 2))
        
        return distance
    
    
    def getAngleOfThreePoints(self, firstPoint, anglePoint, secondPoint, reflexAngle_flag = False):
        """
        Cosine formula
        """
        a = self.getDistanceBetweenPoints(firstPoint, anglePoint)
        b = self.getDistanceBetweenPoints(anglePoint, secondPoint)
        c = self.getDistanceBetweenPoints(firstPoint, secondPoint)
        
        angle = acos(
                        (
                            pow(a,2) + pow(b,2) - pow(c,2)
                        ) 
                            / (2 * a * b)
                    )
        
        if reflexAngle_flag:
            angle = 2 * pi - angle
            
        return angle
    
    
    def limitFloatFrom0To1(self, floatVal):
        return min(max(floatVal, 0.0), 1.0)




