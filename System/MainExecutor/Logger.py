'''
Created on Mar 4, 2023

@author: piotr
'''
import sys


switch_ = None
toFlush_strings = []


class StdFileWrapper_AbstCls():
    
    def __init__(self, filePath):
        self.filePath = filePath
        self.filePath_str = str(self.filePath)
    
    def flush(self): # python related flush
        pass

    def flushToFile(self, message):
        
        global toFlush_strings
                
        with open(self.filePath, "a") as file:
            file.write(message)
        
    def write(self, message):  
        
        global toFlush_strings, switch_
              
        self.std.write(message)
        
        if switch_ is not self:
            self.flushToFile(message)


class StdOutWrapper_Cls(StdFileWrapper_AbstCls):
    
    def start(self):
        
        if isinstance(sys.stdout, StdFileWrapper_AbstCls):
            self.nestedStart = True
        else:
            self.nestedStart = False
            self.std = sys.stdout
            sys.stdout = self
        
    def stop(self):
        
        if not self.nestedStart:
            sys.stdout = self.std
        
    def fileno(self):
        return 1


class StdErrWrapper_Cls(StdFileWrapper_AbstCls):
    
    def start(self):
        self.std = sys.stderr
        sys.stderr = self
        
    def stop(self):
        sys.stderr = self.std
        
    def fileno(self):
        return 2


class Logger_Cls(object):
    
    def __init__(self, filePath):
        self.filePath = filePath
        self.stdout = StdOutWrapper_Cls(self.filePath)
        self.stderr = StdErrWrapper_Cls(self.filePath)
        
    def getFilePath(self):
        return str(self.filePath)
    
    def flush(self):
        self.stdout.flushToFile()
        self.stdout.flushToFile()
        
    def redirect(self):
        self.stdout.start()
        self.stderr.start()
        
    def revertRedirection(self):
        self.stdout.stop()
        self.stderr.stop()





