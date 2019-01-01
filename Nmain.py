# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 08:54:32 2017

@author: A0068182
"""

from NGenerateMaps import *
import datetime

time1='2008-12-09 14:00'
time2='2008-12-09 15:59'
#time1='2013-01-8 14:00:00'
#time2='2013-08-28 14:59:00'
################ MAIN CODE ###################    
if __name__ == '__main__':
    ini=datetime.datetime.now()
    genMaps=NGenerateMaps(time1,time2)    
    end=datetime.datetime.now()
    
    print '   '
    
    print('time start all process :',ini)
    print('time end all process  :',end)