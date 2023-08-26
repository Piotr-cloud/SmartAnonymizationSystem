'''
Created on Oct 29, 2022

@author: piotr
'''
import numpy as np

from ContentRecognizer.Recognition import RecognizedPlateNumbers_Cls
from NonPythonFiles.WorkersFiles.ContentRecognizer.EasyOCR import EasyOCR_config_filePath,\
    EasyOCR_weights_filePath, EasyOCR_dataset_filePath, EasyOCR_filesDir,\
    EasyOCR_tempImgFile_fileName, EasyOCR_DLL_filePath
from NonPythonFiles import EasyOcrWorskapce_dir
from ctypes import CDLL, RTLD_GLOBAL, c_int, c_void_p, c_float, c_char_p, POINTER, pointer
from ContentRecognizer.LicensePlateRecognizer._EasyOCR.types import IMAGE,\
    DETECTION, METADATA, Label
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path
from CommonTools.ContextManagers import WorkingDirectorySwitch_Cls
from ContentRecognizer.LicensePlateRecognizer.LicensePlateRecognizer import LicensePlateRecognizer_AbstCls
from SpaceSpecificProcessor._2D.ArrayProcessor import ArraySpecificProcessor_Cls
from Space._2D.ImageParts import ImagePart_Cls
from Space._2D.Image import Image_Cls
from SW_Licensing.SW_License import License_Cls



