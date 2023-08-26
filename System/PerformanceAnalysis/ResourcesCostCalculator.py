'''
Created on Jun 12, 2023

@author: piotr
'''
from PolymorphicBases.Decorators import singleton
from PerformanceAnalysis.WorkersPerformanceAnalyzer import WorkerPerformanceAnalysisData_Cls
import math
from PolymorphicBases.ABC import Base_AbstCls, final
from abc import abstractclassmethod, abstractmethod



@singleton
class _ResourcesCostCalculator_Cls(object):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        self._expectedFrameTime_ms = 100
        self._partOfSequenceServiced_dict = {"Detector" :             1/6,
                                             "Tracker" :              1/6,
                                             "Stabilizer" :           1/6,
                                             "Content recognizer" :   1/6,
                                             "Content generator" :    1/6,
                                             "Content swapper" :      1/6,
                                             "Annotator" :            3/6,
                                             "Anonymizer" :           3/6}
        
        self._RAM_availability_GB = 32 # 5GB for Operating system and other applications
        self._GPU_RAM_availability_GB = 2.5 # not in use
        
        self._memoryAllowToLeak_perc = 50            # subtracts from total memory availability and allows leakage
        self._memoryPeakExpected_perc = 50           # if RAM is used at this percentage then cost is considered as neutral
        self._memoryLeakageExpected_perc = 20        # if RAM is used at this percentage then cost is considered as neutral

        self._maxCost = 1000
        self._framesProcessedQuantityPredetermined = 1000
        
    
    def _getReductionFactorOfLongTermResources(self, workerPerformanceAnalysisData):
        """
        Since some of the workers shall coop in one sequence some resources like RAM leaked shall be divided proprtionally. This function returns divider
        """
        
        workerGenericTyeName = workerPerformanceAnalysisData.getWorkerGenericTypeName()
        
        return self._partOfSequenceServiced_dict[workerGenericTyeName] # Part in sequence shall be defined in resources cost calculator

    
    
    def _getCost_ReLU(self, value, expected):
        "When value == expected then returns 1"
        
        assert expected > 0, "Value expected shall be grater than zero"
        
        if value < 0:
            return 0
            
        return value / expected
    
    
    def _getCost_rangedTangens(self, value, max_, expected):
        "When value == expected then returns 1"
        
        assert max_ > 0 and expected > 0
        assert max_ > expected
        
        if value < 0:
            return 0
        
        elif value >= max_:
            return  self._maxCost
        
        factor = math.pi / (2 * max_)                      # Range setting - asimptote movement
        expectationDivider = math.tan(expected * factor)   # makes: function(Expected value) == 1
        
        evalResult = math.tan(value * factor) / expectationDivider
        
        return evalResult
    



class _Cost_AbstCls(Base_AbstCls):
    
    def __init__(self):
        self._infoParams_dict = {}
    
        
    @abstractclassmethod
    def getVal(self):
        pass
    
    
    def getValInStr(self):
        
        val = self.getVal()
        
        if val == None:
            val = "Unable to define"
        else:
            val = str(val)
        
        return val


    def __repr__(self):
        return str(self)
    
    
    @final
    def costToStringLines(self, indent = 2, addInfo = True):
        
        assert isinstance(indent, int)
        assert isinstance(addInfo, bool) or isinstance(addInfo, float) or isinstance(addInfo, int)
        
        output_lines = []
        
        output_lines.extend(self._costToStringLines(indent, addInfo))
        
        printInfo = False
        
        if addInfo is True:
            printInfo = True
            
        elif isinstance(addInfo, float) or isinstance(addInfo, int):
            val = self.getVal()
            if val is None or val > addInfo:
                printInfo = True
        
        if printInfo and self._infoParams_dict:
            
            longestParamNameLen = len(max(self._infoParams_dict, key=len))
                
            for paramName, value in self._infoParams_dict.items():
                output_lines.append(self._getParamSerializationLine(paramName, value, indent, longestParamNameLen, isInfo = True)) 
        
        return output_lines
    
    
    @abstractmethod
    def _costToStringLines(self, indent, addInfo):
        pass
    
    
    def _getParamSerializationLine(self, name, value, indent, paramNameLJust, isInfo = False):
        
        output_str = ""
        
        output_str += " " * indent
        
        if isInfo:
            output_str += "(INFO) "
         
        output_str += (str(name) + ":").ljust(paramNameLJust + 1 + 2) + str(value)
        
        return output_str
        
    
    def addInfoParam(self, name, value):
        
        assert isinstance(name, str)
        assert name not in self._infoParams_dict
        
        self._infoParams_dict[name] = value



