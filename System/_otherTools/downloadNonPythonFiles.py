'''
Created on Aug 29, 2023

@author: piotr
'''

import requests

from pathlib import Path
import os
from PolymorphicBases.ABC import abstractmethod, final, Base_AbstCls
import hashlib
import shutil
import zipfile
import time


outputBaseDir = Path(__file__).parent.parent.parent


class TempPath_Cls():

    def __init__(self):
        self._path = self._getNonExistingPath()
    
    def __enter__(self):
        if self._path.exists():
            raise FileExistsError("The following path exists: " + str(self._path))
        
        return self._path
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        
        if self._path.exists():
            if self._path.is_file():
                os.remove(str(self._path))
            elif self._path.is_dir():
                shutil.rmtree(str(self._path))


    def _getNonExistingPath(self):
        
        directory_ = Path(__file__).parent
        name_candidate_cnt = 0
        name_candidate_cnt_limit = 10000
        
        path_ = None
        
        while not path_ or path_.exists():
            path_ = directory_ / (str(name_candidate_cnt))
            name_candidate_cnt += 1
            if name_candidate_cnt > name_candidate_cnt_limit:
                raise IndexError("Cannot find non existing path")
        
        return path_




class ExternalFileInfo_AbstCls(Base_AbstCls):
    
    @abstractmethod
    def download(self, targerFilePath):
        pass
    


class GoogleDriveFile_Cls(ExternalFileInfo_AbstCls):
    
    retrydelay_ms = 2000
    
    def __init__(self, fileId):
        self.fileId = fileId
        self._lastDownloadTryTimestamp = None
    
    
    def download(self, targetFilePath):
        
        if self._lastDownloadTryTimestamp is not None:
            delayLeft_s = self._lastDownloadTryTimestamp + (GoogleDriveFile_Cls.retrydelay_ms / 1000) - time.time()
            if delayLeft_s > 0:
                if delayLeft_s > 10:
                    delayLeft_s = 10
                if delayLeft_s > 1:
                    print("\n -> Google drive download retry delay: {:.3f} s <-".format(delayLeft_s), flush = True)
                    
                time.sleep(delayLeft_s)
        
        self._lastDownloadTryTimestamp = time.time()
        
        return self._download_file_from_google_drive(self.fileId, targetFilePath)
    
    
    def _download_file_from_google_drive(self, fileID, destination):
        
        URL = "https://docs.google.com/uc?export=download&confirm=1"
        session = requests.Session()
        
        try:
            response = session.get(URL, params={"id": fileID}, stream=True)
        except:
            print("Cannot download from Google Drive file with id: " + str(fileID), flush = True)
            return False
        
        token = self._get_confirm_token(response)
    
        if token:
            params = {"id": fileID, "confirm": token}
            response = session.get(URL, params=params, stream=True)
    
        self._save_response_content(response, destination)
        
        return True
    
    
    def _get_confirm_token(self, response):
        
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value
    
        return None
    
    
    def _save_response_content(self, response, destination):
        
        CHUNK_SIZE = 32768
    
        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)



class PartDownload_AbstCls(Base_AbstCls):
    
    def __init__(self, artifactName, externalFilesInfo_list, fileHash):
        
        assert all([isinstance(el, ExternalFileInfo_AbstCls) for el in externalFilesInfo_list])
        
        self.externalFilesInfo_list = externalFilesInfo_list
        self.artifactName = artifactName
        self.fileHash_expected = fileHash if isinstance(fileHash, str) else None
    
    
    @abstractmethod
    def isAlreadyDownloaded(self):
        pass
    
    
    @final
    def download(self):
        
        if self.isAlreadyDownloaded():
            print("Skipping download: \"" + self.artifactName + "\"  ->  Already downloaded!", flush = True)
            return True
        
        else:
            print("Downloading:  \"" + self.artifactName + "\" ", end = "", flush = True)
            
            ret = False
            
            with TempPath_Cls() as tempPath:
                
                for efi in self.externalFilesInfo_list:
                    ret = efi.download(tempPath)
            
                    if ret:
                        hashCalculated = self.calculateFileHash(tempPath)
                        
                        if self.fileHash_expected is not None:
                            if hashCalculated != self.fileHash_expected:
                                print("\nHash mismatch! expected: " + str(self.fileHash_expected) + ", downloaded: " + hashCalculated, flush = True)
                                
                                ret = False
                                
                                if hashCalculated == "7869797f40804a2de10a7d1e8cb32177":
                                    print("Warning! It probably failed due to download automation protection by Google Drive server. Try again later...")
                                    break
                                    
                                continue
                        else:
                            print(" Hash: " + hashCalculated , end = "", flush = True)
                            
                        ret = self._pasteIntoTheProject(tempPath)
                        
                        if ret:
                            print(" - Done", flush = True)
                            break
            
            if not ret:
                print(" - Failed", flush = True)
            
            return ret
    
    
    def calculateFileHash(self, filePath):
        
        m = hashlib.md5()
        
        with open(str(filePath), 'rb') as file_:
            while True:
                data = file_.read(8192)
                if not data:
                    break
                m.update(data)
                
            hash_value = m.hexdigest()
        
        return hash_value
    
    
    def _copy(self, src, dest):
        
        if not dest.parent.exists():
            os.makedirs(dest.parent)
            
        return shutil.copy2(src, dest)

    
    def _getFileAbsPath(self, relPathInProject):
        return outputBaseDir / relPathInProject
    
    
    @abstractmethod
    def _pasteIntoTheProject(self, filePath):
        pass




