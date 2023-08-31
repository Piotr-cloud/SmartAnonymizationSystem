'''
Created on Sep 8, 2021

@author: piotr
'''
from Detections.DetectionsMap import DetectionsMap_Cls
from Detections.DetectionsMapSequence import DetectionsMapSequence_Cls
from MainExecutor.ProcessingConfiguration import ProcessingConfiguration_Cls

import sys, os
from ProgressLogger.Steps import Step_ImageModifiation_Cls, Step_VideoDetection_Cls,\
    Step_VideoTracking_Cls, Step_VideoModifiation_Cls,\
    Step_ConstructingWorkers_Cls, Step_TestingWorkers_Cls,\
    Step_WorkerConstruction_Cls, Step_VideoPrepareForAnonymization_Cls, \
    Step_SystemExecution_Cls, Step_AnonymizerProcessing_Cls,\
    Step_AnnotatorProcessing_Cls, Step_TrackerProcessing_Cls,\
    Step_DetectorProcessing_Cls, Step_ImageDetection_Cls,\
    Step_ImageProcessing_Cls, Step_VideoProcessing_Cls,\
    Step_PreparingWorkers_Cls, Step_WorkerPreparation_Cls,\
    Step_VideoTrackingPreparation_Cls, Step_VideoStabilization_Cls,\
    Step_FrameProcessing_Cls, Step_StabilizerProcessing_Cls,\
    Step_VideoSaving_Cls, Step_SingleObjectRepresentationPreparation_Cls
    
from ProgressLogger.ProgressLogger import ProgressLogger_Cls
from CommonTools.ContextManagers import PrintingDisabler_Cls
from PolymorphicBases.Worker import Worker_AbstCls
from Tracker.Tracker import VideoAndDetectionsMapSequenceProvider_Cls
from Tester.StartupTester import StartupTester_Cls
from Space._2D.Array import npArrayAbstractionConfiguration
#from _otherTools.NpArrayViewer import viewer


