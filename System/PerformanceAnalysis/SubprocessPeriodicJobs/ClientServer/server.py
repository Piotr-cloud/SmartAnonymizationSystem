


import sys
import time
import os
import socket
import re

import importlib.util
from pathlib import Path


debug_clientServer_flag = False


class Server_Cls():
    
    def __init__(self, socket_port):
        
        if debug_clientServer_flag:
            print("Server port:  ", socket_port)
            print("Server pid:   ", os.getpid())
        
        self.port = int(socket_port)
        
        self.basicPeriod_s = self.basicPeriod_ms() / 1000.
        assert self.basicPeriod_s > 0.
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostname(), self.port))
        self.socket.setblocking(0)
        
        self.jobClassName_2_jobTypeId_dict = {}
        self.jobTypeId_2_jobClass_dict = {}
        
        self.jobInstanceId_2_jobInstance = {}
        
        # Gauges servicing
        self.gauge_2_jobInstances_dict = {}
        self.jobInstance_2_gauges_dict = {}
        
        self.gaugeConstructionVars_2_gaugeConstructed_dict = {}
        self.gaugeConstructed_2_gaugeConstructionVars_dict = {}
        
        self.jobsTypesCnt = 0
        self.jobsInstancesCnt = 0
        
    
    
    def getOriginalGauge(self, jobInstance, gaugeCls, *args, **kw_args):
        
        dictPairs = []
        
        for key_ in sorted(kw_args):
            dictPairs.append((key_, kw_args[key_]))
        
        gaugeConstructionVars = (gaugeCls, args, tuple(dictPairs))
        
        # construct unique gauge
        if gaugeConstructionVars not in self.gaugeConstructionVars_2_gaugeConstructed_dict:
            gauge = gaugeCls(*args, **kw_args)
            self.gaugeConstructionVars_2_gaugeConstructed_dict[gaugeConstructionVars] = gauge
            
        else:
            gauge = self.gaugeConstructionVars_2_gaugeConstructed_dict[gaugeConstructionVars]

        
        # make linkage gauge <-> job instance
        if gauge not in self.gauge_2_jobInstances_dict:
            self.gauge_2_jobInstances_dict[gauge] = set()
            
        self.gauge_2_jobInstances_dict[gauge].add(jobInstance)

        
        if jobInstance not in self.jobInstance_2_gauges_dict:
            self.jobInstance_2_gauges_dict[jobInstance] = set()
        
        self.jobInstance_2_gauges_dict[jobInstance].add(gauge)
        
        
        return gauge
    
    
    def deregisterGauges(self, jobInstance):
        
        for gauge in self.jobInstance_2_gauges_dict[jobInstance]:
            
            self.gauge_2_jobInstances_dict[gauge].remove(jobInstance)
            
            if not self.gauge_2_jobInstances_dict[gauge]:
                del self.gauge_2_jobInstances_dict[gauge]
        
        del self.jobInstance_2_gauges_dict[jobInstance]
            
    
    
    @staticmethod
    def basicPeriod_ms():
        '''
        Period that server runs. Each periodic event communication is serviced and jobs are 
        allowed to be executed
        
        Modification of this value strongly impacts host CPU time of Server process and should be 
        done with respect to SubprcessPeriodicJob's periodicy, since suprocJobs might require more 
        precise base period
        '''
        return 1.
    
    
    def periodicEvent(self):
        
        self._periodicEvent_jobs()
    
    
    def _recieve(self):
        
        try:
            msg = self.socket.recv(1024)
            return msg
        except:
            return None
    
    
    def getSubprocessJobClass(self, classModulePath, className):

        classModulePath = str(classModulePath)
        className = str(className)
        
        spec = importlib.util.spec_from_file_location("classModulePath", classModulePath)
        
        module_ = importlib.util.module_from_spec(spec)
        
        spec.loader.exec_module(module_)
        
        try:
            cls = module_.__dict__[className]
            return cls
        
        except:
            raise ImportError("Cannot import variable: " + className + " from file: " + classModulePath)
    
    
    def getJobRegistered(self, jobInstanceId):
        return self._jobs_dict[jobInstanceId]
    
    
    
    def _periodicEvent_communication(self):
        
        msg = self._recieve()
        
        
        if msg:
            
            msg = msg.decode('utf-8')
            
            if debug_clientServer_flag:
                print("-> Server:   \"" + msg + "\"")
            
            if msg == 'close':
                
                return 'break'
                
            
            elif match_ := re.findall('^Get result: (\d+)', msg):
                
                jobInstanceId = int(match_[0])
                
                result = self.getJobResult(jobInstanceId)
                
                self.sendResponse(result)
            
            
            elif match_ := re.findall('^Start: (\d+) (.*)', msg):
                
                jobTypeId = int(match_[0][0])
                instanceArgsStrPart  = match_[0][1] 
                
                instanceArgs = instanceArgsStrPart.split("&")
                
                newJobId = self.startJob(jobTypeId, instanceArgs)
                
                self.sendResponse(newJobId)
                
            
            elif match_ := re.findall('^Finish: (\d+)', msg):
                
                jobInstanceId = int(match_[0])
                
                self.finishJob(jobInstanceId)
                
                self.sendResponse('ack')
                
            
            elif match_ := re.findall('^Register: (\/.*?\.[\w:]+)\&(\w+)', msg):
                
                classModulePath, className = match_[0]
                
                jobTypeId = self.registerJob(classModulePath, className)
                
                self.sendResponse(jobTypeId)
    
    
    def _periodicEvent_jobs(self):
        
        # jobs
        for jobInstance in  self.jobInstanceId_2_jobInstance.values():
            jobInstance.server_periodicExec()
    
        
    def runScheduler(self):
        
        self.setPeriodReference()
        
        while True:
            
            if self._periodicEvent_communication() == 'break' :
                break
            
            self._periodicEvent_jobs()
            
            # set gauges "to refresh" to get fresh data just after waiting time
            for gauge in self.gauge_2_jobInstances_dict:
                gauge.setToRefresh()
                
            self.waitForNextPeriod()
    
    
    def setPeriodReference(self):
        self.startTime_s = self.getTime_s()
    
    
    def waitForNextPeriod(self):
        
        currentTime_s = self.getTime_s()
        
        overtake_s = abs((currentTime_s - self.startTime_s) % self.basicPeriod_s)
            
        remainig_s = self.basicPeriod_s - overtake_s
        
        if remainig_s > 0:
            if remainig_s > self.basicPeriod_s:
                self.wait(self.basicPeriod_s)
            else:
                self.wait(remainig_s)
    
    
    def wait(self, time_s):
        time.sleep(time_s)
    
    
    def getTime_s(self):
        return time.time()
    
    
    def registerJob(self, classModulePath, className):
        
        classIdentificationDetails = (classModulePath, className)
        
        if classIdentificationDetails not in self.jobClassName_2_jobTypeId_dict:
            
            jobTypeId = self.jobsTypesCnt
            self.jobClassName_2_jobTypeId_dict[classIdentificationDetails] = jobTypeId
            self.jobTypeId_2_jobClass_dict[jobTypeId] = self.getSubprocessJobClass(*classIdentificationDetails)
            self.jobsTypesCnt += 1

        jobTypeId = self.jobClassName_2_jobTypeId_dict[classIdentificationDetails]
        
        return jobTypeId
        
    
    def startJob(self, jobTypeId, instanceArgs):
        
        jobInstanceId = self.jobsInstancesCnt
        
        jobClass = self.jobTypeId_2_jobClass_dict[jobTypeId]

        jobClass.server_setServerSide()
        jobInstance = jobClass()
        jobInstance.server_linkTheServer(self)
        jobInstance.server__init__(instanceArgs)
        
        self.jobInstanceId_2_jobInstance[jobInstanceId] = jobInstance
        self.jobsInstancesCnt += 1
        
        return jobInstanceId
    
    
    def getJobResult(self, jobInstanceId):
        
        try:
            jobInstance = self.jobInstanceId_2_jobInstance[jobInstanceId]
        except:
            jobInstance = self.jobInstanceId_2_jobInstance[jobInstanceId]
        
        return jobInstance.server_getSimpleOutputObject()
    
    
    def finishJob(self, jobInstanceId):
        jobInstance = self.jobInstanceId_2_jobInstance[jobInstanceId]
        self.deregisterGauges(jobInstance)
        del self.jobInstanceId_2_jobInstance[jobInstanceId]
    
    
    def sendResponse(self, response):
        response = str(response)
        if debug_clientServer_flag:
            print("Server ->    \"" + response + "\"")
        self.socket.send(response.encode('utf-8'))
    
    
    def performOperation(self, input_):
        try: 
            input_ = int(input_)
            return input_ + 1
        except:
            return str(input_) + " modified" 
        

       




if __name__ == "__main__":
    
    # This is not a test code - this is process start point. File name starts with lowercase letter
    
    sys.path.append(str(Path(__file__).parent.parent.parent.parent))
    
    if debug_clientServer_flag:
        print("Server started with args: ", str(sys.argv))
    
    socket_port = sys.argv[1]
    
    server = Server_Cls(socket_port)
    server.runScheduler()






