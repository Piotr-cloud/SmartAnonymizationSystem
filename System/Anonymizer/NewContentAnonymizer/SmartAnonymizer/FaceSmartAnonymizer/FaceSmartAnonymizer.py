'''
Created on 26 sty 2021

@author: piotr
'''
from ObjectsDetectable.Classes import FaceID
from Anonymizer.NewContentAnonymizer.CustomAnonymizer import CustomAnonymizer_Cls


class FaceSmartAnonymizer_AbstCls(CustomAnonymizer_Cls):
    
    @staticmethod
    def getClassesServiced():
        return {FaceID}
    
    def __init__(self, contentGenerator, contentSwapper):
        assert type(self) != FaceSmartAnonymizer_AbstCls
        CustomAnonymizer_Cls.__init__(self, contentGenerator, contentSwapper)
        
    @staticmethod
    def getLicense():
        pass

