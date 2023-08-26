'''
Created on Sep 21, 2022

@author: piotr
'''


Loading_OK = "OK"
Loading_MissingDecisions             =   "Configuration mismatch: Provided cfg do not cover all the decisions!"
Loading_IgnoredDecisions             =   "Configuration mismatch: Some decisions of provided cfg are ignored!"
Loading_MissingAndIgnoredDecisions   =   "Configuration mismatch: Provided cfg do not cover all the decisions and some of the provided cfg are ignored!"
Loading_NonImported                  =   "Configuration mismatch: None decisions are imported! File is not loaded"
Loading_NoImportRequested            =   None

# Non-degradable error codes
Loading_WrongFileFormat  =  "Wrong file format"
Loading_FileDontExist    =  "Provided path does not exist"
Loading_PathNotAFile     =  "Provided path is not a file"


def mergeLoadingErrorCodes(first_, second_):
    
    anyDecisionMissing_flag = False
    anyDecisionIgnored_flag = False
    anyDecisionImported_flag = False
    
    
    if Loading_OK in [first_, second_]:
        anyDecisionImported_flag = True
    
    if Loading_MissingDecisions in [first_, second_]:
        anyDecisionMissing_flag = True
        anyDecisionImported_flag = True
    
    if Loading_IgnoredDecisions in [first_, second_]:
        anyDecisionIgnored_flag = True
        anyDecisionImported_flag = True
    
    if Loading_MissingAndIgnoredDecisions in [first_, second_]:
        anyDecisionMissing_flag = True
        anyDecisionIgnored_flag = True
        anyDecisionImported_flag = True
        
    if Loading_NonImported in [first_, second_]:
        anyDecisionMissing_flag = True
    
    
    if anyDecisionImported_flag is False:
        outputErrorCode = Loading_NonImported
    
    else:
        if not anyDecisionMissing_flag and not anyDecisionIgnored_flag:
            outputErrorCode = Loading_OK
            
        elif anyDecisionMissing_flag and not anyDecisionIgnored_flag:
            outputErrorCode = Loading_MissingDecisions
            
        elif not anyDecisionMissing_flag and anyDecisionIgnored_flag:
            outputErrorCode = Loading_IgnoredDecisions
        
        else:
            outputErrorCode = Loading_MissingAndIgnoredDecisions
    
    return outputErrorCode



if __name__ == "__main__":
    
    print(
        mergeLoadingErrorCodes(
            Loading_NonImported,
            Loading_IgnoredDecisions
            )
        )
