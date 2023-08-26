'''
Created on Jan 31, 2023

@author: piotr


MainExector_Cls execution startup tester

'''

from PolymorphicBases.Worker import Worker_AbstCls
from Anonymizer.Anonymizer import Anonymizer_AbstCls
from Detector.Detector import Detector_AbstCls
from Tracker.Tracker import Tracker_AbstCls
from Annotator.Annotator import Annotator_Cls
from Detections.DetectionsMap import DetectionsMap_Cls
from Detections.Detection import BoundingBox_Cls, detectionClasses_IDs,\
    Tetragon_Cls
from ObjectsDetectable.Classes import ClassIDs
from Space.Point import Point_Cls

import numpy
from Detections.DetectionsMapSequence import DetectionsMapSequence_Cls
from TrackStabilizer.TrackStabilizer import TrackStabilizer_AbstCls
from Space._2D_p_time.Video import OutputVideo_Cls
from Space._2D_p_time.Frame import Frame_Cls



class StartupTester_Cls():
    
    def __init__(self):
        pass
    
    def test_workersWithTrivialUC(self, workersList, progressLogger = None):
    
        anonymizers = []
        detectors = []
        trackers = []
        stabilizers = []
        anotators = []
        
        for worker in workersList:
            if worker is not None:
                assert isinstance(worker, Worker_AbstCls)
                
                if isinstance(worker, Detector_AbstCls):
                    detectors.append(worker)
                    
                if isinstance(worker, Tracker_AbstCls):
                    trackers.append(worker)
                    
                if isinstance(worker, TrackStabilizer_AbstCls):
                    stabilizers.append(worker)
                    
                if isinstance(worker, Anonymizer_AbstCls):
                    anonymizers.append(worker)
                    
                if isinstance(worker, Annotator_Cls):
                    anotators.append(worker)
        
        
        video = self.getTrivialUC_video()
        firstFrame = video[0]
        detectionsMap = self.getTrivialUC_detectionMap()
        
        
        for detector in detectors:
            output = detector.detect(firstFrame)
            assert output is None or isinstance(output, DetectionsMap_Cls)
        
        
        for anotator in anotators:
            output = anotator.annotate(firstFrame, detectionsMap)
            
            assert output is None or isinstance(output, Frame_Cls)
        
        
        for anonymizer in anonymizers:
            output = anonymizer.anonymize(firstFrame, detectionsMap)
            
            assert output is None or isinstance(output, Frame_Cls)
            
        
        if trackers:
            
            init_detectionMaps_list = []
            
            for _ in range(len(video)):
                init_detectionMaps_list.append(detectionsMap)#.copy())
            
            detectionsMapSequence = DetectionsMapSequence_Cls(init_detectionMaps_list, videoRelated = video) 
            
            for tracker in trackers:
                
                tracker.startTrackingSession(detectionsMapSequence, video)
        
                for frame, detectionsMap in tracker.generator_nextFrameAndDetectionsMap():
                    
                    tracker.trackDetections(frame, detectionsMap)
                
                output = tracker.getTrackingResult()
            
                assert isinstance(output, DetectionsMapSequence_Cls)
                
                tracker.cleanupTrackingSessionConfiguration()
        
    
    def getTrivialUC_video(self, numberOfFrames = 4):
        
        frameHeight = 100
        frameWidth = 100
        
        video = OutputVideo_Cls("PerformanceIntegrityCheckVideo", fps = 10, frameHeight = frameHeight, frameWidth = frameWidth)
        
        for _ in range(numberOfFrames):

            nparray = (numpy.random.rand(frameHeight,frameWidth,3) * 255).astype('uint8')
            
            video.append(nparray)
            
        return video
    
    
    def getTrivialUC_detectionMap(self):
        
        detectionsMap = DetectionsMap_Cls()
        
        numberOfClasses = len(ClassIDs) 
        numberOfDetections = len(detectionClasses_IDs) # divide area into numberOfClasses x numberOfDetections cells and fill with consequtive classes detections
        
        detectionCounter = 0
        
        for detectionId in detectionClasses_IDs:
            
            detectionClass = detectionClasses_IDs[detectionId]
        
            classCoutner = 0
            
            for classId in ClassIDs:
                
                left    =   classCoutner / numberOfClasses
                right   =  (classCoutner + 1) / numberOfClasses
                top     =   detectionCounter / numberOfDetections
                bottom  =  (detectionCounter + 1) / numberOfDetections
                
                
                if(detectionClass == Tetragon_Cls):
                    
                    vertexes = []
                    
                    vertexes.append(Point_Cls(x_coord = left, y_coord = top + 1 / (numberOfDetections ** 2)))
                    vertexes.append(Point_Cls(x_coord = left + 1 / (numberOfClasses ** 2), y_coord = top))
                    vertexes.append(Point_Cls(x_coord = right, y_coord = bottom))
                    vertexes.append(Point_Cls(x_coord = right, y_coord = top))
                    
                    detectionsMap.addDetection(Tetragon_Cls(classId, vertexes))
                    
                
                elif (detectionClass == BoundingBox_Cls):
                    
                    detectionsMap.addDetection(BoundingBox_Cls(classId, left, top, right, bottom))
            
                classCoutner += 1
                
            detectionCounter += 1
        
        return detectionsMap





