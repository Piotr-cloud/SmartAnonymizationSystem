'''
Created on Feb 10, 2023

@author: piotr
'''
from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls,\
    ClassProcessingConfiguration_Cls, ClassWorkerChoice_Cls
from Configuration.ConfigurationObjects.WorkerConfiguration import WorkerConfigurationObject_Cls,\
    ChoiceOf_WorkerConfigurationObject_Cls
from Configuration.integrationCfg import workersIncluder
from ObjectsDetectable.ClassesCfg import ClassName_dict
from Configuration.ConfigurationObjects.ConfigurationObject import ConfigurationObject_Activatable_AbstCls
from Configuration.ConfigurationObjects.Choice import Choice_Cls,\
    ListOfChoices_Cls
import random




class NodesBuilder_Cls():
    
    def build(self, object_, upperNode = None, selfActivationObject = None):
        """
        Nested nodes builder
        """
        
        if isinstance(object_, ClassesProcessingConfiguration_Cls):
            choice = object_._classesChoice
            name = choice.getName()
            
            node = Node_Cls(name, upperNode, choice, object_)
            
            for cpc_option in choice.getOptions():
                cpc = cpc_option.getValue()
                
                self.build(cpc, node, cpc_option)
        
        
        elif isinstance(object_, ClassProcessingConfiguration_Cls):
            
            name = ClassName_dict[object_.getClassId()]
            node = Node_Cls(name, upperNode, selfActivationObject, object_)
            
            for baseWorkerChoice in object_:
                self.build(baseWorkerChoice, node, baseWorkerChoice)
        
        
        elif isinstance(object_, ChoiceOf_WorkerConfigurationObject_Cls): # also instances of ClassWorkerChoice_Cls
            
            name = object_.getName()
            node = Node_Cls(name, upperNode, selfActivationObject, object_)
            
            for workerOption in object_.getOptions():
                workerCfg = workerOption.getValue()
                self.build(workerCfg, node, workerOption)
        
        elif isinstance(object_, WorkerConfigurationObject_Cls):
            
            name = object_.getName()
            node = Node_Cls(name, upperNode, selfActivationObject, object_)
            
            for argument in object_._arguments:
                if isinstance(argument, ChoiceOf_WorkerConfigurationObject_Cls):
                    self.build(argument, node, argument)     
        
        return node
    
    
    def getLevelChoices(self, object_):
        
        if isinstance(object_, ClassesProcessingConfiguration_Cls):
            return [object_._classesChoice]
        
        elif isinstance(object_, ClassProcessingConfiguration_Cls):
            return list(object_._workerBaseType_2_choice_dict.values())
        
        elif isinstance(object_, WorkerConfigurationObject_Cls):
            output_list = []
        
            for argument in object_._arguments:
                if isinstance(argument, ChoiceOf_WorkerConfigurationObject_Cls):
                    output_list.append(argument)
        
            return output_list
        
        else:
            return []




