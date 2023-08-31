'''
Created on Oct 22, 2022

@author: piotr
'''
from ContentGenerator.LicensePlateGenerator.LicensePlateGenerator import LicensePlateGenerator_AbstCls
from ContentRecognizer.ContentRecognizer import ContentRecognizer_AbstCls
from Configuration.ConfigurationObjects.WorkerConfiguration import ChoiceOf_WorkerConfigurationObject_Cls
import random
import re
from Configuration.ConfigurationObjects.WorkerConfigurationArgument import UserCfg_Int_Limited,\
    UserCfg_Bool
from NonPythonFiles.WorkersFiles.ContentGenerators.PlatesMania import PlatesMania_platesImages_dir
import copy
from Space._2D.Image import Image_Cls
from SW_Licensing.SW_License import HostSWLicense_Cls
import os

#random.seed(2)

class _Node_Cls(object):
    
    def __init__(self):
        
        self._subNodes_dict = {}
        self._leaf = None # node can link to sub nodes or be a leaf or both at the same time, self._leaf keeps leaf sign is any
        
        self._workData_nodesSize_dict = {}
        self._leafUsed_flag = True
        
        self._superNode = None
        self._size = 0
                
    
    def _assignSuperNode(self, node):
        
        assert isinstance(node, _Node_Cls)
        
        if self._superNode is not node:
            assert self._superNode is None
            self._superNode = node
    
    
    def addLeaf(self, string_, targetData, originString = ""):
        
        if not originString:
            originString = string_
        
        if string_:
            
            sign = string_[0]
            string_ = string_[1:]
            
            if sign not in self._subNodes_dict:
                self._subNodes_dict[sign] = _Node_Cls()
            
            subNode = self._subNodes_dict[sign]
            subNode._assignSuperNode(self)
            
            ret = subNode.addLeaf(string_, targetData, originString)
            
            if ret:
                self._size += 1
                
            return ret
                
        else:
            
            if self._leaf != targetData:
                
                if self._leaf is None:
                    
                    assert self._leaf is None
                
                    self._leaf = targetData
                    self._size += 1
                    
                    return True
                
                else:
                    print("Warning! Path: \"" + str(originString) + "\" is repeated! Leaf: \"" + targetData + "\" skipped" )
                    return False
            
            else:
                
                return False # repeated
    
    
    def _chooseOne(self, values):
        return random.choice(values)
    
    
    def _chooseOne_Weighted(self, value_2_weights_dict):
        
        values = []
        weights = []
        
        for value, weight in value_2_weights_dict.items():
            values.append(value)
            weights.append(weight)
            
        return random.choices(population = values, weights = weights, k = 1)[0]
    
    
    def _popRandomLeaf(self):
        
        choices_dict = {}
        
        if not self._isEmpty():
            
            if self._isFullyPoped():
                self._reloadLeafs()
                
            if self._workData_nodesSize_dict:
                choices_dict.update(self._workData_nodesSize_dict)
            
            if not self._leafUsed_flag:
                choices_dict[''] = 1
            
            if choices_dict:
                choice = self._chooseOne_Weighted(choices_dict)
                
                if choice == "":
                    self._leafUsed_flag = True
                    return self._leaf
                
                else:
                    popedLeaf = self._subNodes_dict[choice]._popRandomLeaf()
                    
                    if popedLeaf is not None:
                        self._workData_nodesSize_dict[choice] -= 1
                        
                        if self._workData_nodesSize_dict[choice] == 0:
                            del self._workData_nodesSize_dict[choice]
                        
                    return popedLeaf
    
    
    def _isEmpty(self):
        return self._size == 0
    
    
    def _hasAllSubNodesEmpty(self):
        return all([subNode._isEmpty() for subNode in self._subNodes_dict.values()])
    
    
    def _isFullyPoped(self):
        return not self._workData_nodesSize_dict and self._leafUsed_flag
    
    
    def _findMostMatchingNode(self, beginning_str):
            
        if not beginning_str:
            return self
        
        else:
            sign = beginning_str[0]
            beginning_str = beginning_str[1:]
            
            if sign in self._subNodes_dict:
                subNode = self._subNodes_dict[sign]
                
                return subNode._findMostMatchingNode(beginning_str)
            
            elif sign in ["0","O"]: # special case to keep "0" close to "O"
                
                if sign == "0":   sign = "O"
                else:             sign = "0"
                    
                if sign in self._subNodes_dict:
                    subNode = self._subNodes_dict[sign]
                    
                    return subNode._findMostMatchingNode(beginning_str)
                else:
                    return self
            else:
                return self
    
    
    def _getNodeAtPath(self, path_):
        
        if not path_:
            return self
        
        else:
            sign = path_[0]
            path_ = path_[1:]
            
            return self._subNodes_dict[sign]._getNodeAtPath(path_)
    
    
    def _findPathToMostMatchingNode(self, beginning_str):
        
        commonPart = ""
        
        if beginning_str:
            sign = beginning_str[0]
            
            if sign in self._subNodes_dict:
                
                subNode = self._subNodes_dict[sign]
                
                commonPart += sign + subNode._findPathToMostMatchingNode(beginning_str[1:])
            
        return commonPart
    
    
    def _findMostMatchingNode_alternative(self, beginning_str):
        
        path_ = self._findPathToMostMatchingNode(beginning_str)
        matchingNode = self._getNodeAtPath(path_)
        
        return matchingNode
        
    
    def getLeafData(self, beginning_str):
        """
        Returns most matching(but not exact) plate data
        or None is no plate data available
        This function handles poping plate data in regards to beginning_str
        """
        matchingNode = self._findMostMatchingNode(beginning_str)
        
        if matchingNode is not None:
            return matchingNode._popRandomLeaf()
        
    
    
    def _getSize(self):
        return self._size
    
    def _reloadLeafs(self, printStatement_flag = False):
        
        if printStatement_flag:
            print("  <<< reloading >>>")
        
        self._workData_nodesSize_dict = {}
        
        for sign, subNode in self._subNodes_dict.items():
            subNode._reloadLeafs(False)
            subNodeSize = subNode._getSize()
            self._workData_nodesSize_dict[sign] = subNodeSize
        
        if self._leaf is not None:
            self._leafUsed_flag = False
            
    
    def _getNumberOfActiveLeafs(self):
        return (0 if self._leafUsed_flag else 1) + sum(self._workData_nodesSize_dict.values())
        
    
    def _getStrLines(self, activeOnly):
        
        lines = []
        
        if activeOnly:
            
            leafAvailable = self._leaf if self._leafUsed_flag else None
            subNodes_signs = self._workData_nodesSize_dict.keys()
        
        else:
            leafAvailable = self._leaf
            subNodes_signs = self._subNodes_dict.keys()
        
        
        if leafAvailable:
            lines.append("   ->  " + str(self._leaf))
            
        for sign in subNodes_signs:
            lines.append(sign)
            lines.extend([" " * 2 + line_ for line_ in self._subNodes_dict[sign]._getStrLines(activeOnly)])
            
        return lines
    
    
    def __str__(self, activeOnly = True):
        
        lines = self._getStrLines(activeOnly)
        if lines:
            output_str = "\n".join(lines) + "\n"
        else:
            output_str = "<<< No data >>>"
            
        return output_str
    
    
    def __repr__(self):
        return str(self)
            
    
    def _updateLeafsNumber(self):
        
        size = 0
        
        for subKey in self._subNodes_dict:
            size += self._subNodes_dict[subKey]._getSize()
        
        if size != self._size:
            self._size = size
            if self._superNode:
                self._superNode._updateLeafsNumber()
        


