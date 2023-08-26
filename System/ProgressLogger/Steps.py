

import time
from ProgressLogger.Common import framesProcessings_key,\
    videosProcessed_key, imagesProcessed_key
from ObjectsDetectable.Classes import ClassName_dict
from PolymorphicBases.ABC import Base_AbstCls, final
from PolymorphicBases.Worker import Worker_AbstCls
import inspect





class Step_AbstCls(Base_AbstCls):
    
    name = None
    
    enterStatement = None
    exitStatement = None
    
    def __init__(self):
        
        assert type(self) != Step_AbstCls
        
        self._startTime = None
        self._endTime = None
        self._name = type(self).name
        
        self._enterStatement = type(self).enterStatement
        self._exitStatement = type(self).exitStatement
        
        self._state = 0 # 0 - waiting, 1 - entered, 2 - exited
        
        self._subSteps_dict = {} # name to steps list
        self._subStepsOrder_list = []
        self._subSteps_list = []
        
        self._startPerformanceData = None
        self._endPerformanceData = None
        
        self._stepPerformanceResultsParams_dict = {}
        
        self._durationTime_Gross = 0
        self._durationTime_Net = 0
    
    
    def addSubStep(self, subStep):
        
        subStepName = subStep.getName()
        
        if subStepName not in self._subSteps_dict:
            self._subStepsOrder_list.append(subStepName)
            self._subSteps_dict[subStepName] = [subStep]
        
        else:
            self._subSteps_dict[subStepName].append(subStep)
        
        self._subSteps_list.append(subStep)
        
        self._durationTime_Net += subStep.getStepDuration_Net()
            
    
    def addPerformanceResultParam(self, paramName, paramValue = 1):
        if not paramName in self._stepPerformanceResultsParams_dict: 
            self._stepPerformanceResultsParams_dict[paramName] = paramValue
        else:
            self._stepPerformanceResultsParams_dict[paramName] += paramValue
    
    
    def getPerformanceResultsDict(self):
        return self._stepPerformanceResultsParams_dict
    
    
    def getStatsticsData(self):
        return self._durationTime_Gross, self._durationTime_Net, self._stepPerformanceResultsParams_dict.copy()
    
    
    @final
    def enter(self):
        
        if self._state != 0:
            raise EnvironmentError("Cannot re-enter state")
        
        self._state = 1
        
        self._startTime = time.time()
        
        return self._enter()
    
    def _enter(self):
        pass
    
    @final
    def exit(self):
        if self._state != 1:
            raise EnvironmentError("Cannot re-exit state")
        
        self._state = 2
        
        self._endTime = time.time()
        
        self._durationTime_Gross = self._endTime - self._startTime
        
        if not self._subSteps_dict:
            self._durationTime_Net = self._durationTime_Gross
        
        return self._exit() 
    
    
    def _exit(self):
        pass
    
    
    def getName(self):
        return self._name
    
    
    def getSubSteps(self):
        return self._subSteps_list
    
    
    def getEnterStatement(self):
        return self._enterStatement
    
    def getExitStatement(self):
        return self._exitStatement
    
    def getStartTime_s(self):
        return self._startTime
    
    def getEndTime_s(self):
        return self._endTime
    
    def getStepDuration_Gross(self):
        return self._durationTime_Gross

    def getStepDuration_Net(self):
        return self._durationTime_Net
    
    
###########################################################################
# Base step
###########################################################################

class Step_SystemExecution_Cls(Step_AbstCls):
    
    name = "System execution"
    
    enterStatement  = "Starting system execution"
    exitStatement   = "Execution finished sucessfully!"
    
    


###########################################################################
# Initial steps
###########################################################################

class Step_ConstructingWorkers_Cls(Step_AbstCls):
    
    name = "Workers construction"
    
    enterStatement = "Constructing workers"
    exitStatement = "Workers constructed"


class Step_PreparingWorkers_Cls(Step_AbstCls):
    
    name = "Workers preparation"
    
    enterStatement = "Preparing workers"
    exitStatement = "Workers prepared"
    
    

