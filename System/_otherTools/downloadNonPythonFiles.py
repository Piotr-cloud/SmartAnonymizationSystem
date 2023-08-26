'''
Created on Aug 9, 2023

@author: piotr
'''

import argparse
import gdown
from pathlib import Path
import os
import zipfile


filesDownloadDict = {
    "System/NonPythonFiles/WorkersFiles/Anonymizers/AgentSmit/AgentSmith.jpeg": "https://drive.google.com/file/d/1gT8vRF3RQy7H7k1NJ1iuFoaa6EakKu_B/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentGenerators/ExampleProvider/Face/Face_example.jpeg" : "https://drive.google.com/file/d/1ymd2oAzgv8dOwqjAQQ2_Ih27S12q7VVb/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentGenerators/ExampleProvider/Plate/Plate_example.png" : "https://drive.google.com/file/d/1yLVKDav2wNh3eic7mXtUl4ezBC3_Ofmu/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentRecognizer/EasyOCR/darknet/libdarknet.so" : "https://drive.google.com/file/d/1t28odQvlcLYQxJgRY0yaaJnGcVfKk-OR/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentSwappers/DlibBasedSwapper/models/shape_predictor_68_face_landmarks.dat" : "https://drive.google.com/file/d/1NyuYzWWaDLLik9GiT62lRINYtuFuAmT6/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentSwappers/MKFaceSwapper/predictor/shape_predictor_68_face_landmarks.dat" : "https://drive.google.com/file/d/1NyuYzWWaDLLik9GiT62lRINYtuFuAmT6/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentSwappers/MKFaceSwapper/model/candide.npz" : "https://drive.google.com/file/d/12OTwUK5pUREPITiR1eHo4JIcQTqI94QA/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentSwappers/WuHukaiFaceSwapper/models/shape_predictor_68_face_landmarks.dat" : "https://drive.google.com/file/d/1NyuYzWWaDLLik9GiT62lRINYtuFuAmT6/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/DlibCNN/Model/mmod_human_face_detector.dat" : "https://drive.google.com/file/d/19D2EG-X-1DHekLW9eUPifbPnuaOqpmey/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Haar/configuration/haarcascade_frontalface2.xml" : "https://drive.google.com/file/d/1MU3nzBS4BiIZN1SrwVXqOWaKCx1Prj2e/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Lpd_ThorPham/data/coco.names" : "https://drive.google.com/file/d/1hrhI2IyVVkQeqpnGYrEFYBiewwThv7nO/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Lpd_ThorPham/cfg/coco.data" : "https://drive.google.com/file/d/1k_iFBgqIx146JqulDUxpSvvkImyW_I4y/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Lpd_ThorPham/cfg/yolov3.cfg" : "https://drive.google.com/file/d/1iGt666e7Cj1qnjZDeoSHJhdbb3ZPkZiL/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Lpd_ThorPham/weights/best.pt" : "https://drive.google.com/file/d/1ya4Xk2ZJU3YLLxqIKlZfwAbRgWhxSMoV/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/LPD_YuNet/Models/license_plate_detection_lpd_yunet_2023mar.onnx" : "https://drive.google.com/file/d/19geq1lNXMbZTvU_Glc5weUOGDyiBFDrh/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/LPD_YuNet/Models/license_plate_detection_lpd_yunet_2023mar_int8.onnx" : "https://drive.google.com/file/d/1rTwGwstPjpDDidbaGT-gaTmK0InxMvuu/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/UnderstandAI/weights_face_v1.0.0.pb" : "https://drive.google.com/file/d/19vZl38IYmhaAzxYTxgVFXk2PFObP6ZP6/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/UnderstandAI/weights_plate_v1.0.0.pb" : "https://drive.google.com/file/d/1u5MrRCgKPC3Zxs3g9YIb1NOp2dIfNBPs/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/WpodNet/wpod-net.h5" : "https://drive.google.com/file/d/1vHEiUXj0blxGzQ0UX82p-ZF2zm3ZLscL/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/WpodNet/wpod-net.json" : "https://drive.google.com/file/d/1V7IfFHN_zNFW_6XX8832fwCjOFSz1CsI/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/YuNet/Models/face_detection_yunet_2023mar.onnx" : "https://drive.google.com/file/d/10yAbTx0aC-pltHBP7eNfdYQprOqiENRT/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Trackers/DeepSort/resources/networks/mars-small128.pb": "https://drive.google.com/file/d/1chZpMkH5Ih6wfdu_NjsQ62rXFesOcwvb/view?usp=sharing"
    }

