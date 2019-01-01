# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 22:22:19 2017

@author: Andre Luiz
"""

import string, os, fnmatch, struct

#!/usr/bin/python

class SSTMethods:
        
    #######################################################################################  
    def  __sst_julian_date(self,isotime):
        '''
        # sst_julian_date
        #
        # Aim: to return the Julian Date for SST data
        #      i.e. no need to check whether date is before Gregorian Reform
        #
        # Input: isotime is a string with a time in ISO format
        #        ISO time format = YYYY-MM-DD hh:mm:ss
        # 
        # Output: the julian date
        #
        # Examples:
        # >>> import sst_methods as sst
        # >>> print sst.sst_julian_date('2014-10-11 13:05:22.5645678')
        #
        # Change record:
        #     Adapted from SST procedure in ephem_lib.c (AM & JERC)
        #     First written by Guigue on 19 February 2015, in Sao Paulo
        #
        ########################################################################################
        '''
        try: 
            ymd,time = isotime.strip().split(" ",1)
        except:
            ymd = isotime.strip()
            time = ''

        year  = float(ymd[0:4])
        month = float(ymd[5:7])
        day   = float(ymd[8:10])

        if (len(time)):
            ss = float(time[7:])
            mm = float(time[4:6])
            hh = float(time[0:3])  
            f_of_day = (hh+mm/60.0+ss/3600.0)/24.0   
        else:
            f_of_day = 0.0

        # Gregorian adopted in Oct., 15, 1582
        greg = 15L + 31L * (10L + 12L * 1582L) ;

        if(month > 2):
            jy = year 
            jm = month + 1 
        else:
            jy = year - 1 
            jm = month + 13 

        jd = long(365.25 * jy) + long(30.6001 * jm) + day + 1720995L 

        if ( day + (31L * (month + 12L * year )) >= greg ) :
            ja = long(0.01 * jy)
            jd = jd + 2 -ja + long(0.25 * ja) 
	
        return float(jd)+f_of_day-0.5 
  

    #######################################################################################  
    def  __sst_base_name(self,isotime):
        '''
        # sst_base_name
        #
        # Aim: to return the SST base name
        #      if a time is given, it also returns this time in hundreds of millisecond (hus)
        #
        # Input: isotime is a string with a time in ISO format
        #        ISO time format = YYYY-MM-DD hh:mm:ss
        # 
        # Output: the SST base name, the time in hus and the isotime of the day
        #
        # Examples:
        # >>> import sst_methods as sst
        # >>> print sst.sst_base_methods('2014-10-11')
        # >>> 1141011 2014-10-11
        # >>> print sst.sst_base_methods('2014-10-11 14:25:33')
        # >>> ['1141112', 519330000L,'2014-10-11']
        #
        # Change record:
        #     First written by Guigue on a sunny day of October 2014, in Sao Paulo
        #     Added the isotime of the day, Feb 2015
        #
        ########################################################################################
        '''
        try: 
            ymd,time = isotime.strip().split(" ",1)
        except:
            ymd = isotime.strip()
            time = ''
    
        year  = ymd[0:4]
        month = ymd[5:7]
        day   = ymd[8:10]
        base_name = str(int(year)-1900)+month+day
  
        if len(time): 
            ss = 0 
            mm = 0
        if len(time) > 5:
            ss = time[6:8]
        if len(time) > 3:
            mm = time[3:5]
            hh = time[0:2]  
            hus = long(hh)*36000000L+long(mm)*600000L+long(ss)*10000L    
            return [base_name,hus,ymd]  
        else:
            return [base_name,0,ymd]  

    ########################################################################################################
    def  __sst_define_fmt(self,sst_file_type,sst_file_date):
        '''
        #
        # sst_define_fmt
        #
        # Aim: to define the string format to be used with struct.unpack() to separate the
        #      different variables. It takes intou account the time evolution of the SST data format.
        #
        #       Letter Code   Numerical Type          Number of Bytes     IDL equivalence
        #            b        byte                           1                 BYTE
        #            B        unsigned byte                  1                 BYTE
        #            h        short integer                  2                 INT
        #            H        unsigned short integer         2                 UINT
        #            i        integer                        4                 LONG
        #            f        float                          4                 FLOAT
        #       The simbol '=' is used here to define the C alignement
        #
        # Inputs:
        #       sst_file_type:  string 'rs' | 'rf' | 'bi' 
        #       sst_file_date:  isotime string with the date
        #
        # Output
        #       a strin with the unpacking format
        #
        # Change Record
        #       First written by Guigue, February 20, 2015 in Sao Paulo
        #
        #
        '''
        if (sst_file_type == 'rs') or (sst_file_type == 'rf'):
            if (sst_file_date > '2002-12-13'):
                sst_bin_fmt='=iHHHHHHiiihhiihhhhhhhhBBhi'
            elif (sst_file_date > '2002-12-03' and sst_file_date <= '2002-12-13'):
                sst_bin_fmt='=iiiiiiiiiihhiihhhhhhhhBBhi'
            elif (sst_file_date > '1999-05-01' and sst_file_date <= '2002-12-03'):
                sst_bin_fmt='=ihhhhhhhhiiihhiihhhhhhhhBBhhi'
            else: 
                sst_bin_fmt=[0,'']
        elif (sst_file_type == 'bi'):
            if (sst_file_date > '2002-12-13'):
                sst_bin_fmt='=iffffHHHHHHffffffhhBBhhhhhhfffffffffffBi'
            elif (sst_file_date > '2002-11-23') and (sst_file_date <= '2002-12-13'):
                sst_bin_fmt='=iffffiiiiiiffffffhhhBBhhhhhhfffffffffffBi'
            elif (sst_file_date > '2002-09-15') and (sst_file_date <= '2002-11-23'):
                sst_bin_fmt='=iffffhhhhhhhhffffffffhhhBBhhhhhhhhhhhhfffffffffffffffffffffffBi'
            elif (sst_file_date <= '2002-09-15') : 
                sst_bin_fmt='=iffffhhhhhhhhffffffffhhhBBhhhhhhhhhhhhfffffffffffffffffffffffBi'
            else:
                sst_bin_fmt=''
        else:
            sst_bin_fmt=''

        return sst_bin_fmt      

    ########################################################################################################
    def  __sst_read_one_record(self,sst_fd,sst_fmt):
        sst_record=os.read(sst_fd,struct.calcsize(sst_fmt))
        return struct.unpack(sst_fmt,sst_record)

    ########################################################################################################
    ''' old - to be substituted by new see below    
    def  __sst_unpack_one_record(self,ur,sst_file_date,sst_file_type):

      hours = ur[0] / 36000000L
      minutes = (ur[0] % 36000000L)/600000L
      seconds = ((ur[0] % 36000000L)%600000L)/1.0E+04
      time_stamp=sst_file_date + \
          '  {0:=02d}'.format(hours)+':{0:=02d}'.format(minutes)+':{0:=07.4f}'.format(seconds)  
      jd = self.__sst_julian_date(time_stamp)
      if (sst_file_type == 'rs') or (sst_file_type == 'rf'):
          if (sst_file_date > '2002-12-13'):
              sst_unpacked_record={'hus_time':ur[0], \
			   'adc':ur[1:7], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
			   'pos_time':ur[7], \
			   'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
			   'pm': [ur[10]/1000.0,ur[11]/1000.0], \
			   'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
			   'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
			   'rec_offset':ur[16:22] , \
			   'target':ur[23] % 32, \
			   'mirror_pos':ur[23] /32 , \
			   'julday': jd , \
			   'time':time_stamp }  
          elif (sst_file_date > '2002-12-03') and (sst_file_date <= '2002-12-13'):
              sst_unpacked_record={'hus_time':ur[0], \
			   'adc':ur[1:7], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
			   'pos_time':ur[7], \
			   'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
			   'pm': [ur[10]/1000.0,ur[11]/1000.0], \
			   'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
			   'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
			   'rec_offset':ur[16:22] , \
			   'target':ur[23] % 32, \
			   'mirror_pos':ur[23] /32 , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_date > '2002-05-20' and sst_file_date <= '2002-12-03'):
          sst_unpacked_record={'hus_time':ur[0], \
			   'adc':ur[1:7], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
			   'pos_time':ur[7], \
			   'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
			   'pm': [ur[10]/1000.0,ur[11]/1000.0], \
			   'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
			   'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
			   'rec_att':ur[16:22] , \
			   'target':ur[23] % 32, \
			   'mirror_pos':ur[23] /32 , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_date > '1999-05-01' and sst_file_date <= '2002-05-20'):
          sst_unpacked_record={'hus_time':ur[0], \
			   'adcval':ur[1:9], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0] , \
			   'pos_time':ur[9], \
			   'ant_coord':[ur[10]/1000.0,ur[11]/1000.0], \
			   'ant_vel': [ur[12]/1000.0,ur[13]/1000.0], \
			   'ant_coord_err': [ur[14]/1000.0,ur[15]/1000.0], \
			   'scan_off':  [ur[16]/1000.0,ur[17]/1000.0], \
			   'rec_att':ur[18:27] , \
			   'target':ur[28] % 32, \
			   'mirror_pos':ur[28] / 32 , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_type == 'bi'):
          if (sst_file_date > '2002-12-13'):
              sst_unpacked_record={'hus_time':ur[0], \
                           'ant_coord':[ur[1],ur[2]], \
			   'ant_coord_err': [ur[3],ur[4]], \
			   'adc':ur[5:11], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                           'adc_sigma':ur[11:17], \
                           'gps_status': ur[17], \
                           'acq_gain': ur[18] , \
			   'target':ur[19] % 32, \
			   'mirror_pos':ur[19] /32 , \
                           'opmode' : ur[20] , \
                           'adc_offset': ur[21:27] , \
                           'hot_temp': ur[27] , \
                           'amb_temp': ur[28] , \
                           'opt_temp': ur[29] , \
                           'if_board_temp': ur[30] , \
                           'radome_temp': ur[31] , \
                           'humidity': ur[32] , \
                           'temperature': ur[33] , \
                           'opac_210': ur[34] , \
                           'opac_405': ur[35] , \
                           'elevation': ur[36] , \
                           'pressure' : ur[37] , \
                           'burst' : ur[38] , \
                           'errors' : ur[39] , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_date > '2002-11-23' and sst_file_date <= '2002-12-13'):
          sst_unpacked_record={'hus_time':ur[0], \
                           'ant_coord':[ur[1],ur[2]], \
			   'ant_coord_err': [ur[3],ur[4]], \
			   'adc':ur[5:11], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                           'adc_sigma':ur[11:17], \
                           'gps_status': ur[17], \
                           'acq_gain': ur[18] , \
			   'target':ur[19] % 32, \
			   'mirror_pos':ur[19] /32 , \
                           'opmode' : ur[20] , \
                           'adc_offset': ur[21:27] , \
                           'hot_temp': ur[27] , \
                           'amb_temp': ur[28] , \
                           'opt_temp': ur[29] , \
                           'if_board_temp': ur[30] , \
                           'radome_temp': ur[31] , \
                           'humidity': ur[32] , \
                           'temperature': ur[33] , \
                           'opac_210': ur[34] , \
                           'opac_405': ur[35] , \
                           'elevation': ur[36] , \
                           'pressure' : ur[37] , \
                           'burst' : ur[38] , \
                           'errors' : ur[39] , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_date > '2002-09-15' and sst_file_date <= '2002-11-23'):
          sst_unpacked_record={'hus_time':ur[0], \
                           'ant_coord':[ur[1],ur[2]], \
			   'ant_coord_err': [ur[3],ur[4]], \
			   'adc':ur[5:13], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                           'adc_sigma':ur[13:21], \
                           'gps_status': ur[21], \
                           'daq_status': ur[22], \
                           'acq_gain': ur[23] , \
			   'target':ur[24] % 32, \
			   'mirror_pos':ur[24] /32 , \
                           'opmode' : ur[25] , \
                           'adc_attenuators': ur[26:32] , \
                           'adc_offset': ur[32:38] , \
                           'mix_voltage': ur[38:44] , \
                           'mix_current': ur[44:50] , \
                           'hot_temp': ur[50] , \
                           'amb_temp': ur[51] , \
                           'opt_temp': ur[52] , \
                           'if_board_temp': ur[53] , \
                           'radome_temp': ur[54] , \
                           'humidity': ur[55] , \
                           'temperature': ur[56] , \
                           'opac_210': ur[57] , \
                           'opac_405': ur[58] , \
                           'elevation': ur[59] , \
                           'pressure' : ur[60] , \
                           'burst' : ur[61] , \
                           'errors' : ur[62] , \
			   'julday': jd , \
			   'time':time_stamp }  
      elif (sst_file_date <= '2002-09-15'):
          sst_unpacked_record={'hus_time':ur[0], \
                           'ant_coord':[ur[1],ur[2]], \
			   'ant_coord_err': [ur[3],ur[4]], \
			   'adc':ur[5:13], \
			   'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                           'adc_sigma':ur[13:21], \
                           'gps_status': ur[21], \
                           'daq_status': ur[22], \
                           'acq_gain': ur[23] , \
			   'target':ur[24] % 32, \
			   'mirror_pos':ur[24] /32 , \
                           'opmode' : ur[25] , \
                           'adc_attenuators': ur[26:32] , \
                           'adc_offset': ur[32:38] , \
                           'mix_voltage': ur[38:44] , \
                           'mix_current': ur[44:50] , \
                           'hot_temp': ur[50] , \
                           'amb_temp': ur[51] , \
                           'opt_temp': ur[52] , \
                           'if_board_temp': ur[53] , \
                           'radome_temp': ur[54] , \
                           'humidity': ur[55] , \
                           'wind': ur[56] , \
                           'opac_210': ur[57] , \
                           'opac_405': ur[58] , \
                           'elevation': ur[59] , \
                           'seeing' : ur[60] , \
                           'burst' : ur[61] , \
                           'errors' : ur[62] , \
			   'julday': jd , \
			   'time':time_stamp }  

      return sst_unpacked_record
'''
    ########################################################################################################
    #### new
    def __sst_unpack_one_record(self,ur,sst_file_date,sst_file_type):
    
      hours = ur[0] / 36000000L
      minutes = (ur[0] % 36000000L)/600000L
      seconds = ((ur[0] % 36000000L)%600000L)/1.0E+04
      time_stamp=sst_file_date + \
              '  {0:=02d}'.format(hours)+':{0:=02d}'.format(minutes)+':{0:=07.4f}'.format(seconds)  
      jd = self.__sst_julian_date(time_stamp)
      if (sst_file_type == 'rs') or (sst_file_type == 'rf'):
        if (sst_file_date > '2002-12-13'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'adc':ur[1:7], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'pos_time':ur[7], \
                               'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
                               'pm': [ur[10]/1000.0,ur[11]/1000.0], \
                               'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
                               'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
                               'rec_offset':ur[16:22] , \
                               'target':ur[23] % 32, \
                               'mirror_pos':ur[23] /32 , \
                               'opmode':ur[23] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date > '2002-12-03') and (sst_file_date <= '2002-12-13'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'adc':ur[1:7], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'pos_time':ur[7], \
                               'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
                               'pm': [ur[10]/1000.0,ur[11]/1000.0], \
                               'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
                               'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
                               'rec_offset':ur[16:22] , \
                               'target':ur[23] % 32, \
                               'mirror_pos':ur[23] /32 , \
                               'opmode':ur[23] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date > '2002-05-20' and sst_file_date <= '2002-12-03'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'adc':ur[1:7], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'pos_time':ur[7], \
                               'ant_coord':[ur[8]/1000.0,ur[9]/1000.0], \
                               'pm': [ur[10]/1000.0,ur[11]/1000.0], \
                               'ant_coord_err': [ur[12]/1000.0,ur[13]/1000.0], \
                               'scan_off':  [ur[14]/1000.0,ur[15]/1000.0], \
                               'rec_att':ur[16:22] , \
                               'target':ur[23] % 32, \
                               'mirror_pos':ur[23] /32 , \
                               'opmode':ur[23] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date > '1999-05-01' and sst_file_date <= '2002-05-20'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'adc':ur[1:9], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0] , \
                               'pos_time':ur[9], \
                               'ant_coord':[ur[10]/1000.0,ur[11]/1000.0], \
                               'ant_vel': [ur[12]/1000.0,ur[13]/1000.0], \
                               'ant_coord_err': [ur[14]/1000.0,ur[15]/1000.0], \
                               'scan_off':  [ur[16]/1000.0,ur[17]/1000.0], \
                               'rec_att':ur[18:27] , \
                               'target':ur[24] % 32, \
                               'mirror_pos':ur[28] / 32 , \
                               'opmode':ur[25] , \
                               'julday': jd , \
                               'time':time_stamp }  
      elif (sst_file_type == 'bi'):
        if (sst_file_date > '2002-12-13'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'ant_coord':[ur[1],ur[2]], \
                               'ant_coord_err': [ur[3],ur[4]], \
                               'adc':ur[5:11], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'adc_sigma':ur[11:17], \
                               'gps_status': ur[17], \
                               'acq_gain': ur[18] , \
                               'target':ur[19] % 32, \
                               'mirror_pos':ur[19] /32 , \
                               'opmode' : ur[20] , \
                               'adc_offset': ur[21:27] , \
                               'hot_temp': ur[27] , \
                               'amb_temp': ur[28] , \
                               'opt_temp': ur[29] , \
                               'if_board_temp': ur[30] , \
                               'radome_temp': ur[31] , \
                               'humidity': ur[32] , \
                               'temperature': ur[33] , \
                               'opac_210': ur[34] , \
                               'opac_405': ur[35] , \
                               'elevation': ur[36] , \
                               'pressure' : ur[37] , \
                               'burst' : ur[38] , \
                               'errors' : ur[39] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date > '2002-11-23' and sst_file_date <= '2002-12-13'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'ant_coord':[ur[1],ur[2]], \
                               'ant_coord_err': [ur[3],ur[4]], \
                               'adc':ur[5:11], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'adc_sigma':ur[11:17], \
                               'gps_status': ur[17], \
                               'acq_gain': ur[18] , \
                               'target':ur[19] % 32, \
                               'mirror_pos':ur[19] /32 , \
                               'opmode' : ur[20] , \
                               'adc_offset': ur[21:27] , \
                               'hot_temp': ur[27] , \
                               'amb_temp': ur[28] , \
                               'opt_temp': ur[29] , \
                               'if_board_temp': ur[30] , \
                               'radome_temp': ur[31] , \
                               'humidity': ur[32] , \
                               'temperature': ur[33] , \
                               'opac_210': ur[34] , \
                               'opac_405': ur[35] , \
                               'elevation': ur[36] , \
                               'pressure' : ur[37] , \
                               'burst' : ur[38] , \
                               'errors' : ur[39] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date > '2002-09-15' and sst_file_date <= '2002-11-23'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'ant_coord':[ur[1],ur[2]], \
                               'ant_coord_err': [ur[3],ur[4]], \
                               'adc':ur[5:13], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'adc_sigma':ur[13:21], \
                               'gps_status': ur[21], \
                               'daq_status': ur[22], \
                               'acq_gain': ur[23] , \
                               'target':ur[24] % 32, \
                               'mirror_pos':ur[24] /32 , \
                               'opmode' : ur[25] , \
                               'adc_attenuators': ur[26:32] , \
                               'adc_offset': ur[32:38] , \
                               'mix_voltage': ur[38:44] , \
                               'mix_current': ur[44:50] , \
                               'hot_temp': ur[50] , \
                               'amb_temp': ur[51] , \
                               'opt_temp': ur[52] , \
                               'if_board_temp': ur[53] , \
                               'radome_temp': ur[54] , \
                               'humidity': ur[55] , \
                               'temperature': ur[56] , \
                               'opac_210': ur[57] , \
                               'opac_405': ur[58] , \
                               'elevation': ur[59] , \
                               'pressure' : ur[60] , \
                               'burst' : ur[61] , \
                               'errors' : ur[62] , \
                               'julday': jd , \
                               'time':time_stamp }  
        elif (sst_file_date <= '2002-09-15'):
          sst_unpacked_record={'hus_time':ur[0], \
                               'ant_coord':[ur[1],ur[2]], \
                               'ant_coord_err': [ur[3],ur[4]], \
                               'adc':ur[5:13], \
                               'ant_temp':[0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0,0.0E0], \
                               'adc_sigma':ur[13:21], \
                               'gps_status': ur[21], \
                               'daq_status': ur[22], \
                               'acq_gain': ur[23] , \
                               'target':ur[24] % 32, \
                               'mirror_pos':ur[24] /32 , \
                               'opmode' : ur[25] , \
                               'adc_attenuators': ur[26:32] , \
                               'adc_offset': ur[32:38] , \
                               'mix_voltage': ur[38:44] , \
                               'mix_current': ur[44:50] , \
                               'hot_temp': ur[50] , \
                               'amb_temp': ur[51] , \
                               'opt_temp': ur[52] , \
                               'if_board_temp': ur[53] , \
                               'radome_temp': ur[54] , \
                               'humidity': ur[55] , \
                               'wind': ur[56] , \
                               'opac_210': ur[57] , \
                               'opac_405': ur[58] , \
                               'elevation': ur[59] , \
                               'seeing' : ur[60] , \
                               'burst' : ur[61] , \
                               'errors' : ur[62] , \
                               'julday': jd , \
                               'time':time_stamp }  
    
      return sst_unpacked_record
    ########################################################################################################
    def  __sst_files(self,isotime1,isotime2,sst_file_type,sst_path):
        t1=self.__sst_base_name(isotime1)
        t2=self.__sst_base_name(isotime2)
        if (t1[0] != t2[0]): return []
        
        h1 = t1[1] / 36000000L
        m1 = (t1[1] % 36000000L)/600000L

        h2 = t2[1] / 36000000L
        m2 = (t2[1] % 36000000L)/600000L

        if (sst_file_type.lower() == 'rs'):
            hours = range(h1,h2+1) 
            sst_file_names = []
            for i in hours : sst_file_names.append(sst_path+'/rs'+t1[0]+'.'+'{0:=02d}'.format(i)+'00')
        elif (sst_file_type.lower() == 'bi'):
            sst_file_names = [sst_path+'/bi'+t1[0]]
        else:
            sst_file_names = []

        return sst_file_names


    ########################################################################################################
    def  __sst_read_data(self,sst_file_names,t1,t2,sst_file_type):  
      sst_data =[]
      for fname in sst_file_names :
        if os.path.exists(fname) :
          # LINUX fd     = os.open(fname,os.O_RDONLY)
         fd = os.open(fname,os.O_BINARY)
         fmt    = self.__sst_define_fmt(sst_file_type,t1[2])
    
         if ( len(fmt) < 1 ) : return
    
         nrec   = os.fstat(fd).st_size / struct.calcsize(fmt)
         for irec in range(nrec) :
            ur = self.__sst_read_one_record(fd,fmt)
            if (ur[0] >= t1[1] and ur[0] <= t2[1]):
              sst_record = self.__sst_unpack_one_record(ur,t1[2],sst_file_type)
              sst_data.append(sst_record)
        else:
          print 'File '+fname+'  not found'
    
      return sst_data



    #######################################################################################  
    def sst_read(self,time1,time2,sst_file_type,sst_path) :
        '''
        ########################################################################################
        #sst_read
        #
        # Aim: read SST data
        #
        # Input: time1, time2 : are strings with a time in ISO format indicating start and end
        #                       of data to be read. ISO time format = YYYY-MM-DD hh:mm:ss
        #                       If days are not the same, the program returns an empty list.
        #        sst_file_type : 'bi' | 'rs' | 'rf' for instrumental, raw slow or raw fast data
        #        sst_path :     string with the directory where to find sst data files 
        # 
        # Output: a list of dictionaries. The structure depends on the data type and epoch
        #         (SST data changed over time....)
        #
        # Examples:
        # >>> import sst_methods as sst
        # >>> data = sst.sst_read('2003-12-15 13:15','2003-12-15 15:17:20','rf','/home/guigue/solar/sst')
        #
        # Change record:
        #     First written by Guigue on 19 February 2015, in Sao Paulo
        #
        ########################################################################################
        '''
        lista = self.__sst_files(time1,time2,sst_file_type,sst_path)
        t1   = self.__sst_base_name(time1)
        t2   = self.__sst_base_name(time2)
        return self.__sst_read_data(lista,t1,t2,sst_file_type)

