'''
Created on Oct 29, 2022

@author: piotr
'''
from PolymorphicBases.ABC import Base_AbstCls
from ObjectsDetectable.ClassesCfg import LicensePlateID



class Recognition_AbstCls(Base_AbstCls):
    '''
    Product of Content Recognizer.
    Wraps recognition data
    '''

    def __init__(self, features):
        '''
        features shall be data or None - if no data available
        '''
        self._features = features
    
    
    def __bool__(self):
        return self._features is not None
        
    
    def getFeatures(self):
        return self._features




class RecognizedPlateNumbers_Cls(Recognition_AbstCls):
    
    def __init__(self, numbers):
            
        if not numbers:
            numbers = None
        
        assert isinstance(numbers, str) or numbers is None
        assert numbers is None or len(numbers) >= 1

        Recognition_AbstCls.__init__(self, numbers)




recognitionClasses_dict = {
    LicensePlateID : RecognizedPlateNumbers_Cls
    }





