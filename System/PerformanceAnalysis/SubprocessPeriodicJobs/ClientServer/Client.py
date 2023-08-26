'''
Created on Feb 20, 2023

@author: piotr
'''

from PolymorphicBases.Decorators import singleton
from subprocess import Popen
import time
import sys

import socket
from socket import SHUT_RDWR

import inspect
from PerformanceAnalysis.SubprocessPeriodicJobs.ClientServer.server import Server_Cls, debug_clientServer_flag
import os
import json
from PerformanceAnalysis.SubprocessPeriodicJobs.ClientServer.subprocTerminationSync import monitorAndKill




@singleton
class Client_Cls():
    
    portsToUse = list(range(6000,6010))
    syncReceiveTimeout_ms = 3000
    
    def __init__(self):
        
        self.connection = None
        
        portsToUse = self.__class__.portsToUse
    
        socket_ = self._bindSocket(portsToUse)
        
        if not socket_:
            raise OSError("Cannot find non available port!\nPorts checked:" + "".join(["\n - " + str(port) for port in portsToUse]))
        
        self.socket = socket_
        
        self.socket.listen(5)
        
        if debug_clientServer_flag:
            print("Client port:  ", self.socket.getsockname()[1])
            print("Client pid:   ", os.getpid())
        
        self.runServer(socket_.getsockname()[1])
        
        self.socket.settimeout(3)
        self.connection, _ = self.socket.accept()
        
        self.connection.setblocking(0)
        
        self.runMonitorProcessMonitor()
        
        self.subJobClassName_2_clientJobTypeId_dict = {}
        
        self.jobInstance_2_clientJobId_dict = {} # Job class to job class Id recieved from server
    
    
    def __del__(self):
        
        self._closeServerProcess()
        
        self.serverProcess.kill()
        self.monitorProcess.kill()
    
            
    def _tryPort(self, portNr):
        
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_.bind((socket.gethostname(), portNr))
        except:
            socket_ = None
            
        return socket_
    
    
    def _bindSocket(self, ports):
        
        socket_ = None
        
        for port_candidate in ports:
            
            socket_ = self._tryPort(port_candidate)
            
            if socket_:
                break
        
        return socket_
    
    
    
    def _getSubprocessJobTypeId(self, subprocessJob):
        'Registers job if not available'
        
        classIdentificationDetails = self._getClassIdentificationDetails(subprocessJob.__class__)
        
        if classIdentificationDetails not in self.subJobClassName_2_clientJobTypeId_dict:
            raise RuntimeError("Cannot use job before it is registered")
        
        return self.subJobClassName_2_clientJobTypeId_dict[classIdentificationDetails]
    
    
    def _getJobInstanceId(self, subprocessJob, errorStatement):
        
        self._getSubprocessJobTypeId(subprocessJob) # check against registration
        
        if subprocessJob not in self.jobInstance_2_clientJobId_dict:
            raise RuntimeError(errorStatement)
        
        return self.jobInstance_2_clientJobId_dict[subprocessJob]
    
    
    def _getClassIdentificationDetails(self, subprocessJobCls):
        
        className = subprocessJobCls.__name__
        classModulePath = inspect.getfile(subprocessJobCls)
        
        return classModulePath, className
    
    
    def _registerJobType(self, classModulePath, className):
        self.send('Register: ' + classModulePath + "&" + className)
        jobTypeId = self.receive_Synchronous()
        return jobTypeId
    
    
    def register(self, subprocessJob):
        
        classIdentificationDetails = self._getClassIdentificationDetails(subprocessJob.__class__)
        
        if classIdentificationDetails not in self.subJobClassName_2_clientJobTypeId_dict:
            
            clientJobTypeId = self._registerJobType(*classIdentificationDetails)
            
            self.subJobClassName_2_clientJobTypeId_dict[classIdentificationDetails] = clientJobTypeId
            
    
    def start(self, subprocessJob):
            
        jobTypeId = self._getSubprocessJobTypeId(subprocessJob)
        
        if subprocessJob not in self.jobInstance_2_clientJobId_dict:
            
            instanceArgs = subprocessJob.client_getServerInstanceArgs()
            
            instanceArgsStrPart = "&".join([str(el) for el in instanceArgs])
            
            self.send('Start: ' + str(jobTypeId) + " " + instanceArgsStrPart)
            jobInstanceId = self.receive_Synchronous()
            
            self.jobInstance_2_clientJobId_dict[subprocessJob] = jobInstanceId
            
        return jobInstanceId
            

    def getResult(self, subprocessJob):
        
        jobInstanceId = self._getJobInstanceId(subprocessJob, "Cannot get result of job before it is started")
        
        self.send('Get result: ' + str(jobInstanceId))
        recievedMsg = self.receive_Synchronous()
        
        simpleOutputObj = json.loads(recievedMsg)
        
        result = subprocessJob.client_postProcessSimpleOutputObject(simpleOutputObj)
        
        return result
        

    def finish(self, subprocessJob):
        
        jobInstanceId = self._getJobInstanceId(subprocessJob, "Cannot finish job before it is started")
    
        self.send('Finish: ' + str(jobInstanceId))
        result = self.receive_Synchronous()
        
        assert result == 'ack'
        
        del self.jobInstance_2_clientJobId_dict[subprocessJob]
        
    
    def isConnected(self):
        
        return bool(self.connection)
        
        
    def receive_Synchronous(self):
        
        timeout = Timeout_Cls(self.__class__.syncReceiveTimeout_ms)
        
        while not timeout:
            
            if msg := self.receive_Asynchronous():
                return msg
        
        else:
            raise TimeoutError("Message from client was not recieved within: " + str(timeout.getTimeout_ms()) + " ms")
        
        
    def receive_Asynchronous(self):
        try:
            msg = self.connection.recv(1024).decode("utf-8")
            if msg:
                if debug_clientServer_flag:
                        print("-> Client:   \"" + str(msg) + "\"")
                return msg
            else:
                return None
            
        except Exception as exception:
            exception # unused
            #print(exception)
            return None
    
    
    def _closeServerProcess(self):
        
        if self.isConnected():
            
            if debug_clientServer_flag:
                print("Closing from Client")
            
            self.send('close')
            self.connection.shutdown(SHUT_RDWR)
            self.connection.close()
            self.connection = None
    
    
    def runMonitorProcessMonitor(self):
        
        subProc_pid = self.serverProcess.pid
        superProc_pid = os.getpid()
        
        monitorScript_path = inspect.getfile(monitorAndKill)
        
        args = [sys.executable, monitorScript_path, superProc_pid, subProc_pid]
        
        self.monitorProcess = Popen([str(arg) for arg in args])
        
    
    def runServer(self, socket_port):
        
        serverStartScript_path = inspect.getfile(Server_Cls)
        
        args = [sys.executable, serverStartScript_path, socket_port]
        
        self.serverProcess = Popen([str(arg) for arg in args])

    
    def send(self, msg = 'message example'):
        if debug_clientServer_flag:
            print("Client ->    \"" + str(msg) + "\"")
        self.connection.send(msg.encode('utf-8'))



class Timeout_Cls():
    
    def __init__(self, time_ms):
        self.timeout_ms = time_ms
        if self.timeout_ms is not None:
            self.endTime_s = time.time() + time_ms / 1000.
    
    def __bool__(self):
        if self.timeout_ms is not None:
            return time.time() > self.endTime_s
        else:
            return False
    
    def getTimeout_ms(self):
        return self.timeout_ms




if __name__ in ["__main__"]:
    
    # To test interaction between Client and server set the following flag in Server.py files to True: debug_clientServer_flag
    client = Client_Cls()
    
    time.sleep(.2)
    
    for i in range(1, 5):
        client.send("message: " + str(i))
        time.sleep(.5)
        
    