zippedFoldersDownloadDict = {
    "System/NonPythonFiles/WorkersFiles/ContentGenerators/PlatesMania/PlatesImages" : "https://drive.google.com/file/d/1dwP2ZXwR8pv7ykQ0WD2X99W2eUSlLHQ8/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentGenerators/ThisPersonDoesNotExist/FacesDownloaded" : "https://drive.google.com/file/d/1UgBlTtwb2oYyw8SwWCK19RhzHWPWXqV0/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/ContentRecognizer/EasyOCR/data/ocr" : "https://drive.google.com/file/d/1wjLGJ6VNyGlwM-WOLH1ScCdQYBNxGkTg/view?usp=sharing",
    "System/NonPythonFiles/WorkersFiles/Detectors/Dnn/Models" : "https://drive.google.com/file/d/1EtrCzb3pFHty0PhQYLpfrIFylgdClPqB/view?usp=sharing"
}

outputBaseDir = Path(__file__).parent.parent.parent



class GoogleDriveDownload_Cls():
    
    def __init__(self, overwrite=False):
        self._overwrite_flag = bool(overwrite)
    
    
    def downloadFile(self, url, destPath, noPrint = False):
        """
        Creates directory when missing
        """
        destPath = Path(destPath)
        
        if not destPath.parent.exists():
            raise NotADirectoryError("The following directory does not exist: \"" + str(destPath.parent) + "\"")
        
        else:
            if destPath.exists() and not self._overwrite_flag:
                if not noPrint:
                    print("Skipping download of: \"" + str(destPath) + "\" - File exists already")
                return
            
            else:
                if not noPrint:
                    print("Downloading: \"" + str(destPath) + "\"", end = "", flush=True)
                
                cnt = 5
                
                while cnt:
                    try:
                        gdown.download(url, str(destPath), quiet=True,fuzzy=True)
                        if destPath.exists():
                            break
                    except:
                        pass
                    
                    time.sleep(0.1)
                    print("Reattempting download...")
                    cnt-=1
                
                if cnt == 0:
                    raise ConnectionError("Download failure! Cannot download the url: " + str(url))
                
                if not noPrint:
                    print("  -  Done!")
             
        
    def downloadFiles(self, outputBaseDir, downloadDict):
        """
        outputBaseDir  -  base directory for relative paths used in downloadDir
        downloadDict   -  {relative file path : url}
        
        Download files from google drive into specific locations
        """
        
        outputBaseDir = Path(outputBaseDir)
        
        if not outputBaseDir.exists():
            raise NotADirectoryError("The following directory does not exist: \"" + str(outputBaseDir) + "\"")
        
        
        for destRelPath, url in downloadDict.items():
            destPath = outputBaseDir / destRelPath
        
            if not destPath.parent.exists():
                os.makedirs(str(destPath.parent))
            
            self.downloadFile(url, destPath)
    
    
    def _getNonExistingPath(self):
        
        directory_ = Path(__file__).parent
        name_candidate_int = 0
        
        path_ = None
        
        while not path_ or path_.exists():
            path_ = directory_ / (str(name_candidate_int) + ".zip")
            name_candidate_int += 1
        
        return path_
            
    
    def downloadZippedFolder(self, url, destPath):
        
        if destPath.exists() and not self._overwrite_flag:
            print("Skipping download zipped folder of: \"" + str(destPath) + "\" - Directory exists already")
            return
        
        else:
        
            print("Downloading zipped folder: \"" + str(destPath) + "\"", end = "", flush=True)
            
            with ZipTempFile_Cls(self._getNonExistingPath()) as zipTempFile_path:
                self.downloadFile(url, zipTempFile_path, noPrint = True)
                
                os.makedirs(str(destPath))
                
                with zipfile.ZipFile(str(zipTempFile_path), 'r') as z:
                    z.extractall(str(destPath))
                    
            print("  -  Done!")

    
    def downloadZippedFolders(self, outputBaseDir, downloadDict):
        """
        outputBaseDir  -  base directory for relative paths used in downloadDir
        downloadDict   -  {relative file path : url}
        
        Download files from google drive into specific locations
        """
        
        outputBaseDir = Path(outputBaseDir)
        
        if not outputBaseDir.exists():
            raise NotADirectoryError("The following directory does not exist: " + str(outputBaseDir))
        
        
        for destRelPath, url in downloadDict.items():
            destPath = outputBaseDir / destRelPath
        
            if not destPath.parent.exists():
                os.makedirs(str(destPath.parent))
            
            self.downloadZippedFolder(url, destPath)
    


class ZipTempFile_Cls():

    def __init__(self, filePath):
        self._filePath = Path(filePath)
    
    def __enter__(self):
        if self._filePath.exists():
            raise FileExistsError("The following path exists: " + str(self._filePath))
        
        return self._filePath
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        os.remove(str(self._filePath))




if __name__ == "__main__":


    argsParser = argparse.ArgumentParser("The interface to perform downloading of large files")

    argsParser.add_argument(
        "-overwrite",
        default=False,
        action="store_true",
        help="Overwrite existing files and folders" 
        )
    
    args = argsParser.parse_args()
    

    gdd = GoogleDriveDownload_Cls(overwrite = args.overwrite)
    
    gdd.downloadFiles(outputBaseDir, filesDownloadDict)
    gdd.downloadZippedFolders(outputBaseDir, zippedFoldersDownloadDict)




















