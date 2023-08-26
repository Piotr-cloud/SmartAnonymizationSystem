'''
Created on Feb 4, 2023

@author: piotr
'''
from ObjectsDetectable.ClassesCfg import FaceID
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path
from Configuration.ConfigurationObjects.WorkerConfiguration import ChoiceOf_WorkerConfigurationObject_Cls
from Detector.Detector import Detector_AbstCls
from ContentGenerator.ExampleProvider import ExampleProvider_AbstCls
from NonPythonFiles.WorkersFiles.ContentGenerators.ExampleProvider import faceExample_path,\
    faceExamples_dir


class FaceExampleProvider_Cls(ExampleProvider_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Face example provider"
        
    @staticmethod
    def getDescription():
        return "Generator returning example image, optionally applying detection first"
    
    @staticmethod
    def getClassesServiced():
        return {FaceID}

        
    def __init__(self, 
                 
                 example_file_path = UserCfg_Path(
                     name = "Image path", 
                     description="Bitmap to be used as data source", 
                     path=faceExample_path,
                     referenceFolder = faceExamples_dir),
                 
                 detector = ChoiceOf_WorkerConfigurationObject_Cls(name = "Preprocessing detector",
                                                                   description = "Detector that is applied to an image to narrow bitmap to the interesting part of an image, producing so called \"view\"",
                                                                   workersBaseType = Detector_AbstCls,
                                                                   singleChoice_flag = True,
                                                                   activatable = True)):
        
        ExampleProvider_AbstCls.__init__(self, example_file_path, detector)









