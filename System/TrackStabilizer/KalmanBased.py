'''
Created on Jan 3, 2023

@author: piotr
'''
from TrackStabilizer.TrackStabilizer import TrackStabilizer_AbstCls
from filterpy.kalman.kalman_filter import KalmanFilter
import numpy as np
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Int_Limited,\
    UserCfg_Float_Limited
from SW_Licensing.SW_License import HostSWLicense_Cls




class KalmanBasedStabilizer_Cls(TrackStabilizer_AbstCls):
    
    @staticmethod
    def getName(): 
        return "KalmanBasedStabilizer"
    
    @staticmethod
    def getDescription():
        return "Kalman based stabilizer using python package filterpy.kalman"

    @staticmethod
    def getClassesServiced():
        return "All"

    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    
    def __init__(self,
                 
                 expectedNoiseLvl = UserCfg_Float_Limited(name = "Expected noise level",
                                                          description = "Gauss noise cancellation reaction. The higher noise expected the higher this param should be",
                                                          lower_limit = 0.,
                                                          defaultValue = 10.,
                                                          upper_limit = 10000.),
                 
                 covarianceLvl = UserCfg_Float_Limited(name = "Covariance level",
                                                       description = "Kalman covariance factor that says how much we trust detections instead of kalman model dynamics. The higher the value is the less kalman dynamics is used",
                                                       lower_limit = 0.,
                                                       defaultValue = 10.,
                                                       upper_limit = 1.e10),
                 
                 allowedDetectionGap = UserCfg_Int_Limited(name = "Allowed gap <not tested>",
                                                           description = "Number of consecutive frames with no detection until filter gets reset",
                                                           lower_limit = 0,
                                                           defaultValue = 0,
                                                           upper_limit = 1000)):
        
        self._expectedNoiseLvl      =  self.resolveArgument(expectedNoiseLvl)
        self._covarianceLvl         =  self.resolveArgument(covarianceLvl)
        self._allowedDetectionGap   =  self.resolveArgument(allowedDetectionGap)
        
        TrackStabilizer_AbstCls.__init__(self)
        
        
    def _convert_box_2_X(self, box):
        """
        [x1,y1,x2,y2] -> [x,y,s,r] 
        where x,y s is the scale/area and r is
        the aspect ratio
        """
        w = box[2] - box[0]
        h = box[3] - box[1]
        x = box[0] + w/2.
        y = box[1] + h/2.
        s = w * h        #scale is just area
        r = w / float(h)
        return np.array([x, y, s, r]).reshape((4, 1))
    
    
    def _convert_X_2_box(self, x):
        """
        [x,y,s,r] -> [x1,y1,x2,y2]
        where x,y s is the scale/area and r is
        the aspect ratio
        """
        w = np.sqrt(x[2] * x[3])
        h = x[2] / w
        
        x1 = self.limitFloatFrom0To1(float(x[0]-w/2.))
        y1 = self.limitFloatFrom0To1(float(x[1]-h/2.))
        x2 = self.limitFloatFrom0To1(float(x[0]+w/2.))
        y2 = self.limitFloatFrom0To1(float(x[1]+h/2.))
        
        return x1,y1,x2,y2
    
    
    def _getNewFilter(self, initialBoxFormatted):
        
        kf = KalmanFilter(dim_x=7, dim_z=4) 
        kf.F = np.array([[1,0,0,0,1,0,0],[0,1,0,0,0,1,0],[0,0,1,0,0,0,1],[0,0,0,1,0,0,0],    [0,0,0,0,1,0,0],[0,0,0,0,0,1,0],[0,0,0,0,0,0,1]])
        kf.H = np.array([[1,0,0,0,0,0,0],[0,1,0,0,0,0,0],[0,0,1,0,0,0,0],[0,0,0,1,0,0,0]])

        kf.R[2:,2:] *= self._expectedNoiseLvl
        kf.P[4:,4:] *= 1000. #give high uncertainty to the unobservable initial velocities
        kf.P        *= self._covarianceLvl
        kf.Q[-1,-1] *= 0.01
        kf.Q[4:,4:] *= 0.01
        
        kf.x[:4] = initialBoxFormatted
        
        return kf
    
    
    def _stabilize(self, obj_):
        
        kf = None
        
        gapSize = 0
        
        for view in obj_.iterFramesViews():
            
            if view is None:
                
                if kf is not None:
                    
                    gapSize += 1
                    
                    if gapSize > self._allowedDetectionGap:
                        kf = None
                    else:
                        kf.predict()
                    
            else:
                detection = view.getDetection()
                shape = detection.getShape()
                
                box = shape.getExtremumCoordinates()[0]
                
                measured_X = self._convert_box_2_X(box)
                
                if kf is None:
                    kf = self._getNewFilter(measured_X)
                
                else:
                    kf.predict()
                    kf.update(measured_X)
                    
                    new_X = kf.x
                    
                    new_box = self._convert_X_2_box(new_X)
                    
                    if not np.any(np.isnan(new_box)): # do not apply stabilization if any issue
                        shape.transformIntoBox(*new_box)






















