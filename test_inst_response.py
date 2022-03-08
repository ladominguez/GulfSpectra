import obspy as o
from ssn import get_response_files
import json
import matplotlib.pyplot as plt


fparam  = open('params.json')
params  = json.load(fparam)
station = 'LPIG'
eq4 = '/Users/antonio/Dropbox/espectrosGolfo/2018-08-24-mw4.0/20180824160332.IG.LPIG.HHZ.sac'
eq5 = '/Users/antonio/Dropbox/espectrosGolfo/2018-11-09-mw5.2/LPIG/20181109143351.IG.LPIG.HHZ.sac'
eq6 = '/Users/antonio/Dropbox/espectrosGolfo/2013-10-19-mw6.3/20131019175455.IG.LPIG.HHZ.sac'

st  = o.read(eq4)
st += o.read(eq5)
st += o.read(eq6)
tr = st[0]

RESP_FILE, fmax = get_response_files(params['iresp'], station, tr.stats.starttime)
pre_filt        = [0.005, 0.0125, 30, 40]
resp_type       = 'VEL'

inv = o.read_inventory(RESP_FILE)
st.remove_response(inventory=inv, output=resp_type, zero_mean=True, pre_filt=pre_filt, taper=True)

plt.subplot(3,1,1)
plt.plot(st[0].times(),st[0].data,'k',linewidth=0.5) 
plt.xlim(0, 100)
plt.subplot(3,1,2)
plt.plot(st[1].times(),st[1].data,'k',linewidth=0.5) 
plt.xlim(0, 100)
plt.subplot(3,1,3)
plt.plot(st[2].times(),st[2].data,'k',linewidth=0.5) 
plt.xlim(0, 100)

plt.show()