class EasyOCR_Cls(LicensePlateRecognizer_AbstCls):
    
    @staticmethod
    def getDescription():
        return "Darknet and FAST-YOYO based OCR"

    @staticmethod
    def getName():
        return "EasyOCR"
    
    def __init__(self,
                 configFile = UserCfg_Path(name = "Configuration file",
                                           description = "EasyOCR configuration file",
                                           path = EasyOCR_config_filePath),
                 
                 weightsFile = UserCfg_Path(name = "Weights file",
                                            description = "EasyOCR network weight file",
                                            path = EasyOCR_weights_filePath)):
        
        configFile = self.resolveArgument(configFile)
        weightsFile  = self.resolveArgument(weightsFile)
        
        LicensePlateRecognizer_AbstCls.__init__(self)
        
        self._loadDLL()

        self._ocr_net  = self._dll_lib.load_network(
            str(configFile).encode('utf-8'), 
            str(weightsFile).encode('utf-8'), 0)
        
        with WorkingDirectorySwitch_Cls(EasyOCR_filesDir):
            self._ocr_meta = self._dll_lib.get_metadata(str(EasyOCR_dataset_filePath).encode('utf-8'))
        
        #self._imageWriter = ImageWriter_Cls()
        
        self._tempImgFile_fileName = EasyOCR_tempImgFile_fileName
        self._temp_dir = EasyOcrWorskapce_dir
        
        self._tempImgFile_filePath = self._temp_dir / self._tempImgFile_fileName
        self._tempImgFile_filePath_bytes = str(self._tempImgFile_filePath).encode('utf-8')
        
        self._arraySpecificProcessor = ArraySpecificProcessor_Cls()
    
    
    def _loadDLL(self):
        
        self._dll_lib = CDLL(EasyOCR_DLL_filePath, RTLD_GLOBAL)
        self._dll_lib.network_width.argtypes = [c_void_p]
        self._dll_lib.network_width.restype = c_int
        self._dll_lib.network_height.argtypes = [c_void_p()]
        self._dll_lib.network_height.restype = c_int
        
        predict = self._dll_lib.network_predict
        predict.argtypes = [c_void_p, POINTER(c_float)]
        predict.restype = POINTER(c_float)
        
        set_gpu = self._dll_lib.cuda_set_device
        set_gpu.argtypes = [c_int]
        
        make_image = self._dll_lib.make_image
        make_image.argtypes = [c_int, c_int, c_int]
        make_image.restype = IMAGE
        
        get_network_boxes = self._dll_lib.get_network_boxes
        get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int)]
        get_network_boxes.restype = POINTER(DETECTION)
        
        make_network_boxes = self._dll_lib.make_network_boxes
        make_network_boxes.argtypes = [c_void_p]
        make_network_boxes.restype = POINTER(DETECTION)
        
        free_detections = self._dll_lib.free_detections
        free_detections.argtypes = [POINTER(DETECTION), c_int]
        
        free_ptrs = self._dll_lib.free_ptrs
        free_ptrs.argtypes = [POINTER(c_void_p), c_int]
        
        network_predict = self._dll_lib.network_predict
        network_predict.argtypes = [c_void_p, POINTER(c_float)]
        
        reset_rnn = self._dll_lib.reset_rnn
        reset_rnn.argtypes = [c_void_p]
        
        load_net = self._dll_lib.load_network
        load_net.argtypes = [c_char_p, c_char_p, c_int]
        load_net.restype = c_void_p
        
        do_nms_obj = self._dll_lib.do_nms_obj
        do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]
        
        do_nms_sort = self._dll_lib.do_nms_sort
        do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]
        
        free_image = self._dll_lib.free_image
        free_image.argtypes = [IMAGE]
        
        letterbox_image = self._dll_lib.letterbox_image
        letterbox_image.argtypes = [IMAGE, c_int, c_int]
        letterbox_image.restype = IMAGE
        
        load_meta = self._dll_lib.get_metadata
        load_meta.argtypes = [c_char_p]
        load_meta.restype = METADATA
        
        load_image = self._dll_lib.load_image_color
        load_image.argtypes = [c_char_p, c_int, c_int]
        load_image.restype = IMAGE
        
        rgbgr_image = self._dll_lib.rgbgr_image
        rgbgr_image.argtypes = [IMAGE]
        
        predict_image = self._dll_lib.network_predict_image
        predict_image.argtypes = [c_void_p, IMAGE]
        predict_image.restype = POINTER(c_float)
    
    
    def detect(self, net, meta, image, thresh, hier_thresh=.5, nms=.45):
        im = self._dll_lib.load_image_color(image, 0, 0)
        num = c_int(0)
        pnum = pointer(num)
        self._dll_lib.network_predict_image(net, im)
        dets = self._dll_lib.get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum)
        num = pnum[0]
        if (nms): self._dll_lib.do_nms_obj(dets, num, meta.classes, nms);
    
        res = []
        for j in range(num):
            for i in range(meta.classes):
                if dets[j].prob[i] > 0:
                    b = dets[j].bbox
                    res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
        res = sorted(res, key=lambda x: -x[1])
        wh = (im.w,im.h)
        self._dll_lib.free_image(im)
        self._dll_lib.free_detections(dets, num)
        return res,wh


    def _dknet_label_conversion(self, R,img_width,img_height):
        
        WH = np.array([img_width,img_height],dtype=float)
        L  = []
        for r in R:
            center = np.array(r[2][:2])/WH
            wh2 = (np.array(r[2][2:])/WH)*.5
            L.append(Label(ord(r[0]),tl=center-wh2,br=center+wh2,prob=r[1]))
            
        return L

        
    def _IOU(self, tl1,br1,tl2,br2):
        
        wh1,wh2 = br1-tl1,br2-tl2
        assert((wh1>=.0).all() and (wh2>=.0).all())
        
        intersection_wh = np.maximum(np.minimum(br1,br2) - np.maximum(tl1,tl2),0.)
        intersection_area = np.prod(intersection_wh)
        area1,area2 = (np.prod(wh1),np.prod(wh2))
        union_area = area1 + area2 - intersection_area;
        return intersection_area/union_area
    
    
    def _IOU_labels(self, l1,l2):
        return self._IOU(l1.tl(),l1.br(),l2.tl(),l2.br())
    
    
    def _nms(self, labels,iou_threshold=.5):
    
        selectedLabels = []
        labels.sort(key=lambda l: l.prob(),reverse=True)
        
        for label in labels:
    
            non_overlap = True
            for sel_label in selectedLabels:
                if self._IOU_labels(label,sel_label) > iou_threshold:
                    non_overlap = False
                    break
    
            if non_overlap:
                selectedLabels.append(label)
    
        return selectedLabels
    
    
    def _recognize(self, view):
        
        npArray = self._arraySpecificProcessor.getDetectionViewAsRectangleArray(view)
        
        return self._recognizeOfNpArray(ImagePart_Cls(npArray))


        
    def _recognizeOfNpArray(self, imagePart):
        
        # npArray shall go thought temporary file since compiled solution uses stbi_load to define an object
        imagePart.write(str(self._tempImgFile_filePath), createDir = True)
        
        R,(width,height) = self.detect(self._ocr_net, self._ocr_meta, self._tempImgFile_filePath_bytes, thresh=0.1, nms=None)
        
        if len(R):

            L = self._dknet_label_conversion(R,width,height)
            L = self._nms(L,.45)

            L.sort(key=lambda x: x.tl()[0])
            numbers = "".join([chr(x.cl()) for x in L])
        else:
            numbers = None
            
        return RecognizedPlateNumbers_Cls(numbers)
    
    
    @staticmethod
    def getLicense():
        return License_Cls(
            type_ = "MIT",
            srcCodeLocation = "https://github.com/sergiomsilva/alpr-unconstrained",
            fullStatement = """
Copyright (C) 2018, Sergio Montazzolli Silva and Claudio Rosito Jung

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

If you use results produced by our code in any publication,
please cite our paper:

Sergio Montazzolli Silva and Claudio Rosito Jung,
"License Plate Detection and Recognition in Unconstrained Scenarios",
In Proceedings of the European Conference on Computer Vision (ECCV),
pp. 580-596. 2018.  """)


if __name__ == "__main__":
    
    from NonPythonFiles.WorkersFiles.ContentGenerators.PlatesMania import PlatesMania_platesImages_dir
    
    imagePath = PlatesMania_platesImages_dir / "PL_BAU_1Z5LD.png"
    
    ocr = EasyOCR_Cls()
    
    def readLpNumbers(imagePath):
        image = Image_Cls(imagePath)
        output = ocr._recognizeOfNpArray(image)
        
        return output.getFeatures()
    
    print(readLpNumbers(imagePath))














        
