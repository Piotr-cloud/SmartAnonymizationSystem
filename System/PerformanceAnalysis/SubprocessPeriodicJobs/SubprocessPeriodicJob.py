'''
Created on Feb 23, 2023

@author: piotr
'''

from abc import abstractmethod
import time
from PolymorphicBases.ABC import final, Base_AbstCls
import json


def importClientCls():
    
    varName = " client "
    try:
        return globals()[varName]
    except:
        from PerformanceAnalysis.SubprocessPeriodicJobs.ClientServer.Client import Client_Cls
        globals()[varName] = Client_Cls
        return globals()[varName]
        
    


class SubprocessJob_AbstCls(Base_AbstCls):
    """
    
    Subprocess is initialized by user by creation of this object

    Construction sequence triggered by the user:
    
       User -> This object(client side) -> Client -> Server -> This Object(server side) -> Subprocess
    
    Any subclass shall be defined in this file
     
    """
    
    jobPeriod_ms = 5
    issuedClasses_set = set()
    serverSide = False
    
    ######################################################################
    # user methods
    ######################################################################
    def __init__(self):
        
        self.serverSide_flag = self.__class__.serverSide 
        
        if not self.serverSide_flag:
            clientCls = importClientCls()
            self.clientObj = clientCls() # Client_Cls is anyway a singleton
            self.clientObj.register(self)
            self.jobId = None
            self.isFinished = False
        else:
            self.jobPeriod_s = self.__class__.jobPeriod_ms / 1000
            self.cnt = 0
            self.issue_flag = False
            self.server = None
    
    @final
    def start(self):
        return self.clientObj.start(self)


    @final
    def getResult(self):
        return self.clientObj.getResult(self)


    @final
    def finish(self):
        ret = self.clientObj.finish(self)
        self.isFinished = True
        return ret
    
    ######################################################################
    # configuration methods
    ######################################################################
    @final
    def getJobPeriod_ms(self):
        jobPeriod_ms = self._getJobPeriod_ms()
        assert isinstance(jobPeriod_ms, int), "" 
    
    
    def _getJobPeriod_ms(self):
        return 5
    
    ######################################################################
    # destructor
    ######################################################################
    def __del__(self):
        
        if not self.serverSide_flag:
            if self.isFinished is not True:
                self.finish()
            
    ######################################################################
    # client side methods
    ######################################################################
    @abstractmethod
    def client_getServerInstanceArgs(self):
        pass

    @final
    def client_postProcessSimpleOutputObject(self, simpleOutputObject):
        
        if simpleOutputObject != "None":
            return self._client_postProcessSimpleOutputObject(simpleOutputObject)
        else:
            return None
    
    
    def _client_postProcessSimpleOutputObject(self, simpleOutputObject):
        "so called 'simple output object' (word: 'simple' refers to type and nested types) can be converted to any oher complexed form that is not serializable by json"
        return simpleOutputObject
    
    
    ######################################################################
    # server side methods
    ######################################################################
    @classmethod
    def server_setServerSide(cls):
        ''''
        Called on server side - Do not call anywhere else !
        Changes instances initialization procedure
        '''
        cls.serverSide = True
    
    
    @final
    def server_getOriginalGauge(self, gaugeCls, *args, **kw_args):
        gauge = self.server.getOriginalGauge(self, gaugeCls, *args, **kw_args)
        gauge.setToRefresh()
        return gauge
        
        
    @final
    def server_linkTheServer(self, server):
        
        assert self.server is None
        self.server = server
        
    
    @final
    def server_markExecIssue(self):
        cls = self.__class__
        
        if cls not in SubprocessJob_AbstCls.issuedClasses_set:
            SubprocessJob_AbstCls.issuedClasses_set.add(cls)
            print("Issue with subprocess job: " + cls.__name__)
            
        self.issue_flag = True
    
    
    @final
    def server_checkIfTimeToPerform(self):
        
        currentTime = time.time()
        
        if self.cnt == 0:
            
            self.startTime = currentTime
            return True
        
        else:
            newCnt = (currentTime - self.startTime) % self.jobPeriod_s
            
            if newCnt > self.cnt:
                self.cnt = newCnt
                return True
            else:
                return False
            
    
    @abstractmethod
    def server__init__(self, *argsForServerJob_listOfStrings):
        pass
    
    
    @final
    def server_getSimpleOutputObject(self):
        
        if self.issue_flag is False:
            self.server_additionalExecAtGetResult()
            objToSerialize = self._server_getSimpleOutputObject() 
            return json.dumps(objToSerialize)
        else: return None
    
    
    @final
    def server_additionalExecAtGetResult(self):
        
        if self.issue_flag is False:
            self._server_additionalExecAtGetResult()
    
    
    @abstractmethod
    def _server_additionalExecAtGetResult(self):
        pass
    
    
    @final
    def server_periodicExec(self):
        
        if self.issue_flag is False:
            
            if self.server_checkIfTimeToPerform():
                self._server_periodicExec()
    
    
    @abstractmethod
    def _server_periodicExec(self):
        pass
    
    
    @abstractmethod
    def _server_getSimpleOutputObject(self):
        "Output object shall be json serializable - so called 'simple output object' (word: 'simple' refers to type and nested types)"
        pass












