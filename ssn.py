import os
from obspy.core.utcdatetime import UTCDateTime

NARS=set(line.strip() for line in open('NARS.stations'))

def get_response_files(dir_resp, station_name, t_start):
    fmax = 20
    if station_name.strip() == 'ARIG':
        RESP_FILE = os.path.join(dir_resp, 'ARIG_IG_20090308_21001231.RESP')
    elif station_name.strip() == 'CAIG':
        if t_start >= UTCDateTime(1993, 2, 12) and t_start < UTCDateTime(2007, 5, 12):
            RESP_FILE = os.path.join(
                dir_resp, 'CAIG_IG_19930212_20070512.RESP')
        elif t_start >= UTCDateTime(2007, 5, 12):
            RESP_FILE = os.path.join(
                dir_resp, 'CAIG_IG_20070512_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() == 'CRIG':
        RESP_FILE = os.path.join(dir_resp, 'CRIG_IG_20140323_21001231.RESP')
    elif station_name.strip() == 'DAIG':
        RESP_FILE = os.path.join(dir_resp, 'DAIG_IG_20150402_21001231.RESP')
    elif station_name.strip() == 'HSIG':
        RESP_FILE = os.path.join(dir_resp, 'HSIG_IG_20070618_21001231.RESP')
    elif station_name.strip() == 'HPIG':
        RESP_FILE = os.path.join(dir_resp, 'HPIG_IG_20061211_21001231.RESP')
    elif station_name.strip() == 'PNIG':
        if t_start >= UTCDateTime(1994, 3, 28) and t_start < UTCDateTime(2007, 7, 11):
            fmax = 8
            RESP_FILE = os.path.join(
                dir_resp, 'PNIG_IG_19940328_20070711.RESP')
        elif t_start >= UTCDateTime(2007, 7, 11) and t_start < UTCDateTime(2013, 10, 29):
            RESP_FILE = os.path.join(
                dir_resp, 'PNIG_IG_20070711_20131029.RESP')
        elif t_start >= UTCDateTime(2013, 10, 29) and t_start < UTCDateTime(2014, 6, 24):
            RESP_FILE = os.path.join(
                dir_resp, 'PNIG_IG_20131029_20140624.RESP')
        elif t_start >= UTCDateTime(2014, 6, 24) and t_start < UTCDateTime(2018, 10, 20):
            RESP_FILE = os.path.join(
                dir_resp, 'PNIG_IG_20140624_20181020.RESP')
        elif t_start >= UTCDateTime(2018, 10, 20):
            RESP_FILE = os.path.join(
                dir_resp, 'PNIG_IG_20181020_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() == 'MAIG':
        if t_start >= UTCDateTime(1996, 2, 25) and t_start < UTCDateTime(2013, 8, 15):
            RESP_FILE = os.path.join(
                dir_resp, 'MAIG_IG_19960225_20130815.RESP')
        elif t_start >= UTCDateTime(2013, 8, 15) and t_start < UTCDateTime(2016, 9, 5):
            RESP_FILE = os.path.join(
                dir_resp, 'MAIG_IG_20130815_20160905.RESP')
        elif t_start >= UTCDateTime(2016, 9, 5) and t_start < UTCDateTime(2018, 11, 5):
            RESP_FILE = os.path.join(
                dir_resp, 'MAIG_IG_20160905_20181105.RESP')
        elif t_start >= UTCDateTime(2018, 11, 5):
            RESP_FILE = os.path.join(
                dir_resp, 'MAIG_IG_20181105_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()

    elif station_name.strip() == 'MEIG':
        if t_start >= UTCDateTime(2004, 9, 8) and t_start < UTCDateTime(2014, 4, 26):
            fmax = 8
            RESP_FILE = os.path.join(
                dir_resp, 'MEIG_IG_20040908_20140426.RESP')
        elif t_start >= UTCDateTime(2014, 4, 26):
            RESP_FILE = os.path.join(
                dir_resp, 'MEIG_IG_20140426_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() == 'LPIG':
        if t_start >= UTCDateTime(1996, 9, 8) and t_start < UTCDateTime(2008, 2, 10):
            RESP_FILE = os.path.join(
                dir_resp, 'LPIG_IG_19960908_20080210.RESP')
        elif t_start >= UTCDateTime(2008, 2, 10):
            RESP_FILE = os.path.join(
                dir_resp, 'LPIG_IG_20080210_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() == 'MOIG':
        if t_start >= UTCDateTime(1995, 6, 8) and t_start < UTCDateTime(2000, 6, 1):
            RESP_FILE = os.path.join(dir_resp, 'MOIG_IG_19950608_2000601.RESP')
        elif t_start >= UTCDateTime(2000, 6, 1) and t_start < UTCDateTime(2013, 8, 12):
            RESP_FILE = os.path.join(dir_resp, 'MOIG_IG_2000601_20130812.RESP')
        elif t_start >= UTCDateTime(2013, 8, 12) and t_start < UTCDateTime(2017, 10, 25):
            RESP_FILE = os.path.join(
                    dir_resp, 'MOIG_IG_20130812_20171025.RESP')
        elif t_start >= UTCDateTime(2017, 10, 25):
            RESP_FILE = os.path.join(
                    dir_resp, 'MOIG_IG_20171025_21001231.RESP')
        else: 
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() in NARS:	   
        RESP_FILE = os.path.join(dir_resp,  'RESP.' + station_name.strip() + '.NR..BHZ')

    elif station_name.strip() == 'OXIG':
        if t_start >= UTCDateTime(1994, 3, 2) and t_start < UTCDateTime(2007, 1, 22):
            fmax = 8
            RESP_FILE = os.path.join(
                dir_resp, 'OXIG_IG_19940302_20070122.RESP')
        elif t_start >= UTCDateTime(2007, 1, 22):
            RESP_FILE = os.path.join(
                dir_resp, 'OXIG_IG_20070122_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    elif station_name.strip() == 'PEIG':
        RESP_FILE = os.path.join(dir_resp, 'PEIG_IG_20120922_21001231.RESP')

    elif station_name.strip() == 'PLIG':
        if t_start >= UTCDateTime(1993, 10, 23) and t_start < UTCDateTime(2009, 1, 16):
            fmax = 8
            RESP_FILE = os.path.join(
                dir_resp, 'PLIG_IG_19931023_20090116.RESP')
        elif t_start >= UTCDateTime(2009, 1, 16):
            RESP_FILE = os.path.join(
                dir_resp, 'PLIG_IG_20090116_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None

    elif station_name.strip() == 'YOIG':
        if t_start >= UTCDateTime(2012, 9, 6) and t_start < UTCDateTime(2014, 6, 20):
            RESP_FILE = os.path.join(
                dir_resp, 'YOIG_IG_20120906_20140620.RESP')
            RESP_FILE = None  # Error found
        elif t_start >= UTCDateTime(2014, 6, 20) and t_start < UTCDateTime(2014, 9, 3):
            RESP_FILE = os.path.join(
                dir_resp, 'YOIG_IG_20140620_20140903.RESP')
        elif t_start >= UTCDateTime(2014, 9, 3):
            RESP_FILE = os.path.join(
                dir_resp, 'YOIG_IG_20140903_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None

    elif station_name.strip() == 'TLIG':
        RESP_FILE = os.path.join(dir_resp, 'TLIG_IG_20091013_21001231.RESP')

    elif station_name.strip() == 'TSIG':
        RESP_FILE = os.path.join(dir_resp, 'TSIG_IG_20101110_21001231.RESP')
    elif station_name.strip() == 'SRIG':
        RESP_FILE = os.path.join(dir_resp, 'SRIG_IG_20080228_21001231.RESP')
    elif station_name.strip() == 'SPIG':
        if t_start >= UTCDateTime(2008, 2, 26) and t_start < UTCDateTime(2010, 10, 28):
            RESP_FILE = os.path.join(
                dir_resp, 'SPIG_IG_20080226_20101028.RESP')
        elif t_start > UTCDateTime(2010, 10, 28):
            RESP_FILE = os.path.join(
                dir_resp, 'SPIG_IG_20101028_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None

    elif station_name.strip() == 'TXIG':
        if t_start >= UTCDateTime(2012, 9, 3) and t_start < UTCDateTime(2014, 4, 8):
            RESP_FILE = os.path.join(
                dir_resp, 'TXIG_IG_20120903_20140408.RESP')
        elif t_start >= UTCDateTime(2014, 4, 8) and t_start < UTCDateTime(2014, 6, 21):
            RESP_FILE = os.path.join(
                dir_resp, 'TXIG_IG_20140408_20140621.RESP')
        elif t_start >= UTCDateTime(2014, 6, 21) and t_start < UTCDateTime(2015, 8, 6):
            RESP_FILE = os.path.join(
                dir_resp, 'TXIG_IG_20140621_20150806.RESP')
        elif t_start >= UTCDateTime(2015, 8, 6):
            RESP_FILE = os.path.join(
                dir_resp, 'TXIG_IG_20150806_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None

    elif station_name.strip() == 'ZIIG':
        if t_start >= UTCDateTime(1993, 12, 3) and t_start < UTCDateTime(2007, 5, 7):
            fmax = 8
            RESP_FILE = os.path.join(
                dir_resp, 'ZIIG_IG_19931203_20070507.RESP')
        elif t_start >= UTCDateTime(2007, 5, 7) and t_start < UTCDateTime(2014, 5, 17):
            RESP_FILE = os.path.join(
                dir_resp, 'ZIIG_IG_20070507_20140517.RESP')
        elif t_start >= UTCDateTime(2014, 5, 17) and t_start < UTCDateTime(2018, 2, 27):
            RESP_FILE = os.path.join(
                dir_resp, 'ZIIG_IG_20140517_20180227.RESP')
        elif t_start >= UTCDateTime(2018, 2, 27):
            RESP_FILE = os.path.join(
                dir_resp, 'ZIIG_IG_20180227_21001231.RESP')
        else:
            print('ERROR: No RESP file for ',
                  station_name, ' at time: ', t_start)
            exit()
            return None, None
    else:
        RESP_FILE = os.path.join(dir_resp, station_name + '*.RESP')
    return RESP_FILE, fmax