class PartDownload_File_Cls(PartDownload_AbstCls):
    
    def __init__(self, artifactName, targetPath_singleOrList, externalFilesInfo_list, fileHash = None):
        
        PartDownload_AbstCls.__init__(self, artifactName, externalFilesInfo_list, fileHash)
        
        if isinstance(targetPath_singleOrList, str):
            targetPath_singleOrList = [targetPath_singleOrList]
            
        self.targetPaths_list = [self._getFileAbsPath(relPathInProject) for relPathInProject in targetPath_singleOrList]


    def isAlreadyDownloaded(self):
        return all([path_.exists() for path_ in self.targetPaths_list])


    def _pasteIntoTheProject(self, tempPath):
        for targetPath in self.targetPaths_list:
            if not targetPath.exists():
                if not self._copy(tempPath, targetPath):
                    return False
        return True



class PartDownload_ZipedFolder_Cls(PartDownload_File_Cls):
    
    def _pasteIntoTheProject(self, tempPath):
        
        for targetPath in self.targetPaths_list:
            if not targetPath.exists():
                os.makedirs(str(targetPath))
                
                with zipfile.ZipFile(str(tempPath), 'r') as zfile:
                    zfile.extractall(str(targetPath))
            
            backupTargetFilePath = targetPath.with_suffix(".zip.bak")
            
            if not backupTargetFilePath.exists():
                self._copy(tempPath, backupTargetFilePath)
            
                
        return True



class PartDownload_ZipedArtifacts_Cls(PartDownload_File_Cls):
    
    def __init__(self, artifactName, zipFile_2_targetMapping_dict, externalFilesInfo_list, fileHash = None):
        
        PartDownload_AbstCls.__init__(self, artifactName, externalFilesInfo_list, fileHash)
        self.zipFile_2_targetMapping_dict = zipFile_2_targetMapping_dict


    def isAlreadyDownloaded(self):
        return all([self._getFileAbsPath(destPath).exists() for destPath in self.zipFile_2_targetMapping_dict])
            
    
    def _pasteIntoTheProject(self, tempPath):
        
        with TempPath_Cls() as unpackedDownloadFilePath:
            
            with zipfile.ZipFile(str(tempPath), 'r') as zfile:
                zfile.extractall(str(unpackedDownloadFilePath))
            
            for destPath, srcPath in self.zipFile_2_targetMapping_dict.items():
                
                srcPath = unpackedDownloadFilePath / srcPath 
                destPath = self._getFileAbsPath(destPath)
                
                if not destPath.exists():
                    self._copy(srcPath, destPath)
            
            
        return True




class DownloadSession_Cls():
    
    downloadRetries = 8
    
    def __init__(self, downloadParts_list):
        
        assert all([isinstance(el, PartDownload_AbstCls) for el in downloadParts_list])
        self.downloadParts_list = list(downloadParts_list)
    
    
    def _downloadParts(self, parts_list, recursionCountdown = downloadRetries):
        
        partsDownloaded_list = []
        partsFailedToDownload_list = []
        
        for part in parts_list:
            
            downloadResult = part.download() 
            if downloadResult:
                partsDownloaded_list.append(part)
            else:
                partsFailedToDownload_list.append(part)
        
        if partsFailedToDownload_list:
            if recursionCountdown > 0:
                
                print("\nThere are failed downloads. Retrying [{}/{}]...\n".format((DownloadSession_Cls.downloadRetries -recursionCountdown) + 1, DownloadSession_Cls.downloadRetries))
                
                return self._downloadParts(partsFailedToDownload_list, recursionCountdown - 1)
            else:
                return False
        
        return True


    def download(self):
        
        return self._downloadParts(self.downloadParts_list)





