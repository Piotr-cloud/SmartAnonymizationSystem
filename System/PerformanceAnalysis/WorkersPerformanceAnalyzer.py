'''
Created on Feb 12, 2023

@author: piotr
'''
from texttable import Texttable
from abc import abstractmethod
import numpy as np
from PolymorphicBases.ABC import final, Base_AbstCls
import json
from Annotator.Annotator import Annotator_Cls
from PerformanceAnalysis.WorkersPerformanceLogger import WorkerConstructionLog_Cls,\
    WorkerPreparationLog_Cls, WorkerExecutionLog_Cls,\
    WorkerPerformanceLog_AbstCls
from PerformanceAnalysis.FormattingUnits import formatTime, formatRAM


NoData_key = "-"

ResourcesCost_Cls = None
def getClass_ResourcesCost_Cls():
    global ResourcesCost_Cls
    if ResourcesCost_Cls is None:
        from PerformanceAnalysis.ResourcesCostCalculator import ResourcesCost_Cls
    return ResourcesCost_Cls


class WorkersPerformanceAnalysisData_Cls():
    
    def __init__(self):
        
        self._workersPerformanceData_dict = {}
        self.GPU_ids = set()
    
    
    def registerGPU_id(self, GPU_id):
        
        self.GPU_ids.add(GPU_id)
    
    
    def __add__(self, other):
        self._importFromDumpObj(other._getDumpObj())
        return self
    
    def _getDumpObj(self):
        
        workersData_dict = {}
        
        dump_dict = {
            "GPU ids" :           tuple(self.GPU_ids),
            "workers data" :      workersData_dict
            }
        
        for workerKey, workerData in self._workersPerformanceData_dict.items():
            workersData_dict[workerKey] = workerData._getDumpObj()
            
        return dump_dict
    
    
    def _importFromDumpObj(self, dumpObj):
        
        for GPU_id in dumpObj["GPU ids"]:
            self.registerGPU_id(GPU_id)
        
        workersData_dict = dumpObj["workers data"]
        
        for workerKey in workersData_dict:
            
            if workerKey not in self._workersPerformanceData_dict:
                self._workersPerformanceData_dict[workerKey] = WorkerPerformanceAnalysisData_Cls(self, workersData_dict[workerKey][1])
            
            self._workersPerformanceData_dict[workerKey]._importFromDumpObj(workersData_dict[workerKey])
                
        self.complementMissingGPU_RAM_usageParamsGroups()
        
    
    def dumpToFile(self, filePath):
        
        dumpObj = self._getDumpObj()
        
        with open(str(filePath), 'w') as f:
            json.dump(dumpObj, f, indent=2)
    
    
    def importFromFile(self, filePath):
        
        with open(filePath) as f:
            loadObj = json.load(f)
        
        self._importFromDumpObj(loadObj)
        
    
    def importFromLogger(self, wp_logger):
        
        while wp_log:= wp_logger.popLog():
            if not issubclass(wp_log.getWorkerCls(), Annotator_Cls): # do not collect information about Annotator_Cls
                self.importFromWorkerPerformanceLog(wp_log)
    
    
    def importFromWorkerPerformanceLog(self, logData):
        
        workerKey = logData.getWorkerCls().getName()
        
        if workerKey not in self._workersPerformanceData_dict:
            self._workersPerformanceData_dict[workerKey] = WorkerPerformanceAnalysisData_Cls(self, logData.getWorkerCls().getWorkerGenericName())
        
        self._workersPerformanceData_dict[workerKey].addLogData(logData)


    def complementMissingGPU_RAM_usageParamsGroups(self):
        
        for workerAnalysisData in self._workersPerformanceData_dict.values():
            workerAnalysisData.complementMissingGPU_RAM_usageParamsGroups(self.GPU_ids)
    
    
    def getWorkersPerformanceDataDict(self):
        return self._workersPerformanceData_dict
    
            
    def _getWorkersPerformanceDataStrings_list(self, paramsVertical):
        
        output_list = []
        
        #self.dumpToFile(r"/home/piotr/ProjektMagisterski/Drafts/tempDebug/wpad") #TODO: remove
        self.complementMissingGPU_RAM_usageParamsGroups()
        
        workerKeys_sorted = sorted(self._workersPerformanceData_dict)
        
        for workerKey in workerKeys_sorted:
            
            workerAnalysisData = self._workersPerformanceData_dict[workerKey]
            output_list.append(
                workerAnalysisData.getTableString(workerKey, paramsVertical) + "\n\n" + 
                "Worker: \"" + str(workerKey) + "\"\n\n" +  
                getClass_ResourcesCost_Cls()(workerAnalysisData).toStr(infoThreshold = True, workerJobHeader = False)
                )
            
        return output_list


    def getWorkersPerformanceDataString(self, addHeader = True, paramsVertical = True):
        
        wpds_list = self._getWorkersPerformanceDataStrings_list(paramsVertical)
        
        output_str = ""
        
        if wpds_list:
            if addHeader:
                output_str += "\nWorkers performance details:\n\n"
            
            output_str += "\n\n\n\n".join(wpds_list) + "\n"
        
        return output_str
            


