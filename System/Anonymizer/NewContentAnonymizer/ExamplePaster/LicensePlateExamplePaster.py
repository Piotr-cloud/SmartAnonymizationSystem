'''
Created on Feb 5, 2022

@author: piotr
'''
from ObjectsDetectable.Classes import LicensePlateID
from Anonymizer.NewContentAnonymizer.CustomAnonymizer import CustomAnonymizer_Cls
from ContentSwapper.CloneSwapper import SeamlessCloneSwapper_Cls
from ContentGenerator.LicensePlateGenerator.LicensePlateExample import LicensePlateExampleProvider_Cls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path,\
    UserCfg_Bool
from PolymorphicBases.ABC import final
from NonPythonFiles.WorkersFiles.ContentGenerators.ExampleProvider import licensePlateExample_path,\
    licensePlateExamples_dir
from Detector.LicensePlatesDetectors.Wpod_Net import Wpod_Net_Cls


class LicensePlateExamplePaster_Cls(CustomAnonymizer_Cls):
    
    @staticmethod
    def getName(): 
        return "License Plate Example Paster"
    
    @final
    @staticmethod
    def getClassesServiced():
        return {LicensePlateID}

    def __init__(self,
                 example_file_path = UserCfg_Path(
                     name = "License plate image path", 
                     description="Bitmap to be used as source data", 
                     path=licensePlateExample_path,
                     referenceFolder = licensePlateExamples_dir),

                 applyDetector = UserCfg_Bool(
                     name = "Apply detector first?", 
                     description = "Shall object be first detected on the provided image with class detector? Otherwise detected area is replaced with provided image - no preprocessing is done", 
                     defaultValue = True)):
        
        applyDetector = self.resolveArgument(applyDetector)
        
        if applyDetector:
            detector = Wpod_Net_Cls
        else:
            detector = None
            
        CustomAnonymizer_Cls.__init__(self,
                                      contentGenerator = LicensePlateExampleProvider_Cls(example_file_path, detector),
                                      contentSwapper = SeamlessCloneSwapper_Cls())

        
        
