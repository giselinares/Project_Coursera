import numpy as np
import matplotlib.pyplot as pp
import urllib.request

# urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt','readme.txt')
# urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt','stations.txt')
# urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_gsn.tar.gz','ghcnd_gsn.tar.gz')
# urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-countries.txt','ghcnd-countries.txt')

def get_stations():
    open('stations.txt','r').readlines()[:10]
    stations = {}

    for line in open('stations.txt','r'):  # read every line of stations
        if 'GSN' in line:
            fields = line.split()
            stations[fields[0]] = ' '.join(fields[4:]) #columns name and location of the station
    return stations

def findstation(s):
    found = {code: name for code, name in stations.items() if s in name}
    print(found)

def findstation_country(s):
    found_country = {code: name for code,name in get_stations().items() if code.startswith(s)}
    print(found_country)

def parse_dly(filename): #use readme.txt to set parameters
    return np.genfromtxt(filename,
                        delimiter=dly_delimiter,
                        usecols=dly_usecols,
                        dtype=dly_dtype,
                        names=dly_names)
dly_delimiter=[11,4,2,4]+[5,1,1,1]*31 #ID, year,month,element + value and flags
dly_usecols=[1,2,3]+[4*i for i in range(1,32)] #columns for year, month, element and value
dly_dtype=[np.int32,np.int32,(np.str_,4)]+[np.int32]*31 #data types for year, month, element, value
dly_names=['year','month','obs']+[str(day) for day in range(1,31+1)]

def date_format(record):
    startdate = np.datetime64('{}-{:02}'.format(record['year'], record['month']))
    dates = np.arange(startdate, startdate + np.timedelta64(1, 'M'), np.timedelta64(1, 'D'))

    rows = [(date, record[str(i + 1)] / 10) for i, date in enumerate(dates)]
    return np.array(rows, dtype=[('date', 'M8[D]'), ('value', 'd')])

def getobs(filename, obs):
    data = np.concatenate([date_format(row) for row in parse_dly(filename) if row[2] == obs])

    data['value'][data['value'] == -999.9] = np.nan  # replace missing data for nan

    return data
tromso_tmax = getobs('NO000001026.dly','TMAX')
tromso_tmin = getobs('NO000001026.dly','TMIN')

def fillnans(data):
    dates_float=data['date'].astype(np.float64) #interpolate missing data with neighbor values
    nan = np.isnan(data['value'])

    data['value'][nan]= np.interp(dates_float[nan],dates_float[~nan],data['value'][~nan])

def plot_smoothed(t,win=10):#average smooth function
    smoothed=np.correlate(t['value'],np.ones(win)/win,'same')
    pp.plot(t['date'],smoothed)

pp.figure(figsize=(12,6))
pp.plot(tromso_tmin[32000:39000]['date'],tromso_tmin[32000:39000]['value'], label="TMIN")

plot_smoothed(tromso_tmin[32000:39000],50)
pp.title('Minimum temperature in Tromso from 2008-2022')
pp.ylabel('Temperature (degrees C)')
pp.xlabel('Years')
pp.legend(loc="upper left")
pp.grid(visible='True')

pp.figure(figsize=(12,6))
pp.plot(tromso_tmax[30000:37000]['date'],tromso_tmax[30000:37000]['value'], label="TMAX")

plot_smoothed(tromso_tmax[30000:37000],50)
pp.title('Maximum temperature in Tromso from 2008-2022')
pp.ylabel('Temperature (degrees C)')
pp.xlabel('Years')
pp.legend(loc="upper left")
pp.grid(visible='True')

pp.figure(figsize=(12,6))
plot_smoothed(getobs('NO000001026.dly','TMIN'),365)
plot_smoothed(getobs('NO000001026.dly','TMAX'),365)

pp.title('TMIN and TMAX in Tromso weather station from 1930 to 2022')
pp.axis(xmin=np.datetime64('1930'),xmax=np.datetime64('2022'),ymin=-5,ymax=10)
pp.ylabel('Temperature (degrees C)')
pp.xlabel('Years')
pp.grid(visible='True')

pp.show()


