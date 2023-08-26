'''
Created on Feb 24, 2023

@author: piotr
'''

def singleton(class_):
    
    instances = {}
    
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    
    return getinstance



