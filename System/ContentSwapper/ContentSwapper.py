'''
Created on Jan 25, 2022

@author: piotr
'''
from SpaceSpecificProcessor._2D.ArrayProcessor import ArraySpecificProcessor_Cls
from View.View import View_Cls
from PolymorphicBases.Worker import Worker_AbstCls
from PolymorphicBases.ABC import final, abstractmethod
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj


class ContentSwapper_AbstCls(Worker_AbstCls):
    """
    Swaps detection content from one object view to another
    stateless class
    """
        
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Content swapper"
        
    @staticmethod
    def getJobName():
        return "Content swapping"
    

    def __init__(self):
        assert type(self) != ContentSwapper_AbstCls
        self._asp = ArraySpecificProcessor_Cls()
    
    @final
    def swap(self, srcObjectView, destObjectView):
        """
        Scales and resizes and then replaces
        takes srcView, destView and returns new modified nparray or "Failed"
        Returning "Failed" means operation not performed so callers can skip adaptation to non-existing change
        """
        assert isinstance(srcObjectView, View_Cls)
        assert isinstance(destObjectView, View_Cls)
        
        with workersPerformanceLoggerObj.startContext_executuion(self):
            output_nparray = self._swap(srcObjectView, destObjectView)
        
        return output_nparray
    
    
    def _validateSrcObjectView(self, srcObjectView):
        
        srcObjectView
        
        return True # stubbed


    @abstractmethod
    def _swap(self, srcObjectView, destObjectView):
        raise NotImplementedError()





