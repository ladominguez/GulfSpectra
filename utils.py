import glob
import os
from obspy.core.utcdatetime import UTCDateTime
import numpy as np
import json

def residuals(d_obs, d_model):
	return np.mean(np.power(d_obs-d_model,2))

def variance_reduction(d_obs, d_model):
	#d_avg = np.mean(d_obs)
	#d_obs = d_obs - d_avg
	#d_model = d_model - d_avg
	return (1.-np.sum(np.power(d_obs - d_model,2))/np.sum(np.power(d_obs,2)))*100.

def coeff_r2(d_obs, d_model):
	d_avg   = np.mean(d_obs)
	tot_var = np.sum(np.power(d_obs - d_avg,2))
	res     = np.sum(np.power(d_obs - d_model,2))
	return (1.-res/tot_var)*100


def clean_directory(dir,type_resp):
    #previous = glob.glob(os.path.join(dir, "*" + type_resp  + "*.png"))
    previous = glob.glob(os.path.join(dir, "*.png")) # Clean all
    for png_file in previous:
        os.remove(png_file)


def G(r, azimuth):
    # See Garcia et al. 2009
    R0 = 1
    return R0/r
    # Costal


#    if ((azimuth >= 260) and (azimuth <= 315)) or ((azimuth >= 100) and (azimuth <= 150)):
#        if r <= R0:
#            return 1./r
#        else:
#            return 1.0/(np.sqrt(R0*r))
	
	# Towards the continent
#    else:
#        if r <= R0:
#            return 1./r
#        elif (r > R0) and (r <= 3.0*R0):  # 150km 
#            return 1.0/R0
#        else:
#            return np.sqrt(3.0)/np.sqrt(R0*r)





def Q(f, azimuth):
    #return 39*np.power(f,0.64)
    #return 380*np.power(f,0.1)  # Ortega 2007
#    return 223*(9/4.0)*np.power(f,1.2)  #Castro et al 2019
	# See Garcia et al. 2009
    # Costal
    if ((azimuth >= 260) and (azimuth <= 315)) or ((azimuth >= 100) and (azimuth <= 150)):
        return (175.0*9/4.0)*np.power(f, 0.52)

	# Towards the continent
    else:
        return (211.0*9/4.0)*np.power(f, 0.46)


def M0_func(Mw):
    return np.power(10, Mw*1.5+9.1)

def Mw_log(M0_log):
    return (2./3.)*(M0_log - 9.1)

def stress_drop(freq_cut, kappa, vel_wave, Moment):
    #print('kappa: ', kappa)
    #print('beta', vel_wave)
    return (7./16)*Moment*(freq_cut/(kappa*vel_wave))**3


def rms(data):
    return np.sqrt(np.mean(np.power(data, 2)))

def brune_spectrum(f,M0,fc, resp_type):
    if resp_type == "DISP":
        Sb = M0/(1+(f/fc)**2)
    elif resp_type == "VEL":
        Sb = M0*(2*np.pi*f)/(1+(f/fc)**2)
    elif resp_type == "ACC":
        Sb = M0*(2*np.pi*f)**2/(1+(f/fc)**2)
    else:
        None
    return Sb

def fit_curve(fdata, Bdata, resp_type):
    B0 = np.round(np.log10(np.mean(Bdata)))
    Bt = np.linspace(np.round(np.log10(np.mean(Bd)))-1, np.round(np.log10(np.mean(Bd)))+1, 21)
    ft = np.linspace(0.5,14,15)
    return None

#def brune_log(f, log_M0, fc):
#    if resp_type == "DISP":
#        Sb_log = log_M0-np.log10((1+(f/fc)**2))
#    elif resp_type == "VEL":
#        Sb_log = log_M0+np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
#    elif resp_type == "ACC":
#        Sb_log = log_M0+2*np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
#    else:
#        None
#    return Sb_log

# def brune_1p(f, fc):
#    if resp_type == "DISP":
#        Sb_log = -np.log10((1+(f/fc)**2))
#    elif resp_type == "VEL":
#        Sb_log = np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
#    elif resp_type == "ACC":
#        Sb_log = 2*np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
#    else:
#        None
#    return Sb_log
