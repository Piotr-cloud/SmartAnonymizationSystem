'''
Created on Mar 7, 2023

@author: piotr
'''
from PolymorphicBases.Decorators import singleton


from PerformanceAnalysis.SubprocessPeriodicJobs.RAMsMonitor import HostProces_RAM_Monitor_SubprocessJob_Cls,\
    HostProces_GPURAMs_Monitor_SubprocessJob_Cls
import inspect
import time
import os



class WorkerPerformanceLog_AbstCls():
    
    def __init__(self, workerCls):
        
        self._workerCls = workerCls
        self._RAM_MonitorJob = HostProces_RAM_Monitor_SubprocessJob_Cls()
        self._GPUsRAM_MonitorJob = HostProces_GPURAMs_Monitor_SubprocessJob_Cls()
        
        workerName = workerCls.getName()
        
        self._RAM_MonitorJob.client_setServerInstanceInitArgs(os.getpid(), workerName + " (log id: " + str(id(self)) + ")")
        self._GPUsRAM_MonitorJob.client_setServerInstanceInitArgs(os.getpid(), workerName)
    
    
    def __str__(self):
        return self.getWorkerCls().getName()
    
    
    def __repr__(self): return str(self)
    
    
    def getWorkerCls(self):
        return self._workerCls
    
    
    def __enter__(self):
        self._RAM_MonitorJob.start()
        self._GPUsRAM_MonitorJob.start()
        self._startTime = time.time()
    
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        
        exc_value, exc_tb # unused
         
        self._RAM_info = self._RAM_MonitorJob.getResult()
        self._GPUsRAM_info = self._GPUsRAM_MonitorJob.getResult()
        
        self._RAM_MonitorJob.finish()
        self._GPUsRAM_MonitorJob.finish()
        self._endTime = time.time()
        
        if exc_type:
            return False
        
    
    def getStartTime_s(self):
        return self._startTime
    
    def getEndTime_s(self):
        return self._endTime
        
    def getRAM_Info(self):
        return self._RAM_info
    
    
    def getGPUsRAM_Info(self):
        return self._GPUsRAM_info


        
class WorkerConstructionLog_Cls(WorkerPerformanceLog_AbstCls): pass
class WorkerPreparationLog_Cls(WorkerPerformanceLog_AbstCls): pass
class WorkerExecutionLog_Cls(WorkerPerformanceLog_AbstCls): 
    
    def __init__(self, workerCls, firstUse_flag):
        WorkerPerformanceLog_AbstCls.__init__(self, workerCls)
        self.firstUse_flag = bool(firstUse_flag)
    
    def isFirstExecutionRelated(self):
        return self.firstUse_flag


@singleton
class _WorkersPerfomanceLogger_Cls():
    
    def __init__(self):
        self.logs_list = []
    
    
    def popLog(self):
        if self.logs_list:
            return self.logs_list.pop()
        else:
            return None
    
    
    def _getWorkerCls(self, worker):
        
        if inspect.isclass(worker):
            workerCls = worker
        else:
            workerCls = worker.__class__
        
        return workerCls
    
    
    def startContext_construction(self, worker):
        
        log = WorkerConstructionLog_Cls(self._getWorkerCls(worker))
        self.logs_list.insert(0, log)
        
        return log
    

    def startContext_preparation(self, worker):
        
        log = WorkerPreparationLog_Cls(self._getWorkerCls(worker))
        self.logs_list.append(log)
        
        return log
    

    def startContext_executuion(self, worker):
        
        firstUse = worker._setLogFirstUseFlag()
        log = WorkerExecutionLog_Cls(self._getWorkerCls(worker), firstUse)
        self.logs_list.append(log)
        
        return log



workersPerformanceLoggerObj = _WorkersPerfomanceLogger_Cls()





































