'''
Created on 24 sty 2021

@author: piotr
'''
from ContentGenerator.ContentGenerator import ContentGenerator_NoInput_AbstCls
from Space._2D.Image import Image_Cls
from SW_Licensing.SW_License import HostSWLicense_Cls


class ExampleReaderWithCache_Cls():
    """
    Cache image during whole runtime assuming that examples are not in change
    """
    
    imagesCache = {}
        

    def read(self, imagePath):
        
        if imagePath not in ExampleReaderWithCache_Cls.imagesCache:
            
            readImage = Image_Cls(imagePath)
            
            if readImage is not None:
                
                ExampleReaderWithCache_Cls.imagesCache[imagePath] = readImage
            
                return ExampleReaderWithCache_Cls.imagesCache[imagePath]
        
            return None
        
        else:
            return ExampleReaderWithCache_Cls.imagesCache[imagePath]





class ExampleProvider_AbstCls(ContentGenerator_NoInput_AbstCls):

    
    @staticmethod
    def getDescription():
        return "Generator returning example image, optionally applying detection first"
    
    @classmethod
    def allowOneInstanceServicingMultipleClassesAtATime(cls):
        return False

    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
        
    def __init__(self, 
                 example_file_path,
                 detector):
        
        # Resolve worker arguments in case of direct use(skipping dynamic configuration mechanism)
        self._example_file_path = self.resolveArgument(example_file_path)
        
        ContentGenerator_NoInput_AbstCls.__init__(self, detector)
        
    
    def _prepare(self):
        ContentGenerator_NoInput_AbstCls._prepare(self)
        self._prepareExampleView()
    
    
    def _prepareExampleView(self):
        
        # if not os.path.exists(self._example_file_path):
        #     raise IOError("Example file path does not exist: " + self._example_file_path)
        
        exampleImage = Image_Cls(self._example_file_path)
        
        self._exampleView = self._changeNpArrayToDetectionView(exampleImage.getNpArrayCopy())
    
    
    def _getGeneratedView(self):
        return self._exampleView

    
    def _defineStaticAnonymizedViewReferenceForEachObject(self, objectFound, contentSwapperValidating):
        
        self._dSAVRFEO_ignoringAnyView(objectFound, contentSwapperValidating)
    


















