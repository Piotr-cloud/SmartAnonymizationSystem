'''
Created on Oct 8, 2022

@author: piotr
'''

# Main configuration
ClassName_dict = {
    0: "Face", # Face is an image part that is produced by detector performance on a person view, so context is necessary and boundaries differs between detectors. whenever we say "face" we mean person view evaluated by detector
    1: "License plate"}

ClassName_2_Abbrev_dict = {
    "Face" : "face",
    "License plate" : "lp"}


# Secondary variables
FaceID = 0
LicensePlateID = 1
