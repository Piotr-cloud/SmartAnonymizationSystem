'''
Created on Sep 21, 2022

@author: piotr
'''
from PolymorphicBases.Worker import Worker_AbstCls
from PolymorphicBases.ABC import final 
from abc import abstractmethod
from ObjectsDetectable.Objects import Object_Cls
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj


class TrackStabilizer_AbstCls(Worker_AbstCls):
    '''
    Worker that performs object track stabilization, so helps to improve precision of track using post analysis based on tracked object coordinates in time. As result track stabilizer corrects all coordinates of tracked object in time.
    '''
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Stabilizer"
        
    @staticmethod
    def getJobName():
        return "Stabilization"
    
    
    def __init__(self):
        '''
        Constructor
        '''
        assert type(self) != TrackStabilizer_AbstCls
        Worker_AbstCls.__init__(self)
        

    @final
    def stabilize(self, objects):
        
        assert hasattr(objects, "__iter__")
        assert all([isinstance(obj_, Object_Cls) for obj_ in objects])
        
        with workersPerformanceLoggerObj.startContext_executuion(self):
            for obj_ in objects:
                self._stabilize(obj_)
    
    @abstractmethod    
    def _stabilize(self, obj_):
        pass





