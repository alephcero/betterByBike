#import libraries
import os
import pandas as pd
import geopandas as gpd
import numpy as np
import googlemaps
import datetime as dt
import time


#set origin destination
destino = (-34.605537,-58.373022,)
#load census data
radios = gpd.read_file('data/informacion_censal_por_radio_2010_GKBA/informacion_censal_por_radio_2010.shp')
radios = radios.loc[:,['CO_FRAC_RA','geometry']]
radios = radios.to_crs(epsg=4326)
radios['centroids'] = radios.geometry.centroid

print 'Data loaded, rows:', radios.shape[0]

#define query fuction
def queryGoogleAPI(origen):
    key = os.getenv('GOOGLEAPI')
    gmaps = googlemaps.Client(key=key)
    travel = gmaps.distance_matrix(origins = origen,
                               destinations = destino,
                               mode="transit", #driving
                               traffic_model="best_guess")
    tiempo = travel['rows'][0]['elements'][0]['duration']['value']
    dinero = travel['rows'][0]['elements'][0]['fare']['value']
    output = {'tiempo':tiempo,'dinero':dinero}
    return output

tiempos = []
dinero = []

googleLimit = 2400
lastQueryID = 0

while True:
    #check if the task is completed

    if len(tiempos) == radios.shape[0]:
        break

    #at 9 am
    elif ((dt.datetime.now().hour == 9) and (dt.datetime.now().minute == 0)):

        #start running the loop
        for i in range(lastQueryID,lastQueryID + googleLimit):

            #check if the task is completed

            if i == radios.shape[0]:
                break

            #run googleQuery
            origen = (radios.centroids.loc[i].y,radios.centroids.loc[i].x)
            queryResult = queryGoogleAPI(origen)
            tiempos.append(queryResult['tiempo'])
            dinero.append(queryResult['dinero'])

        #save the last row of the query
        lastQueryID = i + 1

    time.sleep(60)

radios['tiempos'] = tiempos
radios['dinero'] = dinero
radios.drop(['centroids'],axis=1,inplace=True)
ratios.to_file('data/googleQuery')
