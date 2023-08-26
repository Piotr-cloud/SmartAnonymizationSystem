'''
Created on 24 sty 2021

@author: piotr
'''
from ContentGenerator.ContentGenerator import ContentGenerator_AbstCls
from ObjectsDetectable.Classes import LicensePlateID
from PolymorphicBases.ABC import final
from abc import abstractmethod
from View.View import View_Cls
from Detections.Detection import BoundingBox_Cls
from ContentRecognizer.Recognition import RecognizedPlateNumbers_Cls
from Levenshtein import distance



class LicensePlateGenerator_AbstCls(ContentGenerator_AbstCls):
        
    @staticmethod
    def getJobName():
        return "License plate generation"

    @staticmethod
    def getClassesServiced():
        return set({LicensePlateID})
    

    def __init__(self, recognizer = None):
        assert type(self) != LicensePlateGenerator_AbstCls
        ContentGenerator_AbstCls.__init__(self, recognizer)
    
    @final
    def _generate(self, view):
        
        lp_nparray = self._generate_LP(view)
        detection = BoundingBox_Cls(LicensePlateID, 0.0, 0.0, 1.0, 1.0)  # All np array represents license plate with no additional context
        
        return View_Cls(lp_nparray, detection)
    
    @abstractmethod
    def _generate_LP(self, view):
        "Return license plate image array(in case of license plates there are no need of any context, as it is for example for faces)"
        pass
    
    
    def _chooseNumbersWithMinimalsumOfLevenshteinDistance(self, recognizedNumbers_list):
        
        recognizedNumbers_list = [number for number in recognizedNumbers_list if isinstance(number, str) and number]
        
        if recognizedNumbers_list:
            shortestDistance_sum = None
            shortestDistance_element = recognizedNumbers_list[0]
            
            for recognizedNumbers in recognizedNumbers_list:
                
                distanceSum = sum([distance(recognizedNumbers, recognizedNumbers_other) for recognizedNumbers_other in recognizedNumbers_list])
                
                if shortestDistance_sum is None or distanceSum < shortestDistance_sum:
                    shortestDistance_sum = distanceSum
                    shortestDistance_element = recognizedNumbers
                    
            return shortestDistance_element
        else:
            return ""
    
    
    def _analyzeRecognizedPlateNumbersAndGetBestCompromise(self, recognizedNumbers_list):
        return self._chooseNumbersWithMinimalsumOfLevenshteinDistance(recognizedNumbers_list)
    
    
    def _dSAVRFEO_byAnalysingAllPerspectives(self, objectFound):
        
        assert self._performsRecognitionBefore()
            
        recognizedFeatures = []
        
        for objectView in objectFound.iterViews():
            
            recognition = self._recognizer._recognize(objectView)
            assert isinstance(recognition, RecognizedPlateNumbers_Cls)
            
            recognizedFeatures.append(recognition.getFeatures())
            
        numbersDecided = self._analyzeRecognizedPlateNumbersAndGetBestCompromise(recognizedFeatures)
        
        objectiveRecognition = RecognizedPlateNumbers_Cls(numbersDecided)
        
        for objectView in objectFound.iterViews():
            objectView.setRecognition(objectiveRecognition)
        
        objectView = self._generate(objectView)
        objectFound.assignAnonymizedView(objectView)
            








