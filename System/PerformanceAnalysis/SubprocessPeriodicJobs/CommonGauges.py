'''
Created on Feb 25, 2023

@author: piotr
'''
from abc import abstractmethod
import psutil
from PolymorphicBases.ABC import final, Base_AbstCls
import gc
import time
import csv
from NonPythonFiles import memoryMonitorWorkspace_Logs_dir, getUserDecision_memoryMonitoring
import datetime



class CommonGauges_AbstCls(Base_AbstCls):

    def __init__(self):
        
        self._to_refresh = False
        self._data = None
        self._memoryMonitorWorkspace_Logs_dir = memoryMonitorWorkspace_Logs_dir
        
    
    def _getCsvFilePath(self):
        
        if "_logFilePath" not in self.__dict__:
            self._logFilePath = memoryMonitorWorkspace_Logs_dir / str(self.getTimestampToStr() + ":  " + self.__class__.__name__ + ".csv")
            
            if self._logFilePath.exists():
                if self._logFilePath.is_file():
                    os.remove(str(self._logFilePath))
                else:
                    raise IsADirectoryError("Cannot use the following path as log file since it is a directory: " + str(self._logFilePath))
            
            
        return self._logFilePath
    
    
    def getTimestampToStr(self):
        timestamp = self.getTimestamp()
        return datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.') + (str(timestamp).split(".")[1]).ljust(7, "0")
    
    
    def getTimestamp(self):
        return time.time()
    
    @final
    def setToRefresh(self):
        self._to_refresh = True
    
    
    @final
    def _logSample(self, sample, additionalInfo = ""):
        
        if getUserDecision_memoryMonitoring():
            
            csvFilePath = self._getCsvFilePath()
            
            timestamp_str = str(self.getTimestamp())
            sample_str = str(sample)
            additionalInfo_str = str(additionalInfo)
            
            dumpList = [timestamp_str, sample_str, additionalInfo_str]
            
            with open(csvFilePath, "a") as csvFile:
                csvWriter = csv.writer(csvFile)
                csvWriter.writerow(dumpList)
            
    
    
    @final
    def readTheMostFresh(self, additionalInfo = "RequestedMostFresh"):
        self._data = self._read()
        self._logSample(self._data, additionalInfo = additionalInfo)
        return self._data
    
    
    @final
    def read(self):

        if self._to_refresh:
            self._data = self._read()
            self._logSample(self._data)
            
        return self._data
    

    @abstractmethod
    def _read(self):
        "Implement sensor logic here"
        pass


    
class RAM_Gauge_Cls(CommonGauges_AbstCls):
    
    def __init__(self, pid):
        self._processId = pid
        try:
            self._psutilProcess = psutil.Process(self._processId)
            self._psutilProcess.memory_info()
            
        except:
            self._psutilProcess = None
            print(" Warning! RAM_Gauge_Cls: Cannot monitor RAM usage!")
        
        CommonGauges_AbstCls.__init__(self)
            
    def __eq__(self, other)->bool:
        if other.__class__ == self.__class__:
            return other.pid == self.pid
    
    def __hash__(self)->int:
        return CommonGauges_AbstCls.__hash__(self)
    
    def _getVirtualRAM_usage(self):
        return self._psutilProcess.memory_info().vms # Virtual RAM
    
    def _getPhysicalRAM_usage(self):
        return self._psutilProcess.memory_info().rss # Physical RAM
    
    def _read(self):
        if self._psutilProcess:
            gc.collect()
            return self._getVirtualRAM_usage()
        else:
            return None



class GPUs_RAM_Gauge_Cls(CommonGauges_AbstCls):

    def __init__(self, pid):
        self._processId = pid

        try:
            import nvidia_smi
            self._nvidia_smi = nvidia_smi
        
            self._GPU_devices_dict = {}
            
            if self._nvidia_smi is not None:
                self._nvidia_smi.nvmlInit()
                
                GPU_deviceCount = nvidia_smi.nvmlDeviceGetCount()
                
                for deviceIndex in range(GPU_deviceCount):
                    
                    handle = self._nvidia_smi.nvmlDeviceGetHandleByIndex(deviceIndex)
                    
                    name = self._nvidia_smi.nvmlDeviceGetName(handle).decode("utf-8")
                    
                    # try to get some info else do not provide any output
                    self._GPU_devices_dict[deviceIndex] = {
                        "name"    : name,
                        "handle"  : handle
                        }
                    
                    info = self._nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                    info.used
                    
        except:
            # if any issue found - do not provide any output 
            self._nvidia_smi = None
            print(" Warning! GPUs_RAM_Gauge_Cls: Cannot monitor GPUs memory usage!")
        
        CommonGauges_AbstCls.__init__(self)

                
    def _read(self):
        
        self.GPUsRAM_dict = {}
        
        if self._nvidia_smi is not None:
            
            for deviceIndex in self._GPU_devices_dict:
                
                name = self._GPU_devices_dict[deviceIndex]["name"]
                handle = self._GPU_devices_dict[deviceIndex]["handle"]
                
                info = self._nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                
                deviceId = name
                
                self.GPUsRAM_dict[deviceId] = info.used
        
        return  self.GPUsRAM_dict.copy()



if __name__ == "__main__":
    
    import os
    
    ramGauge = RAM_Gauge_Cls(os.getpid())
    
    print(ramGauge.read())
    
    ramGauge.setToRefresh()

    print(ramGauge.read())
    
    ramConsumption = bytearray(512000000)
    
    ramGauge.setToRefresh()
    
    print(ramGauge.read())














