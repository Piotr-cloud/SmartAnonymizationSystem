'''
Created on 19 sty 2021

@author: piotr
'''
from PolymorphicBases.ABC import Base_AbstCls
from ObjectsDetectable.ClassesCfg import ClassName_dict



class Object_AbstCls(Base_AbstCls):
    
    nextId = 1
    
    def __init__(self):
        assert type(self) != Object_AbstCls
        self._objID = self._defineID()


    def getID(self):
        return self._objID

    @staticmethod
    def _defineID():
        
        id_ = Object_AbstCls.nextId
        Object_AbstCls.nextId += 1
        
        return id_
    
    
    def __hash__(self):
        return self.getID()
    
    
    def __eq__(self, other):
        return self._objID  == other._objID


    def __lt__(self, other):
        return self._objID  < other._objID



class Object_Cls(Object_AbstCls):
    
    _statesList = [
        "undefined",
        "classified",
        "photographed",
        "anonymized"
        ]
    
    def __init__(self, classId = None, videoRelated = None):
        super().__init__()
        self._currentState = "undefined"
        self._frameIndex_2_objectView_dict = {}
        self._frames_list = []
        self._videoRelated = videoRelated
        
        self._classId = None
        
        if classId is not None:
            self.classify(classId)    # defines self._classId
            
        self._photography = None      # image + detection shape
        self._anonymizedView = None   # numpy array
        self._viewType = _get_View_Cls()
    
    
    def getName(self):
        return str(self)
    
    
    def addView(self, frame, detection):
        
        assert frame.getVideoRelated() is self._videoRelated, "Object cannot be assigned to more than one video"
        
        frame_index = frame.getIndex()

        self._addView(frame_index, frame, detection)
    
    
    def _addView(self, frame_index, frame, detection):
        
        view = self._viewType(frame, detection)
        self._frames_list.append(view)
        
        if frame_index not in self._frameIndex_2_objectView_dict:
            self._frameIndex_2_objectView_dict[frame_index] = view
        
        detection.assignObject(self)
    
    
    def _getVideAtFrameByIndexgetViewAtFrame(self, frame):
        
        assert frame.getVideoRelated() is self._videoRelated, "Object cannot be assigned to more than one video"
        
        frame_index = frame.getIndex()
        
        return self._frameIndex_2_objectView_dict.get(frame_index, None)
    
    
    def _getVideAtFrameByIndex(self, frame_index):
        "Restricted use: donot use if architecture is unknown to you; Object is designed to be strongly related to a single video instance, but usage of this method allows to cheat on the constraint"
        return self._frameIndex_2_objectView_dict.get(frame_index, None)
    
    
    
    def getMaxKnownSizeOfVideo(self):
        return max(self._frameIndex_2_objectView_dict.keys())
    
    
    def iterFramesViews(self):
        
        maxFrames = self.getMaxKnownSizeOfVideo()
        
        for frameIdx in range(maxFrames + 1):
            if frameIdx in self._frameIndex_2_objectView_dict:
                yield self._frameIndex_2_objectView_dict[frameIdx]
            else:
                yield None
                
    
    def iterViews(self):
        
        yield from self._frames_list
            
    
    def getVideoRelated(self):
        return self._videoRelated


    def __repr__(self):  return str(self)
    
    
    def __str__(self):
        
        output_string = self._currentState + " object with id: " + str(self.getID())
        
        if self._classId is not None:
            output_string += " of class: " + str(ClassName_dict[self._classId])
             
        return output_string 
    
    
    def _switchState(self, stateName):
        
        statesList = Object_Cls._statesList
        
        assert stateName in statesList, "Destination state does not exist"
        
        stateInd = statesList.index(stateName)
        currentStateInd = statesList.index(self._currentState)
        
        assert currentStateInd <= stateInd, "State machine wrong transition"
        
        self._currentState = stateName
     
        
    def classify(self, classId):
        self._switchState("classified")
        self._classId = classId
    
    
    def assignBestPhotography(self, objectView):
        """
        Best view shall be added
        """
        assert isinstance(objectView, self._viewType)
        self._switchState("photographed")
        self._photography = objectView


    def getBestPhotography(self):
        if self._currentState == "photographed":
            return self._photography
        return None


    def assignAnonymizedView(self, anonymizedView):
        assert isinstance(anonymizedView, self._viewType)
        self._switchState("anonymized")
        self._anonymizedView = anonymizedView


    def isAtAnonymizedState(self):
        return self._currentState == "anonymized"
    
    
    def getAnonymizedView(self):
        if self.isAtAnonymizedState():
            return self._anonymizedView
        return None
            


# prevention against recursive import 
    
if not "__viewImported" in globals():
    __viewImported = False
    __View_Cls = None


def _get_View_Cls():
    
    global __viewImported, __View_Cls
    
    if not __viewImported:
        from View.View import View_Cls
        __View_Cls = View_Cls
        __viewImported = True
    
    return __View_Cls
        



