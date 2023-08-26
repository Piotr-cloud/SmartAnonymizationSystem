'''
Created on 23 lis 2020

@author: piotr

Detection - a class aggregating shape class object and some more

Detection differs from shape because detection:
    - stores detected object class id
    - limits number of shapes only to compatible ones
    - implements link to SW object related to detected object 
    
'''
from ObjectsDetectable.Classes import ClassIDs
from Space._2D.Shapes.Polygon import PolygonShape_Cls
from Space._2D.Shapes.Box import BoxShape_Cls
from ObjectsDetectable.Objects import Object_Cls
from PolymorphicBases.ABC import Base_AbstCls, abstractmethod
from ObjectsDetectable.ClassesCfg import FaceID, LicensePlateID, ClassName_dict



class Detection_AbstCls(Base_AbstCls):
    
    detectionShape = None
    
    classExpositionFactor_dict = {FaceID:           0.9,
                                  LicensePlateID :  1.0} # by default 1.0
    
    def __init__(self, class_, shape):
        
        assert type(self) != Detection_AbstCls
        class_ = int(class_)
        
        assert type(shape) is type(self).detectionShape or isinstance(self, DetectionCopy_Cls)
        
        if not class_ in ClassIDs:
            raise ValueError("Class with Id: " + str(class_) + " is unknown")
        
        self.class_ = class_
        self.shape = shape
        self.object_ = None  # Is this link needed on this level ? 
        self.trackerField = None # this field is reserved for tracker worker use
    
    
    def assignObject(self, object_):
        assert isinstance(object_, Object_Cls)
        assert self.object_ is None # can be assigned only once
        self.object_ = object_
    
    
    def isObjectNotAssigned(self):
        return self.object_ is None
    
    
    def getAnonymizedView(self):
        
        if self.object_ is not None:
            return self.object_.getAnonymizedView()
        
        return None
    
    
    def getObject(self):
        return self.object_
    
    
    def getObjectID(self):
        
        if self.object_ is not None:  id_ = self.object_.getID()
        else:                         id_ = None
            
        return id_
    
    
    def getShape(self):
        return self.shape
    
    def getClassId(self):
        return self.class_
    
    def getLongestEdgeExposition(self):
        
        expositionFactor = Detection_AbstCls.classExpositionFactor_dict.get(self.class_, 1.0)
        return self.shape.getLongestEdge() * expositionFactor
    
    
    def __hash__(self):
        return object.__hash__(self)
    
    
    def __eq__(self, other):
        try:
            return self.getDetectionParams() == other.getDetectionParams()
        except:
            return False
    
        
    def __str__(self):
        return ClassName_dict[self.class_] + " at " + str(self.shape)
    
    
    def __repr__(self):
        return str(self)
    
    @abstractmethod
    def getID(self):
        """
        Internal id of detection class. Shall exclusively identify detection class - each subclass shall have id number mapped exclusively
        """
        raise NotImplementedError()
    
    
    def getDetectionParams(self):
        return [self.class_] + [self.getID()] + list(self.shape.getShapeParamsPacked())
    
    
    def dumpToString(self):
        return " ".join(self.getDetectionParams()) 
    
    
    def getIouWith(self, otherDetection):
        self.shape.getIouWith(otherDetection.shape)
    
    def copy(self):
        return DetectionCopy_Cls(self)



class DetectionCopy_Cls(Detection_AbstCls):
    
    def __init__(self, baseDetection):
        self._originalDetectionType = type(baseDetection)
        Detection_AbstCls.__init__(self, baseDetection.getClassId(), baseDetection.getShape())
    
    def getID(self):
        return self._originalDetectionType.getID(self) 
    


class Polygon_AbstCls(Detection_AbstCls):
    
    detectionShape = PolygonShape_Cls

    def __init__(self, class_, vertexes):
        
        assert type(self) != Polygon_AbstCls
        shape = type(self).detectionShape(vertexes)
        
        Detection_AbstCls.__init__(self, class_, shape)
        



class Tetragon_Cls(Polygon_AbstCls):
    
    def __init__(self, class_, vertexes):
        
        assert len(vertexes) == 4
        
        Polygon_AbstCls.__init__(self, class_, vertexes)


    def getID(self):
        return 1




class BoundingBox_Cls(Tetragon_Cls):
    
    detectionShape = BoxShape_Cls
    
    def __init__(self, class_, left, top, right, bottom):
        
        shape = type(self).detectionShape(left = left,
                                          top = top,
                                          right = right,
                                          bottom = bottom)
        
        Detection_AbstCls.__init__(self, class_, shape)


    def getID(self):
        return 0



detectionClasses_IDs = {
    0: BoundingBox_Cls,
    1: Tetragon_Cls
}


































