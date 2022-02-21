import obspy as ob
from obspy.signal.cross_correlation import xcorr_pick_correction
from obspy.core.utcdatetime import UTCDateTime
from ssn import get_response_files
import numpy as np
import json
import glob
import os
from matplotlib import pyplot as plt
from scipy.signal import tukey
from ssn import get_response_files
from mtspec import mtspec
from scipy.optimize import curve_fit
from utils import *
plt.rcParams.update({'font.size': 16})


fparam  = open('params.json')
fstress = open('stress.json')
stress  = json.load(fstress)
params  = json.load(fparam)
path    = os.path.join(params['root'] )

resp_type = stress["resp_type"]
type_wave = stress["type_wave"]
pre_filt  = stress["pre_filt"]
tbef      = stress["tbef"]
Nfft      = stress["Nfft"]
fmin      = stress["fmin"]
#fmax      = stress["fmax"]
plotting  = True #stress["plotting"]

directories = glob.glob(path)
directories.sort()

dict_ylabel = {"DISP": f"$m$", "VEL": f"$m/s$", "ACC": f"$m/s^2$"}
dict_title  = {"DISP": "Displacement", "VEL": "Velocity", "ACC": "Acceleration"}
vel         = {"P": 6230, "S": 3900}

print("0. stress: ", stress)


#def brune_spectrum(f, fc, stress):
#	print('M0: ', M0)
#	if stress["resp_type"] == "DISP":
#		Sb = M0*(2*np.pi*f)/(1+(f/fc)**2)
#	elif stress["resp_type"] == "ACC":
#		Sb = M0*(2*np.pi*f)**2/(1+(f/fc)**2)
#	else:
#		None
#	return Sb


def brune_log(f, fc, log_M0 ):
	if resp_type == "DISP":
		Sb_log = log_M0-np.log10((1+(f/fc)**2))
	elif resp_type == "VEL":
   		Sb_log = log_M0+np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
	elif resp_type == "ACC":
		Sb_log = log_M0+2*np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
	else:
 		None

	return Sb_log

def brune_1p(f, fc):
    if resp_type == "DISP":
        Sb_log = -np.log10((1+(f/fc)**2))
    elif resp_type == "VEL":
        Sb_log = np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
    elif resp_type == "ACC":
        Sb_log = 2*np.log10(2*np.pi*f)-np.log10(1+(f/fc)**2)
    else:
        None
    return Sb_log