class Step_TestingWorkers_Cls(Step_AbstCls):
    
    name = "Workers testing"
    
    enterStatement = "Testing workers with trivial UC"
    exitStatement = "Workers tested with trivial UC"



##############################################
# Helpers abstract classes
##############################################
class Step_ObjectNameAppender_AbstCls(Step_AbstCls):

    def __init__(self, namedObject):
        
        assert type(self) != Step_ObjectNameAppender_AbstCls
        Step_AbstCls.__init__(self)

        self._enterStatement  =  (self._enterStatement + ": ", namedObject.getName())
        self._exitStatement   =  (self._exitStatement + ": ", namedObject.getName())



###########################################################################
# Image processing
###########################################################################

class Step_ImageProcessing_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Image processing"
    
    enterStatement =   "Processing"
    exitStatement =    "Processed"

    
    def _exit(self):
        self.addPerformanceResultParam(imagesProcessed_key, 1)
        


class Step_ImageLoading_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Image loading"
    
    enterStatement =   "Loading"
    exitStatement =    "Loaded"
        


class Step_ImageDetection_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Image detection"
    
    enterStatement =   "Detecting"
    exitStatement =    "Detected"
    


class Step_ImageModifiation_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Image modification"
    
    enterStatement =   "Modifing"
    exitStatement =    "Modified"


###########################################################################
# Frame (explicit) processing
###########################################################################

class Step_FrameDetectionsTracking_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Frame detections tracking"
    
    enterStatement =   "Tracking"
    exitStatement =    "Tracked"

    

###########################################################################
# Progress steps
###########################################################################

class Step_FrameProcessing_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Frame processing"
    
    enterStatement =   "Frame processing"
    exitStatement =    "Frame processed"

    def _exit(self):
        self.addPerformanceResultParam(framesProcessings_key, 1)


###########################################################################
# Video processing
###########################################################################

class Step_VideoProcessing_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video processing"
    
    enterStatement =   "Processing"
    exitStatement =    "Processed"


    def _exit(self):    
        self.addPerformanceResultParam(videosProcessed_key, 1)
        



class Step_VideoLoading_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video loading"
    
    enterStatement =   "Loading"
    exitStatement =    "Loaded"
        


class Step_VideoSaving_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video saving"
    
    enterStatement =   "Saving"
    exitStatement =    "Saved"



class Step_VideoDetection_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video detection"
    
    enterStatement =   "Detecting"
    exitStatement =    "Detected"



class Step_VideoTracking_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video tracking"
    
    enterStatement =   "Tracking"
    exitStatement =    "Tracked"



class Step_VideoStabilization_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video stabilization"
    
    enterStatement =   "Stabilizing"
    exitStatement =    "Stabilized"



class Step_VideoTrackingPreparation_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Preparation for video tracking"
    
    enterStatement =   "Tracking preparation"
    exitStatement =    "Tracking prepared"



class Step_VideoPrepareForAnonymization_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video anonyization preperation"
    
    enterStatement =   "Preparing for anonymization"
    exitStatement =    "Prepared for anonymization"



class Step_SingleObjectRepresentationPreparation_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Object preparation"
    
    enterStatement =   "Object preparing"
    exitStatement =    "Object prepared"


class Step_VideoModifiation_Cls(Step_ObjectNameAppender_AbstCls):
    
    name = "Video modification"
    
    enterStatement =   "Modifing"
    exitStatement =    "Modified"







###########################################################################
# Workers
###########################################################################

class Step_WorkerRelated_AbstCls(Step_AbstCls):
    
    def __init__(self, worker):
        
        if inspect.isclass(worker):
            workerCls = worker
        else:
            workerCls = worker.__class__
            
        assert issubclass(workerCls, Worker_AbstCls)
        
        Step_AbstCls.__init__(self)
        
        self._workerCls = workerCls


    def getWorkerCls(self):
        return self._workerCls