downloadSession = DownloadSession_Cls([
        PartDownload_File_Cls(
            "UnderstandAI - Face detector model", 
            "System/NonPythonFiles/WorkersFiles/Detectors/UnderstandAI/weights_face_v1.0.0.pb", 
            [
                GoogleDriveFile_Cls("1CwChAYxJo3mON6rcvXsl82FMSKj82vxF"),
                GoogleDriveFile_Cls("19vZl38IYmhaAzxYTxgVFXk2PFObP6ZP6")
            ],
            "16277fcb860e6682a73b3b8fa3d251c3"
            
        ),
        PartDownload_File_Cls(
            "UnderstandAI - License plate model", 
            "System/NonPythonFiles/WorkersFiles/Detectors/UnderstandAI/weights_plate_v1.0.0.pb", 
            [
                GoogleDriveFile_Cls("1Fls9FYlQdRlLAtw-GVS_ie1oQUYmci9g"),
                GoogleDriveFile_Cls("1u5MrRCgKPC3Zxs3g9YIb1NOp2dIfNBPs")
            ],
            "b170be93e808e70390829606da4fa067"
        ),
        PartDownload_File_Cls(
            "Dlib face keypoints predictor model", 
            [
                "System/NonPythonFiles/WorkersFiles/ContentSwappers/DlibBasedSwapper/models/shape_predictor_68_face_landmarks.dat",
                "System/NonPythonFiles/WorkersFiles/ContentSwappers/MKFaceSwapper/predictor/shape_predictor_68_face_landmarks.dat",
                "System/NonPythonFiles/WorkersFiles/ContentSwappers/WuHukaiFaceSwapper/models/shape_predictor_68_face_landmarks.dat"
            ], 
            [
                GoogleDriveFile_Cls("1NyuYzWWaDLLik9GiT62lRINYtuFuAmT6")
            ],
            "73fde5e05226548677a050913eed4e04"
            
        ),
        
        
        PartDownload_ZipedArtifacts_Cls(
            "Other models and files",
            {
                "System/NonPythonFiles/WorkersFiles/Anonymizers/AgentSmit/AgentSmith.jpeg": "AgentSmith.jpeg",
                "System/NonPythonFiles/WorkersFiles/ContentGenerators/ExampleProvider/Face/Face_example.jpeg" : "Face_example.jpeg",
                "System/NonPythonFiles/WorkersFiles/ContentGenerators/ExampleProvider/Plate/Plate_example.png" : "Plate_example.png",
                "System/NonPythonFiles/WorkersFiles/ContentRecognizer/EasyOCR/darknet/libdarknet.so" : "libdarknet.so",
                "System/NonPythonFiles/WorkersFiles/ContentSwappers/MKFaceSwapper/model/candide.npz" : "candide.npz",
                "System/NonPythonFiles/WorkersFiles/Detectors/DlibCNN/Model/mmod_human_face_detector.dat" : "mmod_human_face_detector.dat",
                
                "System/NonPythonFiles/WorkersFiles/Detectors/Haar/configuration/haarcascade_frontalface2.xml" : "haarcascade_frontalface2.xml",
                "System/NonPythonFiles/WorkersFiles/Detectors/LPD_YuNet/Models/license_plate_detection_lpd_yunet_2023mar.onnx" : "license_plate_detection_lpd_yunet_2023mar.onnx",
                "System/NonPythonFiles/WorkersFiles/Detectors/LPD_YuNet/Models/license_plate_detection_lpd_yunet_2023mar_int8.onnx" : "license_plate_detection_lpd_yunet_2023mar_int8.onnx",
                "System/NonPythonFiles/WorkersFiles/Detectors/WpodNet/wpod-net.h5" : "wpod-net.h5",
                "System/NonPythonFiles/WorkersFiles/Detectors/WpodNet/wpod-net.json" : "wpod-net.json",
                "System/NonPythonFiles/WorkersFiles/Detectors/YuNet/Models/face_detection_yunet_2023mar.onnx" : "face_detection_yunet_2023mar.onnx",
                "System/NonPythonFiles/WorkersFiles/Trackers/DeepSort/resources/networks/mars-small128.pb" : "mars-small128.pb"
            },
            [
                GoogleDriveFile_Cls("1oCNedTP-cP8oirYdmQ-ssgNsbxfSofWP")
            ],
            "1f8e4fe7f71545913b4a62a1cbe7d34f"
        ),
                                        
        
        
        PartDownload_ZipedFolder_Cls(
            "License plates images", 
            "System/NonPythonFiles/WorkersFiles/ContentGenerators/PlatesMania/PlatesImages",
            [
                GoogleDriveFile_Cls("1dwP2ZXwR8pv7ykQ0WD2X99W2eUSlLHQ8")
            ],
            "caac87812598345794df2b6b175449f3"
        ),
        PartDownload_ZipedFolder_Cls(
            "ThisPersonDoesNotExist faces images", 
            "System/NonPythonFiles/WorkersFiles/ContentGenerators/ThisPersonDoesNotExist/FacesDownloaded", 
            [
                GoogleDriveFile_Cls("1UgBlTtwb2oYyw8SwWCK19RhzHWPWXqV0")
            ],
            "a5cc780b9d9dd3f37ecb479ef4076d3a"
        ),
        PartDownload_ZipedFolder_Cls(
            "EasyOCR models", 
            "System/NonPythonFiles/WorkersFiles/ContentRecognizer/EasyOCR/data/ocr", 
            [
                GoogleDriveFile_Cls("1wjLGJ6VNyGlwM-WOLH1ScCdQYBNxGkTg")
            ],
            "27d348d643d4bc6c83ff185002e07648"
        ),
        PartDownload_ZipedFolder_Cls(
            "Dnn models", 
            "System/NonPythonFiles/WorkersFiles/Detectors/Dnn/Models", 
            [
                GoogleDriveFile_Cls("1EtrCzb3pFHty0PhQYLpfrIFylgdClPqB")
            ],
            "d55be9eca8ea63392bf2fb7cd5ffe361"
        ),
    ])





if __name__ == "__main__":
    ret = downloadSession.download()
    
    if not ret:
        exit(1)















