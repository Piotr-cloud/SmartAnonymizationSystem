'''
Created on 24 sty 2021

@author: piotr
'''
from ContentGenerator.ContentGenerator import ContentGenerator_AbstCls
from ObjectsDetectable.Classes import FaceID
from PolymorphicBases.ABC import final


class FaceGenerator_AbstCls(ContentGenerator_AbstCls):
    """
    Face generator:
    1. takes person view
    2. detects face
    3. generates new face in person view
    
    Inner detector is necessary
    """
    
    @staticmethod
    def getJobName():
        return "Face generation"
    
    @final
    @staticmethod
    def getClassesServiced():
        return {FaceID}
    

    def __init__(self, recognizer = None):
        assert type(self) != FaceGenerator_AbstCls
        ContentGenerator_AbstCls.__init__(self, recognizer)



