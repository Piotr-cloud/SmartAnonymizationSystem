'''
Created on Mar 5, 2022

@author: piotr
'''
from ContentSwapper.ContentSwapper import ContentSwapper_AbstCls


class SmartSwapper_AbstCls(ContentSwapper_AbstCls):
    
    @staticmethod
    def getName(): 
        return "Smart swapper"
        