class WorkerPerformanceAnalysisData_Cls():
    
    def __init__(self, rootContainer, workerGenericTypeName):
        
        assert isinstance(rootContainer, WorkersPerformanceAnalysisData_Cls)
        
        self.constructionData   =  ConstructionAnalysisData_Cls(rootContainer)
        self.preparationData    =  PreparationAnalysisData_Cls(rootContainer)
        self.firstExecData      =  FirstExecAnalysisData_Cls(rootContainer)
        self.secondaryExecData  =  SecondaryExecAnalysisData_Cls(rootContainer)
        
        self.analysisData_list = [ # order is important for serialization/deserialization
            self.constructionData,
            self.preparationData,
            self.firstExecData,
            self.secondaryExecData
            ]
        
        self._workerGenericTypeName = workerGenericTypeName
    
    
    def getPhaseData_Construction(self):    return self.constructionData
        
    def getPhaseData_Preparation(self):     return self.preparationData
        
    def getPhaseData_FirstExec(self):       return self.firstExecData
    
    def getPhaseData_SecondaryExec(self):   return self.secondaryExecData
    
    
    def getPhasesData_list(self):
        return self.analysisData_list[:]
    
    
    def getWorkerGenericTypeName(self):
        return self._workerGenericTypeName
    
    
    def _getDumpObj(self):
        
        data_list = []
        workerGenericTypeName_str = self._workerGenericTypeName
        
        for analysisData_container in self.analysisData_list:
            data_list.append(analysisData_container._getDumpObj())
        
        return data_list, workerGenericTypeName_str
    
    
    def _importFromDumpObj(self, dumpObj):
        
        data_list, workerGenericTypeName_str = dumpObj
        
        assert self._workerGenericTypeName == workerGenericTypeName_str
        
        for idx, el in enumerate(data_list):
            self.analysisData_list[idx]._importFromDumpObj(el)
        
    
    def _getDataInTable(self, workerId):
        
        headers_row = [workerId]
        
        headers_row_remaining = None
        
        # define column headers and check data integrity
        for anaysisData in self.analysisData_list:
            if headers_row_remaining is None:
                headers_row_remaining = anaysisData.getColumnsHeaders()
            else:
                assert headers_row_remaining == anaysisData.getColumnsHeaders()
                
        headers_row.extend(headers_row_remaining)
        
        output_table = [headers_row]
        
        
        for anaysisData in self.analysisData_list:
            output_table.append([anaysisData.__class__.name] + anaysisData.getValues())
            
        
        return output_table
    
    
    def complementMissingGPU_RAM_usageParamsGroups(self, GPU_ids):
        
        for anaysisData in self.analysisData_list:
            anaysisData.complementMissingGPU_RAM_usageParamsGroups(GPU_ids)
    
    
    def transposeMatrice(self, matrice2d):
        ar = np.array(matrice2d)
        return list(ar.transpose())
            
            
        
    def getTableString(self, workerId, paramsVertical):
        
        table = Texttable()
        tableValues = self._getDataInTable(workerId)
        
        if paramsVertical:
            tableValues = self.transposeMatrice(tableValues)
            
        table.add_rows(tableValues)
        table.set_max_width(250)
        
        return table.draw()
    
    
    
    def addLogData(self, logData):
        
        assert isinstance(logData, WorkerPerformanceLog_AbstCls)
        
        if isinstance(logData, WorkerConstructionLog_Cls):
            self.constructionData.addLogData(logData)
            
        elif isinstance(logData, WorkerPreparationLog_Cls):
            self.preparationData.addLogData(logData)
        
        elif isinstance(logData, WorkerExecutionLog_Cls):
            if logData.isFirstExecutionRelated():
                self.firstExecData.addLogData(logData)
            else:
                self.secondaryExecData.addLogData(logData)
                



