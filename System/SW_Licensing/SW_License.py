'''
Created on May 13, 2023

@author: piotr
'''

class License_Cls(object):


    def __init__(self, 
                 type_,
                 srcCodeLocation,
                 fullStatement):
        '''
        type_ stands for license type and can be something like "MIT", "Apache License",  "Freeware", "GNU General Public License" or "GPL"
        Constructor
        '''
        assert isinstance(type_, str)
        assert isinstance(fullStatement, str)
        assert isinstance(srcCodeLocation, str)
        
        self._type = type_
        self._fullStatement = fullStatement
        self._srcCodeLocation = srcCodeLocation
        
        
    def getType(self):
        return self._type
    
    def getFullStatement(self):
        return self._fullStatement
    
    def getSrcCodeLocation(self):
        return self._srcCodeLocation




class HostSWLicense_Cls(License_Cls):
    """
    License that apllies to all the SW developed in this project. For more details see LICENSE.txt file located in the root folder in repository 
    """
    
    def __init__(self):
        License_Cls.__init__(self,
                             "LICENSE.txt",
                             "See project git repository origin url",
                             "This solution is developed as a part of the project. For more licensing info see file LICENSE.txt located in the root folder in repository ")






