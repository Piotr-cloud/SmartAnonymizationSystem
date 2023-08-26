'''
Created on Mar 10, 2023

@author: piotr

When host process is killed suddenly or it's desctuction sequene is broken(for ex. tkinter creation) this file detects host process termination and kills related subprocess

Operating system reason

'''
import time
import psutil
import sys


period_s = 2


def monitorAndKill(superProc_pid, subProc_pid):
    
    superProc_pid = int(superProc_pid)
    subProc_pid = int(subProc_pid)
    
    while True:
        
        if not psutil.pid_exists(superProc_pid):
            
            if psutil.pid_exists(subProc_pid):
                
                subProc = psutil.Process(subProc_pid)
                subProc.kill()
            
            break
        
        time.sleep(period_s)



if __name__ == "__main__":
    
    # This is not a test code - this is process start point. File name starts with lowercase letter
    
    monitorAndKill(sys.argv[1], sys.argv[2])





