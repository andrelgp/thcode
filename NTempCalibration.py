# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 11:40:38 2018

@author: AndreLGP
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
from NTempCalibration import *
import datetime

## 26-03-2018 - novo metodo para obter calibração do sol - preciso
from Gauss import *

NBINS=200
ZERO=0
ONE=1
TWO=2
### 23-03-2018 - aumento de variação  para 20% a partir do sol calmo
#LOWVALUE=0.9
#HIGHVALUE=1.1

### 28-03-2018 - Devido a valores ruins, voltar nos valores originais
LOWVALUE=0.95
HIGHVALUE=1.05
#### 212 GHZ --> 6179 ± 259 K
#### 405 GHZ --> 5679 ± 238 K

TSUN_212_jorge=6179.
TSUN_405_jorge=5679.
TSUN_212_Adriana=5900.
TSUN_405_Adriana=5100.

_212GHZ=212
_405GHZ=405

class TempCalibration:

    #def __init__(self):
    limbSunADCValue=0
    
    ### deprecated em 26-03-2018####
    '''
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
    '''
    def __genMainADCValues(self, mapadc):
        
        adcHistogram=np.histogram(mapadc,bins=NBINS)
                
        self.skyADCValue = np.max(adcHistogram[ONE][np.where(adcHistogram[ZERO] == np.max(adcHistogram[ZERO][:(NBINS/2)]))])
        if (self.skyADCValue < np.min(mapadc)):
            self.skyADCValue = np.min(mapadc)
        #print("self.skyADCValue:",self.skyADCValue)
        self.quietSunADCValue = np.max(adcHistogram[ONE][np.where(adcHistogram[ZERO] == np.max(adcHistogram[ZERO][(NBINS/2):]))])
        intervalquietSunBelongs=adcHistogram[ONE][np.where((adcHistogram[ONE]>=LOWVALUE*self.quietSunADCValue)&(adcHistogram[ONE]<=HIGHVALUE*self.quietSunADCValue))]
        #print("np.average(intervalquietSunBelongs):",np.average(intervalquietSunBelongs))
        self.quietSunADCValue = np.average(intervalquietSunBelongs)-self.skyADCValue
        self.limbSunADCValue = (self.quietSunADCValue/2)
        #print("self.quietSunADCValue:",self.quietSunADCValue)
        #print("self.limbSunADCValue:",self.limbSunADCValue)
        #print("max:",np.max(adcHistogram[ONE]))
        #print("min:",np.min(adcHistogram[ONE]))
    ### novo genMainADCValues - 26-03-2018
    def __nGenMainADCValues(self, mapadc):
        
        adcHist_h,adcHist_xh=np.histogram(mapadc,bins=NBINS)
        
        p_sun,yfit_sun,cov_sun   = fit1d(adcHist_xh[100:199],adcHist_h[100:199])
        
        p_sky,yfit_sky,cov_sky   = fit1d(adcHist_xh[0:100],adcHist_h[0:100])
        #print("p_sun[1]:",p_sun[1])
        #print("p_sun[1]-p_sky[1]:",p_sun[1]-p_sky[1])
        #print("p_sky[1]",p_sky[1])
        #print("max:",np.max(adcHist_xh))
        #print("min:",np.min(adcHist_xh))
        return p_sun[1]-p_sky[1],p_sky[1]
        
                
    def getTempCalibMap(self,mapadc,ghz,ref):
        
        if (ref == 1):
            TSUN_212 = TSUN_212_jorge
            TSUN_405 = TSUN_405_jorge
        else:
            TSUN_212 = TSUN_212_Adriana
            TSUN_405 = TSUN_405_Adriana

        if (ghz == _212GHZ):
            tsun=TSUN_212
        else:
            tsun=TSUN_405
        
        ### DEPRECATED IN 26-03-2018
        #self.__genMainADCValues(mapadc)
        flag=True
        try:
            adc_sun,adc_sky=self.__nGenMainADCValues(mapadc)
            print("nGenMainADCValues")
            flag=True
        except:
            self.__genMainADCValues(mapadc)
            print("exception - using genMainADCValues")
            flag=False
        
        
        calibmap=np.zeros(len(mapadc),dtype='float')
    
        for cont in range(len(mapadc)):
            if (flag == True):
                #print("calibmap[cont]:",calibmap[cont])
                #print("adc_sky:",adc_sky)
                calibmap[cont]=((mapadc[cont]-adc_sky)*tsun)/adc_sun
                if (calibmap[cont]<(tsun/2)):
                    calibmap[cont]=(tsun/2)-100
            else:
                calibmap[cont]=((mapadc[cont]-self.skyADCValue)*tsun)/self.quietSunADCValue
                if (calibmap[cont]<(tsun/2)):
                    calibmap[cont]=(tsun/2)-100
        return calibmap
    
    def getQuietSunADCValue(self):
        return self.quietSunADCValue
    
    def getLimbSunADCValue(self):
        return self.getlimbSunADCValue
    
    def getSkyADCValue(self):
        return self.getskyADCValue