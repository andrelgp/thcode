# -*- coding: utf-8 -*-
"""
Created on Mon Mar 06 15:25:29 2017

@author: Andre Luiz
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata 
import sys
import numpy.ma as ma 
import numpy as np
from scipy.io.idl import readsav # alternativa a idlsave
from scipy.signal import correlate
from ArtificialMap import *
from PlotMap import *
import csv
### inserted in 21-02-2018
import datetime
###

FLOAT='float'
ZEROVALUE=0
_212GHZ=212
_405GHZ=405

class MapRepair:

    def __init__(self, pathBpos, pathstbeams):
        self.pathBpos=pathBpos
        self.pathstbeams=pathstbeams

        
    def repairMap(self,indicemap, map, xoff, yoff,ghz):
        self.map=map
        self.indicemap=indicemap
        self.xoff=xoff
        self.yoff=yoff
        flag=False
        
        if (flag == True):
            ###
            print("original map modified - ini")
            print(datetime.datetime.now())
            ###
        
        originalmapmodified = (self.map - np.min(self.map)).astype(FLOAT)
        originalmapmodified = originalmapmodified/np.max(originalmapmodified)
        
        if (flag == True):
            ###
            print("original map modified - end")
            print(datetime.datetime.now())
            ###
        
        if (flag == True):
            ###
            print("constructor artificial map - ini")
            print(datetime.datetime.now())
            ###
        
        artificialMap = ArtificialMap(self.xoff, self.yoff, self.pathBpos, self.pathstbeams) 
        
        if (flag == True):
            ###
            print("constructor artificial map - end")
            print(datetime.datetime.now())
            ###        
        if (flag == True):
            ###
            print("getArtificialMap - ini")
            print(datetime.datetime.now())
            ###
        normcs1 = artificialMap.getArtificialMap(self.indicemap)
        if (flag == True):
            ###
            print("getArtificialMap - end")
            print(datetime.datetime.now())
            ###
        if (flag == True):
            ###
            print("getCoordinates - ini")
            print(datetime.datetime.now())
            ###    
        nxoff,nyoff=artificialMap.getCoordinates()
        if (flag == True):
            ###
            print("getCoordinates - end")
            print(datetime.datetime.now())
            ###    
        if (flag == True):
            ###
            print("getCoordinates ghz- ini")
            print(datetime.datetime.now())
            ###    
        
        xcal1,ycal1,xcal,ycal=artificialMap.getCalCoordinates(ghz)
        if (flag == True):
            ###
            print("getCoordinates ghz- end")
            print(datetime.datetime.now())
            ###    
        
        repairedMap = np.zeros(originalmapmodified.shape,dtype='float')
        
        dify = np.ediff1d(ycal1,to_end=ZERO)
        msk = (dify <> ZERO) 
        one =  ma.array(xcal1,mask=msk)
        onecont = ma.notmasked_contiguous(one)
        
        if (flag == True):
            ###
            print("loop de correcao delta - ini")
            print(datetime.datetime.now())
            ###
        
        for k in range(len(onecont)):#tiras:
            minnxoff = np.min(nxoff[onecont[k]])
            maxnxoff = np.max(nxoff[onecont[k]])
            lennxoff = len(nxoff[onecont[k]])        
            #xx = np.linspace(minnxoff,maxnxoff,lennxoff)
            tiempo = np.arange(1-lennxoff,lennxoff)
            lineOriginalMod = originalmapmodified[onecont[k]]
            lineNormcs1 = normcs1[onecont[k]]
            cross_correlation = correlate(lineOriginalMod,lineNormcs1)
            shift_calculated = tiempo[cross_correlation.argmax()]*1.0*maxnxoff/lennxoff
            corregido = np.roll(map[onecont[k]],-np.int(shift_calculated/2.))
            repairedMap[onecont[k]] = corregido

        if (flag == True):
            ###
            print("loop de correcao delta - end")
            print(datetime.datetime.now())
            ###
        
        if (flag == True):
            ###
            print("adjusting final antes de sair da rotina - ini")
            print(datetime.datetime.now())
            ###
        
        # adjusting the map to originals values
        for i in range(len(repairedMap)):
            if (repairedMap[i]==ZEROVALUE):
                repairedMap[i]=(np.min(map)).astype(float)
        
        if (flag == True):
            ###
            print("adjusting final antes de sair da rotina - end")
            print(datetime.datetime.now())
            ###
        return repairedMap