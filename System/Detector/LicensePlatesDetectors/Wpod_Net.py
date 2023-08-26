'''
Created on 9 sty 2021

@author: piotr
'''
import cv2
import numpy as np
import logging
import pathlib
from os.path import splitext
from Detections.DetectionsMap import DetectionsMap_Cls
from Detections.Detection import Tetragon_Cls
from Space.Point import Point_Cls
from ObjectsDetectable.Classes import LicensePlateID
from Detector.LicensePlatesDetectors.LicensePlatesDetector import LicensePlatesDetector_AbstCls
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Path
from NonPythonFiles.WorkersFiles.Detectors.WpodNet import WpodNet_netModelConfig_path
from CommonTools.ContextManagers import PrintingDisabler_Cls
from SW_Licensing.SW_License import License_Cls




class Wpod_Net_Cls(LicensePlatesDetector_AbstCls):
    
    @staticmethod
    def getName(): 
        return "WpodNet"
        
    @staticmethod
    def getDescription():
        return "AI license plate detector in form of tetragon (not only a Bounding Box)"
    
    @staticmethod
    def getLicense():
        return License_Cls(
            type_ = "MIT License",
            srcCodeLocation = "https://github.com/quangnhat185/Plate_detect_and_recognize",
            fullStatement = """MIT License

Copyright (c) 2020 Quang Nguyen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
            """)
            
    def __init__(self, 
                 wpod_net_path = UserCfg_Path(
                     name="Model file", 
                     description="Model file path", 
                     path = WpodNet_netModelConfig_path)
                 ):
        
        # Resolve worker arguments in case of direct use(skipping dynamic configuration mechanism)
        wpod_net_path = self.resolveArgument(wpod_net_path)
        
        wpod_net_path = pathlib.Path(wpod_net_path)
        
        if not wpod_net_path.exists():
            wpod_net_path = pathlib.Path(__file__).absolute().parent.joinpath(wpod_net_path)
        
        wpod_net_path = str(wpod_net_path)
        
        import tensorflow as tf
        tf.get_logger().setLevel(logging.ERROR)
        self.model = self._load_model(wpod_net_path)
        
        LicensePlatesDetector_AbstCls.__init__(self)
    
    

    def _detect(self, nparray):
        detections = DetectionsMap_Cls()
        
        if nparray is not None:
            platesCoordinates = self._get_plate(nparray)
            
            for plateCoordinates in platesCoordinates:
                x_coords = plateCoordinates[0]
                y_coords = plateCoordinates[1]
                
                tetragonPoints = []
                
                for index in range(4):
                    
                    y_coord = self.limitFloatFrom0To1(y_coords[index] / nparray.shape[0])
                    x_coord = self.limitFloatFrom0To1(x_coords[index] / nparray.shape[1])
                    
                    tetragonPoints.append(Point_Cls(x_coord = x_coord, y_coord = y_coord))
                
                detections.addDetection(Tetragon_Cls(class_ = LicensePlateID, vertexes = tetragonPoints))
        
        return detections


    def _getWH(self, shape):
        return np.array(shape[1::-1]).astype(float)


    def _IOU(self, tl1, br1, tl2, br2):
        wh1, wh2 = br1-tl1, br2-tl2
        assert((wh1 >= 0).all() and (wh2 >= 0).all())
        
        intersection_wh = np.maximum(np.minimum(br1, br2) - np.maximum(tl1, tl2), 0)
        intersection_area = np.prod(intersection_wh)
        area1, area2 = (np.prod(wh1), np.prod(wh2))
        union_area = area1 + area2 - intersection_area
        return intersection_area/union_area


    def _IOU_labels(self, l1, l2):
        return self._IOU(l1.tl(), l1.br(), l2.tl(), l2.br())


    def _nms(self, Labels, iou_threshold=0.5):
        SelectedLabels = []
        Labels.sort(key=lambda l: l.prob(), reverse=True)
        
        for label in Labels:
            non_overlap = True
            for sel_label in SelectedLabels:
                if self._IOU_labels(label, sel_label) > iou_threshold:
                    non_overlap = False
                    break
    
            if non_overlap:
                SelectedLabels.append(label)
        return SelectedLabels



    def _find_T_matrix(self, pts, t_pts):
        A = np.zeros((8, 9))
        for i in range(0, 4):
            xi = pts[:, i]
            xil = t_pts[:, i]
            xi = xi.T
            
            A[i*2, 3:6] = -xil[2]*xi
            A[i*2, 6:] = xil[1]*xi
            A[i*2+1, :3] = xil[2]*xi
            A[i*2+1, 6:] = -xil[0]*xi
    
        [U, S, V] = np.linalg.svd(A)
        U, S # unused
        H = V[-1, :].reshape((3, 3))
        return H


    def _getRectPts(self, tlx, tly, brx, bry):
        return np.matrix([[tlx, brx, brx, tlx], [tly, tly, bry, bry], [1, 1, 1, 1]], dtype=float)
    
    
    def _normal(self, pts, side, mn, MN):
        pts_MN_center_mn = pts * side
        pts_MN = pts_MN_center_mn + mn.reshape((2, 1))
        pts_prop = pts_MN / MN.reshape((2, 1))
        return pts_prop
    

    # Reconstruction function from predict value into plate crpoped from image
    def _reconstruct(self, I, Iresized, Yr, lp_threshold):
        # 4 max-pooling layers, stride = 2
        net_stride = 2**4
        side = ((208 + 40)/2)/net_stride
    
        # one line and two lines license plate size
        one_line = (470, 110)
        two_lines = (280, 200)
    
        Probs = Yr[..., 0]
        Affines = Yr[..., 2:]
    
        xx, yy = np.where(Probs > lp_threshold)
        # CNN input image size 
        WH = self._getWH(Iresized.shape)
        # output feature map size
        MN = WH/net_stride
    
        vxx = vyy = 0.5 #alpha
        base = lambda vx, vy: np.matrix([[-vx, -vy, 1], [vx, -vy, 1], [vx, vy, 1], [-vx, vy, 1]]).T
        labels = []
        labels_frontal = []
    
        for i in range(len(xx)):
            x, y = xx[i], yy[i]
            affine = Affines[x, y]
            prob = Probs[x, y]
    
            mn = np.array([float(y) + 0.5, float(x) + 0.5])
    
            # affine transformation matrix
            A = np.reshape(affine, (2, 3))
            A[0, 0] = max(A[0, 0], 0)
            A[1, 1] = max(A[1, 1], 0)
            # identity transformation
            B = np.zeros((2, 3))
            B[0, 0] = max(A[0, 0], 0)
            B[1, 1] = max(A[1, 1], 0)
    
            pts = np.array(A*base(vxx, vyy))
            pts_frontal = np.array(B*base(vxx, vyy))
    
            pts_prop = self._normal(pts, side, mn, MN)
            frontal = self._normal(pts_frontal, side, mn, MN)
    
            labels.append(_DLabel(0, pts_prop, prob))
            labels_frontal.append(_DLabel(0, frontal, prob))
            
        final_labels = self._nms(labels, 0.1)
        final_labels_frontal = self._nms(labels_frontal, 0.1)
    
        #print(final_labels_frontal)
        #assert final_labels_frontal, "No License plate is found!"
        
        TLp = []
        Cor = []
        if len(final_labels):
            # LP size and type
            out_size, lp_type = (two_lines, 2) if ((final_labels_frontal[0].wh()[0] / final_labels_frontal[0].wh()[1]) < 1.7) else (one_line, 1)
            final_labels.sort(key=lambda x: x.prob(), reverse=True)
            for _, label in enumerate(final_labels):
                t_ptsh = self._getRectPts(0, 0, out_size[0], out_size[1])
                ptsh = np.concatenate((label.pts * self._getWH(I.shape).reshape((2, 1)), np.ones((1, 4))))
                H = self._find_T_matrix(ptsh, t_ptsh)
                Ilp = cv2.warpPerspective(I, H, out_size, borderValue=0)
                TLp.append(Ilp)
                Cor.append(ptsh)
        else:
            lp_type = None
            
        return final_labels, TLp, lp_type, Cor
    
    
    def _detect_lp(self, model, I, max_dim, lp_threshold):
        min_dim_img = min(I.shape[:2])
        factor = float(max_dim) / min_dim_img
        w, h = (np.array(I.shape[1::-1], dtype=float) * factor).astype(int).tolist()
        Iresized = cv2.resize(I, (w, h))
        T = Iresized.copy()
        T = T.reshape((1, T.shape[0], T.shape[1], T.shape[2]))
        with PrintingDisabler_Cls():
            Yr = model.predict(T)
        Yr = np.squeeze(Yr)
        #print(Yr.shape)
        L, TLp, lp_type, Cor = self._reconstruct(I, Iresized, Yr, lp_threshold)
        return L, TLp, lp_type, Cor
    
    
    
    def _load_model(self, path):
        from keras.models import model_from_json
        try:
            path = splitext(path)[0]
            with open('%s.json' % path, 'r') as json_file:
                model_json = json_file.read()
            model = model_from_json(model_json, custom_objects={})
            model.load_weights('%s.h5' % path)
            print("Loading model successfully...")
            return model
        except Exception as e:
            raise e
    
    
    def _preprocess_image(self, img,resize=False):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img / 255
        if resize:
            img = cv2.resize(img, (224,224))
        return img

    # forward image through model and return plate's image and coordinates
    # if error "No Licensese plate is founded!" pop up, try to adjust Dmin
    def _get_plate(self, img, Dmax=608, Dmin=256):
        img = self._preprocess_image(img)
        ratio = float(max(img.shape[:2])) / min(img.shape[:2])
        side = int(ratio * Dmin)
        bound_dim = min(side, Dmax)
        _ , _, _, cor = self._detect_lp(self.model, img, bound_dim, lp_threshold=0.5)
        return cor



