

from ObjectsDetectable.ClassesCfg import *  # import all objects defined in classesCfg due to secondary imports


ClassID_dict = dict([(value, key) for key, value in ClassName_dict.items()])



ClassNames = list(ClassID_dict.keys())
ClassIDs = list(ClassName_dict.keys())


# Class ids implies also anonymization order at final anonymization stage(content replacement), so in case of conflict higher class id objects are going to cover the lower ones
ClassesOrderProcessing_idsList = sorted(ClassIDs) # classes Ids order list





