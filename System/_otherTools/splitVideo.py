'''
Created on Jul 5, 2023

@author: piotr
'''
import argparse
from pathlib import Path
import cv2
import mimetypes
import shutil
import os


clearFirst = False



class FramesWorkspacePreparator_Cls():
    
    def __init__(self, outputDir, imagesToSeparateFolder_flag=True):

        self._outputDir = Path(outputDir)
        self._imagesToSeparateFolder_flag = bool(imagesToSeparateFolder_flag)
        
        self._imagesOutputDir = self._outputDir
        
        if self._imagesToSeparateFolder_flag:
            self._imagesOutputDir /= "_Images"
            
        print("Output directory: " + str(self._outputDir))
        
        if self._outputDir.exists():
            
            if clearFirst:
                print("Clearing directory: " + str(self._outputDir))
                shutil.rmtree(str(self._outputDir))
        
        if not self._outputDir.exists():
            os.mkdir(str(self._outputDir))
    
    
    def processInputPaths(self, srcFilePaths):
        
        for srcFilePath in srcFilePaths:
            srcFilePath = Path(srcFilePath)
            if srcFilePath.is_file():
                self.processInputFile(srcFilePath)
            elif srcFilePath.is_dir():
                self.processFilesInDir(srcFilePath)
            else:
                print("Input path does not exist: " + str(srcFilePath))
        
    
    def processFilesInDir(self, srcDir):
        for root, _, files in os.walk(srcDir):
            for filename in files:
                srcFilePath = Path(root) / filename
                self.processInputFile(srcFilePath)
            break
        
    
    def processInputFile(self, srcFilePath):
        
        srcFilePath = Path(srcFilePath)
        
        if srcFilePath.is_file():
            fileType = mimetypes.guess_type(srcFilePath)[0]
            
            if fileType:
                if fileType.startswith('image'):
                    print("Processing image: " + str(srcFilePath.name))
                    self._copyImage(srcFilePath)
                    return
                
                elif fileType.startswith('video'):
                    print("Processing video: " + str(srcFilePath.name))
                    self._splitVideo(srcFilePath)
                    return
        
        print("Skipping input: " + str(srcFilePath))
                    
    
    def processInputFiles(self, srcFilePaths):
        
        for srcFilePath in srcFilePaths:
            self.processInputFile(srcFilePath)
    
    
    def _splitVideo(self, srcFilePath):
        
        srcFileBaseName = srcFilePath.stem
        
        outputPath_basePart = str(self._outputDir / srcFileBaseName)
        
        cap = cv2.VideoCapture(str(srcFilePath))
        framesCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        
        framesRead_number = 0
        
        while(cap.isOpened()) and \
            (framesRead_number < framesCount):
            flag, nparray = cap.read()
        
            if flag:
                
                framesRead_number += 1
                
                outputFilePath = outputPath_basePart + "_Frame_" + str(framesRead_number) + ".jpg"
                
                cv2.imwrite(outputFilePath, nparray)
    
    
    def _copyImage(self, srcFilePath):
    
        if not self._imagesOutputDir.exists():
            os.mkdir(str(self._imagesOutputDir))
            
        outputFilePath = str(self._imagesOutputDir / srcFilePath.name)
        
        shutil.copyfile(srcFilePath, outputFilePath)




if __name__ == "__main__":


    argsParser = argparse.ArgumentParser("Split videos and copy images into dir, preserving file base name")
    
        
    argsParser.add_argument(
        "i",
        nargs='+',
        type=str,
        default=[],
        help="Paths of input file(s) or directories"
        )
    
    argsParser.add_argument(
        "o",
        type=str,
        help="Output directory"
        )
    args = argsParser.parse_args()
    
    fwp = FramesWorkspacePreparator_Cls(args.o)
    fwp.processInputPaths(args.i)
        

























