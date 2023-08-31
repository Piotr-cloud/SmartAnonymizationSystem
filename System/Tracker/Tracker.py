'''
Created on Sep 7, 2021

@author: piotr
'''
from PolymorphicBases.Worker import Worker_AbstCls
from PolymorphicBases.ABC import final, abstractmethod, Base_AbstCls
from Detections.DetectionsMap import DetectionsMap_Cls
from Space._2D_p_time.Frame import Frame_Cls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj


class Tracker_AbstCls(Worker_AbstCls):
    '''
    Worker that performs tracking of object, so identifying objects in consecutive frames. Can optionally implement track stabilization(prediction stabilization can be a part of tracking, so not to repeat calculations in tract stabilization stage it can be applied here with no additional performance costs)  
    '''
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Tracker"
        
    @staticmethod
    def getJobName():
        return "Object tracking"
    
    
    def __init__(self):
        '''
        Constructor
        '''
        assert type(self) != Tracker_AbstCls
    
    
    @final
    def getTrackerInitialState(self):
        trackerInitialState = self._getTrackerInitialState()
        assert isinstance(trackerInitialState, TrackerState_AbstCls)
        return trackerInitialState
    

    @abstractmethod
    def _getTrackerInitialState(self):
        """
        This method shall restart tracker internal state
        """
        raise NotImplementedError()
    
    
    @final
    def track(self, frame, detectionsMap, trackerState):
        """
        Modifies tracker state and returns new detectionsMap
        """
        
        assert isinstance(frame, Frame_Cls)
        assert isinstance(detectionsMap, DetectionsMap_Cls)
        assert isinstance(trackerState, TrackerState_AbstCls)

        with workersPerformanceLoggerObj.startContext_executuion(self):
            newDetectionsMap = self._track(frame, detectionsMap, trackerState)
        
        assert isinstance(newDetectionsMap, DetectionsMap_Cls)
        
        return newDetectionsMap 
    
    @abstractmethod
    def _track(self, frame, detectionsMap, trackerState):
        pass



class TrackerState_AbstCls(Base_AbstCls): pass





class VideoAndDetectionsMapSequenceProvider_Cls():
    """
    Assists to synchronize frame with DetectionsMap and performs precheck
    """
    
    def __init__(self, video, detectionsMapSequence):
        
        assert len(video) == len(detectionsMapSequence), "There should be as many detections maps as the number of video frames"
        assert len(video) > 0, "Video shall contain frames"
       
        self._detectionsMapSequence = detectionsMapSequence
        self._video = video
        
    
    def __iter__(self):
        
        frame_index = 0
        
        for frame in self._video:
            
            detectionsMap = self._detectionsMapSequence[frame_index]
            
            yield frame, detectionsMap
            
            frame_index += 1








