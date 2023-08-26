'''
Created on Oct 8, 2022

@author: piotr
'''
from graphviz import Digraph
from PolymorphicBases.ABC import Base_AbstCls
from NonPythonFiles import graphvizWorkspace_dir
from MainExecutor.ProcessingConfiguration import ProcessingConfiguration_Cls
from ObjectsDetectable.ClassesCfg import ClassName_dict



class Diagram_AbstCls(Base_AbstCls):
    
    tempFilePath = graphvizWorkspace_dir / "temp"
    
    def __init__(self, horizontal = False):
        
        self._filePath = Diagram_AbstCls.tempFilePath
        
        self.g = Digraph(filename=str(self._filePath), name = "Processing diagram")
        
        if horizontal:
            self.g.graph_attr["rankdir"] = "LR"
            
        self.g.graph_attr["splines"] = "ortho"
        #self.g.graph_attr["nodesep"] = "0.8"
        self.g.graph_attr["compound"] = "true"
        #self.g.graph_attr["ranksep"] = "0.8"
        
        # self.g.graph_attr["concentrate"] = "true"
        # self.g.edge_attr["headclip"] = "false"
        # self.g.edge_attr["tailclip"] = "false"
    
    def view(self):
        self.g.render(view=1, cleanup=1)

        
    def save(self, filePath):
        self.g.save(filename = str(filePath))
    
    def saveToDefault(self):
        self.save(graphvizWorkspace_dir / "defaultSave.gv")
    
    def toString(self):
        return self.g.source





