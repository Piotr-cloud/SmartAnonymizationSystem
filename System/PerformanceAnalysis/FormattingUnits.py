'''
Created on Feb 26, 2023

@author: piotr
'''
from datetime import datetime



def formatTimestamp(time):
    datetime_ = datetime.fromtimestamp(time)
    return datetime_.strftime("%Y-%b-%d %H:%M:%S.%f")


def formatTime(seconds):
    miliseconds = seconds * 1000
    microseconds = miliseconds * 1000
    
    minutes = seconds / 60
    hours = minutes / 60
    
    if miliseconds < 1:
        return "{:.3f} us".format(microseconds)
    if seconds < 1:
        return "{:.3f} ms".format(miliseconds)
    elif minutes < 1:
        return "{:.3f} s".format(seconds)
    else:
        seconds %= 60
        if hours < 1:
            return "{}min {}s".format(int(minutes), int(seconds))
        else:
            minutes %= 60
            return "{}h {}min {}s".format(int(hours), int(minutes), int(seconds))


def formatMemoryInfo(num, suffix='B'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)



def formatRAM(RAM):
    return formatMemoryInfo(RAM)