class _LeafCost_Cls(_Cost_AbstCls):
    
    def __init__(self):
        self._value = None
        _Cost_AbstCls.__init__(self)
        
    
    def setVal(self, value):
        
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("The following value does not represent cost: " + str(value))
        
        self._value = float(value)
    
    
    def getVal(self):
            
        return self._value
    
    
    def _costToStringLines(self, indent, addInfo):
        return []
    
    
    def __str__(self):
        return str(self.getVal())



class _StructuredCost_Cls(_Cost_AbstCls):
    
    def __init__(self):
        
        self._costsDict = {}
        _Cost_AbstCls.__init__(self)
    
    
    def toStr(self, addInfo = False):
        """
        addInfo:
         - <float value>   -  threshold above which info occurs
         - True            -  allways
         - False           -  never
        """
        
        return "\n".join(self.costToStringLines(addInfo = addInfo))
    
    
    def __str__(self):
        
        return self.toStr(3)
    
    
    def _costToStringLines(self, indent, addInfo):
        
        output_lines = []
        
        if self._costsDict:
            
            longestKeyLen = len(max(self._costsDict, key=len))
            
            for key_, cost in self._costsDict.items():
                
                output_lines.append(self._getParamSerializationLine(key_, cost.getValInStr(), indent, longestKeyLen))
                output_lines.extend(cost.costToStringLines(indent + 2, addInfo))
        
        return output_lines
    

    def addCost(self, name, value):
        
        assert isinstance(name, str)
        
        if not isinstance(value, _Cost_AbstCls):
            cost = _LeafCost_Cls()
            cost.setVal(value)
        
        else:
            cost = value
                
        self._costsDict[name] = cost
    
    
    def _getAverageOfCosts(self, costsList):
        
        if not costsList: return None
        
        costValues= [cost.getVal() for cost in costsList if cost.getVal() is not None]
        
        if costValues:
            return sum(costValues) / len(costValues)
        else:
            return None
    
    
    def getVal(self):
        
        val = self._getAverageOfCosts(self._costsDict.values())
                
        return val



