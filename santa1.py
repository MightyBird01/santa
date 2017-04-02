# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 11:06:29 2017

@author: gs
"""

# top score 12384075106.1875



import pandas as pd

from haversine import haversine

MAX_WEIGHT = 1000
EMPTY_WEIGHT = 1000
NORTH_POLE = (0,0)

print ('Read gifts file...')
gifts = pd.read_csv('~/DataScientist/santa/gifts.csv')
print ('done.')

print (gifts.shape)
print (gifts.head())

giftLat = {}
giftLon = {}
giftWeight = {}

for row in gifts.iterrows():
    global giftLat
    global giftLon
    global giftWeight
    id = int(row[1]['GiftId'])
    giftLat[id] = row[1]['Latitude']
    giftLon[id] = row[1]['Longitude']
    giftWeight[id] = row[1]['Weight']

#lyon = (45.7597, 4.8422)
#paris = (48.8567, 2.3508)
#print (haversine(lyon, paris))
#print (haversine(lyon, paris, miles=True))

# Lat/Lon (NS, EW, +-90, +-180)

print ('Max Lat: ' + str(max(gifts['Latitude'])))
print ('Min Lat: ' + str(min(gifts['Latitude'])))
print ('Max Lon: ' + str(max(gifts['Longitude'])))
print ('Min Lon: ' + str(min(gifts['Longitude'])))


# calc path length*weights

def wrw (tripGifts):
    wrw = 0.0
    actualWeight = 10
    actualPos = (0,0)
    # weighted reindeer weariness
    # get path
    # calc starting weight
    for g in tripGifts:
        actualWeight += giftWeight[g]
    print ('initialWeight: {}'.format(actualWeight))
    # follow path, add wrw, remove weight
    for g in tripGifts:
        newPos = (giftLat[g], giftLon[g])
        wrw += haversine(actualPos, newPos) * actualWeight
        actualWeight -= giftWeight[g]
        actualPos = newPos
    # head home (10kg)
    wrw += haversine(actualPos, NORTH_POLE) * EMPTY_WEIGHT

    return wrw
    
    

giftsLeft = range(1,100001)


print (wrw([1]))
print (wrw([2]))
print (wrw([1,2]))
print (wrw([2,1]))