class Platesmania_Cls(LicensePlateGenerator_AbstCls):
    
    '''
    Offline
    classdocs
    '''

    @staticmethod
    def getName(): 
        return "PlatesMania"
    
    @staticmethod
    def getDescription():
        return "Based on platesMania online generator. Url: https://platesmania.com/"
    
    @staticmethod
    def getLicense():
        return HostSWLicense_Cls()
    
    
    def __init__(self, 
                 recognizer = ChoiceOf_WorkerConfigurationObject_Cls(name = "Plate recognizer",
                                                                     description = "Plate recognizer that is used to identify plate numbers",
                                                                     workersBaseType = ContentRecognizer_AbstCls,
                                                                     activatable = True, # Plate recognizer is optional
                                                                     singleChoice_flag = True),
                 
                 startingLettersNumber = UserCfg_Int_Limited(name = "Keep original starting letters",
                                                             description = "",
                                                             lower_limit = 1,
                                                             defaultValue = 4,
                                                             upper_limit = 4),
                 
                 analyseAllPossiblePerspectives = UserCfg_Bool(name = "Apply shortest Levenshtein distance",
                                                             description = "Application of Lavenshtein distance to all occurences of tracked license plate to get the most real recognition before generation new graphical representation of the object",
                                                             defaultValue = False),
                 ):
        '''    
        Constructor
        '''
        recognizer = self.resolveArgument(recognizer)
        startingLettersNumber = self.resolveArgument(startingLettersNumber)
        analyseAllPossiblePerspectives = self.resolveArgument(analyseAllPossiblePerspectives)
        
        if recognizer is not None:
            assert isinstance(recognizer, ContentRecognizer_AbstCls)
            
        assert isinstance(startingLettersNumber, int)
        assert isinstance(analyseAllPossiblePerspectives, bool)
        
        self._startingLettersNumber = startingLettersNumber
        self._analyseAllPossiblePerspectives = analyseAllPossiblePerspectives
        
        LicensePlateGenerator_AbstCls.__init__(self, recognizer)
        
        self._dataDir = PlatesMania_platesImages_dir
        
        self._platesTrees_dict = {}
        self._loadPlatesDict()
    
    
    def _loadPlatesDict(self):
    
        loadedDict = {}
            
        for _, _, fileNames in os.walk(str(self._dataDir)):
            
            for fileName in fileNames:
                fileName = fileName
                try:
                    country, region, numbers = fileName.split(".")[0].split("_") # filename shall follow the pattern: <country>_<region>_<numbers>.<extension>
                except:
                    continue
                
                country, region, numbers = country.upper(), region.upper(), numbers.upper()
                
                if country not in loadedDict: loadedDict[country] = {}
                if region not in loadedDict[country]:  loadedDict[country][region] = {}
                loadedDict[country][region][numbers] = fileName
                    
            break # no recursion - search for files only in dir self._dataDir not in subdirectories 

        for country in loadedDict:
            self._platesTrees_dict[country] = _Node_Cls()
        
            platesTree = self._platesTrees_dict[country]
            
            for region in loadedDict[country]:
                
                
                for numbers in loadedDict[country][region]:
                    
                    plateSigns = region + numbers
                    plateData = loadedDict[country][region][numbers]
                    
                    platesTree.addLeaf(plateSigns, plateData)
                
            platesTree._reloadLeafs(False)
            
    
    def _getNodeWithPath(self, searchTree_dict, path_, superPath = ""):
        
        assert searchTree_dict, "Cannot use empty dicts"
        
        if not path_:
            return superPath, searchTree_dict
        else:
            sign = path_[0]
            path_ = path_[1:]
            if sign not in searchTree_dict or not searchTree_dict[sign]: # node is valid if contains at least one plate that is different(in case of full path provision) 
                return superPath, searchTree_dict
            else:
                superPath += sign
                return self._getNodeWithPath(searchTree_dict[sign], path_, superPath)
    
    
    def _getAlternativePlatePath(self, country, begining):
        
        begining = begining.upper()
        
        plateData = self._platesTrees_dict[country].getLeafData(begining)
        platePath = self._dataDir / plateData
        
        return platePath
    
    
    def _getAlternativePlate(self, country, begining):
        
        platePath = self._getAlternativePlatePath(country, begining)
        plate_npArray = Image_Cls(platePath).getNpArrayCopy()
        
        return plate_npArray
    
    
    def _useRandomLeaf(self, node, superPath = ""):
        
        output = ""
        
        if node:
            sign = self._chooseBranch(node)
            
            output += sign
            
            superPath += sign
            
            if node[sign]:
                output += self._useRandomLeaf(node[sign], superPath)
                
            if not node[sign]:
                del node[sign]
            
        return output
        
    
    def _chooseBranch(self, node):
        branches = list(node.keys())
        return random.choice(branches)
    
    
    def _getFreshNode(self, originalSearchTree_dict, path_):
        
        while path_: # move src dict node forward to matching point
            sign, path_ = path_[0], path_[1:]
            
            originalSearchTree_dict = originalSearchTree_dict[sign]
        
        return copy.deepcopy(originalSearchTree_dict)

    
    def _generate_LP(self, view):
        
        recognition = view.getRecognition()
        
        country = self._choosePlateCountry()
        
        beginning = ""
        
        if recognition:
            self.getRecognizer().validateRecognitionCls(recognition)
            
            platesNumbers = recognition.getFeatures()
            
            if platesNumbers[0].isalpha():
                
                findResult = re.findall("^\w+", platesNumbers)
                
                if findResult:
                    beginning = findResult[0][:self._startingLettersNumber]
                            
        return self._getPlateImage(country, beginning)
    
    
    def _choosePlateCountry(self):
        return random.choice(list(self._platesTrees_dict.keys()))
        
            
    def _getPlateImage(self, country, begining):
        return self._getAlternativePlate(country, begining)
    
    
    def _defineStaticAnonymizedViewReferenceForEachObject(self, objectFound, contentSwapperValidating):
        
        if self._analyseAllPossiblePerspectives:
            
            self._dSAVRFEO_byAnalysingAllPerspectives(objectFound)
            
        else:
            self._dSAVRFEO_byAnonymizingBestView(objectFound, contentSwapperValidating)
    




