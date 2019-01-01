# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 16:20:25 2017

@author: A0068182
"""

import sys
import numpy as np
import oSST
from matplotlib import pyplot as plt, cm, colors
from scipy.io.idl import readsav # alternativa a idlsave


# TIPO DE DADO A SER RETIRADO DO SST
FIELDFROMSSTMETHODS = np.array(['adc','opmode','scan_off','target','time'])
TARGET=2
X_AXIS=0
Y_AXIS=1
# beams
BEAM_ONE=0
BEAM_TWO=1
BEAM_TREE=2
BEAM_FOUR=3
BEAM_FIVE=4
BEAM_SIX=5
ARCSECFACTOR=3600 #PARA TRANSFORMACAO EM ARCSEGUNDOS
DIMENSIONFIELDSCANOFF=2 #DIMENSIONANDO DADOS SCANOFF
DIMENSIONFIELDADC=6  #DIMENSIONANDO DADOS ADC

class NSSTMap:
    #construct the class
    def __init__(self, dthinit, dthend, typesstfile, pathSSTMaps):
        self.pathSSTMaps = pathSSTMaps
        self.dthinit     = dthinit
        self.dthend      = dthend
        self.osst=oSST.SST()
        self.osst.data_path=pathSSTMaps
        self.osst.initial_time=self.osst.str2datetime(dthinit)
        self.osst.final_time=self.osst.str2datetime(dthend)
        self.osst.data_type=typesstfile
        self.osst.data
        
        self.listOfmaps=([])
        self.listOfxoffs=([])
        self.listOfyoffs=([])
        self.listOfHourMaps=([])
        #### 10-04-2018 incluindo lista de times para correção de eta e P ###
        self.timeArray=([])
        
        #read de files
        self.__readFiles()
        
        #fill the main structure data
        self.__getDataMaps(FIELDFROMSSTMETHODS)
       
        
    #####################################
    # Leitura dos dados
    def getMaps(self):
        #### 10-04-2018 incluindo lista de times para correção de eta e P ###
        return self.listOfmaps, self.listOfxoffs, self.listOfyoffs,self.listOfHourMaps,self.timeArray
        
    
    def __doContiguo(self,opmoderange):
    # Identifica pulos nos indices
    # pp = indices dos pulos   
        nu = len(opmoderange)
        if (nu < 2):
            return np.zeros([2,1],int)
        n = nu-1
        ad = 0
    
        dif = opmoderange[1:]-opmoderange[:-1]
        
        if ((dif[0] != 1) & (dif[1] == 1)):
            opmoderange = opmoderange[1:]
            dif = opmoderange[1:]-opmoderange[:-1]
            ad = 1
            nu = nu-1
            n = n-1
    
        if ((dif[n-1] != 1) & (dif[n-2] == 1)):
            opmoderange = opmoderange[0:n-1]
            dif = opmoderange[1:]-opmoderange[:-1]
            nu = nu-1
            n = n-1
    
        tt, = np.where(dif == 1)
    
        if (len(tt) == 0): 
            return np.zero([2,1],int)
        
        if (len(tt) == nu-1):
            pp = np.zeros([2,1],int)
            pp[0,0] = 0
            pp[1,0] = nu-1
            return pp+ad
        
        k, = np.where(dif != 1)
        dif[k] = 0
        dif2 = dif[1:]-dif[:-1]
        
        pi, = np.where(dif2 == -1)
        pf, = np.where(dif2 == 1)
        
        if (pi[0] < pf[0]):
            tmp = np.zeros(len(pi)+1,int)
            for i in range(len(pi)):
                tmp[i+1] = pi[i]
            pi = tmp
        
        if (pi[len(pi)-1] < pf[len(pf)-1]):
            tmp = np.zeros(len(pf)+1,int)
            for i in range(len(pf)):
                tmp[i] = pf[i]
            tmp[len(pf)] = nu-1
            pf = tmp        
            
        pi[1:] = np.array(pi[1:])+2 # FABIAN; Pra tentar dar u jeito no encavalamento
        pp = np.zeros([2,len(pi)],int)
        pp[0,:] = pi
        pp[1,:] = pf
        
        return (pp+ad).T

    def __readFiles(self):
        self.osst.read()
        self.data=oSST.yAxis()
 
    def __getDataMaps(self,fieldsFromSstMethods):
        
        '''EXTRAÇÃO DE DADOS SST'''
        #numberOflevels = 6 # numero de canais    
        
        self.data.getValues(self.osst,fieldsFromSstMethods[0])
        adc=self.data.adc
        numberOfregs = len(adc)
        
        print("numberOfregs : ",numberOfregs)
        #plt.rc('figure',figsize=(32,4))
        #plt.plot(adc)
        
        # 10-01-2018 - to get file names found
        hoursOfeachRecord = self.osst.getDataFilesFound()
        '''
        if numberOfregs > 1:
            print("hoursOfeachRecord :",hoursOfeachRecord[0])
        #print(len(hoursOfeachRecord))
        '''
        if numberOfregs < 100:
            print ('Incompleted data for the map :', self.osst.initial_time)
            return ([]),([]),([])
    
        self.data.getValues(self.osst,fieldsFromSstMethods[1])
        opmode=self.data.opmode
        self.data.getValues(self.osst,fieldsFromSstMethods[2])
        scanoff=self.data.scan_off
        self.data.getValues(self.osst,fieldsFromSstMethods[3])
        target=self.data.target
        scanoffT = scanoff.T
 
        xoff,yoff=([]),([])
        for i in range(numberOfregs):
            xoff.append(scanoff[i][0])
            yoff.append(scanoff[i][1])
        arxoff = np.array(xoff)
        aryoff = np.array(yoff)    
        ## Obtendo o tamanho
        '''EXTRAIR SOMENTE OS DADOS DO MAPA OPMODE <= 4'''   
        opmoderange, = np.where((1 <= opmode) & (opmode <= 4))# | ((21 <= opmode) & (opmode <= 23)))
        numberOfopmoderange = len(opmoderange)
        #print(k_04) opmoderange    
        #print nk numberOfopmoderange
        if numberOfopmoderange < 100:
            print ('No map was found!')
            print (' ')
        
        ### Getting time 09-04-2018 ###
        self.data.getValues(self.osst,'time')
        dataTime=self.data.time
    
        #print time1[:10], '  ',
        
        '''DETERMINAR TIPO DE MAPA, OPMODE:'''
        oprangemap = opmode[opmoderange]
        #print k_04.shape
        #print op.shape oprangemap
        medianOprangemap = np.median(oprangemap)
        
        '''DETERMINAR NUMERO DE MAPAS'''
        NumberOfMaps = self.__doContiguo(opmoderange)
        # print c
        NumberOfMaps1 = len(NumberOfMaps)
        print (NumberOfMaps1, '\tmaps\t')
        print(' ')
        if NumberOfMaps.shape[1] == 1:
            NumberOfMaps2 = NumberOfMaps.T
        else:
            NumberOfMaps2 = []
            for i in range(len(NumberOfMaps)):
                if (NumberOfMaps[i,1]-NumberOfMaps[i,0])>100:
                    NumberOfMaps2.append(NumberOfMaps[i])
        NumberOfMaps = np.array(NumberOfMaps2)
        NumberOfMaps2 = len(NumberOfMaps)
        if (NumberOfMaps1 != NumberOfMaps2):
            NumberOfMaps1 = NumberOfMaps2
            print ('correct.\t', NumberOfMaps1, 'maps')
            print(' ')
        mapas=([])
        mxoff=([])
        myoff=([])
        nameMaps=([])
        ### Getting time 09-04-2018 ###
        times=([])
        # Em 13-01-2018 colocado os horarios de cada mapa
        nphourMap=np.array(hoursOfeachRecord)
        '''
        if numberOfregs > 1:
            print("nphourMap :",nphourMap[0])
        '''
        hourMaps=([])
    
        #
        '''EXTRAIR MAPAS INDIVIDUALMENTE'''
        for m in range(NumberOfMaps1):
            k = opmoderange[NumberOfMaps[m,0]:NumberOfMaps[m,1]]
            if (len(k)==0):
                continue
            # print 'k', np.shape(k)
            adc_aux = adc[k]
            xoff_aux = arxoff[k]
            yoff_aux = aryoff[k]
            ### Getting time 09-04-2018 ###
            time_aux=dataTime[k]
            
            # Em 13-01-2018 colocado os horarios de cada mapa
            hourmap_aux = nphourMap[k]
            '''
            if numberOfregs > 1:
                print("k : ", k)
                print(" hourmap_aux :",hourmap_aux)
                print(" nphourMap :",nphourMap[k])
                print(" nphourMap :",nphourMap)
            '''
            #
            # print 'adc_aux', np.shape(adc_aux)
            op_aux = oprangemap[NumberOfMaps[m,0]:NumberOfMaps[m,1]]
            # print 'op_aux', np.shape(op_aux)
            medianOprangemap = np.median(op_aux)
            # print ty
            kk, = np.where(op_aux == medianOprangemap)
            
            #print ('adc_aux :',adc_aux)
            #print ('shape   :', adc_aux.shape)
            #plt.plot(adc_aux)
            mapas.append(adc_aux)
            #nameMaps.append('')
            mxoff.append(xoff_aux)
            myoff.append(yoff_aux)
            ### Getting time 09-04-2018 ###
            times.append(time_aux)
            
            # Em 13-01-2018 colocado os horarios de cada mapa
            hourMaps.append(hourmap_aux)
            
            #print("num mapas: ",len(mapas))
            #print("num xoff: ",len(mxoff))
            #print("num yoff: ",len(myoff))        
        
        # colocando nas listas
        # Em 13-01-2018 colocado os horarios de cada mapa e eliminando dados desnecessarios
        
        self.listOfmaps =  mapas
        self.listOfxoffs = mxoff
        self.listOfyoffs = myoff
        self.listOfHourMaps = hourMaps
        ### Getting time 09-04-2018 ###
        self.timeArray = times
        
        #return mapas,mxoff,myoff,hourMaps