class MeasurementStageAnalysisData_AbstCls():
    
    def __init__(self, rootContainer):
        
        self.rootContainer = rootContainer
        
        self.measurmentsQuantity = 0
        self.timeConsumption = TimeConsumption_ParamsGroup_Cls()
        self.RAM_usage = RAM_usage_ParamsGroup_Cls()
        self.GPU_RAM_usage = {}
    
    
    def anyMeasurements(self):
        return bool(self.measurmentsQuantity)
    
    
    def getNumberOfMeasurements(self):
        return self.measurmentsQuantity
    
    
    def complementMissingGPU_RAM_usageParamsGroups(self, GPU_ids):
        
        for GPU_id in GPU_ids:
            if GPU_id not in self.GPU_RAM_usage:
                self.GPU_RAM_usage[GPU_id] = GPU_RAM_usage_ParamsGroup_Cls(GPU_id)
                
    
    def getColumnsHeaders(self):
        
        output_list = ["Measurements"] + self.timeConsumption.getColumnsHeaders() + self.RAM_usage.getColumnsHeaders()
        
        for GPU_id in self.GPU_RAM_usage:
            output_list.extend(self.GPU_RAM_usage[GPU_id].getColumnsHeaders())
            
        return output_list
        
    
    def _getDumpObj(self):
        
        GPU_dict = {}
        
        output_dict = {
            'weight' : self.measurmentsQuantity,
            'time' : self.timeConsumption._getDumpObj(),
            'RAM' : self.RAM_usage._getDumpObj(),
            'GPUs RAM' : GPU_dict
            }
        
        for GPU_id, GPU_paramsGroup in self.GPU_RAM_usage.items():
            GPU_dict[GPU_id] = GPU_paramsGroup._getDumpObj()
        
        return output_dict
    
    
    def _importFromDumpObj(self, dumpObj):
        
        quantity_info  = int(dumpObj['weight'])
        
        assert quantity_info >= 0
        
        if quantity_info > 0:
            
            self.measurmentsQuantity += quantity_info
            
            time_info      = dumpObj['time']
            RAM_info       = dumpObj['RAM']
            GPUsRAM_info   = dumpObj['GPUs RAM']
            
            self.timeConsumption._importFromDumpObj(time_info, quantity_info)
            self.RAM_usage._importFromDumpObj(RAM_info, quantity_info)
            
            for GPU_id, GPU_RAM_info in GPUsRAM_info.items():
                if GPU_id not in self.GPU_RAM_usage:
                    self.GPU_RAM_usage[GPU_id] = GPU_RAM_usage_ParamsGroup_Cls(GPU_id)
                    
                self.GPU_RAM_usage[GPU_id]._importFromDumpObj(GPU_RAM_info, quantity_info)
        
    
    def getValues(self):
        
        output_list = [str(self.measurmentsQuantity)] + self.timeConsumption.getValues() + self.RAM_usage.getValues()
        
        for GPU_id in self.GPU_RAM_usage:
            output_list.extend(self.GPU_RAM_usage[GPU_id].getValues())

        return output_list
    
    
    def addLogData(self, logData):
        
        RAM_info       =  logData.getRAM_Info()
        GPUsRAM_info   =  logData.getGPUsRAM_Info()
        
        startTime = logData.getStartTime_s()
        endTime = logData.getEndTime_s()
            
        # measurmentsQuantity
        self.measurmentsQuantity += 1
        
        # timeConsumption
        time_s = endTime - startTime
        self.timeConsumption.addSample(time_s)
        
        # RAM_usage
        self.RAM_usage.addSample(
            RAM_info.getStart(),
            RAM_info.getPeak(),
            RAM_info.getLast()
            )
        
        # GPU_RAM_usage        
        for GPU_id in GPUsRAM_info.getGPUsIds():
            
            if GPU_id not in self.GPU_RAM_usage:
                self.GPU_RAM_usage[GPU_id] = GPU_RAM_usage_ParamsGroup_Cls(GPU_id)
                self.rootContainer.registerGPU_id(GPU_id)
            
            self.GPU_RAM_usage[GPU_id].addSample(
                GPUsRAM_info.getStart(GPU_id), 
                GPUsRAM_info.getPeak(GPU_id), 
                GPUsRAM_info.getLast(GPU_id)
                )
        
        


