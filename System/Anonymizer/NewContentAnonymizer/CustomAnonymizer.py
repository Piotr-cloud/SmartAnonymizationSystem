'''
Created on Feb 3, 2022

@author: piotr
'''

from Anonymizer.Anonymizer import Anonymizer_AbstCls
from ContentSwapper.ContentSwapper import ContentSwapper_AbstCls
from ContentGenerator.ContentGenerator import ContentGenerator_AbstCls
from View.View import View_Cls
from Configuration.ConfigurationObjects.WorkerConfiguration import ChoiceOf_WorkerConfigurationObject_Cls
from SW_Licensing.SW_License import HostSWLicense_Cls



class CustomAnonymizer_Cls(Anonymizer_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Custom anonymizer"
        
    @staticmethod
    def getDescription():
        return "Custom anonymizer defined by pair: content generator and content swapper"
        
    @staticmethod
    def getClassesServiced():
        return "All"
    
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    def __init__(self,
                 contentGenerator =  ChoiceOf_WorkerConfigurationObject_Cls(name = "Content generator",
                                                                            description = "Content generator that is used before content swapping",
                                                                            workersBaseType = ContentGenerator_AbstCls,
                                                                            activatable = False, # Content generator is mandatory
                                                                            singleChoice_flag = True),
                 
                 contentSwapper   =  ChoiceOf_WorkerConfigurationObject_Cls(name = "Content swapper",
                                                                            description = "Content swapper that swaps original content with generated content",
                                                                            workersBaseType = ContentSwapper_AbstCls,
                                                                            activatable = False, # Content swapper is mandatory
                                                                            singleChoice_flag = True) 
                 ):
        
        
        self._contentGenerator = self.resolveArgument(contentGenerator)
        self._contentSwapper = self.resolveArgument(contentSwapper)
        
        Anonymizer_AbstCls.__init__(self)
    
    
    def _confirmObjectView(self, objectView):
        return self._contentSwapper._validateSrcObjectView(objectView)
    
    
    def _swapDetectionRegionWithAnonymizedObjectView(self, destObjectView):
        """
        not-in-place operation
        """
        
        anonymizedObjectDetectionView = destObjectView.getDetection().getObject().getAnonymizedView()
        
        return self._contentSwapper.swap(anonymizedObjectDetectionView, destObjectView)
        
    
    def _anonymizeBySwap(self, nparray, detections):
        """
        not in-place operation
        shall take nparray and detections and return modified nparray
        """
        
        anonymizationPerformed_flag = False

        for detection in detections:
            
            view = View_Cls(nparray, detection, forceRAM = True)
            
            ret = self._swapDetectionRegionWithAnonymizedObjectView(view) 
            
            if ret.__class__ != str or ret != "Failed":
                anonymizationPerformed_flag = True
                nparray = ret
                
        if anonymizationPerformed_flag is False:
            return "Failed"
        
        else:
            return nparray
        
    
    def _anonymize(self, nparray, detections):
        """
        not-in-place operation
        """
        
        anonymizationPerformed_flag = False
        
        for detection in detections:
            
            view = View_Cls(nparray, detection, forceRAM = True)
            
            newView = self._contentGenerator.generate(view)
            
            if newView.__class__ != str or newView != "Failed":
            
                ret = self._contentSwapper.swap(
                    
                    srcObjectView = newView,
                    destObjectView = view
                    
                    )
                
                if ret.__class__ != str or ret != "Failed":
                    anonymizationPerformed_flag = True
                    nparray = ret
                    
#             self._asp.pasteNewContentIntoDestDetectionView(
#                 detectionView,
#                 newContent_rectangle,
#                 self._generatorAdditionalSurroundings_perc)

        if anonymizationPerformed_flag is False:
            return "Failed"
        else:
            return nparray


    def _prepareObjectsForAnonymization(self, objectFound):
        
        self._contentGenerator._defineStaticAnonymizedViewReferenceForEachObject(objectFound, contentSwapperValidating = self._contentSwapper)



