'''
Created on Feb 25, 2023

@author: piotr
'''
from PerformanceAnalysis.SubprocessPeriodicJobs.SubprocessPeriodicJob import SubprocessJob_AbstCls
import time
from PerformanceAnalysis.SubprocessPeriodicJobs.CommonGauges import RAM_Gauge_Cls,\
    GPUs_RAM_Gauge_Cls
from PerformanceAnalysis.SubprocessPeriodicJobs.RAMsInfo import RAM_Info_Cls, GPUsRAM_Info_Cls
from abc import abstractmethod


class ProcesMemory_Monitor_SubprocessJob_AbstCls(SubprocessJob_AbstCls):
    
    gaugeCls = None
    outputObjCls = None
    
    def __init__(self): # client side
        
        SubprocessJob_AbstCls.__init__(self)
        self.clientArgs = []
    
    
    def client_setServerInstanceInitArgs(self, processId, monitorLogName):
        self.clientArgs = [processId, monitorLogName]
        

    def client_getServerInstanceArgs(self):
        return self.clientArgs
    
    
    def server__init__(self, serverInstanceArgs_listOfStrings):
        "jobArgsStrings: List of strings that shall be converted to class members"
        
        processId = int(serverInstanceArgs_listOfStrings[0])
        monitorLogName = str(serverInstanceArgs_listOfStrings[1])
        
        self.processId = processId
        self.measuredObjInfo = monitorLogName if monitorLogName else "<unknown>"
        
        self.gauge          =   self.server_getOriginalGauge(self.__class__.gaugeCls, self.processId)
        self.sample_start   =   self.gauge.readTheMostFresh("Entering by: " + self.measuredObjInfo)
        self.sample_last    =   self.sample_start
        self.sample_max     =   self.sample_last
        
        self.server__init__2()
    
    def server__init__2(self):
        pass

    
    def _server_getSimpleOutputObject(self):
        self.sample_last = self.gauge.readTheMostFresh("Exiting by: " + self.measuredObjInfo)
        return [self.sample_start, self.sample_max, self.sample_last]
    
    
    def _client_postProcessSimpleOutputObject(self, simpleOutputObject):
        
        sample_start, sample_max, sample_last = simpleOutputObject
        
        return self.__class__.outputObjCls(sample_start, sample_max, sample_last)
    
    
    @abstractmethod
    def _server_additionalExecAtGetResult(self):
        pass
    
    @abstractmethod
    def _server_periodicExec(self):
        pass



class HostProces_RAM_Monitor_SubprocessJob_Cls(ProcesMemory_Monitor_SubprocessJob_AbstCls):
    
    gaugeCls = RAM_Gauge_Cls
    outputObjCls = RAM_Info_Cls
    
    
    def _server_additionalExecAtGetResult(self):
        self._server_periodicExec()
    
    
    def _server_periodicExec(self):
        self.sample_last = self.gauge.read()
        
        if self.sample_last is not None:
            if self.sample_last > self.sample_max:
                self.sample_max = self.sample_last
    



class HostProces_GPURAMs_Monitor_SubprocessJob_Cls(ProcesMemory_Monitor_SubprocessJob_AbstCls):
    '''
    Monitors CPU RAM and each GPU RAM of specified process
    '''    
    gaugeCls = GPUs_RAM_Gauge_Cls
    outputObjCls = GPUsRAM_Info_Cls
    
    
    def server__init__2(self):
        self.GPU_ids = set(self.sample_start.keys())
        
    
    def _server_additionalExecAtGetResult(self):
        
        self._server_periodicExec()
        
        # fill missing GPU info
        
        for GPU_id in self.GPU_ids:
            
            if GPU_id not in self.sample_start:
                self.sample_start[GPU_id] = None
                
            if GPU_id not in self.sample_last:
                self.sample_last[GPU_id] = None
                
    
    
    def _server_periodicExec(self):
        
        self.sample_last = self.gauge.read()
        
        for GPU_id in self.sample_last:
            
            if GPU_id not in self.GPU_ids:
                self.GPU_ids.add(GPU_id)
                self.sample_max[GPU_id] = self.sample_last[GPU_id]
            
            else:
                if self.sample_last[GPU_id] > self.sample_max[GPU_id]:
                    self.sample_max[GPU_id] = self.sample_last[GPU_id]













if __name__ == "__main__":
    
    withContextSwitch = True
        
    if withContextSwitch:
        
        subprocJob = HostProces_RAM_Monitor_SubprocessJob_Cls()
        jobId = subprocJob.start()
        
        class _ContextSwitch():
            
            def __enter__(self):
                
                print("Entering context: " + str(subprocJob.getResult()))
            
            def __exit__(self, exc_type, exc_value, exc_tb):
                print("Exiting context: " + str(subprocJob.getResult()))
        
        print("At startup: " + str(subprocJob.getResult()))
        
        with _ContextSwitch():
            
            print()
            print("Before allocation: " + str(subprocJob.getResult()))
            ramConsumption = bytearray(1024*1010)
            print("After allocation: " + str(subprocJob.getResult()))
            print()
            
            del ramConsumption
            print("After deletion: " + str(subprocJob.getResult()))
            
        
        print("At finish: " + str(subprocJob.getResult()))
        subprocJob.finish()
    
    else:
        subprocJob = HostProces_RAM_Monitor_SubprocessJob_Cls()
        
        
        jobId = subprocJob.start()
        
        time.sleep(1)
        
        print("Result after 1 secs:  " + str(subprocJob.getResult()))
        
        ramConsumption = bytearray(1024000000)
        
        time.sleep(4)
        
        print("Result after 5 secs:  " + str(subprocJob.getResult()))
        
        del ramConsumption
        print("Result after 5. secs:  " + str(subprocJob.getResult()))
        ramConsumption = bytearray(512000000)
        print("Result after 5. (2) secs:  " + str(subprocJob.getResult()))
        
        
        time.sleep(1)
        
        print("Result after 6 secs:  " + str(subprocJob.getResult()))
        
        subprocJob.finish()
        
        #print("#" * 100 + "\t\t!!Checkout!!")
        #time.sleep(10)
    
