'''
Created on Oct 5, 2022

@author: piotr
'''

from abc import ABCMeta as _ABCMeta, abstractmethod  # import abstractmethod due to secondary imports

import inspect as _inspect



def _getMethodCallStr(methodClass, methodName):
    return methodClass.__name__ + "." + methodName + "(...)"



class _Base_MetaAbstCls(_ABCMeta):
    
    def __new__(mcls, name, bases, namespace, **kwargs):
        
        cls = _ABCMeta.__new__(mcls, name, bases, namespace, **kwargs)
        
        thisAndBase_classes = _inspect.getmro(cls)[::-1]
        methods = []
        issuedMethodsNames_list = []
        finalMethods_names_dict = {}
    
        for class_ in thisAndBase_classes:
            for varName, varVal in vars(class_).items():
                if callable(varVal):
                    methods.append((varName, varVal))
    
                    if varName in finalMethods_names_dict:
                        methodIdentification_str = _getMethodCallStr(class_, varName)
                        issuedMethodsNames_list.append(finalMethods_names_dict[varName] + "  by  " + methodIdentification_str)
    
                    elif hasattr(varVal, "__isfinalmethod__") and varVal.__isfinalmethod__:
                        methodIdentification_str = _getMethodCallStr(class_, varName)
                        finalMethods_names_dict[varName] = methodIdentification_str
        
        if issuedMethodsNames_list:
            if len(issuedMethodsNames_list) == 1:
                error = TypeError("Final method is overwritten:  " + str(issuedMethodsNames_list[0]))
                
            else:
                error = TypeError("Final methods are overwritten: " + "".join(["\n  - " + str(method) for method in issuedMethodsNames_list]))
                
            raise error
    
        return cls


    
class Base_AbstCls(object, metaclass=_Base_MetaAbstCls):
    """
    Base abstract class
    """
    
    @classmethod
    def __validateClassName(cls):
        
        if cls.__name__.endswith("_AbstCls"):
            raise TypeError("Trying to instantiate an abstract class(by name convension: \"*_AbstCls\"): " + cls.__name__)
    
    
    def __new__(cls, *_, **__):
        
        cls.__validateClassName()
        
        return super(Base_AbstCls, cls).__new__(cls) #, *args, **kwargs)




def final(funcobj):
    funcobj.__isfinalmethod__ = True
    return funcobj