class Step_WorkerStatePerformance_AbstCls(Step_WorkerRelated_AbstCls):


    def __init__(self, worker):
        
        assert type(self) != Step_WorkerStatePerformance_AbstCls
        
        Step_WorkerRelated_AbstCls.__init__(self, worker)
        
        # if type(worker) is type:
        #     workerName = worker.getName(1)
        # else:
        workerName = self._workerCls.getName()
        
            
        self._name = type(self).name + " of " + workerName
        
        self._enterStatement = type(self).enterStatement + ": " + workerName
        self._exitStatement  = type(self).exitStatement  + ": " + workerName



class Step_WorkerConstruction_Cls(Step_WorkerStatePerformance_AbstCls):
    
    name = "Constructon"
    
    enterStatement =  "Constructing"
    exitStatement =   "Constructed"
        


class Step_WorkerPreparation_Cls(Step_WorkerStatePerformance_AbstCls):
    
    name = "Preparation"
    
    enterStatement =  "Preparing"
    exitStatement =   "Prepared"
    
    def __init__(self, worker):
        
        Step_WorkerStatePerformance_AbstCls.__init__(self, worker)
        classesReferenceStatement_str = "  (" + ", ". join([ClassName_dict[classId] for classId in worker.getClassesProcessedByInstance()]) + ")"
        
        self._enterStatement  +=  classesReferenceStatement_str
        self._exitStatement   +=  classesReferenceStatement_str
        self._name            +=  classesReferenceStatement_str



class Step_AnonymizerPreparation_Cls(Step_WorkerStatePerformance_AbstCls):
    'Class specified from Step_WorkerPreparation_Cls to be able to distinguish this case'
    
    name = "Preparation"
    
    enterStatement =  "Preparing"
    exitStatement =   "Prepared"
    

    

class Step_WorkerProcessing_AbstCls(Step_WorkerRelated_AbstCls):
    pass
        
    
    

class Step_WorkerVideoProcessing_AbstCls(Step_WorkerProcessing_AbstCls):

    def __init__(self, worker, video):
        
        assert type(self) != Step_WorkerArrayProcessing_AbstCls
        
        Step_WorkerRelated_AbstCls.__init__(self, worker)

        self._name = worker.getJobName() + " with " + worker.getName()
        
        self._enterStatement = ((self._enterStatement + "/" + worker.getName() + ": "), video.getName())
        self._exitStatement  = ((self._exitStatement + "/" + worker.getName() + ": "), video.getName())
        


class Step_WorkerArrayProcessing_AbstCls(Step_WorkerProcessing_AbstCls):

    def __init__(self, worker, imageOrFrame):
        
        assert type(self) != Step_WorkerArrayProcessing_AbstCls
        
        Step_WorkerRelated_AbstCls.__init__(self, worker)

        self._name = worker.getJobName() + " with " + worker.getName()
        
        self._enterStatement = ((self._enterStatement + "/" + worker.getName() + ": "), imageOrFrame.getName())
        self._exitStatement  = ((self._exitStatement + "/" + worker.getName() + ": "), imageOrFrame.getName())
        
        

class Step_DetectorProcessing_Cls(Step_WorkerArrayProcessing_AbstCls):
    
    name = "Detector processing"
    
    enterStatement  =  Step_ImageDetection_Cls.enterStatement
    exitStatement   =  Step_ImageDetection_Cls.exitStatement
    


class Step_AnnotatorProcessing_Cls(Step_WorkerArrayProcessing_AbstCls):
    
    name = "Image annotation"
    
    enterStatement =  "Annotating"
    exitStatement =   "Annotated"



class Step_AnonymizerProcessing_Cls(Step_WorkerArrayProcessing_AbstCls):
    
    name = "Image anonymization"
    
    enterStatement =  "Anonymizing"
    exitStatement =   "Anonymized"
    


class Step_TrackerProcessing_Cls(Step_WorkerArrayProcessing_AbstCls):
    
    name = "Frame tracking"
    
    enterStatement  =  Step_FrameDetectionsTracking_Cls.enterStatement
    exitStatement   =  Step_FrameDetectionsTracking_Cls.exitStatement
    


class Step_StabilizerProcessing_Cls(Step_WorkerVideoProcessing_AbstCls):
    
    name = "Video stabilization"
    
    enterStatement =  "Stabilizing"
    exitStatement =   "Stabilized"













