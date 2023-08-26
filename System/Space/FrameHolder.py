'''
Created on Sep 23, 2021

@author: piotr
'''

from pathlib import Path
from PolymorphicBases.ABC import Base_AbstCls
import os


class FrameHolder_AbstCls(Base_AbstCls):
    
    nameSuffix = ""
    
    def __init__(self, originFilePath, name = None):
        
        assert type(self) != FrameHolder_AbstCls
        
        if originFilePath is not None:
            originFilePath = Path(originFilePath)
        
        if name is None:
            if originFilePath is not None:
                name = originFilePath.name
            else:
                name = "<unnamed>"
            
        self._originFilePath = originFilePath
        self._name = name
        
        
        
    def __str__(self):
        return type(self).__name__ + " named: " + self._name
    
    
    def __repr__(self):
        return str(self)
    
    def getName(self):
        return self._name
        
    def getOriginFilePath(self):
        return self._originFilePath
        
    
    def prepareDir(self, directory_):
        directory_ = Path(directory_)
        if not directory_.exists():
            os.makedirs(directory_)




if __name__ == "__main__":
    
    from NonPythonFiles.WorkersFiles.Anonymizers.AgentSmith import AgentSmithFace_path
    
    class FrameHolder_Test_Cls(FrameHolder_AbstCls):
        def __init__(self): FrameHolder_AbstCls.__init__(self)
        
    fh = FrameHolder_Test_Cls(AgentSmithFace_path)
    
    print(fh.getOriginFilePath())
    


