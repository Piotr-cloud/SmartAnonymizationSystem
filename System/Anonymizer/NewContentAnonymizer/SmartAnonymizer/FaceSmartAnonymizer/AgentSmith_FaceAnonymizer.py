'''
Created on Mar 17, 2022

@author: piotr
'''
from Anonymizer.NewContentAnonymizer.SmartAnonymizer.FaceSmartAnonymizer.FaceSmartAnonymizer import FaceSmartAnonymizer_AbstCls
from Detector.FacesDetectors.Haar import Haar_Cls
from ContentGenerator.FaceGenerator.FaceExample import FaceExampleProvider_Cls
from NonPythonFiles.WorkersFiles.Anonymizers.AgentSmith import AgentSmithFace_path
from SW_Licensing.SW_License import HostSWLicense_Cls
from ContentSwapper.SmartSwapper.FaceSmartSwapper.DlibBasedSwapper import DlibBasedSwapper_Cls


class AgentSmith_FaceAnonymizer_Cls(FaceSmartAnonymizer_AbstCls):
    
    @staticmethod
    def getName(): 
        return "AgentSmith"
    
    @staticmethod
    def getDescription():
        return "Anonymized each detected face with agent smith face"
        
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    def __init__(self):
        
        FaceSmartAnonymizer_AbstCls.__init__(self, 
                                             
                                             FaceExampleProvider_Cls(
                                                 example_file_path = AgentSmithFace_path,
                                                 detector = Haar_Cls
                                                 ), 
                                             DlibBasedSwapper_Cls(
                                                 additionalSurroundings_perc = 100
                                                 )
                                             )