class Node_Cls():
    
    def __init__(self, name, upperNode, actvationObject, originObject):
        
        assert isinstance(name, str)
        assert upperNode is None or isinstance(upperNode, Node_Cls)        
        assert isinstance(actvationObject, ConfigurationObject_Activatable_AbstCls)
        
        self.name = name
        self.upperNode = upperNode
        self.actvationObject = actvationObject
        self.originObject = originObject
        self.subNodes = []
        self.activeSubNodes = []
        self.configurationGenerator = None
        self.subNodesWelcomeActivationState_dict = {}
        self.resetNode()
        
        if self.upperNode is not None:
            self.upperNode.assignSubNode(self)
            
    
    
    def getStrLines(self, indent = 0):
        
        output_lines = []
        
        thisLine = " " * indent
        
        if isinstance(self.actvationObject, ConfigurationObject_Activatable_AbstCls):
            thisLine += ConfigurationObject_Activatable_AbstCls.__str__(self.actvationObject)
        
        thisLine += str(self.name)
        
        output_lines.append(thisLine)
        
        for subNode in self.subNodes:
            output_lines.extend(subNode.getStrLines(indent + 3))
        
        return output_lines
    
    
    def activate(self): # wrapped
        
        if not self.actvationObject.isActive():
            if self.actvationObject.isActivatable():
                return self.actvationObject.activate()
            
        return False
    
    
    def deactivate(self): # wrapped
        if self.actvationObject.isActive():
            if self.actvationObject.isActivatable():
                return self.actvationObject.deactivate()
            
        return False
    
    
    def isActive(self):
        return self.actvationObject.isActive()
    
    
    def __repr__(self):
        return str(self.name)
    
    def __str__(self):
        return "\n".join(self.getStrLines())
    
    
    def getActiveSubNodes(self):
        return [subNode for subNode in self.subNodes if subNode.isActive()]
    
    
    def assignSubNode(self, node):
        self.subNodes.append(node)
        self.subNodesWelcomeActivationState_dict[node] = node.isActive()
        
    
    def getFirstActiveSubNode(self):
        if self.subNodes:
            return self.subNodes[0]
        else:
            return None
    
    
    def resetNode(self):
        
        subNodesToActivate_list = []
        subNodesToDeactivate_list = []
        
        for subNode, activationState in self.subNodesWelcomeActivationState_dict.items():
            if activationState:
                subNodesToActivate_list.append(subNode)
            else:
                subNodesToDeactivate_list.append(subNode)
        
        for node in subNodesToActivate_list:    node.activate()
        for node in subNodesToDeactivate_list:  node.deactivate()
            
        self.configurationGenerator = self.configurationsGenerator()
        
        
    def configurationsGenerator(self):
        """
        Modifies which of subNodes are active
        """
        
        if self.subNodesIsMultipleChoice():
            yield from self.switchSubNodes_multipleOptionsPossible()
        
        else:
            yield from self.switchSubNodes_singleOptions()

    
    def subNodesIsMultipleChoice(self):
        
        if isinstance(self.originObject, Choice_Cls):
            return not self.originObject.isSingleChoiceFlag()
        
        elif isinstance(self.originObject, WorkerConfigurationObject_Cls):
            return False
        
        elif isinstance(self.originObject, ListOfChoices_Cls):
            return True
        
        elif isinstance(self.originObject, ClassesProcessingConfiguration_Cls):
            return not self.actvationObject.isSingleChoiceFlag()
        
        else:
            raise
    

    def switchSubNodes_multipleOptionsPossible(self):
        
        if self.subNodes:
            
            for bitfield in range(1, 2**len(self.subNodes)):
            
                updated_flag = False
            
                activeSubNodes = []
                subNodesToActivate_list = []
                subNodesToDeactivate_list = []
    
                # decide what to (de)activate            
                for subNodeIdx, subNode in enumerate(self.subNodes):
                    if (2**subNodeIdx) & bitfield == 0:
                        subNodesToDeactivate_list.append(subNode)
                    else:
                        subNodesToActivate_list.append(subNode)
    
                # (de)activate what is decided
                for subNode in subNodesToActivate_list:
                    updated_flag |= subNode.activate()
                    activeSubNodes.append(subNode)
                
                for subNode in subNodesToDeactivate_list:
                    updated_flag |= subNode.deactivate()
                
                if updated_flag:
                    yield activeSubNodes
    
    
    def switchSubNodes_singleOptions(self):
        
        if self.subNodes:
            updated_flag = False
            
            for subNodeToActivateIdx in range(len(self.subNodes)):
            
                activeSubNodes = []
                    
                subNodeToActivate = self.subNodes[subNodeToActivateIdx]
                updated_flag |= subNodeToActivate.activate()
                        
                if subNodeToActivate.isActive():
                    activeSubNodes.append(subNodeToActivate)
                
                for subNode in self.subNodes:
                    
                    if subNode is not subNodeToActivate:
                        updated_flag |= subNode.deactivate()
                        
                        if subNode.isActive():
                            activeSubNodes.append(subNode)
                            
                if updated_flag:
                    yield activeSubNodes
            
    
    def switchConfiguration(self):
        
        try:
            self.configurationGenerator.__next__()
            return True
        except StopIteration:
            self.resetNode()
            return False
        
    
    def increment(self):
        """
        Returns:
         - True if incremented
         - False if not incremented, but reseted
        """
        incremented_flag = False

        # LOGIC
        
        for activeSubNode in self.getActiveSubNodes():
        
            if activeSubNode.increment():
                incremented_flag = True
                break
        
        
        if incremented_flag is False:
            incremented_flag = self.switchConfiguration()
        
        return incremented_flag
    
    
    def _getActivationPathObjects(self):
        
        output_list = []
        
        if self.upperNode:
            output_list.extend(self.upperNode._getActivationPathObjects())
        
        output_list.append(self.actvationObject)
        
        return output_list
    
    
    def getNodeActivationPathObjects(self):
        
        return NodeActivationPath_Cls(self._getActivationPathObjects())
    
    