class MainExecutor_Cls(object):
    '''
    Construct object by telling what tools(workers) to use
    then call .execute(inputDataProcessor, outputDataProcessor)
    '''

    def __init__(self, processingConfiguration, startupTests_flag = True):
        '''
        Constructor
        '''
        
        self._processingConfiguration = self._validateSessionConfiguration(processingConfiguration)
        self._progressLogger = None
        self._startupTests_flag = bool(startupTests_flag)
        
        self._print_cfg = None
        
        # Construct progress logger
        self._constructProgressLogger()
        
    
    def _validateSessionConfiguration(self, processingConfiguration):
        assert isinstance(processingConfiguration, ProcessingConfiguration_Cls)
        return processingConfiguration
    
    
    def _constructProgressLogger(self):
        self._progressLogger = ProgressLogger_Cls()
        
    
    def _loadSessionConfiguration(self):
        
        # Load workers
        self.detectorsConstruction_dict     =  self._processingConfiguration.getDetectorsConstructionDict()
        self.trackersConstruction_dict      =  self._processingConfiguration.getTrackersConstructionDict()
        self.stabilizersConstruction_dict   =  self._processingConfiguration.getStabilizersConstructionDict()
        self.anonymizersConstruction_dict   =  self._processingConfiguration.getAnonymizersConstructionDict()
        self.annotatorConstruction          =  self._processingConfiguration.getAnnotatorConstruction()
        
        # Define flags
        self._anonymization_flag   =  self._processingConfiguration.getAnonymizationFlag()
        self._tracking_flag        =  self._processingConfiguration.getTrackingFlag()
        self._stabilization_flag   =  self._processingConfiguration.getStabilizationFlag()
        
        
    def _prepareProgressLogger(self, inputDataProcessor, outputDataProcessor):
        
        self._progressLogger.prepare(
            inputDataProcessor,
            self._processingConfiguration,
            outputDataProcessor
            )
    
    
    def _disablePrint(self):

        self._print_cfg = sys.stdout,sys.stderr, os.environ['TF_CPP_MIN_LOG_LEVEL'] if 'TF_CPP_MIN_LOG_LEVEL' in os.environ else None
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
    
    
    def _enablePrint(self):
        
        if self._print_cfg is not None:
            sys.stdout = self._print_cfg[0]
            sys.stderr = self._print_cfg[1]
            
            if self._print_cfg[2] is not None:
                os.environ['TF_CPP_MIN_LOG_LEVEL'] = self._print_cfg[2]
    
    
    
    def _constructWorker(self, workerConstruction_obj):
        
        if workerConstruction_obj is not None:
            with self._progressLogger.newStep(Step_WorkerConstruction_Cls(workerConstruction_obj.getWorkerCls())):
                worker = Worker_AbstCls.getWorkerConstructedObject(workerConstruction_obj) # starts workers nested creation
        
        else: worker = None
        
        return worker
    
    
    
    def _constructWorkersFromDictKeys(self, dict_):
            
        return {self._constructWorker(workerConstruction_obj): dict_[workerConstruction_obj] for workerConstruction_obj in dict_}
        
    
    
    def _constructWorkers(self):
        
        with self._progressLogger.newStep(Step_ConstructingWorkers_Cls()):
            
            printingDisabler = PrintingDisabler_Cls()
            
            with printingDisabler:
                
                Worker_AbstCls.clearAllWorkersConstructedContainer()
                
                # Detectors
                self.detectors_dict    = self._constructWorkersFromDictKeys(self.detectorsConstruction_dict)
                
                # Tracker
                self.trackers_dict     = self._constructWorkersFromDictKeys(self.trackersConstruction_dict)
                
                # Tracker
                self.stailizers_dict   = self._constructWorkersFromDictKeys(self.stabilizersConstruction_dict)
            
                # Anonymizers
                self.anonymizers_dict  = self._constructWorkersFromDictKeys(self.anonymizersConstruction_dict)
                
                # Annotator
                self.annotator         = self._constructWorker(self.annotatorConstruction)
        
        
        # with printingDisabler:
            #  # testing - optional
            # self._testWorkers_trivialUC()
    
          
        
        
    def _prepareWorkers(self):
        "Finalizes workers construction, by calling worker.prepare() methods for all the workers"

        # Prepare workers - construction stage 2
        with self._progressLogger.newStep(Step_PreparingWorkers_Cls()):
            
            # Find list of all the workers, iterate them and call prepare
            for worker in Worker_AbstCls.getAllWorkersConstructed():
                if worker.anythingToPrepare():
                    with self._progressLogger.newStep(Step_WorkerPreparation_Cls(worker)):
                        worker.prepare()
    
    
    
    def _testWorkers_trivialUC(self):
        
        with PrintingDisabler_Cls():
            
            with self._progressLogger.newStep(Step_TestingWorkers_Cls()):
                
                tester = StartupTester_Cls()
                
                workers = self._getListOfAllTheWorkers()
                
                tester.test_workersWithTrivialUC(workers, self._progressLogger)        
    
    
    
    def _prepareDataProcessors(self, inputDataProcessor, outputDataProcessor):
        
        # Prepare input data processor
        inputDataProcessor.prepare()
        
        # Prepare output data processor
        outputDataProcessor.prepare()
        
        outputDataProcessor.setProcessingID(self._processingConfiguration.getProcessingID())
        outputDataProcessor.setConfigurationDataDict(self._processingConfiguration.getOriginDecisionsCfgDict())
    
    
    
    def _prepareForExecution(self, inputDataProcessor, outputDataProcessor):
        
        # Prepare RAM consumption optimization
        npArrayAbstractionConfiguration.prepare()
        
        # Prepare data processors
        self._prepareDataProcessors(inputDataProcessor, outputDataProcessor)
        
        # Load session configuration
        self._loadSessionConfiguration()
        
        # Construct workers
        self._constructWorkers()
        
        # Prepare workers
        self._prepareWorkers()
        
        # Test workers
        # self._testWorkers_trivialUC()
        
        # Prepare progress logger
        self._prepareProgressLogger(inputDataProcessor, outputDataProcessor)
    
    
    
    def _prepareObjectsAnonymization(self, imagesSequence, detectionsMapSequence):
        """
        Generates new object view for further replacement
        Pre step for images sequence anonymization by replacement
        """
        
        with self._progressLogger.newStep(Step_VideoPrepareForAnonymization_Cls(imagesSequence)):
            
            for anonymizer in self.anonymizers_dict:
                    
                if anonymizer is not None:
                
                    with self._progressLogger.newStep(Step_WorkerPreparation_Cls(anonymizer)): # "Step_WorkerPreparation_Cls(anonymizer)" is done for unification, but restore might be needed: Step_AnonymizerPreparation_Cls(anonymizer)
                        
                        classesIds = self.anonymizers_dict[anonymizer]
                        
                        for objectFound in detectionsMapSequence.getObjectsOfSpecificClasses(classesIds):
                            with self._progressLogger.newStep(Step_SingleObjectRepresentationPreparation_Cls(objectFound)):
                                anonymizer.prepareObjectsForAnonymization(objectFound)
    
    
    def _performImageDetection(self, image):
        
        with self._progressLogger.newStep(Step_FrameProcessing_Cls(image)):
            
            with self._progressLogger.newStep(Step_ImageDetection_Cls(image)):
                
                detections_list = []
                
                for detector in self.detectors_dict:
                    
                    if detector is not None:
    
                        classesIds = self.detectors_dict[detector]
                        
                        with self._progressLogger.newStep(Step_DetectorProcessing_Cls(detector, image)):
                            
                            detectionsMap = detector.detectClasses(image, classesIds)
                            
                            if detectionsMap is not None:
                                detections_list.extend(detectionsMap.getDetections())
                        
                
                if detections_list is not None:
                    detecionsMap = DetectionsMap_Cls(initDetectionsList = detections_list)
                else:
                    detecionsMap = None
            
                return detecionsMap
    
    
    def _performVideoDetection(self, video):
        
        with self._progressLogger.newStep(Step_VideoDetection_Cls(video)):
            
            detectionsMapSequence = DetectionsMapSequence_Cls()
            
            for frame in video:
                
                detectionsMap = self._performImageDetection(frame)
                
                detectionsMapSequence.addFrameDetectionMap(detectionsMap)
        
            assert len(detectionsMapSequence) == len(video)
            
            return detectionsMapSequence
    
    
    def _performVideoDetectionsTracking(self, detectionsMapSequence, inputVideo):
            
        tracker_2_trackerState_dict = {}
        
        with self._progressLogger.newStep(Step_VideoTrackingPreparation_Cls(inputVideo)):
            
            for tracker in self.trackers_dict:
                if tracker is not None:
                    tracker_2_trackerState_dict[tracker] = tracker.getTrackerInitialState()
                
        
        with self._progressLogger.newStep(Step_VideoTracking_Cls(inputVideo)):
            
            classesNonTracked = detectionsMapSequence.getClassesDetected()
            
            provider = VideoAndDetectionsMapSequenceProvider_Cls(inputVideo, detectionsMapSequence)
            
            new_DetectionsMapSequence = DetectionsMapSequence_Cls()
            
            for frame, detectionMap in provider:
                
                with self._progressLogger.newStep(Step_FrameProcessing_Cls(frame)):
                    
                    newDetectionsMap = DetectionsMap_Cls()
                    
                    # Performing tracking for each tracker
                    for tracker, classesServiced in self.trackers_dict.items():
                        
                        if tracker is not None:
                            
                            trackerRelatedDetectionsMap = detectionMap.getDetectionsMapOfSpecificClasses(classesServiced)
                            trackerState = tracker_2_trackerState_dict[tracker]
                            
                            with self._progressLogger.newStep(Step_TrackerProcessing_Cls(tracker, frame)):
                                newDetectionsMap += tracker.track(frame, trackerRelatedDetectionsMap, trackerState)
                                
                            for classServiced in classesServiced:
                                if classServiced in classesNonTracked:
                                    classesNonTracked.remove(classServiced)
                
                    if classesNonTracked:
                        newDetectionsMap += detectionMap.getDetectionsMapOfSpecificClasses(classesNonTracked)
                
                new_DetectionsMapSequence.addFrameDetectionMap(newDetectionsMap)
            
            return detectionsMapSequence #TODO: not a "new_DetectionsMapSequence" ? remove return + tracker.track return too
    
    
    def _performVideoObjectsStabilization(self, detectionsMapSequence, inputVideo):
        
        with self._progressLogger.newStep(Step_VideoStabilization_Cls(inputVideo)):
            
            for stabilizer, classesServiced in self.stailizers_dict.items():
                
                if stabilizer is not None:
                    
                    with self._progressLogger.newStep(Step_StabilizerProcessing_Cls(stabilizer, inputVideo)):
                        
                        objectsToStabilize = detectionsMapSequence.getObjectsOfSpecificClasses(classesServiced)
                    
                        stabilizer.stabilize(objectsToStabilize)
                            
    
    
    def _performImageModification(self, image, detections):
        
        with self._progressLogger.newStep(Step_FrameProcessing_Cls(image)):
            
            with self._progressLogger.newStep(Step_ImageModifiation_Cls(image)):
            
                modifiedImage = image
                
                # First anonymization, then annotation
                anonymizer_2_detectionMap_dict = {}
                annotationDetectionMap = None
                
                for anonymizer in self.anonymizers_dict:
                    classesRelated = self.anonymizers_dict[anonymizer]
                    
                    detectionsMapOfClasses = detections.getDetectionsMapOfSpecificClasses(classesRelated)
                    
                    if anonymizer is not None:
                        anonymizer_2_detectionMap_dict[anonymizer] = detectionsMapOfClasses
                    else:
                        annotationDetectionMap = detectionsMapOfClasses
                    
                
                # First anonymization
                for annonymizer in anonymizer_2_detectionMap_dict:
                    
                    detectionsMap = anonymizer_2_detectionMap_dict[annonymizer]
                    
                    if detectionsMap:
                        # anonymization
                        with self._progressLogger.newStep(Step_AnonymizerProcessing_Cls(annonymizer, modifiedImage)):
                            modifiedImage = annonymizer.anonymize(modifiedImage, detections = detectionsMap)
                
                
                # Then annotation
                if annotationDetectionMap:
                    with self._progressLogger.newStep(Step_AnnotatorProcessing_Cls(self.annotator, modifiedImage)):
                        modifiedImage = self.annotator.annotate(modifiedImage, detections = annotationDetectionMap)
            
            
                #viewer.saveWithID(modifiedImage.getNpArrayCopy(), "modifiedImage")
                
                return modifiedImage
    
    
    
    def _performVideoModification(self, video, detectionsMapSequence):
        
        with self._progressLogger.newStep(Step_VideoModifiation_Cls(video)):
            
            outputVideo = video.getOutputVideoObj()
            
            frame_index = 0
            
            for frame in video:
                
                detectionsMap = detectionsMapSequence[frame_index]; frame_index += 1
                
                modifiedFrame = self._performImageModification(image = frame,
                                                               detections = detectionsMap)
                
                outputVideo.append(modifiedFrame)
            
            
            return outputVideo
                
         
    
    def _doFinalActivities(self, inputDataProcessor, outputDataProcessor):
        
        print("Output directory: " + str(outputDataProcessor.getOutputDir()))
        
        inputDataProcessor.finish()
        outputDataProcessor.finish()
        
        self._progressLogger.finishProgressBar()
        
        npArrayAbstractionConfiguration.finish()
    
    
    def getStepsLogs(self):
        return self._progressLogger.getStepsLogs()
    
    
    #@profile    
    def execute(self, inputDataProcessor, outputDataProcessor, streamProcessing_flag = False, ramOnly_flag = False):
        """
        Processing order:
        - images, then 
        - videos
        """
        
        if ramOnly_flag:
            npArrayAbstractionConfiguration.set_RAM_only()
            
        
        with self._progressLogger.newStep(Step_SystemExecution_Cls()):
            
            if not streamProcessing_flag: # sequential processing

                self._prepareForExecution(inputDataProcessor, outputDataProcessor)
                
                npArrayAbstractionConfiguration.useRAM()
        
        
                # Images 
                for inputImage in inputDataProcessor.getImages():#__iter__(videoHandle_flag = False):
                    
                    with self._progressLogger.newStep(Step_ImageProcessing_Cls(inputImage)):
                        
                        #detect
                        detectionsMap = self._performImageDetection(inputImage)
                        
                        #anonymize or annotate
                        modifiedImage = self._performImageModification(image = inputImage,
                                                                       detections = detectionsMap)
                    
                        outputDataProcessor.write(
                            imageOrVideo = modifiedImage
                            )
                # Images done
                
                if not ramOnly_flag: npArrayAbstractionConfiguration.useHD()
                
                
                # Videos
                for inputVideo in inputDataProcessor.getVideos():
                    
                    with self._progressLogger.newStep(Step_VideoProcessing_Cls(inputVideo)):
                    
                        # Detect frames
                        detectionsMapSequence = self._performVideoDetection(inputVideo)
                        
                        # Tracking
                        if self._tracking_flag:
                            #HERE debug why then tracking is on there if no anonymization done
                            detectionsMapSequence = self._performVideoDetectionsTracking(detectionsMapSequence, inputVideo)
            
                        # Stabilize
                            if self._stabilization_flag:
                                self._performVideoObjectsStabilization(detectionsMapSequence, inputVideo)
                        
                        # Prepare anonymization data and patterns
                        if self._anonymization_flag:
                            self._prepareObjectsAnonymization(inputVideo, detectionsMapSequence)
                        
                        # Modify
                        modifiedVideo = self._performVideoModification(inputVideo, detectionsMapSequence)
                        
                        with self._progressLogger.newStep(Step_VideoSaving_Cls(modifiedVideo)):
                            # Write
                            outputDataProcessor.write(
                                imageOrVideo = modifiedVideo
                                )
                # Videos done
                
                
            else: # stream processing
                raise NotImplementedError("Stream processing is not implemented yet")
            
            
        self._doFinalActivities(inputDataProcessor, outputDataProcessor)