class ResourcesCost_Cls():
    
    expectedFPS = 10
    
    partOfSequenceServiced_dict = {"Detector" :             1/6,
                                   "Tracker" :              1/6,
                                   "Stabilizer" :           1/6,
                                   "Content recognizer" :   1/6,
                                   "Content generator" :    1/6,
                                   "Content swapper" :      1/6,
                                   "Annotator" :            3/6,
                                   "Anonymizer" :           3/6}
    
    RAM_availability_GB = 32             # Simulated size of RAM
    
    RAM_maxLeakage_perc = 50             # percentage of RAM_availability_GB that is reserved for leakage of all the workers, rest takes stack (peak)
    RAM_leakageExpected_perc = 20        # expected occupation of region reserved for leakage
    RAM_maxPeakExpected_perc = 50        # expected max peak

    maxCost = 1000                                # Upper limit of any cost (component or summary)
    framesProcessedQuantityPredetermined = 1000   # Simulated number of frames processed  
        
    
    def __init__(self, wpad):
        
        assert isinstance(wpad, WorkerPerformanceAnalysisData_Cls)
        
        self._wpad = wpad

        self._resourcesCostCalculator = _ResourcesCostCalculator_Cls()
        
        self._reductionFactor = self._resourcesCostCalculator._getReductionFactorOfLongTermResources(wpad)
        
        self._workerGenericTypeName = self._wpad.getWorkerGenericTypeName()
        
        self._cost = self._calcTotalCost()
    
    
    def _calcTotalCost(self):
        
        cost = _StructuredCost_Cls()
        
        cost.addCost("Time", self._calcTimeCost())
        cost.addCost("RAM", self._calcRAM_Cost())
        
        return cost
    
    
    def _calcTimeCost(self):
        
        #############################################
        # Init variables
        #############################################
        cost = _LeafCost_Cls()
        totalTime_s = 0
        
        #############################################
        # Get measurement data
        #############################################
        
        # Construction phase
        constructionPhase = self._wpad.getPhaseData_Construction()
        
        if constructionPhase.anyMeasurements():
            constructionMaxTime_s = constructionPhase.timeConsumption.getMax()
            totalTime_s += constructionMaxTime_s
            
            cost.addInfoParam("Longest construction time [s]",   constructionMaxTime_s)
        
        
        # Preparation phase
        preparationPhase = self._wpad.getPhaseData_Preparation()
        
        if preparationPhase.anyMeasurements():
            preparationMaxTime_s = preparationPhase.timeConsumption.getMax()
            totalTime_s += preparationMaxTime_s
            
            cost.addInfoParam("Longest Preparation  time [s]",   preparationMaxTime_s)
        
        
        # First exec phase
        firstExecPhase = self._wpad.getPhaseData_FirstExec()
        
        if firstExecPhase.anyMeasurements():
            firstExecMaxTime_s = firstExecPhase.timeConsumption.getMax()
            totalTime_s += firstExecMaxTime_s
            
            cost.addInfoParam("Longest first exec. time [s]",    firstExecMaxTime_s)
        
        
        # Secondary exec phase
        secondaryExecPhase = self._wpad.getPhaseData_SecondaryExec()
        
        if secondaryExecPhase.anyMeasurements():
            secondaryExecAvgTime_s = secondaryExecPhase.timeConsumption.getAvg()
            totalTime_s += (secondaryExecAvgTime_s * (ResourcesCost_Cls.framesProcessedQuantityPredetermined - 1))
            
            cost.addInfoParam("Secondary exec. avg time [s]",    secondaryExecAvgTime_s)
        
        else:
            cost.addInfoParam("Secondary exec. avg time [s]",    "Not available!")
            return cost  # cost is by default set as not available
        
        
        #############################################
        # Process measurement data
        #############################################
        frameProcessingTime_s = totalTime_s / ResourcesCost_Cls.framesProcessedQuantityPredetermined
        
        
        #############################################
        # Calculate expectations
        #############################################
        frameProcessingTime_s_expected = (1 / ResourcesCost_Cls.expectedFPS) * self._reductionFactor
        
        
        #############################################
        # Calculate cost
        #############################################
        evaluationResult = self._resourcesCostCalculator._getCost_ReLU(frameProcessingTime_s, frameProcessingTime_s_expected)
            
        cost.setVal(evaluationResult)
        
        
        #############################################
        # Log rest info params
        #############################################
        
        cost.addInfoParam("Expected frame proc. time [s]",   frameProcessingTime_s_expected)
        cost.addInfoParam("Frame proc. time [s]",            frameProcessingTime_s)
        
        
        return cost
    #
    #
    #
    # def _getMax(self, currentMax, newVal):
    #     if currentMax is not None:
    #         if newVal is not None:
    #             return max([currentMax, newVal])
    #         else:
    #             return currentMax
    #     else:
    #         return newVal
    
    
    def _calcRAM_Cost(self):
        
        #############################################
        # Init variables
        #############################################
        cost = _StructuredCost_Cls()
        RAM_leakage_GB = 0
        RAM_maxPeak_GB = 0
        
        #############################################
        # Get measurement data
        #############################################
        
        # Construction phase
        constructionPhase = self._wpad.getPhaseData_Construction()
        
        if constructionPhase.anyMeasurements():
            
            constructionAvgLeakage_GB = constructionPhase.RAM_usage.getLeakageAvg(True)
            constructionMaxPeak_GB = constructionPhase.RAM_usage.getPeakMax(True)
            
            RAM_leakage_GB += constructionAvgLeakage_GB
            RAM_maxPeak_GB = max([RAM_maxPeak_GB, constructionMaxPeak_GB])
            
            cost.addInfoParam("Constuction avg leakage [GB]",   constructionAvgLeakage_GB)
            cost.addInfoParam("Constuction max peak [GB]",      constructionMaxPeak_GB)
        
        
        # Preparation phase
        preparationPhase = self._wpad.getPhaseData_Preparation()
        
        if preparationPhase.anyMeasurements():
            
            preparationAvgLeakage_GB = preparationPhase.RAM_usage.getLeakageAvg(True)
            preparationMaxPeak_GB = preparationPhase.RAM_usage.getPeakMax(True)
            
            RAM_leakage_GB += preparationAvgLeakage_GB
            RAM_maxPeak_GB = max([RAM_maxPeak_GB, preparationMaxPeak_GB])
            
            cost.addInfoParam("Preparation avg leakage [GB]",   preparationAvgLeakage_GB)
            cost.addInfoParam("Preparation max peak [GB]",      preparationMaxPeak_GB)
        
        
        # First exec phase
        firstExecPhase = self._wpad.getPhaseData_FirstExec()
        
        if firstExecPhase.anyMeasurements():
            
            firstExecAvgLeakage_GB = firstExecPhase.RAM_usage.getLeakageAvg(True)
            firstExecMaxPeak_GB = firstExecPhase.RAM_usage.getPeakMax(True)
            
            RAM_leakage_GB += firstExecAvgLeakage_GB
            RAM_maxPeak_GB = max([RAM_maxPeak_GB, firstExecMaxPeak_GB])
            
            cost.addInfoParam("First exec. avg leakage [GB]",    firstExecAvgLeakage_GB)
            cost.addInfoParam("First exec. max peak [GB]",       firstExecMaxPeak_GB)
        
        
        # Secondary exec phase
        secondaryExecPhase = self._wpad.getPhaseData_SecondaryExec()
        
        if secondaryExecPhase.anyMeasurements():
            
            secondaryExecAvgLeakage_GB = secondaryExecPhase.RAM_usage.getLeakageAvg(True)
            secondaryExecMaxPeak_GB = firstExecPhase.RAM_usage.getPeakMax(True)
            
            RAM_leakage_GB += (secondaryExecAvgLeakage_GB * (ResourcesCost_Cls.framesProcessedQuantityPredetermined - 1))
            RAM_maxPeak_GB = max([RAM_maxPeak_GB, secondaryExecMaxPeak_GB])
            
            cost.addInfoParam("Secondary exec. avg leakage [GB]",    secondaryExecAvgLeakage_GB)
            cost.addInfoParam("Secondary exec. max peak [GB]",       secondaryExecMaxPeak_GB)
        
        else:
            cost.addInfoParam("Secondary exec. avg leakage [GB]",    "Not available!")
            cost.addInfoParam("Secondary exec. max peak [GB]",    "Not available!")
            
            return cost  # cost is by default set as not available
        
        
        #############################################
        # Process measurement data
        #############################################
        RAM_leakage_GB
        RAM_maxPeak_GB
        
        
        #############################################
        # Calculate expectations
        #############################################
        
        # RAM leakage
        RAM_leakage_totalSpace_GB   =  ResourcesCost_Cls.RAM_availability_GB * (ResourcesCost_Cls.RAM_maxLeakage_perc / 100)
        RAM_leakage_workerSpace_GB  =  RAM_leakage_totalSpace_GB * self._reductionFactor # Reduction to give a room for other workers in sequence
        
        RAM_leakage_GB_expected  = RAM_leakage_workerSpace_GB * (ResourcesCost_Cls.RAM_leakageExpected_perc / 100)
        
        
        # RAM peak
        RAM_peak_workerSpace_GB = ResourcesCost_Cls.RAM_availability_GB - RAM_leakage_totalSpace_GB
        RAM_peak_GB_expected = RAM_peak_workerSpace_GB * (ResourcesCost_Cls.RAM_maxPeakExpected_perc / 100)
        
        
        #############################################
        # Calculate cost
        #############################################
        
        # RAM leakage
        ramLeakageCost = _LeafCost_Cls()
        ramLeakage_evaluationResult = self._resourcesCostCalculator._getCost_rangedTangens(RAM_leakage_GB, RAM_leakage_workerSpace_GB, RAM_leakage_GB_expected)
        ramLeakageCost.setVal(ramLeakage_evaluationResult)
        
        cost.addCost("RAM leakage", ramLeakageCost)
        
        
        # RAM peak
        ramPeakCost = _LeafCost_Cls()
        ramPeak_evaluationResult = self._resourcesCostCalculator._getCost_rangedTangens(RAM_maxPeak_GB, RAM_peak_workerSpace_GB, RAM_peak_GB_expected)
        ramPeakCost.setVal(ramPeak_evaluationResult)
        
        cost.addCost("RAM peak", ramPeakCost)
            
        
        
        #############################################
        # Log rest info params
        #############################################
        
        ramLeakageCost.addInfoParam("RAM leakage expected [GB]", RAM_leakage_GB_expected)
        ramLeakageCost.addInfoParam("RAM leakage simulated [GB]", RAM_leakage_GB)
        ramLeakageCost.addInfoParam("RAM leakage max [GB]", RAM_leakage_workerSpace_GB)
        
        ramPeakCost.addInfoParam("RAM peak expected [GB]", RAM_peak_GB_expected)
        ramPeakCost.addInfoParam("RAM peak [GB]", RAM_maxPeak_GB)
        ramPeakCost.addInfoParam("RAM peak max [GB]", RAM_peak_workerSpace_GB)
        
        
        return cost
        
    
    def getWorkerGenericTypeName(self):
        return self._workerGenericTypeName
    
    
    def getCost(self):
        return self._cost
    

    def __repr__(self):
        return str(self)


    def __str__(self):
        return self.toStr()
    
    
    def toStrLines(self, infoThreshold = True, workerJobHeader = False):
        output_list = []
        
        if workerJobHeader:
            output_list.append("Worker job:  " + self._workerGenericTypeName)
        
        cost = self.getCost()
        
        output_list.append(" -> Total resources cost:  " + str(cost.getValInStr()))
        output_list.append("")
        output_list.extend(cost.costToStringLines(addInfo = infoThreshold))
        
        return output_list

    def toStr(self, infoThreshold = True, workerJobHeader = False):
        
        return "\n".join(self.toStrLines(infoThreshold, workerJobHeader))




if __name__ == "__main__":
    
    import argparse
    from PerformanceAnalysis.WorkersPerformanceAnalyzer import WorkersPerformanceAnalysisData_Cls
    
    argsParser = argparse.ArgumentParser("The interface to analyse resporces cost of workers performance analysis data file dump")
    
    argsParser.add_argument(
        "i",
        type=str,
        default=None,
        help="Input file containing workers performance data dumped. It is performed by method WorkersPerformanceAnalysisData_Cls.dumpToFile()"
        )
    
    argsParser.add_argument(
        "-p",
        default=False,
        action="store_true",
        help="Additional print of workers performance data loaded from the file"
        )

    args = argsParser.parse_args()
    
    path_ = args.i
    
    wspad = WorkersPerformanceAnalysisData_Cls()
    wspad.importFromFile(filePath = path_)
    
    if args.p:
        print(wspad.getWorkersPerformanceDataString())
    
    wpads_dict = wspad.getWorkersPerformanceDataDict()
    
    for workerName in sorted(wpads_dict):
            
        workerPerformanceData = wpads_dict[workerName]
        
        resourcesCost = ResourcesCost_Cls(workerPerformanceData)
        
        print("Worker: " + str(workerName))
        print(resourcesCost.toStr(6))
        print()





