class EachWorkerInRandomScenario_ConfigurationGenerator_Cls():
    
    def __init__(self, workersIncluder):
        self._cspc = ClassesProcessingConfiguration_Cls(workersIncluder)
        self._baseNode = NodesBuilder_Cls().build(self._cspc)
        self._independentChociesGroups_list = []
        self._defineScenarioIndependentChociesGroups()
    
    
    def _getBaseNode(self):
        return self._baseNode
    
    
    def _getIndependentChoicesGroupsList(self):
        return self._independentChociesGroups_list
    
    
    def _openNewIndependentChoicesGroup(self):
        
        assert self._currentIndependentChoicesGroup is None
        self._currentIndependentChoicesGroup = IndependentChoicesGroup_Cls()
        self._independentChociesGroups_list.append(self._currentIndependentChoicesGroup)
    
    
    def _getCurrentIndependentChoicesGroup(self):
        
        return self._currentIndependentChoicesGroup
    
    
    def _closeCurrentIndependentChoicesGroup(self):
        
        assert isinstance(self._currentIndependentChoicesGroup, IndependentChoicesGroup_Cls)
        self._currentIndependentChoicesGroup = None
    

    def _defineScenarioIndependentChociesGroups(self):
        
        self._independentChociesGroups_list = []
        self._currentIndependentChoicesGroup = None
        
        self._defineScenarioIndependentChociesGroups_recursion(self._baseNode)
    
    
    def _defineScenarioIndependentChociesGroups_recursion(self, node):
        
        if isinstance(node.originObject, ClassWorkerChoice_Cls):
            self._openNewIndependentChoicesGroup() # new group of independence starts
        
        icg = self._getCurrentIndependentChoicesGroup()
        
        if icg is not None:# is group opened
            
            if not node.subNodes:
                icg.addNode(node)
        
        for subNode in node.subNodes:
            self._defineScenarioIndependentChociesGroups_recursion(subNode)
    
    
        if isinstance(node.originObject, ClassWorkerChoice_Cls):
            self._closeCurrentIndependentChoicesGroup()
            
    

    def _getNextPreferredRandomScenario(self):
        
        for icg in self._independentChociesGroups_list:
            activationPath = icg.getNextOption()
            
            if activationPath is not None:
                for activationObj in activationPath:
                    if not activationObj.isActive():
                        if activationObj.isActivatable():
                            activationObj.activate()
        
        return self._cspc
    
    
    def _generatorTerminationCondition(self):
        return all([icg.checkIfChoiceIsSaturated() for icg in self._independentChociesGroups_list])
    
    
    def _restartGenerator(self, eachWorkerAtLeastRepeated):
    
        assert isinstance(eachWorkerAtLeastRepeated, int)
        assert eachWorkerAtLeastRepeated > 0
        
        self.eachWorkerAtLeastRepeated = eachWorkerAtLeastRepeated # for debug reasons only
        
        for icg in self._independentChociesGroups_list:
            icg.prepareGeneration(eachWorkerAtLeastRepeated)
        
        
    
    def generate(self, eachWorkerAtLeastRepeated = 1):
        
        self._restartGenerator(eachWorkerAtLeastRepeated)
        
        while not self._generatorTerminationCondition():
            yield self._getNextPreferredRandomScenario()
    
    
    def getHowManyTimesEachWorkerDict(self):
        
        output_dict = {}
        
        if self._independentChociesGroups_list:
            
            for icg in self._independentChociesGroups_list:
                genStateDict = icg.getGeneratorStateDict()
                    
                for repetitionsKey, pathRepeated_set in genStateDict.items():
                    
                    for path_ in pathRepeated_set:
                        output_dict[path_] = repetitionsKey

        return output_dict


