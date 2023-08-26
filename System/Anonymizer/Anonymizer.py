'''
Created on 16 sty 2021

Anonymizer is the worker that takes image and detections and modifies image contents to anonymize detected areas 
 
@author: piotr
'''
from PolymorphicBases.Worker import Worker_AbstCls
from SpaceSpecificProcessor._2D.ArrayProcessor import ArraySpecificProcessor_Cls
from Space._2D_p_time.Frame import Frame_Cls
from Space._2D.Image import Image_Cls, RAM_Image_Cls
from PolymorphicBases.ABC import final, abstractmethod
from PerformanceAnalysis.WorkersPerformanceLogger import workersPerformanceLoggerObj
import numpy as np
#from _otherTools.NpArrayViewer import viewer



class Anonymizer_AbstCls(Worker_AbstCls):
    
    @final
    @staticmethod
    def getWorkerGenericName():
        return "Anonymizer"
    
    @staticmethod
    def getJobName():
        return "Annonymization"
    
    
    def __init__(self, usesStaticAnonymizedViewAsInputForSwap_flag = False):
        
        assert type(self) != Anonymizer_AbstCls
        self._asp = ArraySpecificProcessor_Cls()
        self._anonymizableClasses = self.getClassesServiced_resolved()
        self._usesStaticAnonymizedViewAsInputForSwap_flag = usesStaticAnonymizedViewAsInputForSwap_flag
    
    
    @final
    def anonymize(self, image, detections):
        
        if detections:
            
            with workersPerformanceLoggerObj.startContext_executuion(self):
            
                newImage_flag = False
                
                nparray = image.getNpArrayCopy()
                
                ram_image = RAM_Image_Cls(numpyArray = nparray, originFilePath = image.getOriginFilePath())
                
                swapAnonymization_detectionsMap, nonSwapAnonymization_detectionsMap = \
                    detections.getPair_anonymizationWithSwapDetections_and_restOfDetections()
                
                if nonSwapAnonymization_detectionsMap:
                    
                    ret = self._anonymize(nparray, nonSwapAnonymization_detectionsMap) 
                    
                    if ret.__class__ != str or ret != "Failed":
                        newImage_flag = True
                        nparray = ret
                
                if swapAnonymization_detectionsMap:
                    
                    ret = self._anonymizeBySwap(nparray, swapAnonymization_detectionsMap) # shall take nparray and detectionsMap and return new modified nparray or "Failed"
                    
                    if ret.__class__ != str or ret != "Failed":
                        newImage_flag = True
                        nparray = ret
                
                if newImage_flag:
                    #viewer.saveWithID(nparray, "nparray")
                    assert isinstance(ret, np.ndarray)
                    ram_image.updateArray(ret)
                    image = ram_image
                    #viewer.saveWithID(ret, "ret")
        
        assert isinstance(image, Image_Cls) or isinstance(image, Frame_Cls)
        
        return image
        
    
    def _anonymizeBySwap(self, image, detections):
        """
        This function shall return modified nparray. In-place operation; Definition non necessary
        Returning "Failed" means operation not performed so callers can skip adaptation to non-existing change
        """
        
        raise NotImplementedError()
    
    
    @abstractmethod
    def _anonymize(self, nparray, detections):
        """
        This function shall return modified nparray. In-place operation
        Returning "Failed" means operation not performed so callers can skip adaptation to non-existing change
        """
        
        raise NotImplementedError()
           
    
    @final
    def prepareObjectsForAnonymization(self, objectFound):
        
        self._prepareObjectsForAnonymization(objectFound)
    
    
    def _prepareObjectsForAnonymization(self, objectFound):
        pass
    
    
    def _confirmObjectView(self, objectView):
        
        objectView
        
        return True # stubbed
    
    
    
