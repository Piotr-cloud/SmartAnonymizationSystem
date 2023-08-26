'''
Created on Sep 21, 2021

@author: piotr
'''

import enlighten
from ProgressLogger.StepsLogs import StepsLogs_Cls
from ProgressLogger.Common import framesProcessings_key,\
    videosProcessed_key, imagesProcessed_key
import datetime
import time

            

class ProgressLogger_Cls():
    
    def __init__(self, consoleFullPrint = True):
        
        
        self._consoleFullPrint = bool(consoleFullPrint)
        
        self._manager = enlighten.get_manager()
        
        self._status_bar = self._manager.status_bar('',
                                        justify=enlighten.Justify.LEFT)
        
        self._stepStack = []
        self._availableMethods = [methodName for methodName in dir(self) if callable(getattr(self, methodName))]
        
        self._stepsLogs = StepsLogs_Cls()
        
        self._ljustVal = 0
        
        self._progressBars_dict = {}
        self._steps_bar = self._manager.counter(desc = "Steps")
        
    
    def prepare(self, inputDataProcessor, processingConfiguration, outputDataProcessor):
        
        outputDataProcessor # unused
        
        self._imagesQuantity = inputDataProcessor._getNumberOfImages()
        self._videosQuantity = inputDataProcessor._getNumberOfVideos()
        
        self._videosFramesQuantity = inputDataProcessor._getNumberOfVideoFrames()
        
        detection_flag       =  processingConfiguration.getDetectionFlag()
        anonymization_flag   =  processingConfiguration.getAnonymizationFlag()
        annotation_flag      =  processingConfiguration.getAnnotationFlag()
        tracking_flag        =  processingConfiguration.getTrackingFlag()
        stabilization_flag   =  processingConfiguration.getStabilizationFlag()
        
        stabilization_flag  # stabilization do not operate on frames but another form. It is performed fast so there is no much sense to include that in the progress bar
        
        
        self._framesToProcess_quantity = self._videosFramesQuantity * [
            
                detection_flag,
                anonymization_flag or annotation_flag,
                tracking_flag
            
            ].count(True) + \
            \
            self._imagesQuantity * [
            
                detection_flag,
                anonymization_flag or annotation_flag
            
            ].count(True)
        
        # Fill _progressBars_dict
        self._progressBars_dict[framesProcessings_key]  = self._manager.counter(
            total=self._framesToProcess_quantity,
            desc = framesProcessings_key,
            unit = framesProcessings_key)
        
        
        self._progressBars_dict[videosProcessed_key]  = self._manager.counter(
            total = self._videosQuantity,
            desc = videosProcessed_key,
            unit = videosProcessed_key
            )
        
        self._progressBars_dict[imagesProcessed_key]  = self._manager.counter(
            total=self._imagesQuantity,
            desc = imagesProcessed_key,
            unit = imagesProcessed_key)

    
    def finishProgressBar(self):
        self._print("")
        self._manager.stop()

    
    
    def newStep(self, step):

        self._stepStack.append(step)
        
        return self
    
    
    def getStepsLogs(self):
        return self._stepsLogs
    
    
    def getStatisticsStatement(self):
        
        return str(self._stepsLogs)
    
    
    def getCurrentStep(self):
        return self._stepStack[-1]
    
    def anyStepsActive(self):
        return bool(self._stepStack)
    

    def _print(self, statementData):
        
        if isinstance(statementData, str):
            
            statement = statementData
            
        elif isinstance(statementData, tuple):
            firstElementLength = len(statementData[0])
            
            if firstElementLength > self._ljustVal:
                self._ljustVal = firstElementLength
            
            statement = statementData[0].ljust(self._ljustVal) + " " + " ".join(statementData[1:])
        
        else: return 
        
        statement = self.getTimestampStr() + ":  " + statement
        
        if self._consoleFullPrint:
            print(statement, flush=True)
        self._status_bar.update(statement)
    
    
    def getTimestampStr(self):
        timestamp = time.time()
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.') + (str(timestamp).split(".")[1]).ljust(7, "0")
    
    
    def __enter__(self):
        
        enteredStep = self.getCurrentStep()
        
        enterStatement = enteredStep.getEnterStatement()
        
        if enterStatement is not None:
            self._print(enterStatement)
        
        enteredStep.enter()
        
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        
        if exc_type:
            return False
        
        exc_value, exc_tb # unused
        
        exitedStep = self._stepStack.pop()
        exitedStep.exit()
        
        if(self.anyStepsActive()):
            upperState = self.getCurrentStep()
            upperState.addSubStep(exitedStep)
            
        else:
            self._stepsLogs.addBaseStep(exitedStep)
        
        exitStatement = exitedStep.getExitStatement()
        
        stepPerformanceResults_dict = exitedStep.getPerformanceResultsDict()
         
        for paramName in self._progressBars_dict:
             
            if paramName in stepPerformanceResults_dict:
                 
                progressSize = stepPerformanceResults_dict[paramName]
                 
                progressBar = self._progressBars_dict[paramName]
                 
                progressBar.update(progressSize)
                 
        
        if exitStatement is not None:
            self._print(exitStatement)

         
        self._steps_bar.update()
        
        return True
    
    

        
    

