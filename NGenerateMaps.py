# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 09:10:45 2017

@author: A0068182
"""

import sys
import numpy as np
from SSTMethods import *
from matplotlib import pyplot as plt, cm, colors
from scipy.io.idl import readsav # alternativa a idlsave
from NSSTMap import *
from ArtificialMap import *
from MapRepair import *
from PlotMap import *
import re
from os import listdir
from os.path import isfile, join
import datetime
from TempCalibration import *
#21-01-2018
import os
IMAGEFOLDERINSUMO='/image/insumo/'
ROOTIMAGEFOLDER = 'E:/RUN/'

### 23-02-2018
from SSTGZIP import *
###

#GENERAL SETUP
# LEITURA DO ARQUIVO DE DADOS
PATHBPOS='E:/RUN/beans/bpos.save'
PATHSTBEAMS='E:/RUN/beans/stackedbeams2012.txt'
DTHINIT='2009-01-07 12:00:00'
DTHEND='2009-01-07 12:59:59'
TYPESSTFILE='rs'
PATHSSTMAPS='E:/RUN/todos_teste'
PATHFIGURE='E:/RUN/todos_teste/Maps/'
NAMEFORMAT='(rs[0-9]+\.[0-9]{4})'
ROOTPATH='E:/SST/'
TIME1=":00:00"
TIME2=":59:59"
MONTH='/M'
DAY='/D'
ENDTAG='/intg'
_212GHZ=212
_405GHZ=405
NUMBEROFMAPAS=5

class NGenerateMaps:

    def __init__(self,dtini,dtend):

        self.generateAllFigures(dtini,dtend)
        
    ### 22-02-2018 including verification of dates
    def __isLeap(self,year):
           if ((year % 4 == 0) and ((year % 400 == 0) or (year % 100 != 0))):
               return 29
           else:
               return 28
        
    def __getMaxDay(self,year,month):
        if ((month == 1) or (month == 3) or (month == 5) or (month == 7) or (month == 8) or (month == 10) or (month == 12)):
            return 31
        else:
            if (month == 2):
                return self.__isLeap(year)
            else:
                return 30
    ###
    ## 26-02-2018 - Check if there are the files ###
    ##
    def __isAreThere(self,file_path):
        listOfNewMasp=([])
        if os.path.exists(file_path):
            listFiles = os.listdir(file_path)
            numberOffiles =  len(listFiles)
        
            for i in range(numberOffiles):
                listOfNewMasp.append(listFiles[i])
            
        return listOfNewMasp
        
    def __getTime(self,fileName):
        retorno = str(int(fileName[2:5]) + 1900) + "-" + fileName[5:7] + "-" + fileName[7:9] + " "
        retorno1 = retorno + fileName[10:12] + TIME1
        retorno2 = retorno + fileName[10:12] + TIME2
        return retorno1, retorno2
    
    def generateAllFigures(self,dtini,dtend):
        year1  = dtini[0:4]
        month1 = dtini[5:7]
        day1   = dtini[8:10]
        hour1  = dtini[11:19]
        year2  = dtend[0:4]
        month2 = dtend[5:7]
        day2   = dtend[8:10]
        hour2  = dtend[11:19]
        
        repairedTitleList=np.array(['map beam1','map beam2','map beam3','map beam4','map beam5','map beam6'])
        
        nameFile = re.compile(NAMEFORMAT)
        path=PATHSSTMAPS
        
        
        plot=PlotMap(PATHFIGURE)
         
        ###### Inicio para geracao dos mapas
 
        totalmaps=0
        SunMaps=([])
        #list=([])
        list2=([])
        
            
        for a in range(int(year1),int(year2)+1):
            ano = str(a)
            list2.append(ano)
            print 'ano:', ano
            for m in range(int(month1),int(month2)+1): # inverno hemsferio sul
                if m < 10:
                    mes = '0'+str(m)
                else:
                    mes = str(m)
                #print '  mes:', mes,
                ### 22-02-2018 including data verification ###
                daymax=self.__getMaxDay(int(ano),int(mes))
                print("daymax :", daymax)
                for d in range(int(day1),daymax+1):#int(day2)+1):
                    
                    if d < 10:
                        dia = '0'+str(d)
                    else:
                        dia = str(d)
                    # o dia inteiro
                    time1 = ano+'-'+mes+'-'+dia+' '+hour1
                    time2 = ano+'-'+mes+'-'+dia+' '+hour2
                    file_path = (ROOTPATH+time1[0:4]+MONTH+time1[5:7]+DAY+time1[8:10]+ENDTAG)
                    print("file_path :",file_path)
                    #### EXTRACT GIZP FILES IF THERE ARE 23-02-2018 ####
                    #sstgzip = SSTGZIP(file_path)
                    #sstgzip.extractGzipFiles()
                    ####
                    ### 26-02-2018 to find if there are maps built!
                    pathToCheck = ROOTIMAGEFOLDER+file_path[3:len(file_path)]+IMAGEFOLDERINSUMO
                    #print("pathToCheck : ",pathToCheck)
                    listFilesToGenMap = self.__isAreThere(pathToCheck)
                    if (len(listFilesToGenMap) == 0):
                        nsstMap = NSSTMap(time1,time2,TYPESSTFILE,file_path)
                        # Em 13-01-2018 colocado os horarios de cada mapa
                        ## em 10-04-2018 recebendo valores de time para correção do mapa
                        
                        mapas,mxoff,myoff,hourMaps,timeArray = nsstMap.getMaps( )
                        flag=1 # can generate maps
                    else:
                        flag=2 #cant generate maps
                        print('Maps already exists on ',pathToCheck)

                    #print("------------------------------ ")
                    #print(" mapas contem : ",mapas)
                    #print("------------------------------ ")
                    #time1, time2 = self.__getTime(fileName)
                    #sstmap = SSTMap(time1,time2,TYPESSTFILE,PATHSSTMAPS)
                    #flag=1
                    flag2=1
                    flagcalib=2
                    if (flag==1):
                        numberOfMaps=len(mapas)
                        
                        for i in range(numberOfMaps):
                            listrepairedmaps = ([])
                            listcalibratedmaps = ([])
                            listpuremaps=([])
                            
                            #fileName=TYPESSTFILE+'1'+time1[0:2]+time1[5:7]+time1[8:10]+"#"+str(i)
                            '''
                            print("ano : ",time1[2:5])
                            print("mes : ",time1[5:7])
                            print("dia : ",time1[8:10])
                            print("numberOfMaps : ", numberOfMaps)
                            print("i : ",i)
                            print(hourMaps[0][1])
                            print(hourMaps[0][0])
                            print("hora : ",hourMaps[i][0])
                            print("str : ",str(i))
                            '''
                            ## to include 1999 files - 07/03/2018
                            if (ano == '1999'):
                                fileName=TYPESSTFILE+time1[2:4]+time1[5:7]+time1[8:10]+"."+hourMaps[i][0]+"#"+str(i)
                            else:
                                fileName=TYPESSTFILE+'1'+time1[2:4]+time1[5:7]+time1[8:10]+"."+hourMaps[i][0]+"#"+str(i)
                            print(fileName)
                            # 15-01-2018 must stay equal to 'yyyy-mm-dd hh:mm'
                            hour=hourMaps[i][0]
                            h=hour[0:2]
                            m=hour[2:4]
                            
                            ### Getting time 09-04-2018 ###
                            
                            try:
                                listTime = timeArray[i]
                                dateToEtaAndP = listTime[int((len(listTime)-1)/2)]
                            except:
                                dateToEtaAndP = datetime(int(time1[2:4]), int(time1[5:7]), int(time1[8:10]), int(hourMaps[i][0]), 00, 00)
                           
                            print ("dateToEtaAndP :",dateToEtaAndP)
                            
                            print(" ")
                            print 'Arquivo %s'%(fileName)
                            print('time start: ',datetime.datetime.now())
                        
                            mapasaux=mapas[i].T
                            repairAndCalib = True
                            ### 24-05-2018
                            if (repairAndCalib == True):
                                #20-01-2018
                                calib = TempCalibration()
                                
                                for j in range(6):
                                    print 'fixing maps in %s...'%(fileName)
                                    mapRepair=MapRepair(PATHBPOS, PATHSTBEAMS)
                                    if (j<=3):
                                        mapr=mapRepair.repairMap(j+1,mapasaux[j],mxoff[i],myoff[i],_212GHZ)
                                        print("map"+str(j+1)+ " repaired in "+str(datetime.datetime.now()))
                                        maprc=calib.getTempCalibMap(mapr,_212GHZ)
                                        print("map"+str(j+1)+ " calibrated in "+str(datetime.datetime.now()))
                                    else:
                                        mapr=mapRepair.repairMap(j+1,mapasaux[j],mxoff[i],myoff[i],_405GHZ)
                                        print("map"+str(j+1)+ " repaired in "+str(datetime.datetime.now()))
                                        maprc=calib.getTempCalibMap(mapr,_405GHZ)
                                        print("map"+str(j+1)+ " calibrated in "+str(datetime.datetime.now()))
                                    
                                    listrepairedmaps.append(mapr)
                                    listcalibratedmaps.append(maprc)
                                    
                                                              
                                repairedlistmaptoplot=np.array(listrepairedmaps)
                                calibratedlistmaptoplot=np.array(listcalibratedmaps)
                                if (flagcalib == 1):
                                    listtoplot=repairedlistmaptoplot
                                else:
                                    listtoplot=calibratedlistmaptoplot
                            else: #pure maps
                                for j in range(6):
                                    listpuremaps.append(mapasaux[j])
                                listtoplot = np.array(listpuremaps)
                            print 'generating maps for %s...'%(fileName)
                            #21-01-2018
                            #Changin folder to deploy image
                            file_path_part = file_path[3:len(file_path)]
                            newpath = ROOTIMAGEFOLDER+file_path_part+IMAGEFOLDERINSUMO
                            if not os.path.exists(newpath):
                                os.makedirs(newpath)
                            print("newpath :",newpath)
                            plot.setPath(newpath)
                            
                            #20-01-2018
                            
                            if (flag2==1):
                                # 15-01-2018 including dateWithPic
                                # 10-04-2018 changing to dateToEtaAndP
                                plot.generateFigure(dateToEtaAndP, fileName,listtoplot,mxoff[i],myoff[i],repairedTitleList)
                            else:
                                # 16-01-2018 generating separated figures
                                # 10-04-2018 changing to dateToEtaAndP
                                plot.generateSepFigure(dateToEtaAndP, fileName,listtoplot,mxoff[i],myoff[i],repairedTitleList)
                                print('time end: ',datetime.datetime.now())
                            print ' '