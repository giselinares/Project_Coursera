import numpy as np
import matplotlib.pyplot as pp
import seaborn
#import urllib.request

#urllib.request.urlretrieve('ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt','stations.txt')
data=open('stations.txt','r')

stations= {}
for line in data:
    if 'GSN' in line:
        fields=line.split()
        stations[fields[0]]=' '.join(fields[4:]) #columns name and location of the station
#print(len(stations))

def findstation(s): #create function
    found = {code: name for code, name in stations.items() if s in name}
#    print(found)
#findstation('LIHUE')
findstation('SAN DIEGO')
findstation('MINNEAPOLIS')
#findstation('IRKUTSK')
datastations=['USW00022536','USW00023188','USW00014922','RSM00030710']

#print(open('USW00022536.dly','r').readlines()[:10])

def parsefile(filename): #use readme.txt to set parameters
    return np.genfromtxt(filename,
                        delimiter=dly_delimiter,
                        usecols=dly_usecols,
                        dtype=dly_dtype,
                        names=dly_names)
dly_delimiter=[11,4,2,4]+[5,1,1,1]*31 #ID, year,month,element + value and flags
dly_usecols=[1,2,3]+[4*i for i in range(1,32)] #columns for year, month, element and value
dly_dtype=[np.int32,np.int32,(np.str_,4)]+[np.int32]*31 #data types for year, month, element, value
dly_names=['year','month','obs']+[str(day) for day in range(1,31+1)]

sandiego=parsefile('USW00023188.dly')
minneapolis=parsefile('USW00014922.dly')

def unroll(record):
    startdate=np.datetime64('{}-{:02}'.format(record['year'],record['month']))
    dates=np.arange(startdate,startdate+np.timedelta64(1,'M'),np.timedelta64(1,'D'))

    rows=[(date,record[str(i+1)]/10) for i,date in enumerate(dates)]

    return np.array(rows,dtype=[('date','M8[D]'),('value','d')])

#print(unroll(sandiego[0]))
#print(unroll(minneapolis[0]))
def getobs(filename,obs): #replace missing data for nan
    data= np.concatenate([unroll(row) for row in parsefile(filename) if row[2]==obs])
    data['value'][data['value']==-1000.0]=np.nan
    return data

sandiego_tmax=getobs('USW00023188.dly','TMAX')
sandiego_tmin=getobs('USW00023188.dly','TMIN')
minn_tmax=getobs('USW00014922.dly','TMAX')
minn_tmin=getobs('USW00014922.dly','TMIN')

#pp.plot(minn_tmax['date'],minn_tmax['value'])

def fillnans(data):
    dates_float=data['date'].astype(np.float64) #interpolate missing data with neighbor values
    nan = np.isnan(data['value'])

    data['value'][nan]= np.interp(dates_float[nan],dates_float[~nan],data['value'][~nan])

fillnans(sandiego_tmax)
fillnans(sandiego_tmin)
fillnans(minn_tmax)
fillnans(minn_tmin)

def plot_smoothed(t,win=10):#average smooth function
    smoothed=np.correlate(t['value'],np.ones(win)/win,'same')
    pp.plot(t['date'],smoothed)


#for i,code in enumerate(datastations): #to plot the four stations
#    pp.subplot(2,2,i+1)
#    plot_smoothed(getobs('{}.dly'.format(code),'TMIN'),365)
#    plot_smoothed(getobs('{}.dly'.format(code),'TMAX'),365)

#    pp.title(stations[code])
#    pp.axis(xmin=np.datetime64('1952'),xmax=np.datetime64('2012'),ymin=-10,ymax=30)

#pp.tight_layout()


def selectyear(data,year): #Displays all the temp for specific year
    start=np.datetime64('{}'.format(year))
    end= start + np.timedelta64(1,'Y')

    return data[(data['date']>= start) & (data['date'] < end)]['value'] #boolean conditions
#print(selectyear(minn_tmin,1951))

years=np.arange(1940,2014+1)

sandiego_tmin_all=np.vstack([selectyear(sandiego_tmin,year)[:365] for year in years]) #arrange T in matrix (64x365)
sandiego_tmax_all=np.vstack([selectyear(sandiego_tmax,year)[:365] for year in years])

minn_tmax_all=np.vstack([selectyear(minn_tmax,year)[:365] for year in years])

#print(minn_tmax_all)
#print(minn_tmax_all.shape)

pp.figure(figsize=(12,4))

#days=np.arange(1,365+1)


sandiego_tmin_recordmin= np.min(sandiego_tmin_all,axis=0)
sandiego_tmin_recordmax= np.max(sandiego_tmin_all,axis=0)

sandiego_tmin_recordmean= np.mean(sandiego_tmin_all,axis=1) #challenge
minn_tmax_recordmean= np.mean(minn_tmax_all,axis=1) #challenge

minn_warmest=years[np.argmax(minn_tmax_recordmean)]
sandiego_coldest=years[np.argmin(sandiego_tmin_recordmean)]

print(minn_warmest,sandiego_coldest)

#sandiego_tmin_recordmin_fix=np.where(sandiego_tmin_recordmin<0,15,sandiego_tmin_recordmin)

pp.plot(years,minn_tmax_recordmean)


pp.plot(years,sandiego_tmin_recordmean)

days = np.arange(1,366+1) #leap years 1948 and 2012

pp.fill_between(days,selectyear(minn_tmin,minn_warmest),selectyear(minn_tmax,minn_warmest),color='b',alpha=0.4)
pp.fill_between(days,selectyear(sandiego_tmin,sandiego_coldest),selectyear(sandiego_tmax,sandiego_coldest),color='r',alpha=0.4)

#pp.fill_between(days,sandiego_tmin_recordmean,np.min(sandiego_tmin_all,axis=0),alpha=0.4) #plot a shaded area
#pp.plot(selectyear(sandiego_tmin,2009))

#pp.fill_between(days,np.min(sandiego_tmax_all,axis=0),np.max(sandiego_tmax_all,axis=0),alpha=0.4) #plot a shaded area
#pp.plot(selectyear(sandiego_tmax,2009))

pp.axis(xmin=0,xmax=366)

pp.title('{} in Minneapolis vs. {} in San Diego'.format(minn_warmest,sandiego_coldest))

#print(lihue_tmin_recordmin_fix)
#print(lihue_tmin_recordmax= np.max(lihue_tmin_all,axis=0))

pp.show()



#print(np.mean(lihue_tmin['value']),np.mean(lihue_tmax['value']))
#pp.plot(lihue_tmin[10000:12000]['date'],lihue_tmin[10000:12000]['value'])
#plot_smoothed(lihue_tmin[10000:12000])
#plot_smoothed(lihue_tmin[10000:12000],30) #higher smooth
#pp.plot(lihue_tmax['date'],lihue_tmax['value'])
#pp.plot(lihue_tmin['date'],lihue_tmin['value'])