class NodeActivationPath_Cls():
    
    def __init__(self, activations_list):
        
        self.activations_path = []
        
        for el in activations_list:
            assert isinstance(el, ConfigurationObject_Activatable_AbstCls)
            self.activations_path.append(el)
    
    def __iter__(self):
        yield from self.activations_path
        
    
    def __str__(self):
        return "/".join([obj_.getName() for obj_ in self])
    
        
    def __repr__(self):
        return str(self)
    


class IndependentChoicesGroup_Cls():
    
    def __init__(self):
        
        self.activationPaths = []
        
        self.eachWorkerAtLeastRepeated = None
    
    
    def prepareGeneration(self, eachWorkerAtLeastRepeated):
        
        self.eachWorkerAtLeastRepeated = eachWorkerAtLeastRepeated
        
        self._generatorState_dict = {
            0 : set()
            } # repetitions : activationPaths set
    
        for activationPath in self.activationPaths:
            self._generatorState_dict[0].add(activationPath)
    
    
    def getGeneratorStateDict(self):
        return self._generatorState_dict.copy() 
    
        
    def getNextOption(self):
        
        if self._generatorState_dict:
            
            lowestRepetitions_key = sorted(self._generatorState_dict.keys())[0]
            lowestRepetitions_set = self._generatorState_dict[lowestRepetitions_key]
            
            chosenElement = random.sample(tuple(lowestRepetitions_set), 1)[0]
            
            lowestRepetitions_set.remove(chosenElement)
            
            if not lowestRepetitions_set:
                del self._generatorState_dict[lowestRepetitions_key]
            
            chosenElement_newKey = lowestRepetitions_key + 1
            
            if not chosenElement_newKey in self._generatorState_dict:
                self._generatorState_dict[chosenElement_newKey] = set()
            
            self._generatorState_dict[chosenElement_newKey].add(chosenElement)
            
            return chosenElement
    
    
    def checkIfChoiceIsSaturated(self):
        return all([repetitions >= self.eachWorkerAtLeastRepeated for repetitions in self._generatorState_dict])
        
    
    def addNode(self, node):
        self.activationPaths.append(node.getNodeActivationPathObjects())
        

    def __iter__(self):
        yield from self.activationPaths



if __name__ == "__main__":
    
    displayDecisionsTreeDynamics_flag = True
    printWorkersRepetitions_flag = False
    
    
    if displayDecisionsTreeDynamics_flag:
        
        # Print decisions tree dynamics
        
        confGen = EachWorkerInRandomScenario_ConfigurationGenerator_Cls(workersIncluder)
        
        if 0:
            for group in confGen._getIndependentChoicesGroupsList():
                print("New group")
                for el in group:
                    print("\t" + str(el))
        else:
            for cspc in confGen.generate(2):
                print(confGen._getBaseNode())
            
            print("\n\nRepetitions of workers:\n")
            for path_, repetitions in confGen.getHowManyTimesEachWorkerDict().items():
                print("- {} : {}".format(path_, repetitions))
                    
        
    
    if printWorkersRepetitions_flag:
        
        # Print how many times each worker is repeated in scenario
        
        builder = NodesBuilder_Cls()
        cspc = ClassesProcessingConfiguration_Cls(workersIncluder)
        node = builder.build(cspc)
        
        print(node)
        
        counter = 1
        
        while node.increment():
            #print("#" * 100)
            #node.increment()
            #print(node)
            counter += 1
        
        print("Number of combinations: ", counter)




