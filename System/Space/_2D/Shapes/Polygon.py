'''
Created on 9 sty 2021

@author: piotr
'''

from Space._2D.Shapes.Shape import Shape_AbstCls
from Space.Point import Point_Cls
from Metrics.Detection.Area import Area_Cls
from math import sqrt, pow, cos
import random
import cv2
from scipy import spatial



class PolygonShape_Cls(Shape_AbstCls):
    
    polygonsNumberOfSides2Names_dict = {3:"Triangle",
                                        4:"Tetragon",
                                        5:"Pentagon",
                                        6:"Hexagon",
                                        7:"Heptagon",
                                        8:"Octagon",
                                        9:"Nonagon",
                                        10:"Decagon"}
    
    def __init__(self, points):
        """
        """
        
        assert isinstance(points, list)
        
        points_set = set(points)
        
        if len(points) > len(points_set):
            raise ValueError("Some shape points are the same")
        
        if len(points_set) < 3:
            raise IOError("Not enought points to define polygon. Number of points: " + str(len(points)))
        
        if not all([isinstance(pointCoordinates, Point_Cls) for pointCoordinates in points]):
            raise IOError("Vertexes input data is not correct")
        
        
        Shape_AbstCls.__init__(self)
        
        self._points = points
        
        self._numberOfSides = len(self._points)
        
        self.__calculateExtremeCorrds()
    
    
    def getMiddlePoint(self):
        
        return Point_Cls(x_coord = self.left + (self.right - self.left) / 2, y_coord = self.top + (self.bottom - self.top) / 2)
             
    
    def transformIntoBox(self, left_new, top_new, right_new, bottom_new):
        
        
        for point in self._points:
            old_x, old_y = point.getCoords()
            
            new_x = left_new + ( (old_x - self.left) * (right_new - left_new)  /  (self.right - self.left) )
            new_y = top_new  + ( (old_y - self.top)  * (bottom_new - top_new)  /  (self.bottom - self.top) )
            
            point._setNewCoords(new_x, new_y)
            
        self.__calculateExtremeCorrds()
    
    
    def triangulate(self):
        return spatial.Delaunay([point.getCoords() for point in self.getPoints()]).simplices
        
    
    def splitIntoTriangles(self, triangulars):
        
        from Space._2D.Shapes.Triangle import Triangle_Cls
    
        triangles = []
        
        points = self.getPoints()
        
        for triangular in triangulars:
            
            triangles.append(
                Triangle_Cls(points[triangular[0]], points[triangular[1]], points[triangular[2]])
            )
        
        return triangles
        
        
    
    def getLongestEdge(self):
        
        longestEdge = 0.0
        
        for point_index in range(len(self._points)):
            if point_index == len(self._points) - 1:
                referencePoint_index = 0
            else:
                referencePoint_index = point_index + 1
            
            edgeLength = self._points[point_index].getDistanceToReferencePoint(self._points[referencePoint_index])
            
            longestEdge = max([longestEdge, edgeLength])
            
        return longestEdge
    
    
    def getPoints(self):
        return self._points.copy()
    
    
    def getNumberOfSides(self):
        return self.getNumberOfVertexes()
    
    
    def _isPointOnTheLeftOfLineByPoints(self, point, line_first_point, line_second_point):
        """
        Throws an exception when invalid data is taken 
        """
        
        if line_first_point != line_second_point:
            if point != line_first_point:
                
                delta_y_12 = line_second_point.y - line_first_point.y
                delta_x_12 = line_second_point.x - line_first_point.x
                
                delta_y_13 = point.y - line_first_point.y
                delta_x_13 = point.x - line_first_point.x
                
                
                if delta_y_12 == 0:
                    if delta_y_13 == 0:
                        raise         # collinear - horizontal
                    else:
                        return (delta_y_13 > 0) ^ (delta_x_12 < 0)
                  
                
                if delta_x_12 == 0:
                    if delta_x_13 == 0:
                        raise         # collinear - vertical
                    else:
                        return (delta_x_13 < 0) ^ (delta_y_12 < 0)
                
                
                if delta_x_13 == 0:
                    return (delta_x_12 < 0) ^ (delta_y_13 > 0) 
                 
                
                if delta_y_13 == 0:
                    return (delta_y_12 < 0) ^ (delta_x_13 < 0) 
                        
                
                direction_12 = delta_y_12 / delta_x_12
                direction_13 = delta_y_13 / delta_x_13
                
                if direction_12 != direction_13: # otherwise collinear - oblique line 
                
                    heading_12 = delta_x_12 > 0 # True - to the right, False - to the left
                    heading_13 = delta_x_13 > 0 # True - to the right, False - to the left
                    
                    # euqal to xor
                    if heading_12 and heading_13:
                        return direction_12 < direction_13
                    
                    elif  heading_12 and not heading_13:
                        return direction_12 > direction_13
                    
                    elif  not heading_12 and heading_13:
                        return direction_12 > direction_13
                    
                    elif  not heading_12 and not heading_13:
                        return direction_12 < direction_13
                    
                    else:
                        print("No such case")
                        raise
            
        raise # invalid in any other case
    
    
    def _checkQuadrilateralVertexesAgainstReversal(self, vertexes):
        
        A,B,C,D = vertexes
        
        # initial values
        A_angle_reversal_flag = False
        B_angle_reversal_flag = False
        C_angle_reversal_flag = False
        D_angle_reversal_flag = False
        
        
        try:
            # Sides of point in reference to line by two other points
            C_AB_side_flag = self._isPointOnTheLeftOfLineByPoints(C, A, B)
            
            #
            D_AB_side_flag = self._isPointOnTheLeftOfLineByPoints(D, A, B)
            D_BC_side_flag = self._isPointOnTheLeftOfLineByPoints(D, B, C)
            D_CA_side_flag = self._isPointOnTheLeftOfLineByPoints(D, C, A)
            
        except:
            return "invalid"
        
        # Unify algorithm to behave like A-B-C are anti-clockwise (reverse flags when C_AB_side_flag is set)
        D_AB_side_flag = D_AB_side_flag ^ (not C_AB_side_flag)
        D_BC_side_flag = D_BC_side_flag ^ (not C_AB_side_flag)
        D_CA_side_flag = D_CA_side_flag ^ (not C_AB_side_flag)
        
        
        if  D_AB_side_flag and \
            D_CA_side_flag and \
            D_BC_side_flag:
            
            D_angle_reversal_flag = True
        
        
        elif    not D_AB_side_flag and \
                not D_CA_side_flag:
            
            A_angle_reversal_flag = True
        
        
        elif    not D_AB_side_flag and \
                not D_BC_side_flag:
            
            B_angle_reversal_flag = True
        
        
        elif    not D_BC_side_flag and \
                not D_CA_side_flag:
            
            C_angle_reversal_flag = True
        
        
        elif not D_CA_side_flag:
            
            pass # no reversal angle
         
        
        else:
            return "invalid"
            
        
        
        return A_angle_reversal_flag, B_angle_reversal_flag, C_angle_reversal_flag, D_angle_reversal_flag
    
    
    def _getArea(self):
        
        S = None
        
        numberOfSides = self.getNumberOfSides()
        
        if numberOfSides == 3:
            
            # Triangle - Heron's formula
            
            vertexes = self.getPoints()
            
            A, B, C = vertexes
            
            a = self.getDistanceBetweenPoints(A,B)
            b = self.getDistanceBetweenPoints(B,C)
            c = self.getDistanceBetweenPoints(C,A)
            
            p = (a + b + c) / 2
            
            S = sqrt( p * (p - a) * (p - b) * (p - c) )
            
        
        elif numberOfSides == 4:
            
            # Quadrilateral - Bretschneider's formula
            
            vertexes = self.getPoints()
            
            A, B, C, D = vertexes
            
            vertexesFlags_output = self._checkQuadrilateralVertexesAgainstReversal(vertexes)
            
            if vertexesFlags_output != "invalid":
                
                A_reversal_flag, _, C_reversal_flag, _ = vertexesFlags_output
                
                a = self.getDistanceBetweenPoints(A,B)
                b = self.getDistanceBetweenPoints(B,C)
                c = self.getDistanceBetweenPoints(C,D)
                d = self.getDistanceBetweenPoints(D,A)
                
                alpha = self.getAngleOfThreePoints(D, A, B, A_reversal_flag)
                gamma = self.getAngleOfThreePoints(B, C, D, C_reversal_flag)
                
                s = (a + b + c + d) / 2
                
                S = sqrt( 
                                (s - a) * (s - b) * (s - c) * (s - d) - 
                            ( 
                                a * b * c * d * pow(
                                                    cos( 
                                                        (alpha + gamma) / 2
                                                        ),
                                                    2 
                                                    )
                            ) 
                        )
            
        if S is None: # if S is still not calculated then use arduous method
            area = Area_Cls()
            area._addPolygon(self)
            S = area.size()
        
        return S
        
    
    def __calculateExtremeCorrds(self):
        
        x_coords_list = list()
        y_coords_list = list()
                
        for point in self._points:
            x = point.x
            y = point.y
            
            x_coords_list.append(x)
            y_coords_list.append(y)
            
        self.top = min(y_coords_list)
        self.left = min(x_coords_list)
        self.bottom = max(y_coords_list)
        self.right = max(x_coords_list)
            
    
    def getExtremumCoordinates(self, additionalSurroundings_perc = None):
        """
        Returns relative coords
        
        additionalSurroundings_perc enchance extremum coordinates
        """
        
        # => HERE <= finished - postInstall ret vals and compatibility
        
        left = self.left
        right = self.right
        
        top = self.top
        bottom = self.bottom
        
        if additionalSurroundings_perc:
            
            additionalSurroundings_perc = float(additionalSurroundings_perc)
            assert additionalSurroundings_perc > 0.0
        
            shapeExtr_w = right - left
            shapeExtr_h = bottom - top
            
            horizontalEnhancement  = (additionalSurroundings_perc * shapeExtr_w) / 100.0
            verticalEnhancement    = (additionalSurroundings_perc * shapeExtr_h) / 100.0
            
            left_addS    = self.limitFloatFrom0To1(left    -  horizontalEnhancement)
            right_addS   = self.limitFloatFrom0To1(right   +  horizontalEnhancement)
            
            top_addS     = self.limitFloatFrom0To1(top     -  verticalEnhancement)
            bottom_addS  = self.limitFloatFrom0To1(bottom  +  verticalEnhancement)

        else:            
            (left_addS, top_addS, right_addS, bottom_addS) = (left, top, right, bottom)
    
        return (left_addS, top_addS, right_addS, bottom_addS), (left, top, right, bottom)
    
    
    def convert_LTRB_2_TLWH(self, left, top, right, bottom):
        return top, left, right - left, bottom - top
    
    
    def getNumberOfVertexes(self):
        return len(self._points)
    
    
    def __repr__(self)->str:
        return str(self)
    
    
    def __str__(self):
        
        polygonName = PolygonShape_Cls.polygonsNumberOfSides2Names_dict.get(len(self._points), "Polygon")
        pointsStatement = " - ".join([str(point) for point in self._points])
        
        return polygonName + "  " + pointsStatement
    
    
    def getShapeParamsPacked(self):
        
        shapeParams = []
        
        for point in self._points:
            shapeParams.extend(point.getCoords())
        
        return shapeParams
    
    
    def unpackShapeParams(self, rawParamsData):
        
        assert len(rawParamsData) % 2 == 0 # is even quantity
        
        shapeParams = []
        
        for rawParamPairIndex in range(int(len(rawParamsData)/2)):
            
            shapeParams.append(
                 Point_Cls(
                     rawParamsData[2 * rawParamPairIndex], 
                     rawParamsData[2 * rawParamPairIndex + 1]
                     )
                )
        
        return (shapeParams,)
    
    
    
    def getPointsAbsoluteCoords(self, image_h, image_w):

        output_list = []
        
        for point in self._points:
            output_list.append(point.getAbsoluteCoords(image_h, image_w))
        
        return tuple(output_list)
    
    


