# -*- coding: utf-8 -*-
"""
Created on Fri Mar 03 16:41:08 2017

@author: Andre Luiz
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate as scp


from scipy.interpolate import griddata 
import sys
import numpy.ma as ma 
import numpy as np
from scipy.io.idl import readsav # alternativa a idlsave
from scipy.signal import correlate
from matplotlib import cm
#08-01-2018
import matplotlib.colors
from datetime import datetime
import sunpy.coordinates
from astropy.coordinates import EarthLocation
import astropy.units as u
import math as m

#15-01-2018
from sunpy.image.transform import affine_transform


#
XLABEL='X_OFF'
YLABEL='Y_OFF'
EXTENSION='.png'
TSUN_212=5900.
TSUN_405=5100.

#################################################################
plt.rc('figure',figsize=(24,12))
font = {'family' : 'Serif',
        'weight' : 'normal',
        'size'   : 14}
plt.rc('font', **font)
plt.rc('xtick', labelsize=12) 
plt.rc('ytick', labelsize=12)
##################################################################

class PlotMap:
    
    def __init__(self, pathFictures):
        self.pathFictures=pathFictures
    
    #21-01-2018        
    def setPath(self, pathFictures):
        self.pathFictures=pathFictures
    
    #04-02-2018
    def getIndex(self,sortedmap,value):
        index=0
        for x in range(len(sortedmap)):
            if ((sortedmap[x]<=value+2) and (sortedmap[x]>=value-2)):
                index=x
        if (index == 0):
            index = len(sortedmap)    
        return index


    # 15-01-2018 
    ## correção em 10-04-2018 para receber apenas um datetime 
    def __getEtaMinusP(self,daterec):
        '''
        print("datarec :",daterec)
        year=int(daterec[0:4])
        month=int(daterec[5:7])
        day=int(daterec[8:10])
        hour=int(daterec[11:13])
        print("hour : ",hour)
        mm=int(daterec[14:16])
        ss=0
        '''
        etaminusp=0.
        time = daterec #datetime(year,month, day, hour, mm, ss)
        #print("PLOT TIME : ",time)
        casleo = [-31.799,-69.303]*u.deg
        loc = EarthLocation(lat=casleo[0], lon=casleo[1])   
        error_angle = 0.0 * u.deg # update this in case your camera was not perfectly level.
        solar_rotation_angle = sunpy.coordinates.get_sun_orientation(loc, time) + error_angle
        #print solar_rotation_angle ##This is (eta -P) angle!!!
        
        dmsangle=solar_rotation_angle.dms
        angle=dmsangle.d
        minute=dmsangle.m
        sec=dmsangle.s
        etaminusp=float(angle+minute/60+sec/3600)
        
        return etaminusp
    
    def mapRotation(self,zobs,datarec):
        theta = self.__getEtaMinusP(datarec)
        print(theta)
        #### 10/04/2018  ####
        #### correção do calculo da rotacao para radianos ###
        
        rmatrix=np.ndarray(shape=(2,2), dtype=float)
        rmatrix[0][0] = m.cos(theta*(np.pi/180))
        rmatrix[0][1] = m.sin(theta*(np.pi/180))
        rmatrix[1][0] = -m.sin(theta*(np.pi/180))
        rmatrix[1][1] = m.cos(theta*(np.pi/180))
        
        maprotated = affine_transform(zobs, rmatrix)

        return maprotated
    ###
    
    def plotMap(self,maptoplot,x,y,title):
    
        num_points=50
        lvls  = np.linspace(np.min(maptoplot),np.max(maptoplot),num_points)
        xi = np.linspace(np.min(x),np.max(x),num_points)
        yi = np.linspace(np.min(y),np.max(y),num_points)
        zi = griddata((x, y), maptoplot, (xi[None,:], yi[:,None]), method='cubic')

        # make figure
        fig = plt.figure()
        fig.suptitle(title, fontsize=20)
        #plt.xlabel(XLABEL, fontsize=18)
        #plt.ylabel(YLABEL, fontsize=16)
        # set aspect = 1 to make it a circle
        ax = fig.add_subplot(111, aspect = 1)
        
        # use different number of levels for the fill and the lines
        #CS = ax.contourf(xi, yi, zi, 60, cmap = plt.cm.jet, zorder = 1,linewidths = 1.2,levels=lvls)
        # 08-01-2018 - test
        # Test1
        #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","violet","blue","black","yellow","green","red","orange","black"])
        #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","red","Orange","yellow","white","red","orange","yellow","red"])
        #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red"])
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","white","white","white","orange","red","orange","yellow","red"])
        #
        CS = ax.contourf(xi, yi, zi,linewidths = 1.2,levels=lvls,cmap=cmap)#cmap='hot')

        # make a color bar
        cbar = fig.colorbar(CS, ax=ax)
        
        plt.grid()

        plt.show()
    def generateFigure(self,dateWithPic,mapname,listmaptoplot,x,y,listtitle):
        num_points=100
        fig=plt.figure(figsize=(24, 12))
        fig.suptitle(mapname, fontsize=16)
    
        for index in range(len(listmaptoplot)):
            try:
                maptoplot=listmaptoplot[index]
                title=listtitle[index]
                lvls  = np.linspace(np.min(maptoplot),np.max(maptoplot),num_points)
                xi = np.linspace(np.min(x),np.max(x),num_points)
                yi = np.linspace(np.min(y),np.max(y),num_points)
                zi = griddata((x, y), maptoplot, (xi[None,:], yi[:,None]), method='cubic')
                #15-01-2018 including zir instead zi
                zir = self.mapRotation(zi,dateWithPic)
                #
                #ax = fig.add_subplot(231+index)
                ax = fig.add_subplot(231+index,axisbg='black')
                ax.set_title(title)
                # 08-01-2018 - test
                # Test1
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","violet","blue","black","yellow","green","red","orange","black"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","red","Orange","yellow","white","red","orange","yellow","red"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","blue"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","white","white","white","orange","red","orange","yellow","red","blue"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","orange","yellow"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","white","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","red"])
                          
                #
                #15-01-2018 including zir instead zi
                CS = ax.contourf(xi, yi, zir,linewidths = 1.2,levels=lvls,cmap='hot')#cmap='hot',clim=(23000,30000))
                #20-01-2018
                ax.contour(xi, yi, zir, linewidths = .1,linewidth=.1,levels=lvls, colors='black')
                
                cbar = fig.colorbar(CS, ax=ax)
            except:
                print("did not was possible generate that picture: ",maptoplot)
          
        plt.savefig(self.pathFictures+mapname+EXTENSION)
        plt.clf()

    ### 21-02-2018 ###
    ### Ideia abandonada
    ###
    '''
    # 15-01-2018 including dateWithPic
    def generateFigure(self,dateWithPic,mapname,listmaptoplot,x,y,listtitle):
        num_points=50
        fig=plt.figure(figsize=(24, 12))
        fig.suptitle(mapname, fontsize=16)
    
        for index in range(len(listmaptoplot)):
            maptoplot=listmaptoplot[index]
            title=listtitle[index]
            lvls  = np.linspace(np.min(maptoplot),np.max(maptoplot),num_points)
            xi = np.linspace(np.min(x),np.max(x),num_points)
            yi = np.linspace(np.min(y),np.max(y),num_points)
            zi = griddata((x, y), maptoplot, (xi[None,:], yi[:,None]), method='cubic')
            #15-01-2018 including zir instead zi
            zir = self.mapRotation(zi,dateWithPic)
            #
            #ax = fig.add_subplot(231+index)
            ax = fig.add_subplot(231+index,axisbg='black')
            ax.set_title(title)
            # 08-01-2018 - test
            # Test1
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","violet","blue","black","yellow","green","red","orange","black"])
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","red","Orange","yellow","white","red","orange","yellow","red"])
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","blue"])
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","white","white","white","orange","red","orange","yellow","red","blue"])
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","orange","yellow"])
            #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","white","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","yellow","red"])
            # 04-02-2018
            if (index <= 3):
                tempRef=TSUN_212
            else:
                tempRef=TSUN_405
                
            sizeMaptoplot=len(np.sort(maptoplot))
            valueOverTempQuietSun=self.getIndex(np.sort(maptoplot),tempRef*1.022)
            iQuietSun=self.getIndex(np.sort(maptoplot),tempRef)
            delta=40
            listLines=([])
            listColors=([])
            for i in range(sizeMaptoplot):
                 if ((i <= iQuietSun+delta) and (i >= iQuietSun-delta)):
                     listLines.append('red')
                     listColors.append('red')
                 else:
                     if (i >= valueOverTempQuietSun):
                         listLines.append('black')
                         listColors.append('yellow')
                     else:
                         if ((i < valueOverTempQuietSun) and (i >= iQuietSun-delta)):
                             listLines.append('white')
                             listColors.append('white')
                         else:
                             listLines.append('black')
                             listColors.append('black')
            
            cmap_lines = matplotlib.colors.LinearSegmentedColormap.from_list("",listLines,N=sizeMaptoplot)
            cmap_colors = matplotlib.colors.LinearSegmentedColormap.from_list("",listColors,N=sizeMaptoplot)

            #
            #15-01-2018 including zir instead zi
            CS = ax.contourf(xi, yi, zir,linewidths = 1.2,levels=lvls,cmap='hot')#cmap='hot',clim=(23000,30000))
            #20-01-2018
            ax.contour(xi, yi, zir, linewidths = .1,linewidth=.1,levels=lvls, colors='black')
            
            cbar = fig.colorbar(CS, ax=ax)
        plt.savefig(self.pathFictures+mapname+EXTENSION)
        plt.clf()
    '''
    # Creating a scale with temperature and colors
    #
    #def generateColorMapCorrelated(self,maptoplot):
        
        #return ncmap
        
    # 16-01-2018 generating separated pictures
    def generateSepFigure(self,dateWithPic,mapname,listmaptoplot,x,y,listtitle):
        num_points=50
        fig=plt.figure(figsize=(4, 4))

    
        for index in range(len(listmaptoplot)):
            ### excepetion handling 11-04-2018
            try:
                maptoplot=listmaptoplot[index]
                title=listtitle[index]
                lvls  = np.linspace(np.min(maptoplot),np.max(maptoplot),num_points)
                xi = np.linspace(np.min(x),np.max(x),num_points)
                yi = np.linspace(np.min(y),np.max(y),num_points)
                zi = griddata((x, y), maptoplot, (xi[None,:], yi[:,None]), method='cubic')
                #15-01-2018 including zir instead zi
                zir = self.mapRotation(zi,dateWithPic)
                #
                #ax = fig.add_subplot(231+index)
                ax = fig.add_subplot(1, 1, 1,axisbg='black')
                #ax.set_title(title)
                ax.axis('off')
                # 08-01-2018 - test
                # Test1
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","violet","blue","black","yellow","green","red","orange","black"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","red","Orange","yellow","white","red","orange","yellow","red"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","blue"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["white","white","white","white","orange","red","orange","yellow","red","blue"])
                #cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","black","white","red","orange","yellow","red","orange","yellow"])
                cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["black","black","black","yellow","yellow","yellow"])
                #
                #15-01-2018 including zir instead zi
                
                CS = ax.contourf(xi, yi, zir,linewidths = 1.2,levels=lvls,cmap='hot')#,clim=(23000,30000))
                #20-01-2018
                ax.contour(xi, yi, zir, linewidths = .1,linewidth=.1,levels=lvls, colors='black')
                #cbar = fig.colorbar(CS, ax=ax)
                print("writing in... ",self.pathFictures+mapname)
                plt.savefig(self.pathFictures+mapname+"-"+title+EXTENSION)
                plt.clf()
            except:
                print("did not was possible generate that picture: ",self.pathFictures+mapname+"-"+title+EXTENSION)
                
           
                