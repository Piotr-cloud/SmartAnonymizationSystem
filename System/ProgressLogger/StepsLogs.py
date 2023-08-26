'''
Created on Dec 13, 2021

@author: piotr
'''




class StepsLogs_Cls():
    
    joinPathsSpecialSign = "/"
    repetitionsKey = 0
    grossTimeKey = 1
    netTimeKey = 2
    paramsKey = -1
    
    stepNameLineToTimeData_printingDistance = 78
    
    occurrenceTimeDivisionSplitSigns = " " * 3
    
    def __init__(self):
        
        self.processingParams_dict = {}
        self.processingParams_list = []
        
        self.baseSteps = []
    
    
    def addBaseStep(self, baseStep):
        self.baseSteps.append(baseStep)
        
    
    def iterSteps(self):
        
        for baseStep in self.baseSteps:
            yield from self._iterStep(baseStep)
        
    
    def _iterStep(self, step):
        
        yield step
        
        for subStep in step.getSubSteps():
            yield from self._iterStep(subStep)
                                       
        
    def addStepTimeConsumption_notInUse(self, stepName, stepDuration):
        
        if stepName not in self.stepDuration_dict:
            self.stepDuration_dict[stepName] = [stepDuration, 1] # total duration, number of steps repetitions executed
            self.stepsAdditionOrder_list.append(stepName)
        
        else:
            self.stepDuration_dict[stepName][0] += stepDuration
            self.stepDuration_dict[stepName][1] += 1
    
    
    def addProcessingParam(self, paramName, processedUnitsQuantity):
        
        if paramName not in self.processingParams_dict:
            self.processingParams_dict[paramName] = processedUnitsQuantity
            self.processingParams_list.append(paramName)
            
        else:
            self.processingParams_dict[paramName] += processedUnitsQuantity
    
    
    def _sumStatisticsData(self, first, second):
        
        firstParamsDict = first[2]
        secondParamsDict = second[2]
        
        resultParams_dict = firstParamsDict.copy()
            
        
        # increment number of repetitinos
        if not StepsLogs_Cls.repetitionsKey in resultParams_dict:
            resultParams_dict[StepsLogs_Cls.repetitionsKey] = 2
        else:
            resultParams_dict[StepsLogs_Cls.repetitionsKey] += 1
        
        for paramName in secondParamsDict:
            
            if isinstance(paramName, str): # sum only string instances - other types are reserved for special params
                    
                if paramName not in resultParams_dict:
                    resultParams_dict[paramName] = secondParamsDict[paramName]
                    
                else:
                    resultParams_dict[paramName] += secondParamsDict[paramName]
                
        
        grossTime = first[0] + second[0]
        netTime = first[1] + second[1]
        
            
        return grossTime, netTime, resultParams_dict
    
    
    def _getStepsPath(self, step):
        
        stepSubSteps = step.getSubSteps()
        
        stepName = step.getName()
                
        output_dict = {}
        
        output_dict[stepName] = step.getStatsticsData()
        
        if stepSubSteps:
            
            for subStep in stepSubSteps:
                
                subSteps_dict = self._getStepsPath(subStep) 
                
                for subStepsPath in list(subSteps_dict):
                    
                    new_subStepsPath = StepsLogs_Cls.joinPathsSpecialSign.join([stepName, subStepsPath])
                    
                    if new_subStepsPath not in output_dict:
                        output_dict[new_subStepsPath] = subSteps_dict[subStepsPath]
                    
                    else:
                        output_dict[new_subStepsPath] = self._sumStatisticsData(output_dict[new_subStepsPath], subSteps_dict[subStepsPath])
        
        return output_dict
    
    
    def _reformStepsStatisticsData(self, stepDict):
        
        output_dict = {}
        
        for stepsPath in stepDict:
            stepPathParams = stepDict[stepsPath]
            
            stepPathParams_dict = stepPathParams[2]
            stepPathParams_dict[StepsLogs_Cls.grossTimeKey] = stepPathParams[0]
            stepPathParams_dict[StepsLogs_Cls.netTimeKey] = stepPathParams[1]
            
            stepsNames_list = stepsPath.split(StepsLogs_Cls.joinPathsSpecialSign)
            
            part_output_dict = output_dict
            
            for stepName in stepsNames_list:
                
                if not stepName in part_output_dict:
                    part_output_dict[stepName] = {}
                    
                part_output_dict = part_output_dict[stepName]
            
            part_output_dict[StepsLogs_Cls.paramsKey] = stepPathParams_dict
        
        return output_dict
    
    
    def _getBaseStepDict(self, baseStep):
        
        stepDict = self._getStepsPath(baseStep)
        
        # overwrite base step params dict with total performance results
        baseStepName = baseStep.getName()
        baseStepParams = stepDict[baseStepName][2]
        
        
        for path_ in stepDict:
            params = stepDict[path_][2]
            
            for paramName in params:
                if isinstance(paramName, str):
                    if paramName not in baseStepParams:
                        baseStepParams[paramName] = params[paramName]
                    else:
                        baseStepParams[paramName] += params[paramName]
        
        
        return self._reformStepsStatisticsData(stepDict)
    
    
    def _formatTime(self, time_s_float):
        return "{:.3f} s".format(time_s_float)
    
    
    def _getGrossAndNetTimeStatement(self, grossTime, netTime):
        
        if grossTime != netTime:
            
            differenceTime = grossTime - netTime
            
            timeData_dict = {
                "g":self._formatTime(grossTime),
                "n":self._formatTime(netTime),
                "d":self._formatTime(differenceTime),
                }
            
            output_strings_list =  []  # "g: " + self._formatTime(grossTime) + "  n: " + self._formatTime(netTime) + "  d: " + self._formatTime(differenceTime)
            
            for timeParamLetter in timeData_dict:
                output_strings_list.append(timeParamLetter + ":" + timeData_dict[timeParamLetter])
            
            output_string = (" " * 2).join(output_strings_list)
        
        else:
            output_string = self._formatTime(grossTime)
            
        return output_string
    
    
    def _getSpecialParamsStatement(self, stepSpecification, totalGrossTime):
        
            
        splitSigns = StepsLogs_Cls.occurrenceTimeDivisionSplitSigns
        
        grossTime = stepSpecification[StepsLogs_Cls.grossTimeKey]
        netTime = stepSpecification[StepsLogs_Cls.netTimeKey]
        
        percentage = "{:.2f}%".format((grossTime / totalGrossTime) * 100)
        
        output_string = ("Time (" + percentage + "):").ljust(14) + splitSigns
        
        output_string += self._getGrossAndNetTimeStatement(grossTime, netTime)
        
        if StepsLogs_Cls.repetitionsKey in stepSpecification:
            
            occurrences = stepSpecification[StepsLogs_Cls.repetitionsKey]
            
            grossTime_perExeution = grossTime / occurrences
            netTime_perExeution = netTime / occurrences
            
            output_string += splitSigns + "/" + splitSigns + str(occurrences) + " occurrences" + \
                splitSigns + "=" + splitSigns + self._getGrossAndNetTimeStatement(grossTime_perExeution, netTime_perExeution)
        
        return output_string
        
        
    def _getStepStatisticsDataStatementLines(self, stepName, stepDict, indent = "", totalGrossTime = None):
        
        output_lines_list = []
        
        stepSpecification = stepDict[stepName]
        stepParams = stepSpecification[StepsLogs_Cls.paramsKey]
        
        if totalGrossTime is None:
            totalGrossTime = stepParams[StepsLogs_Cls.grossTimeKey]
        
        output_lines_list.append(indent + " - " + (stepName).ljust(StepsLogs_Cls.stepNameLineToTimeData_printingDistance) + " " *5  + self._getSpecialParamsStatement(stepParams, totalGrossTime))
        
        # get rest params statement
        params_parts = []
        
        for stepParamKey in stepParams:
            if isinstance(stepParamKey, str):
                params_parts.append(indent + " " * 7 + " -> " + stepParamKey + ": " + str(stepParams[stepParamKey]))
        
        if params_parts:
            output_lines_list.extend(params_parts)
            if output_lines_list[-1] != "":
                output_lines_list.append("")
                #output_lines_list.append("params_parts")
            # add new line
        
        prev_substepIsToBeGrouped_flag = True
        
        anySubStepAdded_flag = False
        
        for subStepName in stepDict[stepName]:
            
            if isinstance(subStepName, str):
                subStepLines_list = self._getStepStatisticsDataStatementLines(subStepName, stepDict[stepName], " " * 3 + indent, totalGrossTime)
                
                if not anySubStepAdded_flag:
                    if output_lines_list[-1] != "":
                        output_lines_list.append("")
                        #output_lines_list.append("anySubStep")
                    anySubStepAdded_flag = True
                
                substepIsToBeGrouped_flag = len(subStepLines_list) <= 1
                
                if not prev_substepIsToBeGrouped_flag or not substepIsToBeGrouped_flag:
                    if output_lines_list[-1] != "":
                        output_lines_list.append("")
                        #output_lines_list.append("prev_substep")
                    
                output_lines_list.extend(subStepLines_list)
                
                prev_substepIsToBeGrouped_flag = substepIsToBeGrouped_flag
        
        if len(output_lines_list) > 1:
            if output_lines_list[-1] != "":
                output_lines_list.append("")
                #output_lines_list.append("leaving more lines")
            
        return output_lines_list
        
    
    def _getTimeConsumptionStatementString_notInUse(self):
        
        if self.stepsAdditionOrder_list:
            # time consumption
            output_string = "Time consumption: \n"
            
            stringComponentsArray = []
            longestElements_list = None
            
            for stepName in self.stepsAdditionOrder_list:
                stepDuration, stepRepetitions = self.stepDuration_dict[stepName]
                
                row_data = [stepName + ":", "    total: ", " {:.3f} s".format(stepDuration), "  /  ", str(stepRepetitions), "  =  ", "{:.3f} ms".format((stepDuration * 1000) / stepRepetitions)]
                
                if longestElements_list is None:
                    longestElements_list = [len(element) for element in row_data]
                else:
                    for index in range(len(row_data)):
                        rowElement_length = len(row_data[index]) 
                        
                        if rowElement_length > longestElements_list[index]:
                            longestElements_list[index] = rowElement_length
                
                stringComponentsArray.append(row_data)
            
            
            for row_data in stringComponentsArray:
                output_string += "\n  "

                for elementIndex in range(len(row_data)):
                    
                    longestElement = longestElements_list[elementIndex]
                    
                    if elementIndex in [2,4,6]:
                        output_string += row_data[elementIndex].rjust(longestElement)
                    
                    else:
                        output_string += row_data[elementIndex].ljust(longestElement)
                        
        
        else:
            output_string = "  -> No time consumption data"
        
        return output_string
    
    
    def _getTimeConsumptionTreeStringLines(self):
        
        output_list = []
        
        for baseStep in self.baseSteps:
            
            baseStepDict = self._getBaseStepDict(baseStep)
            
            for baseStepAttributeKey in baseStepDict:
                
                if isinstance(baseStepAttributeKey, str):
                    baseStepLines = self._getStepStatisticsDataStatementLines(baseStepAttributeKey, baseStepDict)
                    
                    while baseStepLines[-1] == "": # remove empty lines
                        baseStepLines.pop()
                        
                    output_list.extend(baseStepLines)
                    
        return output_list
    
    
    def getTimeConsumptionTreeString(self, addHeader = True):
        
        output_str = ""
        
        if addHeader:
            output_str += "\nTime consumption tree:\n\n"
        
        output_str +=  "\n".join(self._getTimeConsumptionTreeStringLines())
        
        output_str += "\n"
            
        return output_str
    
    
    def __str__(self):
        return self.getTimeConsumptionTreeString()
            
















