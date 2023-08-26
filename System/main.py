'''
Created on Sep 3, 2021

Project: Application of deep neural networks for seamless anonimization of faces and license plates in image sequences

This project provides functionallity of detection and anonymization of specific objects on image or video using 
numerous methods. This project implements abstraction(polymorphism) to allow configuration of specific way to detect or anonymize objects

 
@author: piotr
'''

import argparse
from pathlib import Path



argsParser = argparse.ArgumentParser("The interface to perform smart anonymization of videos or images")

_dir = Path(__file__).parent


argsParser.add_argument(
    "-i",
    nargs='+',
    type=str,
    default=[str(_dir.parent / "userFiles/inputs")],
    help="Paths of input file(s) or directory(-ies). When directory is provided then all the files in that folder are taken into consideration(no recursion applied). Any file indicated shall be an image or a video, otherwise the file is ignored. To apply additional filter on paths - see \"-filter\" argument. There is no recursion searching of subdirectories"
    )

argsParser.add_argument(
    "-o",
    type=str,
    default=str(_dir.parent / "userFiles/outputs"),
    help="Output directory(must exist - for control reason) - output files are placed there in plain structure keeping input file base name(with prefix application, see: -outFilePrefix). In case of conflict on file base name it's indexed by suffix, but anyway tracking can be finally read in produced file: srcPaths.txt"
    )

argsParser.add_argument(
    "-outFilePrefix",
    type = str,
    default = "",
    help="Prefix applied to each output file base name"
    )

argsParser.add_argument(
    "-inputFilter",
    nargs='+',
    type=str,
    default=None,
    help="Regex(python) based filter pattern applied to input files paths. Multiple filters are joined with OR operand(match any filter). Examplary pattern that match any .jpg file is: \".*\.jpg$\""
    )

argsParser.add_argument(
    "-cfg",
    type=lambda string_: [Path(path_str.rstrip().lstrip()) for path_str in string_.split(' / ')],
    default=[],
    help="Path to configuration file(s). When using multiple paths separate them with the following three signs \" / \" ( <space><forward slash><space> ) and put them in common quote. Path \"/\" cannot be used since it is not file path"
    )

argsParser.add_argument(
    "-no-subpr",
    default=False,
    action="store_true",
    help="Disable execution in a subprocesses. When param is set then RAM leakage, unexpected behavior or exception in one execution session impacts the whole program. On the other hand it is easier to debug. Setting this param does not mean that all the execution goes in one process since there are other mechnisms like parallel measurement"
    )

argsParser.add_argument(
    "-no-edit",
    default=False,
    action="store_true",
    help="When no configuration loading issues or warnings, skips processing configuration editor and run processing immediately; When -cfg is not provided this argument is ignored"
    )

argsParser.add_argument(
    "-no-cuda",
    default=False,
    action="store_true",
    help="Force to disable CUDA and torch GPU support, by configuring no visible CUDA devices in system enviroment variables"
    )

argsParser.add_argument(
    "-plainOutput",
    default=False,
    action="store_true",
    help="When using multiple cfg files, outputs are placed to dedicated folder related to cfg. When setting this flag outputs are put to common dir, but distinguised by file name suffix that relates to cfg"
    )

argsParser.add_argument(
    "-cleanFirst",
    default=False,
    action="store_true",
    help="Says whether to clean out output directory from any files that can be mistaken as output files. Cleaning is done before processing startup - during preparation stage"
    )

argsParser.add_argument(
    "-framesSave_dir",
    default = None,
    type=str,
    help="When this param is provided then input and output frames of all processed videos are saved to this directory. Usage of this param allows to see result during processing"
    )

argsParser.add_argument(
    "-stream",
    default=False,
    action="store_true",
    help="(Not implemented yet!) When this param is provided then stream processing is performed instead of sequential processing, what decrases the quality, but requires less memory available (RAM or HD) and changes strategy(for ex. real time videos processing can be done)"
    )

argsParser.add_argument(
    "-ram-only",
    default=False,
    action="store_true",
    help="When this param is provided then all the numpy arrays operated during execution are kept in RAM what might make RAM consumption extremaly large"
    )

argsParser.add_argument(
    "-maxFPS",
    default = None,
    type=float,
    help="Limit fps before processing"
    )

argsParser.add_argument(
    "-maxWidth",
    default = None,
    type=int,
    help="Limit image width before processing(proportion is preserved unless -looseProportion option is chosen)"
    )

argsParser.add_argument(
    "-maxHeight",
    default = None,
    type=int,
    help="Limit image height before processing(proportion is preserved unless -looseProportion option is chosen)"
    )

argsParser.add_argument(
    "-looseProportion",
    default=False,
    action="store_true",
    help="if this param is used then resolution change is done with no respect to original proportion of the image by force limiting to maxHeight and maxWidth"
    )


args = argsParser.parse_args()




if __name__ == "__main__":
    
    from MainExecutor.UserRequestProcessor import UserRequestProcessor_Main_Cls
    
    urp = UserRequestProcessor_Main_Cls()
    
    additionalProcessingParams_dict = {
        "framesSave_dir" : args.framesSave_dir,
        "maxFPS" : args.maxFPS,
        "maxHeight" : args.maxHeight,
        "maxWidth" : args.maxWidth,
        "looseProportion" : args.looseProportion,
        "outFilePrefix": args.outFilePrefix,
        "cleanFirst_flag" : args.cleanFirst,
        "no_cuda": args.no_cuda
        }
    
    urp.run(
        inputPaths = args.i,
        outputDir = args.o,
    
        inputFilters = args.inputFilter,
    
        cfgFilesPaths = args.cfg,
        noEdit_flag = args.no_edit,
    
        streamProcessing_flag = args.stream,
        ramOnly_flag = args.ram_only,
    
        additionalProcessingParams_dict = additionalProcessingParams_dict,
        
        inASubprocesses_flag = not args.no_subpr,
        plainOutput_flag = args.plainOutput
        )




