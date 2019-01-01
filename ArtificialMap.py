# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:24:50 2017

@author: Andre Luiz
"""
import sys
import numpy as np
from scipy.io.idl import readsav # alternativa a idlsave
from SSTMap import *
import numpy.ma as ma 
from PlotMap import *

# RANGE OF BEANS
RANGEBEAM1_INI=0
RANGEBEAM1_END=601 
RANGEBEAM2_INI=601
RANGEBEAM2_END=1202 
RANGEBEAM3_INI=1202
RANGEBEAM3_END=1803 
RANGEBEAM4_INI=1803
RANGEBEAM4_END=2404 
RANGEBEAM5_INI=2404
RANGEBEAM5_END=3005 
RANGEBEAM6_INI=3005
RANGEBEAM6_END=3606 
# beams
BEAM_ONE=0
BEAM_TWO=1
BEAM_TREE=2
BEAM_FOUR=3
BEAM_FIVE=4
BEAM_SIX=5

#defining transformations
PARAM_XYBEAMPOS=60./3.6 

# raios medios do sol
R212_1=16.22
R212_2=16.16
R212_3=16.18
R212_4=16.25
R405_1=16.17
R405_2=16.26
PARAMTOARCSEC=60.
XYOFFEXTENSION=1008+601+600
FACTOR=1.004
ARCSECPERPIXEL=3.6

#ARTIFICIAL MAP
FLOAT='float'
HALF=0.5
NOISEMULT=10
NOISEADD=270
AREADIVIDER=2
VALUEPOWER=2
FILLINGVALUE=6300.0
VINITIAL=0
CONVOLVEVALUE1=300
CONVOLVEVALUE2=301 
CONVOLVEVALUE3=1 
ZERO=0
ONE=1
AMPFACTOR=1

### inserted in 21-02-2018
import datetime
###

class ArtificialMap:

    def __init__(self, xoff, yoff, pathBpos, pathstbeams):
        self.xoff = xoff/3.6
        self.yoff = yoff/3.6
        self.xcal1=0
        self.ycal1=0
        self.pathBpos    = pathBpos
        self.pathstbeams = pathstbeams
        self.__readFiles()
        self.__defBeams()
        self.__defCenterCoordinates()
        self.__defArtificialRadius()
    
    def __readFiles(self):
        self.bposfile = readsav(self.pathBpos)
        self.stbeams = np.loadtxt(self.pathstbeams)
                        
        
    def __defBeams(self):
        self.beam1 = (self.stbeams[RANGEBEAM1_INI:RANGEBEAM1_END,:])
        self.beam2 = (self.stbeams[RANGEBEAM2_INI:RANGEBEAM2_END,:])                                   
        self.beam3 = (self.stbeams[RANGEBEAM3_INI:RANGEBEAM3_END,:])
        self.beam4 = (self.stbeams[RANGEBEAM4_INI:RANGEBEAM4_END,:])
        self.beam5 = (self.stbeams[RANGEBEAM5_INI:RANGEBEAM5_END,:])
        self.beam6 = (self.stbeams[RANGEBEAM6_INI:RANGEBEAM6_END,:])

    def __defCenterCoordinates(self):
        self.xbeampos = self.bposfile.bpos.off[ZERO]*PARAM_XYBEAMPOS #posicao dos feixes em relacao ao azimute
        self.ybeampos = self.bposfile.bpos.el[ZERO]*PARAM_XYBEAMPOS #posicao dos feixes em relacao a elevacao
        # copiando xcenter e ycenter do beam5 mais central.        
        self.xcenter,self.ycenter = self.xbeampos[BEAM_FIVE],self.ybeampos[BEAM_FIVE] 
        self.xbeampos -= self.xcenter # beam 5 como centro
        self.ybeampos -= self.ycenter # beam 5 como centro
                        
    def __defArtificialRadius(self):
        ##################################################################
        #radio del Sol en las dos frequencias
        # Jorge pegou valores medios do raio em radio.
        # ver raio do sunpy -> pesquisar a respeito.
        mr212 = np.mean([R212_1, R212_2, R212_3, R212_4])*PARAMTOARCSEC
        mr405 = np.mean([R405_1, R405_2])*PARAMTOARCSEC
        
        #dimensiones del campo (3.6 arcsec per pixel)
        #largura = w e altura = h
        self.width_field = np.int(XYOFFEXTENSION) #extension del xoff/yoff + borde de 301 p.
        self.height_field = self.width_field
        ## factor quie optimiza el ajuste de radio solar en 212/405 
        #el radio del sol artificial escalado al campo
        self.radius212 = np.int(FACTOR*mr212/ARCSECPERPIXEL)
        self.radius405 = np.int(FACTOR*mr405/ARCSECPERPIXEL)


    ################
    # functions to get artificial maps
    ###
    
    def __defArtificialAreaMap(self):
        #creando el sol artificial 212
        area_sun = np.zeros((self.width_field, self.height_field)).astype(FLOAT) # the background
        self.total_area=np.zeros((self.width_field, self.height_field)).astype(FLOAT) # the background        
        ##the background sky 
        ## populando com numeros aleatorios [0,1] com valor abaixo de 0.5 e multiplicados por 10
        ## somados com 270
        noise = NOISEADD + NOISEMULT*(np.random.rand(len(area_sun),len(area_sun))-HALF)
        self.total_area = area_sun + noise
        #Defining the center for the cyrcle
        self.center_x, self.center_y = np.int(self.width_field/AREADIVIDER), np.int(self.height_field/AREADIVIDER)
        
        
    def __defArtificialMap_212(self):
        
        self.__defArtificialAreaMap()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_212")
            print(datetime.datetime.now())
            ###
        #filling the circle
        self.total_212_area=self.total_area
        x_frame, y_frame = np.ogrid[-self.radius212:self.radius212, -self.radius212:self.radius212]
        index_mask = x_frame**VALUEPOWER + y_frame**VALUEPOWER <= self.radius212**VALUEPOWER
        #define uma matriz com o sol artificial com valor de intensidade =6300 no centro
        self.total_212_area[self.center_x-self.radius212:self.center_x+self.radius212, self.center_y-self.radius212:self.center_y+self.radius212][index_mask] = FILLINGVALUE
                
        #re-localizando los datos de posicion for 212
        self.xcal_212,self.ycal_212 = self.xoff+len(self.total_212_area)/AREADIVIDER,self.yoff+len(self.total_212_area)/AREADIVIDER
        
        # datos deplazados al cuadrante positivo
        #dados deslocados para o quadrante positivo
        
        ##################################################################
        self.xcal1_212 = self.xcal_212 + self.xbeampos[0] #xcal1 = azimute_sol+azimute_beam
        self.ycal1_212 = self.ycal_212 + self.ybeampos[0] #ycal1 = elevação_sol+elevação_beam
        

    def __getArtificialMap_212_beam1(self):
        
        self.__defArtificialMap_212()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_212_beam1")
            print(datetime.datetime.now())
            ###  
        flag=False
        if (flag == True):
            ###
            print("convsum_212_b1 - ini")
            print(datetime.datetime.now())
            ### 
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_212_b1=np.zeros(len(self.xcal_212))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_212= self.total_212_area[self.xcal1_212[j].astype(int)-CONVOLVEVALUE1:self.xcal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_212[j].astype(int)-CONVOLVEVALUE1:self.ycal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_212_b1[j]=np.sum(unver_212*self.beam1[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        
        if (flag == True):
            ###
            print("convsum_212_b1 - end and normcs_212_b1 - ini")
            print(datetime.datetime.now())
            ### 
        self.normcs_212_b1 = (self.convsum_212_b1[ZERO:len(self.xoff)]- np.min(self.convsum_212_b1[ZERO:len(self.xoff)]))/np.max(self.convsum_212_b1[ZERO:len(self.xoff)])
        if (flag == True):
            ###
            print("normcs_212_b1 - end")
            print(datetime.datetime.now())
            ### 
        return self.normcs_212_b1
        
    def __getArtificialMap_212_beam2(self):
        
        self.__defArtificialMap_212()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_212_beam2")
            print(datetime.datetime.now())
            ###        
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_212_b2=np.zeros(len(self.xcal_212))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_212= self.total_212_area[self.xcal1_212[j].astype(int)-CONVOLVEVALUE1:self.xcal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_212[j].astype(int)-CONVOLVEVALUE1:self.ycal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_212_b2[j]=np.sum(unver_212*self.beam2[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        self.normcs_212_b2 = (self.convsum_212_b2[ZERO:len(self.xoff)]- np.min(self.convsum_212_b2[ZERO:len(self.xoff)]))/np.max(self.convsum_212_b2[ZERO:len(self.xoff)])
    
        return self.normcs_212_b2
        
    def __getArtificialMap_212_beam3(self):
                
        self.__defArtificialMap_212()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_212_beam3")
            print(datetime.datetime.now())
            ###
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_212_b3=np.zeros(len(self.xcal_212))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_212= self.total_212_area[self.xcal1_212[j].astype(int)-CONVOLVEVALUE1:self.xcal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_212[j].astype(int)-CONVOLVEVALUE1:self.ycal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_212_b3[j] = np.sum(unver_212*self.beam3[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        
        self.normcs_212_b3 = (self.convsum_212_b3[ZERO:len(self.xoff)]- np.min(self.convsum_212_b3[ZERO:len(self.xoff)]))/np.max(self.convsum_212_b3[ZERO:len(self.xoff)])
    
        return self.normcs_212_b3
        
    def __getArtificialMap_212_beam4(self):
                
        self.__defArtificialMap_212()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_212_beam4")
            print(datetime.datetime.now())
            ###
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_212_b4=np.zeros(len(self.xcal_212))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_212= self.total_212_area[self.xcal1_212[j].astype(int)-CONVOLVEVALUE1:self.xcal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_212[j].astype(int)-CONVOLVEVALUE1:self.ycal1_212[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_212_b4[j] = np.sum(unver_212*self.beam4[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        
        self.normcs_212_b4 = (self.convsum_212_b4[ZERO:len(self.xoff)]- np.min(self.convsum_212_b4[ZERO:len(self.xoff)]))/np.max(self.convsum_212_b4[ZERO:len(self.xoff)])
    
        return self.normcs_212_b4

        
    def __defArtificialMap_405(self):

        self.__defArtificialAreaMap()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_405")
            print(datetime.datetime.now())
            ###
        self.total_405_area=self.total_area
        x_frame, y_frame = np.ogrid[-self.radius405:self.radius405, -self.radius405:self.radius405]
        index_mask = x_frame**VALUEPOWER + y_frame**VALUEPOWER <= self.radius212**VALUEPOWER
        #define uma matriz com o sol artificial com valor de intensidade =6300 no centro
        self.total_405_area[self.center_x-self.radius405:self.center_x+self.radius405, self.center_y-self.radius405:self.center_y+self.radius405][index_mask] = FILLINGVALUE
    
        #re-localizando los datos de posicion for 212
        self.xcal_405,self.ycal_405 = self.xoff+len(self.total_405_area)/AREADIVIDER,self.yoff+len(self.total_405_area)/AREADIVIDER
       
        # datos deplazados al cuadrante positivo
        #dados deslocados para o quadrante positivo
       
        ##################################################################
        self.xcal1_405 = self.xcal_405 + self.xbeampos[0] #xcal1 = azimute_sol+azimute_beam
        self.ycal1_405 = self.ycal_405 + self.ybeampos[0] #ycal1 = elevação_sol+elevação_beam
        

    def __getArtificialMap_405_beam5(self):
                
        self.__defArtificialMap_405()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_405_beam5")
            print(datetime.datetime.now())
            ###
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_405_b5=np.zeros(len(self.xcal_405))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_405= self.total_405_area[self.xcal1_405[j].astype(int)-CONVOLVEVALUE1:self.xcal1_405[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_405[j].astype(int)-CONVOLVEVALUE1:self.ycal1_405[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_405_b5[j] = np.sum(unver_405*self.beam5[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        
        self.normcs_405_b5 = (self.convsum_405_b5[ZERO:len(self.xoff)]- np.min(self.convsum_405_b5[ZERO:len(self.xoff)]))/np.max(self.convsum_405_b5[ZERO:len(self.xoff)])
    
        return self.normcs_405_b5
      
    def __getArtificialMap_405_beam6(self):
                
        self.__defArtificialMap_405()
        flag=False
        if (flag == True):
            ###
            print("Entrei em __getArtificialMap_405_beam6")
            print(datetime.datetime.now())
            ###
        ####################################################################
        # Criando uma variavel para receber a convolucao tamanho=xcal
        self.convsum_405_b6=np.zeros(len(self.xcal_405))
        for j in range(VINITIAL,len(self.xoff)): # de zero ate a qtde de dados de xoff
            unver_405= self.total_405_area[self.xcal1_405[j].astype(int)-CONVOLVEVALUE1:self.xcal1_405[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3,self.ycal1_405[j].astype(int)-CONVOLVEVALUE1:self.ycal1_405[j].astype(int)+CONVOLVEVALUE2:CONVOLVEVALUE3]
            self.convsum_405_b6[j] = np.sum(unver_405*self.beam6[RANGEBEAM1_INI:RANGEBEAM1_END,RANGEBEAM1_INI:RANGEBEAM1_END])
        
        self.normcs_405_b6 = (self.convsum_405_b6[ZERO:len(self.xoff)]- np.min(self.convsum_405_b6[ZERO:len(self.xoff)]))/np.max(self.convsum_405_b6[ZERO:len(self.xoff)])
    
        return self.normcs_405_b6
        
    def getArtificialMap(self,index):
        if (index == 1):
            return self.__getArtificialMap_212_beam1()
        else:
            if (index == 2):
                return self.__getArtificialMap_212_beam2()
            else:
                if (index == 3):
                    return self.__getArtificialMap_212_beam3()
                else:
                    if (index == 4):
                        return self.__getArtificialMap_212_beam4()
                    else:
                        if (index == 5):
                            return self.__getArtificialMap_405_beam5()
                        else:
                            return self.__getArtificialMap_405_beam6()
        
        '''
        switcherMap = {
            1: self.__getArtificialMap_212_beam1(),
            2: self.__getArtificialMap_212_beam2(),
            3: self.__getArtificialMap_212_beam3(),
            4: self.__getArtificialMap_212_beam4(),
            5: self.__getArtificialMap_405_beam5(),
            6: self.__getArtificialMap_405_beam6()}
    
        return switcherMap.get(index, self.__getArtificialMap_212_beam1())
        '''
    def getCoordinates(self):
        return self.xoff,self.yoff
            
    def getCalCoordinates(self,ghz):
        #print("getCalCoordinates - ghz : ",ghz)
        if (ghz==212):
            #print(" coordinates :",self.xcal1_212, self.ycal1_212,self.xcal_212, self.ycal_212)
            return self.xcal1_212, self.ycal1_212,self.xcal_212, self.ycal_212
        else:
            return self.xcal1_405, self.ycal1_405,self.xcal_405, self.ycal_405