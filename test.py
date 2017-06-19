#libraries
import geopandas as gpd
import pandas as pd
import time
import datetime
import os
import googlemaps
import sys


#MODES:
## driving

#python test.py <SHAPEFILE> <DESTINATION ADDRESS> <GEOJSON>
key = os.getenv('GOOGLEAPI')
gmaps = googlemaps.Client(key=key)

def queryGoogleAPIdrive(origen,destinations,departure_time):
    '''
    This function takes an origen coordinates in a tuple (y,x)
    and returns a dictionary with the API result
    '''
    tripInfo = gmaps.distance_matrix(origins = origen,
                                   destinations = destinations,
                                   mode='driving',
                                   departure_time = departure_time,
                                   traffic_model="best_guess")

    return tripInfo
#transit
def queryGoogleAPItransit(origen,destinations,departure_time,transit_mode = [],transit_routing_preference = []):
    '''
    This function takes an origen coordinates in a tuple (y,x)
    and returns a dictionary with the API result
    '''
    tripInfo = gmaps.distance_matrix(origins = origen,
                                   destinations = destinations,
                                   mode='transit',
                                   traffic_model="best_guess",
                                   departure_time = departure_time,
                                   transit_mode = transit_mode,
                                   transit_routing_preference = transit_routing_preference
                                   )
    return tripInfo


## bicycling

def queryGoogleAPIbike(origen,destinations):
    '''
    This function takes an origen coordinates in a tuple (y,x)
    and returns a dictionary with the API result
    '''

    tripInfo = gmaps.distance_matrix(origins = origen,
                                   destinations = destinations,
                                   mode='bicycling')
    return tripInfo




#RUN THE FUNTION

shapefile = sys.argv[1]



#shape file with census polygons
data = gpd.read_file(shapefile)
#data = data.loc[0:3,:]
data = data.to_crs(epsg=4326)
data['centroids'] = data.geometry.centroid
totalRows = data.shape[0]



#set the destination
destination = sys.argv[2]

geocode_result = gmaps.geocode(destination)
coords = geocode_result[0]['geometry']['location']
destinations = (coords['lat'],coords['lng'])


modeOfChoiceIndex = int(raw_input('Choose the mode of transit:\n1- Driving\n2- Public transit\n3- Bicycling\n>'))
modeOfChoiceList = ['driving','transit','bicycling']
modeOfChoice = modeOfChoiceList[modeOfChoiceIndex-1]



if modeOfChoice != 'bicycling':
    #Set departure time
    print 'Choose the departure time (has to be in the future)'
    departYear = int(raw_input('Choose departure YEAR: '))
    departDay = int(raw_input('Choose departure DAY: '))
    departMonth = int(raw_input('Choose departure MONTH: '))
    departHour = int(raw_input('Choose departure HOUR: '))

    departure_time = int(time.mktime(datetime.datetime(departYear,departMonth, departDay, departHour, 0, 0).timetuple()))

    #TRANSIT
    if modeOfChoice == 'transit':

        #set mode of transit choices
        modes = ['bus','suway','train','tram','rail']
        transit_modeIndex = int(raw_input('Choose the transit mode:\n1- bus\n2- subway\n3- train\n4- tramway, light rail\n5- rail (subway,train, light rail)\n6- None \n>'))

        if transit_modeIndex == 6:
            transit_mode= []
        else:
            transit_mode = modes[transit_modeIndex - 1]

        routPrefList = ['less_walking','fewer_transfers']
        routing_preferenceIndex = int(raw_input('Choose the transit mode: \n1- Less walking\n2- Fewer transfers\n3- None\n>'))

        if routing_preferenceIndex == 3:
            transit_routing_preference= []
        else:
            transit_routing_preference = routPrefList[routing_preferenceIndex-1]

        travel = [queryGoogleAPItransit(origen = (data.centroids.loc[i].y,data.centroids.loc[i].x),destinations = destinations,departure_time = departure_time,transit_mode = transit_mode,transit_routing_preference = transit_routing_preference) for i in range(totalRows)]

    #DRIVING
    else:
        travel = [queryGoogleAPIdrive(origen = (data.centroids.loc[i].y,data.centroids.loc[i].x),destinations = destinations,departure_time = departure_time) for i in range(totalRows)]

#BIKE
else:
    travel = [queryGoogleAPIbike(origen = (data.centroids.loc[i].y,data.centroids.loc[i].x),destinations = destinations) for i in range(totalRows)]




#SAVE TO GeoJSON
finalGeoJSON = sys.argv[3]

if os.path.isfile(finalGeoJSON):
    os.system('rm ' + finalGeoJSON)

data['travel'] = travel
data.drop(['centroids'],axis=1,inplace=True)
data.to_file(finalGeoJSON, driver="GeoJSON")