for dir in directories:
	print(dir)
	sac = ob.read(os.path.join(dir, "*sac"))
	sac.detrend('linear')
	sta = set([tr.stats.sac.kstnm     for tr in sac])
	sta = sorted(sta)
	clean_directory(dir, resp_type)
	sequence_id = dir.split('/')[-2]
	Data_out    = os.path.join(dir, sequence_id + '.stress_drop.' + resp_type + '.test')
	fout        = open(Data_out, 'w')

	fout.write('Station  Wave    Type      date_time         distance     Md    Mw     fcut   std_fcut    Mcorr    std_Mcorr   Stress    SNR     VarRed      R2    ID \n')
	for count, station in enumerate(sta):
		print(count + 1, " - ", station)
		sel = sac.select(station=station)
		#if True: #os.path.exists(RESP_FILE):
		#sel.detrend()
		sel.taper(max_percentage=0.05)

		tp_wave = np.zeros((len(sel),1))
		Invalid = False
		#for k in range(len(sel)):
		for k,tr in enumerate(sel):
			RESP_FILE, fmax = get_response_files(params['iresp'], station, tr.stats.starttime)
			#print('fmax: ', fmax)
			#print('RESP: ', RESP_FILE)
			if RESP_FILE is None:
				Invalid = True
				continue
			inv = ob.read_inventory(RESP_FILE)
			tr.remove_response(inventory=inv, output=resp_type, zero_mean=True, pre_filt=pre_filt, taper=True)
			tp_wave[k] = tr.stats.sac.t2

		if Invalid:
			continue

		date  = {}
		Rij   = {}
		az    = {}
		dt    = {}
		mag   = {}


		# Plot waveforms
		waveform_out = os.path.join(dir, station + '.waveform.128s.'+ resp_type + '.png')
		PS_out       = os.path.join(dir, station + '.128s.' + type_wave + '.' + resp_type + '.png')
		FFT_out      = os.path.join(dir, station + '.FFT.128s.' + resp_type + '.png')
		SPEC_out     = os.path.join(dir, station + '.SPE.128s.' + resp_type + '.png')
		Brune_out    = os.path.join(dir, station + '.BRUNE.128s.' + resp_type + '.png')
		if plotting:
			fig, ax = plt.subplots(len(sel) + 1, 1, figsize=(12, 6), sharex=False , squeeze=False)
			ax = ax.flatten()
		for k, tr in enumerate(sel):
			date[k] = tr.stats.starttime.strftime("%Y/%m/%d,%H:%M:%S")
			Rij[k]  = np.sqrt(tr.stats.sac.dist**2+tr.stats.sac.evdp**2)*1e3
			dt[k]   = tr.stats.delta
			mag[k]  = tr.stats.sac.mag
			az[k]   = tr.stats.sac.az

			aux     = tr.copy()
			aux.detrend('linear')
			#aux.filter("bandpass", freqmin = 1.0, freqmax = 10., zerophase=True)
			if plotting:
				ax[k].plot(aux.times(), aux.data, 'k', linewidth=0.25, label=date[k])
				ax[k].plot(aux.stats.sac.t2, 0, 'r*', markersize=15)
				# ax[k].plot(tr.stats.sac.t1,0,'b*',markersize=15)
				ax[k].grid()
				ax[k].legend(fontsize=14)

				ax[k].set_ylabel(dict_ylabel[resp_type], fontsize=14)
				ax[k].set_xlim([0,np.ceil(tp_wave.max()*3/5)*5])
			
				x_lims_wave = ax[k].get_xlim()
				y_data_plot = np.where( (aux.times() > x_lims_wave[0]) &  (aux.times() < x_lims_wave[1]) )[0]
				ax[k].set_ylim( aux.data[y_data_plot].min(), aux.data[y_data_plot].max() )

			index_t5   = np.where(np.logical_and(tr.times() >= t5_mas -1,  aux.times() <= t5_mas + 5 ))
			max_val    = np.amax(np.abs(aux.data[index_t5]))

			roll_aux = 	np.roll(aux.data, nsamples)/max_val
			if plotting:
				ax[len(sel)].plot(aux.times(), roll_aux)
				ax[len(sel)].grid(b=True)
				ax[len(sel)].set_xlim([t5_mas -0.5, t5_mas + 1.0])

				x_lims_wave = ax[len(sel)].get_xlim()
				y_data_plot = np.where( (aux.times() > x_lims_wave[0]) &  (aux.times() < x_lims_wave[1]) )[0]	
				ax[len(sel)].set_ylim( roll_aux[y_data_plot].min(), roll_aux[y_data_plot].max() )


		#plt.subplots_adjust(hspace=0, wspace=0)
		if plotting:
			plt.suptitle(station + ' - ' + resp_type + ' - ' + type_wave + ' wave')
			plt.savefig(waveform_out)
			plt.close()

		# Trim to p-wave
		d       = {}
		noise   = {}
		snr     = {}
		if plotting:
			fig, ax = plt.subplots(len(sel), 1, figsize=(24, 8), sharex=True, squeeze=False )
			ax      = ax.flatten()
		for k, tr in enumerate(sel):
			t = tr.times() + tr.stats.sac.b
			dt[k] = tr.stats.delta
			if type_wave == 'P':
				twave = tr.stats.sac.a
				k_sd = 0.32   # Madariaga 1976 - See Shearer page 270
			else:
				twave = tr.stats.sac.t0  # ERROR CORREGIR
				k_sd = 0.21   # Madariaga 1976 - See Shearer page 270

			tr.data = tr.data  # WARNING *1e-9
			tpn   = np.argmax(t >= twave)
			tnbef = int(np.floor(tbef/dt[k]))
			start_noise = tpn - tnbef - Nfft
			end_noise   = tpn - tnbef
			d[k]  = tr.data[tpn - tnbef:tpn - tnbef + Nfft] - \
			        np.mean(tr.data[tpn - tnbef:tpn - tnbef + Nfft])
			if start_noise < 0:  # This condition avoid negative values of the index when the record is too short for
			                     #the noise
				start_noise = 0

			noise[k] = tr.data[start_noise :end_noise ] - \
			        np.mean(tr.data[start_noise :end_noise ])
			taper  = tukey(Nfft, alpha=0.1)
			d[k]   = np.multiply(d[k], taper)
			snr[k] = rms(d[k])/rms(noise[k])
			if plotting:
				ax[k].plot(np.linspace(-0.5, (Nfft-1)*dt[k]-0.5, Nfft),
			           d[k], 'k', linewidth=1, label=date[k])
				ax[k].legend(fontsize=14)
				ax[k].set_ylabel(dict_ylabel[resp_type], fontsize=14)
				ax[k].plot(np.linspace(-0.5, (Nfft-1)*dt[k]-0.5, Nfft), taper*np.max(d[k]))
				ax[k].grid()

		if plotting:
			plt.suptitle(station + ' - ' + resp_type + ' - ' + type_wave + ' wave')
			plt.subplots_adjust(hspace=0, wspace=0)
			plt.savefig(PS_out)
			plt.close()

		# Estimate the spectrum
		Aspec = {}
		fspec = {}
		Nspec = {}
		if plotting:
			fig, ax = plt.subplots(1, 1, figsize=(12, 6))
		for key, tr in d.items():
			spec, freq, jackknife, _, _   = mtspec(data=tr, delta=dt[key], time_bandwidth=3, nfft=len(tr), statistics=True)
			spec_noise, freq_noise, jackknife_noise, _, _   =  \
			                              mtspec(data=noise[key], delta=dt[key], time_bandwidth=3, nfft=len(noise[key]), statistics=True)
			spec       = np.sqrt(spec/2)
			spec_noise = np.sqrt(spec_noise/2) 
			index = np.where(np.logical_and(freq >= fmin, freq <= fmax))
			error_up   =  np.sqrt(jackknife[index[0], 0]/2)
			error_down =  np.sqrt(jackknife[index[0], 1]/2) 
			std_spec   =  (error_up - error_down)/2

			Aspec[key] = spec[index]
			fspec[key] = freq[index]
			Nspec[key] = spec_noise[index]
			if plotting:
				ax.fill_between(freq[index], error_up, error_down, alpha=0.5)
				ax.loglog(fspec[key], Aspec[key],
			            label=date[key] + ' Mw=' + str(mag[key]))
				ax.loglog(fspec[key], Nspec[key],'k')

		if plotting:
			ax.legend(fontsize=14)
			ax.grid(b=True, which='major', color='k', linestyle='--', linewidth=0.25)
			ax.grid(b=True, which='minor', color='k', linestyle='--', linewidth=0.25)
			plt.xlabel('Frequency [Hz]', fontsize=14)
			plt.title('Original spectrum - ' + station + ' - ' + dict_title[resp_type], fontsize=14)
			plt.savefig(FFT_out)
			plt.close()

		# Geometrical spreading
		Rad = 0.55         # Radiation pattern Boore and Boatwrigth
		F   = 2.0          # Free surface
		P   = 1.0          # Energy partioning
		rho = 2700.0
		C   = Rad*F*P/(4*np.pi*rho*vel[type_wave]**3)


		Slog = {}
		if plotting:
			fig, ax = plt.subplots(1, 1, figsize=(12, 6))
		S = {}
		N = {}

		for key, An in Aspec.items():
			S[key] = (        An*np.exp(np.pi*fspec[key]*Rij[key]/(vel[type_wave]*Q(fspec[key], az[key])))/(C*G(Rij[key],az[key])))
			N[key] = (Nspec[key]*np.exp(np.pi*fspec[key]*Rij[key]/(vel[type_wave]*Q(fspec[key], az[key])))/(C*G(Rij[key],az[key])))
			if plotting:
				ax.loglog(fspec[key], S[key], label=date[key])
				ax.loglog(fspec[key], N[key], color='k', linestyle='--')

		if plotting:
			ax.legend(fontsize=14)
			ax.grid(b=True, which='major', color='k', linestyle='--', linewidth=0.25)
			ax.grid(b=True, which='minor', color='k', linestyle='--', linewidth=0.25)
			plt.xlabel('Frequency [Hz]', fontsize=14)
			plt.title('Spectrum - ' + station + ' - ' +
		          dict_title[resp_type], fontsize=14)
			plt.savefig(SPEC_out)
			plt.close()

		fcut   = {}
		fcuts  = {}
		Mcorr  = {}
		Mcorrs = {}
		stress = {}
		Mw     = {}
		var    = {}
		r2     = {}
		if plotting:
			fig, ax = plt.subplots(1,1, figsize = (8,10))
		for key, fb in fspec.items():
		    M0 = M0_func(mag[key])
		    if plotting:
#		    	ax[0].loglog(fspec[key],S[key], label=date[key] )
#		    	ax[0].loglog(fspec[key],N[key], color='k', linestyle='--')
		    	ax.semilogx(fspec[key],np.log10(S[key]), label=date[key] )
		    	ax.semilogx(fspec[key],np.log10(N[key]), color='k', linestyle='--')
		    popt, pcov  = curve_fit(brune_log, fspec[key],np.log10(S[key]), bounds=([0, 10],[fmax, 20]), maxfev=1000)
		    #popt, pcov  = curve_fit(brune_1p, fspec[key],np.log10(S[key]/M0), bounds=(0.25,[fmax]), maxfev=1000)
		    errors      = np.sqrt(np.diag((pcov)))
		    fcut[key]   = popt[0]
		    fcuts[key]  = errors[0]
		    if resp_type == 'DISP':
		        Mcorr[key]  = np.max(np.log10(S[key]))
		        Mcorrs[key] = 0.0
			    #Mcorr[key]  = np.log10(M0)
			    #Mcorrs[key] = 0.0 
		    else:
		        Mcorr[key]  = popt[1]
		        Mcorrs[key] = errors[1] 
			    #Mcorr[key]  = np.log10(M0)
			    #Mcorrs[key] = 0.0 

		    stress[key] = stress_drop(fcut[key], k_sd, vel['S'], np.power(10,Mcorr[key]))/1e6
		    #stress[key] = stress_drop(fcut[key], k_sd, vel['S'], M0 )/1e6
		if plotting:
			plt.gca().set_prop_cycle(None)
		for key, fb in fspec.items():
		    #M0 = M0_func(mag[key])
		    Mw[key] = Mw_log(Mcorr[key])
		    if plotting:
		    	ax.semilogx(fb, brune_log(fb, fcut[key], Mcorr[key]),'o-')

		    var[key] = variance_reduction(np.log10(S[key]),brune_log(fb, fcut[key], Mcorr[key] ))
		    r2[key]  = coeff_r2(          np.log10(S[key]),brune_log(fb, fcut[key], Mcorr[key] ))
		    print('fcut[', key,']: ', '%5.2f'%fcut[key], ' Mcorr[', key, ']: ', '%5.2f'%Mcorr[key], 
			' Stress drop[', key, ']: ', '%6.3f'%stress[key], 'MPa   SNR: ' + '%5.1f'%snr[key],
			' Mw[', key, ']: ', '%3.1f'%Mw[key], ' Md[', key, ']: ', '%3.1f'%mag[key], ' Res[', key, ']: ',
			'%5.3f'%var[key])
		    fout.write(station + '       '
			    + type_wave + '     ' 
				+ resp_type + '    ' 
				+ date[key] + '    ' 
				+ '%6.1f'%(Rij[key]/1e3) + '    ' 
				+ '%3.1f'%mag[key]  + '    ' 
				+ '%3.1f'%Mw[key]    + '    '   
			    + '%5.2f'%fcut[key]  + '    ' + '%6.3f'%fcuts[key]   + '    '
				+ '%5.2f'%Mcorr[key] + '    ' + '%6.3f'%Mcorrs[key]  + '    '
				+ '%6.3f'%stress[key]  + '    ' 
				+ '%5.1f'%snr[key]     + '    ' 
				+ '%5.3f'%var[key]     + '    '
				+ '%5.1f'%r2[key]      + '    ' 
			 + '\n')

		if plotting:
#			ax[0].grid(b=True, which='major', color='k', linestyle='--',linewidth=0.25)
#			ax[0].grid(b=True, which='minor', color='k', linestyle='--',linewidth=0.25)  
			ax.grid(b=True, which='major', color='k', linestyle='--',linewidth=0.25)
			ax.grid(b=True, which='minor', color='k', linestyle='--',linewidth=0.25)  
			plt.suptitle('Brune Spectrum ' + dict_title[resp_type] + ' - ' + station 
				+ '\nfc = ' + '%5.2f'%fcut[key] + 'Hz ' + ' Stress Drop = ' + '%5.2f'%stress[key] + 'MPa', fontsize=17)
			plt.ylabel(r'$log_{10}($'+ dict_title[resp_type] + ' Spectrum)')				
			plt.xlabel('Frequency [Hz]',fontsize=14)
			plt.savefig(Brune_out)
			plt.close()
	fout.close()
	