if __name__ == "__main__":

    
    import numpy as np
    #from _otherTools.NpArrayViewer import viewer
    
    fine_counter = 0
    
    def testAccuracyOfShapeSizeMethod(shapes):
        
        global fine_counter
        
        tollerance_perc = 2
        
        for shape in shapes:
            
            selfCalculatedArea = shape.getArea()
            
            area_ = Area_Cls()
            area_.addShape(shape)
            
            img = np.array(area_._area).astype(np.uint32) * 255
            
            img = cv2.cvtColor(np.float32(img), cv2.COLOR_GRAY2RGB)
            
            #viewer.saveWithID(img, id_ = "array")
            
            areaCalculatedArea = area_.size()
            
            differecne_perc = 100 * (abs(selfCalculatedArea - areaCalculatedArea)) / areaCalculatedArea
            
            if differecne_perc > tollerance_perc:
                print("Not maching for shape: " + str(shape) + "    self calc area: " + str(selfCalculatedArea)[:8] + "  area calc area: " + str(areaCalculatedArea)[:8] + "   difference: " + str(selfCalculatedArea - areaCalculatedArea))
            
            else:
                fine_counter += 1
    if 0:
        
        # patternShapePoints
        
        A_default = Point_Cls(0.0,0.0)
        B_default = Point_Cls(0.9,0.1)
        C_default = Point_Cls(1.0,1.0)
        D_default = Point_Cls(0.1,0.9)
        
        shapes = []
        
        def testDefaultWithChange(letter = None, x_new = None, y_new = None):
            
            data_dict = { 
                "A": A_default.copy(),
                "B": B_default.copy(),
                "C": C_default.copy(),
                "Configuration": D_default.copy(),
                }
            
            if letter is not None:
                data_dict[letter] = Point_Cls(x_new, y_new)
            
            testQuadrilateralWithPoints([
                data_dict["A"], 
                data_dict["B"],
                data_dict["C"],
                data_dict["Configuration"]
                ]
            )
        
        
        def testQuadrilateralWithPoints(points):
            
            quadrilateral = PolygonShape_Cls(points)
            
            testAccuracyOfShapeSizeMethod([quadrilateral])
            
            
            
        testDefaultWithChange() # no change
        
        testDefaultWithChange("A", 0.8, 0.8) # A reversal
        
        testDefaultWithChange("B", 0.2, 0.8) # B reversal
        testDefaultWithChange("C", 0.2, 0.2) # C reversal
        testDefaultWithChange("Configuration", 0.8, 0.2) # Configuration reversal
         
         
        testQuadrilateralWithPoints([ # First cross
            A_default,
            B_default,
            D_default,
            C_default
                ])
         
        testQuadrilateralWithPoints([ # Second cross
            A_default,
            C_default,
            B_default,
            D_default
                ])
         
        testQuadrilateralWithPoints([ # Third cross
            A_default,
            C_default,
            D_default,
            B_default
                ])
         
        testQuadrilateralWithPoints([ # Fourth cross
            A_default,
            D_default,
            B_default,
            C_default
                ])
             
        
        print("Fine calculations: " + str(fine_counter))
         
    
        
    elif 1:
        
            
        quadrilateral_1 = PolygonShape_Cls(points = [
                Point_Cls(0.1,0.1), 
                Point_Cls(0.1,0.2), 
                Point_Cls(0.2,0.2), 
                Point_Cls(0.2,0.1)
            ]
        )
        quadrilateral_2 = PolygonShape_Cls(points = [
                Point_Cls(0.5,0.0), 
                Point_Cls(1.0,0.5), 
                Point_Cls(0.5,1.0), 
                Point_Cls(0.0,0.5)
            ]
        )
        
        quadrilateral_3 = PolygonShape_Cls(points = [
                Point_Cls(0.5,0.0), 
                Point_Cls(1.0,1.0), 
                Point_Cls(0.5,0.5), 
                Point_Cls(0.0,1.0)
            ]
        )
        
        quadrilateral_4 = PolygonShape_Cls(points = [
                Point_Cls(0.5,0.0), 
                Point_Cls(1.0,1.0), 
                Point_Cls(0.1,0.5), 
                Point_Cls(0.0,1.0)
            ]
        )
        
        shapes = [
            quadrilateral_1,
            quadrilateral_2,
            quadrilateral_3,
            quadrilateral_4]
        
        random.seed(0)
        randint = random.randint
         
        for i in range(300):
             
            newShape = PolygonShape_Cls(points = [
                        Point_Cls(randint(1,10000)/10000,randint(1,10000)/10000), 
                        Point_Cls(randint(1,10000)/10000,randint(1,10000)/10000), 
                        Point_Cls(randint(1,10000)/10000,randint(1,10000)/10000), 
                        Point_Cls(randint(1,10000)/10000,randint(1,10000)/10000)
                    ]
                )
             
            shapes.append(newShape)
         
        #shapes = shapes[:1]
         