class ConstructionAnalysisData_Cls(MeasurementStageAnalysisData_AbstCls):
    name = "Construction"
    

class PreparationAnalysisData_Cls(MeasurementStageAnalysisData_AbstCls):
    name = "Preparation"

class FirstExecAnalysisData_Cls(MeasurementStageAnalysisData_AbstCls):
    name = "First execution"

class SecondaryExecAnalysisData_Cls(MeasurementStageAnalysisData_AbstCls):
    name = "Secondary executions"
    




class StageParamsGroup_AbstCls(Base_AbstCls):
    
    def __init__(self):
        self.quantity = 0
    
    @final
    def addSample(self, *args):
        
        self.quantity += 1
        self._addSample(*args)
    
    
    @final
    def _importFromDumpObj(self, dumpObj, quantity):
        assert isinstance(quantity, int) and quantity > 0
        self._importFromDumpObj_(dumpObj, quantity)
        self.quantity += quantity
    
    
    @abstractmethod
    def _importFromDumpObj_(self, dumpObj, quantity):
        pass
    
    
    def _mergeAverages(self, avg_1, avg_1_weight, avg_2, avg_2_weight):
        
        if avg_1 is None: return avg_2
        if avg_2 is None: return avg_1
        
        return avg_1 * avg_1_weight / (avg_1_weight + avg_2_weight) + avg_2 * avg_2_weight / (avg_1_weight + avg_2_weight)
    
    
    def _getAverage(self, currentAvg, currentAvg_weight, newVal):
        if currentAvg is not None:
            return ((currentAvg * currentAvg_weight) + newVal) / (self.quantity + 1)
        else:
            return newVal
    
    def _getMax(self, currentMax, newVal):
        if currentMax is not None:
            if newVal is not None:
                return max([currentMax, newVal])
            else:
                return currentMax
        else:
            return newVal
    
    
    def _getMin(self, currentMin, newVal):
        if currentMin is not None:
            return min([currentMin, newVal])
        else:
            return newVal
    
    
    def _time2Str(self, time):
        if time is not None:
            return formatTime(time)
        else:
            return NoData_key
    
    def _RAM2Str(self, RAM):
        if RAM is not None:
            return formatRAM(RAM)
        else:
            return NoData_key
    
    
    def _verifyTableCellsStrings(self, listToCheck):
        assert isinstance(listToCheck, list) and all([isinstance(el, str) for el in listToCheck])
        
    
    def getColumnsHeaders(self):
        output_list = self._getColumnsHeaders()
        self._verifyTableCellsStrings(output_list)
        return output_list
    
    @abstractmethod
    def _getColumnsHeaders(self):
        pass
    
    
    def getValues(self):
        output_list = self._getValues()
        self._verifyTableCellsStrings(output_list)
        return output_list
    
    @abstractmethod
    def _getValues(self):
        pass



class TimeConsumption_ParamsGroup_Cls(StageParamsGroup_AbstCls):
        
    def __init__(self):
        
        StageParamsGroup_AbstCls.__init__(self)
        
        self.avg = None
        self.max = None
        self.min = None
        
    
    def getAvg(self):
        return self.avg
    
    def getMax(self):
        return self.max
    
    def getMin(self):
        return self.min
    
    
    def _getDumpObj(self):
        
        return [
            self.avg,
            self.max,
            self.min
            ]
        
    def _importFromDumpObj_(self, dumpObj, quantity):
        
        avg_, max_, min_ = dumpObj
        
        self.max = self._getMax(self.max, max_) 
        self.min = self._getMin(self.min, min_)
        
        self.avg = self._mergeAverages(self.avg, self.quantity, avg_, quantity) 
        
        
    def _addSample(self, time_s):
        
        self.avg = self._getAverage(self.avg, self.quantity, time_s)
        self.max = self._getMax(self.max, time_s)
        self.min = self._getMin(self.min, time_s)
        
        
    def _getColumnsHeaders(self):
        return [
            "Avg exec time",
            "Max exec time",
            "Min exec time"
            ]
    
    def _getValues(self):
        return [
            self._time2Str(self.avg),
            self._time2Str(self.max),
            self._time2Str(self.min)
            ]



