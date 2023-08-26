'''
Created on Dec 3, 2022

@author: piotr
'''
from ContentGenerator.ContentGenerator import ContentGenerator_NoInput_AbstCls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Bool
import requests
import time
from NonPythonFiles.WorkersFiles.ContentGenerators.ThisPersonDoesNotExist import ThisPersonDoesNotExist_facesLocalFileSystem,\
    ThisPersonDoesNotExist_faceFilePrefix, ThisPersonDoesNotExist_faceFileSuffix
from Space._2D.Image import Image_Cls, RAM_Image_Cls
import random
from ContentGenerator.FaceGenerator.FaceGenerator import FaceGenerator_AbstCls
import cv2
import numpy as np
from Configuration.ConfigurationObjects.WorkerConfiguration import ChoiceOf_WorkerConfigurationObject_Cls
from Detector.Detector import Detector_AbstCls
from View.View import StubView_Cls
from SW_Licensing.SW_License import HostSWLicense_Cls
from ObjectsDetectable.Objects import Object_Cls
import os



class ThisPersonDoesNotExist_Cls(ContentGenerator_NoInput_AbstCls, FaceGenerator_AbstCls):
    '''
    Uses faces downloaded from https://thispersondoesnotexist.com
    '''
    
    image_url = "https://thispersondoesnotexist.com/"
    
    
    @staticmethod
    def getDescription():
        return "Provides faces generation results dwonloaded from " + ThisPersonDoesNotExist_Cls.image_url
    
    @staticmethod
    def getName():
        return "StyleGAN - results"
    
    
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    
    def __init__(self, 
                 online = UserCfg_Bool(name = "Online generation",
                                       description = "Download image each time needed with https from " + image_url,
                                       defaultValue = False),
                 detector = ChoiceOf_WorkerConfigurationObject_Cls(name = "Preprocessing detector",
                                                                   description = "Detector that is applied to an image to narrow bitmap to the interesting part of an image, producing so called \"view\"",
                                                                   workersBaseType = Detector_AbstCls,
                                                                   singleChoice_flag = True,
                                                                   activatable = True)):
        '''
        Constructor
        '''
        
        self._online_flag = self.resolveArgument(online)
        
        assert isinstance(self._online_flag, bool)
        
        ContentGenerator_NoInput_AbstCls.__init__(self, detector)
        
        self._lastImgData = None
        
        self._connectionIssueDelay_s = 0.2
        self._errorRaiseTimeout_s = 20.
        
        self._downloadImage_url = ThisPersonDoesNotExist_Cls.image_url
        
        self._faceFileNamePrefix = ThisPersonDoesNotExist_faceFilePrefix
        self._faceFileNameSuffix = ThisPersonDoesNotExist_faceFileSuffix
        
        
        self._faceFiles_dir = ThisPersonDoesNotExist_facesLocalFileSystem
        
        self._availableFaceFilePaths_list = self._getListOfAvailableFaceFilePaths()
        self._leftFacesToProvideRandom_list = []
        
        self._nextFaceFileIndex = 0
    
    
    def _getListOfAvailableFaceFilePaths(self):
        output_list = []
        
        for root, _, filesBaseNames in os.walk(self._faceFiles_dir):
            for fileBaseName in filesBaseNames:
                if fileBaseName.startswith(self._faceFileNamePrefix) and fileBaseName.endswith(self._faceFileNameSuffix): 
                    output_list.append(os.path.join(root, fileBaseName))
        
        return output_list
    
    
    def _validateFaceFile(self, faceFileName):
        
        filePath_candidate = self._faceFiles_dir / faceFileName
        
        if filePath_candidate.exists():
            
            try:
                Image_Cls(filePath_candidate)
                return True
                
            except:
                print("The following file is not loadable as image: " + str(filePath_candidate))
        
        return False
    
    
    def _getGeneratedView(self):
        
        if self._online_flag:
            new_view = self._getFaceViewFromOnlineServer()
        
        else:
            new_view = self._getFaceViewFromLocalFileSystem()
        
        return new_view 
    
    
    def _getFaceViewFromOnlineServer(self):
        npArray = self._downloadNewFaceFromOnlineServer()
        return self._changeNpArrayToDetectionView(npArray)
    
    
    def _getFaceViewFromLocalFileSystem(self):
        
        assert self._availableFaceFilePaths_list, "there should be at least one face available in the local"
        
        if not self._leftFacesToProvideRandom_list and self._availableFaceFilePaths_list:
            self._leftFacesToProvideRandom_list = self._availableFaceFilePaths_list[:]
            random.shuffle(self._leftFacesToProvideRandom_list)
        
        faceFilePath = self._leftFacesToProvideRandom_list.pop()
        
        image = Image_Cls(faceFilePath)
        
        return self._changeNpArrayToDetectionView(image.getNpArrayCopy())
    
    
    def _downloadNewFaceFromOnlineServer(self):
        
        timePassed_s = 0.
        
        while 1:
            
            resp = requests.get(self._downloadImage_url, stream=True).raw
            
            if resp is not None:
                
                npArray = bytearray(resp.read())
            
                if self._lastImgData != npArray:
                    self._lastImgData = npArray
                    break
                
            time.sleep(self._connectionIssueDelay_s)
            timePassed_s += self._connectionIssueDelay_s
            
            if timePassed_s >= self._errorRaiseTimeout_s:
                raise ConnectionError("Cannot download new image in " + str(timePassed_s) + " seconds from url: " + self._downloadImage_url)
            
        npArray = np.asarray(npArray, dtype="uint8")
        npArray = cv2.imdecode(npArray, cv2.IMREAD_COLOR)
                
        return npArray


    def _getNewFaceNewFilePath(self):
        
        while 1:
            
            fileName_candidate = self._faceFiles_dir / (self._faceFileNamePrefix + str(self._nextFaceFileIndex) + self._faceFileNameSuffix)
            
            if fileName_candidate not in self._availableFaceFilePaths_list:
                filePath_candidate = self._faceFiles_dir / fileName_candidate
                
                if not filePath_candidate.exists():
                    break
            
            self._nextFaceFileIndex += 1
            
            if self._nextFaceFileIndex > 10e6:
                raise RuntimeError("Too many tries. While loop protection error")
        
        return fileName_candidate
    

    def _saveFaceToNewFile(self, npArray):
        
        newFaceFilePath = self._getNewFaceNewFilePath()
        
        RAM_Image_Cls(npArray).write(newFaceFilePath)
        
        if self._validateFaceFile(newFaceFilePath):
            self._availableFaceFilePaths_list.append(newFaceFilePath)
    
    
    def _defineStaticAnonymizedViewReferenceForEachObject(self, objectFound, contentSwapperValidating):
        self._dSAVRFEO_ignoringAnyView(objectFound, contentSwapperValidating)
    
        
    def downloadFaces(self, numberOfNewFacesToDownload):
        
        for _ in range(numberOfNewFacesToDownload):
            npArray = self._downloadNewFaceFromOnlineServer()
            self._saveFaceToNewFile(npArray)
    







if __name__ == "__main__":
    
    from ContentSwapper.SmartSwapper.FaceSmartSwapper.FaceSmartSwapper_WuHuikai import FaceSmartSwapper_Wuhuikai_Cls
    
    if 0:
        
        # download one face
        
        generator = ThisPersonDoesNotExist_Cls(online = True)
        generator.downloadFaces(1)
    
    elif 1:
        
        # generate view
        
        generator = ThisPersonDoesNotExist_Cls()
        
        #generator.downloadFaces(20)
        #view = generator._getFaceViewFromOnlineServer()
        view = generator._getFaceViewFromLocalFileSystem()
        
        print(view)
        
        view = generator.generate(StubView_Cls())
        
        print(view)
        
    else:
        
        # Assign new graphical repr to newely created object 
        
        generator = ThisPersonDoesNotExist_Cls()
        
        swapper = FaceSmartSwapper_Wuhuikai_Cls()
        
        for i in range(5):
            print(i)
            generator._dSAVRFEO_ignoringAnyView(Object_Cls(classId = 0), swapper)
    
    











    
    