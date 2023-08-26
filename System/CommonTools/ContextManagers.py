'''
Created on Nov 5, 2022

@author: piotr
'''
import sys
import os
from PolymorphicBases.ABC import Base_AbstCls
from pathlib import Path


class ContextManager_AbstCls(Base_AbstCls): pass



class PrintingDisabler_Cls(ContextManager_AbstCls):

    def __enter__(self):
        
        self._print_cfg = sys.stdout,sys.stderr, os.environ['TF_CPP_MIN_LOG_LEVEL'] if 'TF_CPP_MIN_LOG_LEVEL' in os.environ else None
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        
        if self._print_cfg is not None:
            sys.stdout = self._print_cfg[0]
            sys.stderr = self._print_cfg[1]
            
            if self._print_cfg[2] is not None:
                os.environ['TF_CPP_MIN_LOG_LEVEL'] = self._print_cfg[2]
        
        if exc_type:
            return False
        else:
            return True



class WorkingDirectorySwitch_Cls(ContextManager_AbstCls):
    
    def __init__(self, contextWorkingDirectory):
        
        contextWorkingDirectory = Path(contextWorkingDirectory)
        assert contextWorkingDirectory.exists() and contextWorkingDirectory.is_dir()
        
        self._contextWorkingDirectory = str(contextWorkingDirectory)
        self._originWorkingDir = None
        
        
    def __enter__(self):
        self._originWorkingDir = os.getcwd()
        os.chdir(self._contextWorkingDirectory)
    
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        os.chdir(self._originWorkingDir)




if __name__ == "__main__":
    
    with PrintingDisabler_Cls():
        print("DSAD")
        raise
        


