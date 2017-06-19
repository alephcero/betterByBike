#import time
#import sys

#for i in range(10):
#    time.sleep(1)
#    sys.stdout.write("\r%d%%" % i)
#    sys.stdout.flush()


import geopandas as gpd
import numpy as np

data = gpd.read_file('nycTracts.GeoJSON')
data.head()
data['minutes'] = [data.travel[i]['rows'][0]['elements'][0]['duration']['value'] for i in ]

duration = []
for i in range(data.shape[0]):
    try:
        value = data.travel[i]['rows'][0]['elements'][0]['duration']['value']/60
    except:
        value = np.nan
    duration.append(value)

data['duration'] = duration

data.to_file('nycData')
