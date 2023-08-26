'''
Created on Oct 29, 2022

@author: piotr
'''
from PolymorphicBases.Worker import Worker_AbstCls
from PolymorphicBases.ABC import final
from abc import abstractmethod
from ContentRecognizer.Recognition import Recognition_AbstCls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj



class ContentRecognizer_AbstCls(Worker_AbstCls):
    """
    Is a part of content generation process as pre-recognition to define features vector for generation
    Worker that performs recognition( .recognize() ) and adds features into provided view (in-place operation)
    """
    
    @staticmethod
    def getWorkerGenericName():
        return "Content recognizer"

    @staticmethod
    def getJobName():
        return "Content recognition"
    
    
    def __init__(self, recognitionCls):
        assert issubclass(recognitionCls, Recognition_AbstCls)
        self._recognitionCls = recognitionCls
    
    def validateRecognitionCls(self, recognition):
        assert isinstance(recognition, self._recognitionCls)

    @abstractmethod
    def _recognize(self, view):
        "Shall return recognitionCls object"
        pass
    
    @final
    def recognize(self, view):
        
        if not view.isRecognized():
        
            with workersPerformanceLoggerObj.startContext_executuion(self):
                
                recognition = self._recognize(view)
                
                self.validateRecognitionCls(recognition)
                view.setRecognition(recognition)




