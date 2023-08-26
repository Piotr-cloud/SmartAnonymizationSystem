'''
Created on Jun 29, 2023

This module allows to evaluate all the known workers in random scenarios of cooperation
 
@author: piotr
'''

import argparse
from pathlib import Path



argsParser = argparse.ArgumentParser("The interface to evaluate known workers")

_dir = Path(__file__).parent


argsParser.add_argument(
    "-i",
    nargs='+',
    type=str,
    default=[str(_dir.parent / "userFiles/inputs")],
    help="Paths of input file(s) or directory(-ies). When directory is provided then all the files in that folder are taken into consideration(no recursion applied). Any file indicated shall be an image or a video, otherwise the file is ignored. To apply additional filter on paths - see \"-filter\" argument"
    )

argsParser.add_argument(
    "-o",
    type=str,
    default=str(_dir.parent / "userFiles/outputs_eval"),
    help="Base path to output files - path without extension. The following files are going to be created: <path>.log <path>.txt <path>.json. If no path is provided, then default directory and file base name is used"
    )

argsParser.add_argument(
    "-filter",
    nargs='+',
    type=str,
    default=None,
    help="Regex(python) based filter pattern applied to input files paths. Multiple filters are joined with OR operand(match any filter). Examplary pattern that match any .jpg file is: \".*\.jpg$\""
    )

argsParser.add_argument(
    "-no-subpr",
    default=False,
    action="store_true",
    help="Disable execution in a subprocesses. When param is set then RAM leakage, unexpected behavior or exception in one execution session impacts the whole program. On the other hand it is easier to debug. Setting this param does not mean that all the execution goes in one process since there are other mechnisms like parallel measurement"
    )

argsParser.add_argument(
    "-repeat",
    default=1,
    type=int,
    help="How many times each on worker shall be repeated in total"
    )

argsParser.add_argument(
    "-repeat_inARow",
    default=1,
    type=int,
    help="How many times each on worker shall be repeated in a row - during one session"
    )

argsParser.add_argument(
    "-no-cuda",
    default=False,
    action="store_true",
    help="Force to disable CUDA and torch GPU support, by configuring no visible CUDA devices in system enviroment variables"
    )

argsParser.add_argument(
    "-maxFPS",
    default = None,
    type=float,
    help="Limit fps before processing"
    )

argsParser.add_argument(
    "-maxHeight",
    default = None,
    type=int,
    help="Limit image height before processing(proportion is preserved unless -looseProportion option is chosen)"
    )

argsParser.add_argument(
    "-maxWidth",
    default = None,
    type=int,
    help="Limit image width before processing(proportion is preserved unless -looseProportion option is chosen)"
    )

argsParser.add_argument(
    "-looseProportion",
    default=False,
    action="store_true",
    help="if this param is used then resolution change is done with no respect to original proportion of the image by force limiting to maxHeight and maxWidth"
    )

    

args = argsParser.parse_args()



if __name__ == "__main__":
    
    from MainExecutor.UserRequestProcessor import UserRequestProcessor_Eval_Cls
    
    urp = UserRequestProcessor_Eval_Cls()
    
    additionalProcessingParams_dict = {
        "maxFPS" : args.maxFPS,
        "maxHeight" : args.maxHeight,
        "maxWidth" : args.maxWidth,
        "looseProportion" : args.looseProportion,
        "no_cuda": args.no_cuda
        }
    
    urp.run(
        inputPaths = args.i,
        outputDir = args.o,
        
        inputFilters = args.filter,
        
        streamProcessing_flag = False, # sequential processing
        
        repeatEachWorker_times = args.repeat, 
        repetitionsInARow_times = args.repeat_inARow,
        inASubprocesses_flag = not args.no_subpr,
        
        additionalProcessingParams_dict = additionalProcessingParams_dict
        )


