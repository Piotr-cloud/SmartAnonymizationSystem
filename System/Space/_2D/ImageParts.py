'''
Created on Jan 27, 2022

@author: piotr
'''
from Space._2D.Array import Array_AbstCls



class ImagePart_Cls(Array_AbstCls):
    
    def __init__(self, nparray):
        
        Array_AbstCls.__init__(self, nparray)

    def getName(self):
        return "Part, id: " + str(id(self))