#         shapes = [
#             quadrilateral_1,
#             quadrilateral_2,
#             quadrilateral_3,
#             quadrilateral_4,
#             ]
         
        testAccuracyOfShapeSizeMethod(shapes)
        
        print("Fine calculations: " + str(fine_counter))
    
    else:
        
        # test algorithm to define if point is on left side of the line
        
        testsData = [ 
                # trivial questions
                [ (1,1), (2,2), (3,3), "invalid"],
                [ (1,1), (2,2), (0,0), "invalid"],
                [ (1,1), (2,2), (2,3), True],
                [ (1,1), (2,2), (3,2), False],
                
                # points equal
                [ (1,1), (1,1), (0,0), "invalid"],
                [ (1,1), (0,0), (1,1), "invalid"],
                [ (0,0), (1,1), (1,1), "invalid"],
                [ (1,1), (1,1), (1,1), "invalid"],
                
                # various
                [ (1,1), (0,0), (0,1), False],
                [ (1,1), (0,0), (1,0), True],
                [ (4,4), (0,0), (2,2), "invalid"],
                [ (4,4), (0,0), (1,3), False],
                [ (4,4), (0,0), (3,1), True],
                
                
             ]
        
        for testData in testsData:
            
            point = Point_Cls(testData[0][0]/100.0, testData[0][1]/100.0)
            line_first_point = Point_Cls(testData[1][0]/100.0, testData[1][1]/100.0)
            line_second_point = Point_Cls(testData[2][0]/100.0, testData[2][1]/100.0)
            expectedOutput = testData[3]
            
            try:
                output = PolygonShape_Cls._isPointOnTheLeftOfLineByPoints(None, point, line_first_point, line_second_point)
            except:
                output = "invalid"
            
            if expectedOutput == output:
                statement_prefix = "Passed !      "
                statement_sufix = ""
            else:
                statement_prefix = " -> Failed    "
                statement_sufix = "\t\t Expected output: " + str(expectedOutput) + " output: " + str(output)
            
            print(statement_prefix + "  data: " + str(testData) + statement_sufix)













