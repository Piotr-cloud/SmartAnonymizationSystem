'''
Created on 24 sty 2021

@author: piotr
'''
from PolymorphicBases.Worker import Worker_AbstCls
from View.View import View_Cls, StubView_Cls
from PolymorphicBases.ABC import final, abstractmethod
from ContentRecognizer.ContentRecognizer import ContentRecognizer_AbstCls
from Detections.Detection import BoundingBox_Cls
from Detector.Detector import Detector_AbstCls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj



class ContentGenerator_AbstCls(Worker_AbstCls):
    """
    Generates new content
    from: 
        View_Cls
    to: 
        View_Cls
    """
        
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Content generator"
        
    @staticmethod
    def getJobName():
        return "Content generation"
    

    def __init__(self, recognizer = None):
        assert type(self) != ContentGenerator_AbstCls
        Worker_AbstCls.__init__(self)
        
        if recognizer is not None:
            assert isinstance(recognizer, ContentRecognizer_AbstCls)
            
        self._recognizer = recognizer
    
    
    def _prepare(self):
        if self._recognizer is not None:
            self._recognizer.prepare()
    
    def getRecognizer(self):
        return self._recognizer


    def _performsRecognitionBefore(self):
        return self._recognizer is not None
    
    
    def _validateOperationObjectsTypes(self, objectsToCheck):
        
        for objectToCheck in objectsToCheck:
            if objectToCheck != "Failed":
                assert isinstance(objectToCheck, View_Cls), "Content generator shall operate on View_Cls objects "
            
    @final
    def generate(self, view):
        
        if self._performsRecognitionBefore():
            self._recognizer.recognize(view) # in-place operation
        
        with workersPerformanceLoggerObj.startContext_executuion(self):
            
            self._validateOperationObjectsTypes([view])
            
            output_view = self._generate(view)
            
            assert output_view is not view # not in-place operation
            
            self._validateOperationObjectsTypes([output_view])
        
        return output_view
    
    
    @abstractmethod
    def _generate(self, view):
        raise NotImplementedError()
    
    
    @final
    def generateMultiple(self, views):
        
        if self._performsRecognitionBefore():
            views = [self._recognizer.recognize(view) for view in views]
        
        self._validateOperationObjectsTypes(views)
        
        outputs = self._generateMultiple(views)
        
        self._validateOperationObjectsTypes(outputs)
        
        return outputs
    

    def _generateMultiple(self, views):
        return [self._generate(view) for view in views]
    

    
    def _defineStaticAnonymizedViewReferenceForEachObject(self, objectFound, contentSwapperValidating = None):
        """
        This method allows to use of one anonymized view per each detected object, so face is same, license plates numbers can be static(non-toggling)
        
        Off-the-shelf solutions can be used like:
        
            - self._dSAVRFEO_ignoringAnyView(objectFound, contentSwapperValidating)
            - self._dSAVRFEO_byAnonymizingBestView(objectFound, contentSwapperValidating)
        
        
        dSAVRFEO stands for defineStaticAnonymizedViewReferenceForEachObject
        """
        pass
    
    
    def _dSAVRFEO_ignoringAnyView(self, objectFound, contentSwapperValidating):
        """
        use this method whenever random or static content is used as content generation
        """
        newView = self.generate(StubView_Cls())
        
        assert newView != "Failed", "This kind of generator shall always generate a view"
                                                     
        for _ in range(5): # retry 5 times
            newView = self.generate(StubView_Cls())
            if contentSwapperValidating._validateSrcObjectView(newView):
                # Assign external view as constant reference for further swapping
                objectFound.assignAnonymizedView(newView)
                return
        
        print("Warning! Content generator generated view that is not acceptable by the content swapper!")
            
        
        #it is more contentGenerator related !
    
    
    def _dSAVRFEO_byAnonymizingBestView(self, objectFound, contentSwapperValidating):
        """
        Definition of best view is defined in method: self._findObjectBestView
        """
        
        # Find best views
        bestView = self._findObjectBestView(objectFound, contentSwapperValidating)
        
        if bestView is not None:
            objectFound.assignBestPhotography(bestView)
        
        # Make all the viewes annonymized
        photography = objectFound.getBestPhotography()
        
        if photography is not None:
                                      
            for _ in range(5): # retry 5 times
                newView = self.generate(photography)
                if contentSwapperValidating._validateSrcObjectView(newView):
                    # Assign external view as constant reference for further swapping
                    objectFound.assignAnonymizedView(newView)
                    return
                
            print("Warning! Content generator(" + self.getName() + ") generated view that is not acceptable by the content swapper(" + contentSwapperValidating.getName() + ")!")
        
    
    def _findObjectBestView(self, object_, contentSwapperValidating):
        
        bestView = None
        bestScore = None
        
        bestViews_list = []
        
        # For optimiation reason algorithm is divided in two parts. Measured, that it reduces time consumption by 43%
        objViews = object_.iterViews()
        
        for objectView in objViews:
            
            if objectView is not None:
                score = self._evaluateObjectView(objectView)
                
                if bestScore is None or bestScore < score:
                    bestViews_list.append(objectView)
                    bestScore = score
        
        for bestView in bestViews_list[::-1]:
            if contentSwapperValidating._validateSrcObjectView(objectView):
                return bestView
        
        # if not found by now then use take another way:
        
        bestView = None
        bestScore = None
        
        for objectView in objViews:
        
            if objectView is not None and objectView not in bestViews_list:
                score = self._evaluateObjectView(objectView)
                if bestScore is None or bestScore < score:
                    if contentSwapperValidating._validateSrcObjectView(objectView):
                        bestView = objectView
                        bestScore = score
                        
        return bestView
    
    
    
    def _evaluateObjectView(self, objectView):
        """
        When the following default metric method is not sufficient it is up to specific anonymizer to implement this metric"
        """
        return objectView.getDetection().getShape().getArea()




class ContentGenerator_NoInput_AbstCls(ContentGenerator_AbstCls):
    
    def __init__(self, detector = None):
        """
        Detector might be used to add detection to generated view
        when not provided then detection covers all the frame"""
        
        self._detector = self.resolveArgument(detector)
        assert self._detector is None or isinstance(self._detector, Detector_AbstCls)
        ContentGenerator_AbstCls.__init__(self)
    
    
    def _prepare(self):
        ContentGenerator_AbstCls._prepare(self)
        if self._detector is not None:
            self._detector.prepare()
    
    @final
    def _generate(self, view):
        view # unused
        return self._getGeneratedView()
    
    
    @abstractmethod
    def _getGeneratedView(self):
        pass

    
    def _performDetectionOnExampleImageAndGetFirstDetection(self, npArray):
        
        output = None
        
        outputDetectionMap = self._detector._detectClasses(npArray, self.getClassesProcessedByInstance())
        
        if outputDetectionMap:
            output = outputDetectionMap[0]
        
        return output
    
    
    def _changeNpArrayToDetectionView(self, npArray):
        
        detection = None
        
        if self._detector:
            detection = self._performDetectionOnExampleImageAndGetFirstDetection(npArray)
        
        if detection is None:
            
            if self._detector:
                print("Warning! Content generator detector did not detect any object on example image")
                
            detection = BoundingBox_Cls(
                class_ = self.getClassesProcessedByInstance()[0],
                left = 0.0,
                top = 0.0,
                right = 1.0,
                bottom = 1.0)
        
        return View_Cls(array = npArray, detection = detection)
    
    