class RAM_usage_ParamsGroup_Cls(StageParamsGroup_AbstCls):
    
    def __init__(self):
        
        StageParamsGroup_AbstCls.__init__(self)
        self.diff_avg = None
        self.diff_max = None
        self.peak_avg = None
        self.peak_max = None
        
    
    def convert_B_2_GB(self, noOfBytes):
        return ((noOfBytes / 1024.) / 1024) / 1024.
    
    def getLeakageAvg(self,  to_GB = True):
        return self.diff_avg if to_GB != True else self.convert_B_2_GB(self.diff_avg)
    
    def getLeakageMax(self,  to_GB = True):
        return self.diff_max if to_GB != True else self.convert_B_2_GB(self.diff_max)
    
    def getPeakAvg(self,     to_GB = True):
        return self.peak_avg if to_GB != True else self.convert_B_2_GB(self.peak_avg)
    
    def getPeakMax(self,     to_GB = True):
        return self.peak_max if to_GB != True else self.convert_B_2_GB(self.peak_max)
    
    
    def _getDumpObj(self):
        
        return [
            self.diff_avg,
            self.diff_max,
            self.peak_avg,
            self.peak_max
            ]
        
    def _importFromDumpObj_(self, dumpObj, quantity):
        
        diff_avg, diff_max, peak_avg, peak_max = dumpObj
        
        self.peak_max = self._getMax(self.peak_max, peak_max) 
        self.diff_max = self._getMax(self.diff_max, diff_max)
        
        self.diff_avg = self._mergeAverages(self.diff_avg, self.quantity, diff_avg, quantity)
        self.peak_avg = self._mergeAverages(self.peak_avg, self.quantity, peak_avg, quantity) 


    def _addSample(self, start, peak, end):
        
        try:
            assert isinstance(start, int)
            assert isinstance(end, int)
            
            diff = end - start
            self.diff_avg = self._getAverage(self.diff_avg, self.quantity, diff)
            self.diff_max = self._getMax(self.diff_max, diff)
            
        except: pass
        
        try:
            assert isinstance(peak, int)
            
            peak -= start # convert peak to be relative
            
            self.peak_avg = self._getAverage(self.peak_avg, self.quantity, peak)
            self.peak_max = self._getMax(self.peak_max, peak)
     
        except: pass
        
    
    def _getDeviceName(self):
        return ""
    
     
    def _getColumnsHeaders(self):
        
        deviceNamePart = self._getDeviceName()
        
        if len(deviceNamePart) > 16:    deviceNamePart += "\n"
        elif deviceNamePart:            deviceNamePart += " "
        
        return [
            deviceNamePart + "RAM avg leakage",
            deviceNamePart + "RAM max leakage",
            deviceNamePart + "RAM avg peak",
            deviceNamePart + "RAM max peak"
            ]
    
    def _getValues(self):
        return [
            self._RAM2Str(self.diff_avg) if self.quantity >= 1 else NoData_key,
            self._RAM2Str(self.diff_max) if self.quantity >= 1 else NoData_key,
            self._RAM2Str(self.peak_avg) if self.quantity >= 1 else NoData_key,
            self._RAM2Str(self.peak_max) if self.quantity >= 1 else NoData_key
            ]



class GPU_RAM_usage_ParamsGroup_Cls(RAM_usage_ParamsGroup_Cls):
    
    def __init__(self, GPU_id):
        self.GPU_id = GPU_id
        RAM_usage_ParamsGroup_Cls.__init__(self)
    
    
    def _getDeviceName(self):
        return str(self.GPU_id)



class GPUsRAM_usage_Cls():
    
    def __init__(self):
        self._data_dict = {}
            
    
    def addSample(self, GPU_id, diff, peak):
    
        if GPU_id not in self._data_dict:
            self._data_dict[GPU_id] = GPU_RAM_usage_ParamsGroup_Cls(GPU_id)
        
        self._data_dict[GPU_id].addSample(diff, peak)

























    