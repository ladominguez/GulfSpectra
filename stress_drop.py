#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from socket import AF_X25
import obspy as ob
from obspy.signal.cross_correlation import xcorr_pick_correction
from obspy.core.utcdatetime import UTCDateTime
from scipy.interpolate import interp1d
from ssn import get_response_files
import numpy as np
import json
import glob
import os, sys
from matplotlib import pyplot as plt
from scipy.signal import tukey
from ssn import get_response_files
from mtspec import mtspec
from scipy.optimize import curve_fit
from utils import *
plt.rcParams.update({'font.size': 16})


fparam = open('params.json')
fstress = open('stress.json')
stress = json.load(fstress)
params = json.load(fparam)
path = os.path.join(params['root'])

resp_type = stress["resp_type"]
type_wave = stress["type_wave"]
pre_filt = stress["pre_filt"]
tbef = stress["tbef"]
Nfft = stress["Nfft"]
fmin = stress["fmin"]
fmax = stress["fmax"]
Nint = stress["Nint"]
plotting = True  # stress["plotting"]

directories = glob.glob(path)
directories.sort()

dict_ylabel = {"DISP": f"$m$", "VEL": f"$m/s$", "ACC": f"$m/s^2$"}
dict_title = {"DISP": "Displacement", "VEL": "Velocity", "ACC": "Acceleration"}
vel = {"P": 6230, "S": 3900}

print("0. stress: ", stress)


# def brune_spectrum(f, fc, stress):
#	print('M0: ', M0)
#	if stress["resp_type"] == "DISP":
#		Sb = M0*(2*np.pi*f)/(1+(f/fc)**2)
#	elif stress["resp_type"] == "ACC":
#		Sb = M0*(2*np.pi*f)**2/(1+(f/fc)**2)
#	else:
#		None
#	return Sb


def brune_log(f, fc, log_M0):
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