class _Label:
    def __init__(self, cl=-1, tl=np.array([0., 0.]), br=np.array([0., 0.]), prob=None):
        self.__tl = tl
        self.__br = br
        self.__cl = cl
        self.__prob = prob

    def __str__(self):
        return 'Class: %d, top left(x: %f, y: %f), bottom right(x: %f, y: %f)' % (
        self.__cl, self.__tl[0], self.__tl[1], self.__br[0], self.__br[1])

    def copy(self):
        return _Label(self.__cl, self.__tl, self.__br)

    def wh(self): return self.__br - self.__tl

    def cc(self): return self.__tl + self.wh() / 2

    def tl(self): return self.__tl

    def br(self): return self.__br

    def tr(self): return np.array([self.__br[0], self.__tl[1]])

    def bl(self): return np.array([self.__tl[0], self.__br[1]])

    def cl(self): return self.__cl

    def area(self): return np.prod(self.wh())

    def prob(self): return self.__prob

    def set_class(self, cl):
        self.__cl = cl

    def set_tl(self, tl):
        self.__tl = tl

    def set_br(self, br):
        self.__br = br

    def set_wh(self, wh):
        cc = self.cc()
        self.__tl = cc - .5 * wh
        self.__br = cc + .5 * wh

    def set_prob(self, prob):
        self.__prob = prob


class _DLabel(_Label):
    def __init__(self, cl, pts, prob):
        self.pts = pts
        tl = np.amin(pts, axis=1)
        br = np.amax(pts, axis=1)
        _Label.__init__(self, cl, tl, br, prob)
        