if __name__ == "__main__":
    
    platesmania = Platesmania_Cls()
    baseNode = platesmania._platesTrees_dict["PL"]

    if 0:
        
        # simple use case
        
        testVector = [
            "BGR56965",
            "BGR56965",
            "",
            "BGR56966",
            "BGR56966",
            "",
            "BGR56967",
            "",
            "BGR83",
            "BGR",
            "BGR",
            "BGR",
            "BGR",
            "BGR",
            "BGR",
            "BGR",
            "BGR",
            "",
            "BGR56965",
            "BGR56965",
            "BGR83790",
            "BGR83790",
            "PO3S888",
            "PO3S802",
            ]
        
        for testData in testVector:
            print((testData + ":").ljust(10), platesmania._getAlternativePlatePath("PL", begining = testData).name)
    
    elif 0:
        
        # error resitance test
        
        import string
        
        cnt = 10e5
        
        def getLeterOrSpace():
            return random.choice(string.ascii_letters + " ")
        
        while cnt:
            cnt -= 1
            string_ = ("".join([getLeterOrSpace() for _ in range(3)])).strip()
            
            print("Begining: " + string_ + "  ", end = "")            
            print(platesmania._getAlternativePlatePath("PL", string_).name)
                
        
    # elif 0:
    #
    #     # outdated test
    #
    #     testData_dict = {
    #         "A1"  : "A1",
    #         "A1a" : "A1a",
    #         "A2"  : "A",
    #         "A12" : "A1",
    #         "B"   : "B",
    #         "B1"  : "B1",
    #         "B2"  : "B2",
    #         "B3"  : "B",
    #         "C"   : "",
    #         "AA1" : "A"
    #     }
    #
    #     print("Tree: \n\n" + str(baseNode) + "\n\n")
    #
    #     for testData_input, testData_output in testData_dict.items(): 
    #         output = baseNode._findPathToMostMatchingNode(testData_input)
    #
    #         statement = "Input: " + testData_input.ljust(7) + " Output: " + output.ljust(7) + " " * 2
    #
    #         if output != testData_output:
    #             statement += "FAILED    Expected: \"" + testData_output + "\""
    #         else:
    #             statement += "OK"
    #
    #         print(statement)
        
    else:
        
        print(baseNode.getLeafData("BA1"))
        print(baseNode.getLeafData("BA1"))
        
        print(baseNode.getLeafData("BB1"))
        print(baseNode.getLeafData("BB1"))
        
        print(baseNode.getLeafData("BB2"))
        print(baseNode.getLeafData("BB2"))
        
        
        print(baseNode.getLeafData("BB"))
        print(baseNode.getLeafData("BB"))
        
        print(baseNode.getLeafData("BB"))
        print(baseNode.getLeafData("BB"))
        
        print(baseNode.getLeafData("B"))
        print(baseNode.getLeafData("A"))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    