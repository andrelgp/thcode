# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 23:52:19 2017

@author: Andre Luiz
"""
import sys
import numpy as np
from SSTMethods import *
from matplotlib import pyplot as plt, cm, colors
from scipy.io.idl import readsav # alternativa a idlsave
from SSTMap import *
from ArtificialMap import *
from MapRepair import *
from PlotMap import *
from TempCalibration import *
import datetime

NBINS=200
ZERO=0
ONE=1
TWO=2
LOWVALUE=0.95
HIGHVALUE=1.05
#### 212 GHZ --> 6179 ± 259 K
#### 405 GHZ --> 5679 ± 238 K

#TSUN_212=6179.
#TSUN_405=5679.
TSUN_212=5900.
TSUN_405=5100.

_212GHZ=212
_405GHZ=405

class TempCalibration:

    #def __init__(self):
    limbSunADCValue=0
        
    def __genMainADCValues(self, mapadc):
        
        adcHistogram=np.histogram(mapadc,bins=NBINS)
                
        self.skyADCValue = np.max(adcHistogram[ONE][np.where(adcHistogram[ZERO] == np.max(adcHistogram[ZERO][:(NBINS/2)]))])
        if (self.skyADCValue < np.min(mapadc)):
            self.skyADCValue = np.min(mapadc)
    
        self.quietSunADCValue = np.max(adcHistogram[ONE][np.where(adcHistogram[ZERO] == np.max(adcHistogram[ZERO][(NBINS/2):]))])
        intervalquietSunBelongs=adcHistogram[ONE][np.where((adcHistogram[ONE]>=LOWVALUE*self.quietSunADCValue)&(adcHistogram[ONE]<=HIGHVALUE*self.quietSunADCValue))]
        self.quietSunADCValue = np.average(intervalquietSunBelongs)
        deltaQSunSky = self.quietSunADCValue - self.skyADCValue  
        self.limbSunADCValue = (deltaQSunSky/2) + self.skyADCValue
        
                
    def getTempCalibMap(self,mapadc,ghz):
        if (ghz == _212GHZ):
            tsun=TSUN_212
        else:
            tsun=TSUN_405
        
        self.__genMainADCValues(mapadc)
        calibmap=np.zeros(len(mapadc),dtype='float')
    
        for cont in range(len(mapadc)):
            calibmap[cont]=(mapadc[cont]*tsun)/self.quietSunADCValue
        
        return calibmap
    
    def getQuietSunADCValue(self):
        return self.quietSunADCValue
    
    def getLimbSunADCValue(self):
        return self.getlimbSunADCValue
    
    def getSkyADCValue(self):
        return self.getskyADCValue