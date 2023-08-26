'''
Created on May 6, 2022

@author: piotr

Import all used workers here and include by workersIncluder so then workers becomes available

'''

from Configuration.WorkersIncluder.WorkersIncluder import _WorkersIncluder_Cls

workersIncluder = _WorkersIncluder_Cls()


###################################################################################
#  Global configuration
###################################################################################



###################################################################################
#  >> Including START <<
###################################################################################


###################################################################################
# Detectors
###################################################################################

# Detectors - Import start here


from Detector.FacesDetectors.Haar import Haar_Cls
from Detector.FacesDetectors.Dlib_HOG import Dlib_HOG_Cls
from Detector.FacesDetectors.Dlib_CNN import Dlib_CNN_Cls
from Detector.FacesDetectors.Mtcnn import MTCNN_Cls
from Detector.FacesDetectors.Dnn import Dnn_Cls

from Detector.LicensePlatesDetectors.Wpod_Net import Wpod_Net_Cls
from Detector.MultiClassDetectors.UnderstandAI import UnderstandAI_Cls

from Detector.FacesDetectors.YuNet import YuNet_Cls
from Detector.LicensePlatesDetectors.LPD_YuNet import LPD_YuNet_Cls
 
# Detectors - Import end here

workersIncluder.include(Haar_Cls)
workersIncluder.include(Dlib_HOG_Cls)
workersIncluder.include(Dlib_CNN_Cls)
workersIncluder.include(MTCNN_Cls)
workersIncluder.include(Dnn_Cls)
workersIncluder.include(Wpod_Net_Cls)
workersIncluder.include(UnderstandAI_Cls)

workersIncluder.include(YuNet_Cls)
workersIncluder.include(LPD_YuNet_Cls)
 
 
###################################################################################
# Trackers
###################################################################################

# Trackers - Import start here

from Tracker.DeepSort import DeepSort_Cls
from Tracker.SORT import SORT_Tracker_Cls

# Trackers - Import end here

workersIncluder.include(DeepSort_Cls)
workersIncluder.include(SORT_Tracker_Cls)

 
###################################################################################
# Track stabilizer
###################################################################################

# Track stabilizers - Import start here

from TrackStabilizer.KalmanBased import KalmanBasedStabilizer_Cls

# Track stabilizers - Import end here

workersIncluder.include(KalmanBasedStabilizer_Cls)


###################################################################################
# Anonymizers
###################################################################################
# Anonymizers - Import start here


# Classic anonymizers
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import Blur_MaskedPage_Anonymizer_Cls
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import GaussianBlur_MaskedPage_Anonymizer_Cls
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import ResolutionDowngrade_MaskedPage_Anonymizer_Cls 
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import Black_Anonymizer_Cls
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import WhiteNoise_Anonymizer_Cls
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import AverageColor_Anonymizer_Cls


workersIncluder.include(Blur_MaskedPage_Anonymizer_Cls)
workersIncluder.include(GaussianBlur_MaskedPage_Anonymizer_Cls)
workersIncluder.include(ResolutionDowngrade_MaskedPage_Anonymizer_Cls)
workersIncluder.include(Black_Anonymizer_Cls)
workersIncluder.include(WhiteNoise_Anonymizer_Cls)
workersIncluder.include(AverageColor_Anonymizer_Cls)



# Smart anonymizers
# Common
from Anonymizer.NewContentAnonymizer.CustomAnonymizer import CustomAnonymizer_Cls

# Face
from Anonymizer.NewContentAnonymizer.SmartAnonymizer.FaceSmartAnonymizer.AgentSmith_FaceAnonymizer import AgentSmith_FaceAnonymizer_Cls 

# License plate
from Anonymizer.NewContentAnonymizer.ExamplePaster.LicensePlateExamplePaster import LicensePlateExamplePaster_Cls

# Anonymizers - Import end here

workersIncluder.include(AgentSmith_FaceAnonymizer_Cls)
workersIncluder.include(LicensePlateExamplePaster_Cls)
workersIncluder.include(CustomAnonymizer_Cls)
 

###################################################################################
# Content Generators
###################################################################################

# Content Generators - Import start here
 
from ContentGenerator.FaceGenerator.DeepPrivacy import DeepPrivacy_Cls
from ContentGenerator.LicensePlateGenerator.LicensePlateExample import LicensePlateExampleProvider_Cls
from ContentGenerator.FaceGenerator.FaceExample import FaceExampleProvider_Cls
from ContentGenerator.LicensePlateGenerator.PlatesMania.PlatesMania import Platesmania_Cls
from ContentGenerator.FaceGenerator.ThisPersonDoesNotExist import ThisPersonDoesNotExist_Cls
  
# Content Generators - Import end here

workersIncluder.include(DeepPrivacy_Cls)
workersIncluder.include(FaceExampleProvider_Cls)
workersIncluder.include(LicensePlateExampleProvider_Cls)
workersIncluder.include(Platesmania_Cls)
workersIncluder.include(ThisPersonDoesNotExist_Cls)
 
 
###################################################################################
# Content Recognizers
###################################################################################
from ContentRecognizer.LicensePlateRecognizer.EasyOCR import EasyOCR_Cls

# Content Recognizers - Import start here

workersIncluder.include(EasyOCR_Cls)

# Content Recognizers - Import end here

 
###################################################################################
# Content Swappers
###################################################################################

# Content Swappers - Import start here

from ContentSwapper.CloneSwapper import CloneSwapper_Cls, SeamlessCloneSwapper_Cls
from ContentSwapper.SmartSwapper.FaceSmartSwapper.DlibBasedSwapper import DlibBasedSwapper_Cls
from ContentSwapper.SmartSwapper.FaceSmartSwapper.FaceSmartSwapper_WuHuikai import FaceSmartSwapper_Wuhuikai_Cls
 
# Content Swappers - Import end here

workersIncluder.include(CloneSwapper_Cls)
workersIncluder.include(SeamlessCloneSwapper_Cls)
workersIncluder.include(DlibBasedSwapper_Cls)
workersIncluder.include(FaceSmartSwapper_Wuhuikai_Cls)


###################################################################################
#  >> Including END <<
###################################################################################



#workersIncluder.printContents()
