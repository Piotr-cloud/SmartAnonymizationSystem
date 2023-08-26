'''
Created on Apr 10, 2021

@author: piotr
'''
from Space._2D.Shapes.Polygon import PolygonShape_Cls
from Space._2D.Shapes.Box import BoxShape_Cls



class ShapeSimplifier_Cls():
    
    
    def simplify(self, shapeObj):
        
        if type(shapeObj) == PolygonShape_Cls:
        
            # simplify to Box if possible
            
            if shapeObj.getNumberOfVertexes() == 4:
                # define points candidates
                TL_point, TR_point, BL_point, BR_point = shapeObj.getPoints()
                
                if TL_point.x == BL_point.x:
                    left = TL_point.x # left matches
                    
                    if TL_point.y == TR_point.y:
                        top = TL_point.y # top matches
                        
                        if TR_point.x == BR_point.x:
                            right = BR_point.x # right matches
                            
                            if BL_point.y == BR_point.y:
                                bottom = BR_point.y # bottom matches
                                
                                return BoxShape_Cls(left, top, right, bottom)
        
        # unable to make more simple
        return shapeObj
    
    
    