class ProcessingConfigurationDiagram_ImageProcessing_Cls(Diagram_AbstCls):
    
    processedFileTypeStr = "Images"

    
    def edgeCommon(self, graph, tail_branchPointType, head_branchPointType, tail_name, head_name, *args, **kw_args):
        """
        Does edge creation with common part, by adding invisible node(point):
        
                     r-------  end 1
        start -------+-------  end 2
                     L-------  end 3
                     
        or:
        
        start 1 -----+
        start 2 -----+-------  end
        start 3 -----+
        
        
        see: 
         - https://stackoverflow.com/questions/27504703/in-graphviz-how-do-i-align-an-edge-to-the-top-center-of-a-node
         - https://stackoverflow.com/questions/38410370/edge-pointing-at-edge-with-graphviz-and-dot
         
        tail_branchPointType can be one of:
         - "or"  -  stands for branch choice
         - "*"   -  stands for parallel branches begining
         - None  -  stands for non defined branching
         
        head_branchPointType can be one of:
         - "or"  -  stands for alternative branch join 
         - "+"   -  stands for summing branches
         - None  -  stands for non defined branching end
         
        """
        assert tail_branchPointType in ["or","*", None]
        assert head_branchPointType in ["or","+", None]

    
    def __init__(self, cpc):
        
        processingConfiguration = cpc.resolve()
        assert isinstance(processingConfiguration, ProcessingConfiguration_Cls)
        
        Diagram_AbstCls.__init__(self, horizontal = True)
        
        srcFileNodeName_str = type(self).processedFileTypeStr
        
        self.g.node(srcFileNodeName_str, shape = "note")
        
        with self.g.subgraph(name='cluster_outputs') as subgraph_outputs:
            
            subgraph_outputs.graph_attr["style"] = "dotted"
            subgraph_outputs.attr(label='Outputs')
            
            targetContainers_list = []
            
            targetContainers_list.append("Not changed " + srcFileNodeName_str)
            subgraph_outputs.node(targetContainers_list[0], shape = "note")
            
            if processingConfiguration.getAnnotationFlag():
                targetContainers_list.append("Annotated " + srcFileNodeName_str)
            
            if processingConfiguration.getAnonymizationFlag():
                targetContainers_list.append("Anonymized " + srcFileNodeName_str)
            
            if processingConfiguration.getAnnotationFlag() and processingConfiguration.getAnonymizationFlag():
                targetContainers_list.append("Annotated and anonymized " + srcFileNodeName_str)
            
            for targetContainer in targetContainers_list:
                subgraph_outputs.node(targetContainer, shape = "note")
            
            self.g.edge(srcFileNodeName_str, targetContainers_list[0], constraint = "false", label = "Nothing detected")
        
            with self.g.subgraph(name='cluster_detections') as subgraph_detections:
                
                subgraph_detections.attr(label='Detections Map')
                subgraph_detections.graph_attr["style"] = "dashed"
                
                detectorsConstructionDict = processingConfiguration.getDetectorsConstructionDict()
                #subgraph_detections.graph_attr["margin"] = "0.8"
            
            
                with self.g.subgraph(name='cluster_detectors') as subgraph_detectors:
                    
                    #subg.attr(color='blue')
                    #subgraph_detectors.node_attr['style'] = 'filled'
                    subgraph_detectors.attr(label='Detectors')
                    
                    for detectorConstructionObj, classesIds in detectorsConstructionDict.items():
                        worker_str = str(detectorConstructionObj.getWorkerCls().getName())
                        subgraph_detectors.node(worker_str, shape = "component")
                        self.g.edge(srcFileNodeName_str, worker_str)
                        
                        for classId in classesIds:
                                
                            className_str = ClassName_dict[classId] + "s"
                            subgraph_detections.node(className_str, shape = "box")
                            #subgraph_detections.edge(className_str,"Detections Map")
                            self.g.edge(worker_str, className_str)
                            
            
            with self.g.subgraph(name='cluster_anonymizers') as subgraph_anonymization:
                
                subgraph_anonymization.attr(label="Anonymizers")
                anonymizersConstructionDict = processingConfiguration.getAnonymizersConstructionDict()
                annotatorConstruction = processingConfiguration.getAnnotatorConstruction()
                
                annotatorUsed_flag = processingConfiguration.getAnnotationFlag()
                anonymizerUsed_flag = processingConfiguration.getAnonymizationFlag()
                
                annotator_flag = False
                lastWorker_str = None
                
                for workerConstructionObj, classesIds in anonymizersConstructionDict.items():
                    
                    if workerConstructionObj is None:
                        annotator_flag = True
                        worker_str = str(annotatorConstruction.getWorkerCls().getName())
                    
                    else:
                        worker_str = str(workerConstructionObj.getWorkerCls().getName())
                    
                    subgraph_anonymization.node(worker_str, shape = "component")
                    
                    for classId in classesIds:
                        className_str = ClassName_dict[classId] + "s"
                        #self.g.edge(type(self).processedFileTypeStr, worker_str)
                        self.g.edge(className_str, worker_str)
                    
                    if annotator_flag:
                        if anonymizerUsed_flag:
                            self.g.edge(worker_str, "Annotated and anonymized " + srcFileNodeName_str)
                        self.g.edge(worker_str, "Annotated " + srcFileNodeName_str)
                    else:
                        if annotatorUsed_flag:
                            self.g.edge(worker_str, "Annotated and anonymized " + srcFileNodeName_str)
                            
                        self.g.edge(worker_str, "Anonymized " + srcFileNodeName_str)
                    
                    lastWorker_str = worker_str
                    
                self.g.edge(srcFileNodeName_str, lastWorker_str, lhead = "cluster_anonymizers")

                
        #self.g.edge(srcFileNodeName_str, , constraint = "false", )
            
        if processingConfiguration.getAnonymizationFlag():
            anonymizersConstructionDict = processingConfiguration.getAnonymizersConstructionDict()
        
        self.view()
        print(self.toString())




class ProcessingConfigurationDiagrams_Builder_Cls():
    
    def __init__(self, cpc, anyImages = True):
        
        if anyImages:
            ProcessingConfigurationDiagram_ImageProcessing_Cls(cpc)
    


if __name__ == "__main__":

    from Configuration.integrationCfg import workersIncluder
    from Configuration.ConfigurationObjects.ClassProcessingConfiguration import ClassesProcessingConfiguration_Cls
    
    cpc = ClassesProcessingConfiguration_Cls(workersIncluder)
    
    ProcessingConfigurationDiagrams_Builder_Cls(cpc)