if __name__ == '__main__':
    if len(sys.argv) == 2:
        path=os.path.join(os.getcwd(),sys.argv[1])	  
    print('path: ', path)
    earthquake = path.split('/')[-1]
    print('eq: ', earthquake)
    Data_out = os.path.join(
        path, earthquake + '.stress_drop.' + resp_type + '.dat')
    fout = open(Data_out, 'w')
    fout.write('Station  Wave    Type      date_time         distance     Mcat  Mw     fcut   std_fcut    Mcorr    std_Mcorr   Stress    SNR     VarRed      R2    ID \n')
    # for dir in directories:
    sac = ob.read(os.path.join(path, "waveforms/*HZ*.sac"))
    sac.detrend('linear')
    sta = set([tr.stats.sac.kstnm for tr in sac])
    sta = sorted(sta)
    clean_directory(path, resp_type)
    # Plot waveforms
    waveform_out = os.path.join(path, 'WAVEFORM.' + resp_type + '.png')
    PS_out    = os.path.join(path, type_wave + '.' + resp_type + '.png')
    FFT_out   = os.path.join(path, 'FFT.' + resp_type + '.png')
    SPEC_out  = os.path.join(path, 'SPE.' + resp_type + '.png')
    Brune_out = os.path.join(path, 'BRUNE.' + resp_type + '.png')

    # Plot waveforms
    if plotting:
        fig1, ax1 = plt.subplots(len(sta), 1, figsize=(12, 6), sharex=False, squeeze=False)
        ax1 = ax1.flatten()
        fig2, ax2 = plt.subplots(len(sta), 1, figsize=(24, 8), sharex=True, squeeze=False)
        ax2 = ax2.flatten()
        fig3, ax3 = plt.subplots(1, 1, figsize=(12, 6))
        fig4, ax4 = plt.subplots(1, 1, figsize=(12, 6))
        fig5, ax5 = plt.subplots(1, 1, figsize=(8, 10))

    Rij    = {}
    fcut   = {}
    fcuts  = {}
    Mcorr  = {}
    Mcorrs = {}
    stress = {}
    Mw     = {}
    var    = {}
    r2     = {}
    snr = {}

    for count, station in enumerate(sta):
        print(count + 1, " - ", station)
        sel = sac.select(station=station)
        # if True: #os.path.exists(RESP_FILE):
        # sel.detrend()
        sel.taper(max_percentage=0.05)

        tp_wave = np.zeros((len(sel), 1))
        Invalid = False
        # for k in range(len(sel)):
        for k, tr in enumerate(sel):
            RESP_FILE, fmax_inst = get_response_files(
                params['iresp'], station, tr.stats.starttime)
            #print('RESP: ', RESP_FILE)
            if RESP_FILE is None:
                Invalid = True
                continue
            print('RESP: ', RESP_FILE)
            inv = ob.read_inventory(RESP_FILE, format='RESP')
            tr.remove_response(inventory=inv, output=resp_type,
                               zero_mean=True, pre_filt=pre_filt, taper=True)
            tp_wave[k] = tr.stats.sac.a

        if Invalid:
            continue

        date = {}
        az = {}
        dt = {}
        mag = {}

        # Trim to p-wave
        d = {}
        noise = {}
        t_data = {}
        t_noise = {}

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
            tpn = np.argmax(t >= twave)
            tnbef = int(np.floor(tbef/dt[k]))
            start_noise = tpn - tnbef - Nfft
            end_noise = tpn - tnbef
            d[k] = tr.data[tpn - tnbef:tpn - tnbef + Nfft]  # - \
            # np.mean(tr.data[tpn - tnbef:tpn - tnbef + Nfft])
            t_data[k] = t[tpn - tnbef:tpn - tnbef + Nfft]

            if start_noise < 0:  # This condition avoid negative values of the index when the record is too short for
                # the noise
                start_noise = 0

            t_noise[k] = t[start_noise:end_noise]
            noise[k] = tr.data[start_noise:end_noise]  # - \
            # np.mean(tr.data[start_noise :end_noise ])
            taper = tukey(Nfft, alpha=0.1)
            d[k] = np.multiply(d[k], taper)
            snr[count] = rms(d[k])/rms(noise[k])

        for k, tr in enumerate(sel):
            date[k] = tr.stats.starttime.strftime("%Y/%m/%d,%H:%M:%S")
            Rij[count] = np.sqrt(tr.stats.sac.dist**2+tr.stats.sac.evdp**2)*1e3
            dt[k] = tr.stats.delta
            mag[k] = tr.stats.sac.mag
            az[k] = tr.stats.sac.az

            print("Rij: ", Rij[k]/1e3, " km.")

            aux = tr.copy()
            # aux.detrend('linear')
            #aux.filter("bandpass", freqmin = 1.0, freqmax = 10., zerophase=True)
            if plotting:
                ax1[count].plot(aux.times(), aux.data, 'k', linewidth=0.25,
                                label=station + ' R=' + '%5.1f' % (Rij[count]/1e3) + " km.")
                ax1[count].plot(t_data[k], d[k], 'r')
                ax1[count].plot(aux.stats.sac.a, 0, 'r*', markersize=15)
                ax1[count].plot(t_noise[k], noise[k], 'b')
                # ax[k].plot(tr.stats.sac.t1,0,'b*',markersize=15)
                ax1[count].grid()
                ax1[count].legend(fontsize=14)
                ax1[count].tick_params(axis='x', labelsize=8)
                ax1[count].tick_params(axis='y', labelsize=8)

                ax1[count].set_ylabel(dict_ylabel[resp_type], fontsize=14)
                ax1[count].set_xlim([0, np.ceil(tp_wave.max()*3/5)*5])

                x_lims_wave = ax1[count].get_xlim()
                y_data_plot = np.where((aux.times() > x_lims_wave[0]) & (
                    aux.times() < x_lims_wave[1]))[0]
                ax1[count].set_ylim(aux.data[y_data_plot].min(),
                                    aux.data[y_data_plot].max())

            index_t5 = np.where(np.logical_and(
                tr.times() >= tr.stats.sac.a - 1,  aux.times() <= tr.stats.sac.a + 5))
            max_val = np.amax(np.abs(aux.data[index_t5]))

            nsamples = 0  # No shifting, only needed when analyzing RE
            roll_aux = np.roll(aux.data, nsamples)  # /max_val

            # if plotting:
            #	ax[len(sel)].plot(aux.times(), roll_aux, 'r', linewidth=1)
            #
            #	ax[len(sel)].plot(aux.stats.sac.a, 0, markersize=15)
            #	ax[len(sel)].grid(b=True)
            #	ax[len(sel)].set_xlim([tr.stats.sac.a - tbef, tr.stats.sac.a -tbef + (Nfft-1)*dt[k] ])
            #
            #	x_lims_wave = ax[len(sel)].get_xlim()
            #	y_data_plot = np.where( (aux.times() > x_lims_wave[0]) &  (aux.times() < x_lims_wave[1]) )[0]
            #	ax[len(sel)].set_ylim( roll_aux[y_data_plot].min(), roll_aux[y_data_plot].max() )

        #fig1.subplots_adjust(hspace=0, wspace=0)

        if plotting:
            for k, tr in enumerate(sel):
                if plotting:
                    ax2[count].plot(np.linspace(-0.0, (Nfft-1)*dt[k]-0.0, Nfft),
                                    d[k], 'k', linewidth=2, label=station)
                    ax2[count].legend(fontsize=14)
                    ax2[count].set_ylabel(dict_ylabel[resp_type], fontsize=14)
                    ax2[count].plot(
                        np.linspace(-0.0, (Nfft-1)*dt[k]-0.0, Nfft), taper*np.max(d[k]))
                    ax2[count].grid()

        # Estimate the spectrum
        Aspec = {}
        fspec = {}
        Nspec = {}
        Aintp = {}   # Interpolated variables
        fintp = {}
        for key, tr in d.items():
            spec, freq, jackknife, _, _ = mtspec(data=tr, delta=dt[key], time_bandwidth=3, nfft=len(tr), statistics=True)
            spec_noise, freq_noise, jackknife_noise, _, _ =  \
                mtspec(data=noise[key], delta=dt[key], time_bandwidth=3, nfft=len(
                    noise[key]), statistics=True)
            spec = np.sqrt(spec/2)
            spec_noise = np.sqrt(spec_noise/2)
            index = np.where(np.logical_and(freq >= fmin, freq <= fmax))
            #print("fmax: ", fmax)
            error_up = np.sqrt(jackknife[index[0], 0]/2)
            error_down = np.sqrt(jackknife[index[0], 1]/2)
            std_spec = (error_up - error_down)/2

            Aspec[key] = spec[index]
            fspec[key] = freq[index]
            Nspec[key] = spec_noise[index]

            # Interpolation
            fintp[key] = np.logspace(np.log10(fmin), np.log10(fmax), Nint)

            if plotting:
                ax3.fill_between(freq[index], error_up, error_down, alpha=0.5)
                ax3.loglog(fspec[key], Aspec[key], label=station + ' (' + '%5.1f'%(Rij[count]/1e3)  + ' km)')
                ax3.loglog(fspec[key], Nspec[key], 'k')

        # Geometrical spreading
        Rad = 0.55         # Radiation pattern Boore and Boatwrigth
        F = 2.0          # Free surface
        P = 1.0          # Energy partioning
        rho = 2700.0
        C = Rad*F*P/(4*np.pi*rho*vel[type_wave]**3)

        Slog = {}
        S = {}
        N = {}

        for key, An in Aspec.items():
            S[key] = (An*np.exp(np.pi*fspec[key]*Rij[key]/(vel[type_wave]
                                                           * Q(fspec[key], az[key])))/(C*G(Rij[key], az[key])))
            N[key] = (Nspec[key]*np.exp(np.pi*fspec[key]*Rij[key] /
                                        (vel[type_wave]*Q(fspec[key], az[key])))/(C*G(Rij[key], az[key])))

            if plotting:
                ax4.loglog(fspec[key], S[key], label=station + ' (' + '%5.1f'%(Rij[count]/1e3)  + ' km)')
                ax4.loglog(fspec[key], N[key], color='k', linestyle='--')

        for key, fb in fspec.items():
            M0 = M0_func(mag[key])

            # Interpolation
            func_intp = interp1d(fspec[key], np.log10(
                S[key]), fill_value='extrapolate')
            Aintp[key] = func_intp(fintp[key])

            if plotting:
                line, = ax5.semilogx(fspec[key], np.log10(S[key]), label=station)
                ax5.semilogx(fspec[key], np.log10(N[key]),
                             color='k', linestyle='--')
                #ax5.semilogx(fintp[key], Aintp[key],color='r',marker='o')

            popt, pcov = curve_fit(brune_log, fintp[key], Aintp[key], bounds=(
                [0.01, 14], [3.0, 22]), maxfev=1000)  # Interpolation
            # popt, pcov  = curve_fit(brune_log, fspec[key],np.log10(S[key]), bounds=([0.01, 16],[1.0, 18]), maxfev=1000) # No interpolation
            #popt, pcov  = curve_fit(brune_1p, fspec[key],np.log10(S[key]/M0), bounds=(0.25,[fmax]), maxfev=1000)
            errors = np.sqrt(np.diag((pcov)))
            fcut[count] = popt[0]
            fcuts[count] = errors[0]
            if resp_type == 'DISP':
                #Mcorr[key]  = np.max(np.log10(S[key]))
                Mcorr[count] = popt[1]
                Mcorrs[count] = 0.0
                #Mcorr[key]  = np.log10(M0)
                #Mcorrs[key] = 0.0
            else:
                Mcorr[count] = popt[1]
                Mcorrs[count] = errors[1]
                #Mcorr[key]  = np.log10(M0)
                #Mcorrs[key] = 0.0

            stress[count] = stress_drop(
                fcut[count], k_sd, vel['S'], np.power(10, Mcorr[count]))/1e6
            #stress[key] = stress_drop(fcut[key], k_sd, vel['S'], M0 )/1e6
        #if plotting:
        #    fig5.gca().set_prop_cycle(None)
        for key, fb in fintp.items():
            #M0 = M0_func(mag[key])
            Mw[count] = Mw_log(Mcorr[count])
            if plotting:
                ax5.semilogx(fb, brune_log(fb, fcut[count], Mcorr[count]), 'o-', color=line.get_color())

            var[count] = variance_reduction(
                Aintp[key], brune_log(fb, fcut[count], Mcorr[count]))
            r2[count] = coeff_r2(Aintp[key], brune_log(
                fb, fcut[count], Mcorr[count]))
            print('fcut[', count, ']: ', '%5.2f' % fcut[count], ' Mcorr[', count, ']: ', '%5.2f' % Mcorr[count],
                  ' Stress drop[', count, ']: ', '%6.3f' % stress[count], 'MPa   SNR: ' +
                  '%5.1f' % snr[count],
                  ' Mw[', count, ']: ', '%3.1f' % Mw[count], ' Md[', key, ']: ', '%3.1f' % mag[key], ' Res[', count, ']: ',
                  '%5.3f' % var[count])
            print('r2: ',var[count])
            fout.write(station + '       '
                       + type_wave + '     '
                       + resp_type + '    '
                       + date[key] + '    '
                       + '%6.1f' % (Rij[count]/1e3) + '    '
                       + '%3.1f' % mag[key] + '    '
                       + '%3.1f' % Mw[count] + '    '
                       + '%5.2f' % fcut[count] + '    ' +
                         '%6.3f' % fcuts[count] + '    '
                       + '%5.2f' % Mcorr[count] + '    ' +
                         '%6.3f' % Mcorrs[count] + '    '
                       + '%6.3f' % stress[count] + '    '
                       + '%5.1f' % snr[count] + '    '
                       + '%5.3f' % var[count] + '    '
                       + '%5.1f' % r2[count] + '    ' + '\n')

            #			ax[0].grid(b=True, which='major', color='k', linestyle='--',linewidth=0.25)
            #			ax[0].grid(b=True, which='minor', color='k', linestyle='--',linewidth=0.25)

    if plotting:
        # closiing figure 1 - Waveforms
        fig1.suptitle(date[k] + r' $M_{cat}$ = ' + '%3.1f' % mag[0] + ' - ' + resp_type + ' - ' + type_wave + ' wave')
        fig1.savefig(waveform_out)
        plt.close(fig1)

    # closing figura 2 - P/S wave Zoom
        fig2.suptitle(date[k] + r' $M_{cat}$ = ' + '%3.1f' % mag[0] + ' - ' + resp_type +
                      ' - ' + type_wave + ' wave')
        fig2.subplots_adjust(hspace=0, wspace=0)
        fig2.savefig(PS_out)
        plt.close(fig2)

    # closing figure 3 - Spectrum
        ax3.legend(fontsize=14)
        ax3.grid(b=True, which='major', color='k',
                 linestyle='--', linewidth=0.25)
        ax3.grid(b=True, which='minor', color='k',
                 linestyle='--', linewidth=0.25)
        ax3.set_xlabel('Frequency [Hz]', fontsize=14)
        ax3.set_title('Original spectrum - ' + date[k] + r' $M_{cat}$ = ' + '%3.1f' % mag[0] +
                  ' - ' + dict_title[resp_type], fontsize=14)
        fig3.savefig(FFT_out)
        plt.close(fig3)

    # closing figura 4 -
        ax4.legend(fontsize=14)
        ax4.grid(b=True, which='major', color='k',
                 linestyle='--', linewidth=0.25)
        ax4.grid(b=True, which='minor', color='k',
                 linestyle='--', linewidth=0.25)
        ax4.set_xlabel('Frequency [Hz]', fontsize=14)
        ax4.set_title('Spectrum - ' + r' $M_{cat}$ = ' + '%3.1f' % mag[0] + ' - ' +
                  dict_title[resp_type], fontsize=14)
        fig4.savefig(SPEC_out)
        plt.close(fig4)

    # closing figure 5 -
        mean_stress=np.array(list(stress.values())).mean()
        ax5.legend(fontsize=14)
        ax5.grid(b=True, which='major', color='k',
                 linestyle='--', linewidth=0.25)
        ax5.grid(b=True, which='minor', color='k',
                 linestyle='--', linewidth=0.25)
        fig5.suptitle('Brune Spectrum ' + dict_title[resp_type] + ' - ' + date[k] 
                     + '\nfc = ' + '%5.2f' % fcut[key] + 'Hz ' + r'$\Delta\sigma=$' + '%5.2f' % mean_stress + 'MPa', fontsize=17)
        ax5.set_ylabel(r'$log_{10}($' + dict_title[resp_type] + ' Spectrum)')
        ax5.set_xlabel('Frequency [Hz]', fontsize=14)
        fig5.savefig(Brune_out)
        plt.close(fig5)

    fout.close()


#if __name__ == "__main__":
#    main()
