'''
Created on Nov 5, 2022

@author: piotr
'''
from ContentRecognizer.ContentRecognizer import ContentRecognizer_AbstCls
from ObjectsDetectable.ClassesCfg import LicensePlateID
from ContentRecognizer.Recognition import RecognizedPlateNumbers_Cls




class LicensePlateRecognizer_AbstCls(ContentRecognizer_AbstCls):

    @staticmethod
    def getClassesServiced():
        return set({LicensePlateID})
    
    def __init__(self):
        ContentRecognizer_AbstCls.__init__(self, RecognizedPlateNumbers_Cls)




