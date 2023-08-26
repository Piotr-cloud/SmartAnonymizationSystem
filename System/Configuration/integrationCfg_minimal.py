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

from Detector.FacesDetectors.Dlib_HOG import Dlib_HOG_Cls
 
# Detectors - Import end here

workersIncluder.include(Dlib_HOG_Cls)
 
 
###################################################################################
# Trackers
###################################################################################

# Trackers - Import start here

# Trackers - Import end here

 
###################################################################################
# Track stabilizer
###################################################################################

# Track stabilizers - Import start here

# Track stabilizers - Import end here


###################################################################################
# Anonymizers
###################################################################################
# Anonymizers - Import start here


# Classic anonymizers
from Anonymizer.ClassicAnonymizer.WholePageMasked.WholePageMaskedAnonymizer import GaussianBlur_MaskedPage_Anonymizer_Cls

# Anonymizers - Import end here

workersIncluder.include(GaussianBlur_MaskedPage_Anonymizer_Cls)


###################################################################################
# Content Generators
###################################################################################

# Content Generators - Import start here
 
 
# Content Generators - Import end here
 
 
###################################################################################
# Content Recognizers
###################################################################################

 
 

 
###################################################################################
# Content Swappers
###################################################################################

# Content Swappers - Import start here

 
# Content Swappers - Import end here


###################################################################################
#  >> Including END <<
###################################################################################



#workersIncluder.printContents()
