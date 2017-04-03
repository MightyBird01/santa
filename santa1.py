# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 11:06:29 2017

@author: gs
"""

# top score 12.384.075.106 (1.2 * 10^10)
# random result factor 38
# 
TOP = 12384075106.1875

import pandas as pd
import time

from haversine import haversine
from random import randint

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
    # weighted reindeer weariness
    wrw = 0.0
    actualWeight = 10
    actualPos = NORTH_POLE
    # calc starting weight
    for g in tripGifts:
        actualWeight += giftWeight[g]
    #print ('initialWeight: {}'.format(actualWeight))
    # follow path, add wrw, remove weight
    for g in tripGifts:
        newPos = (giftLat[g], giftLon[g])
        wrw += haversine(actualPos, newPos) * actualWeight
        actualWeight -= giftWeight[g]
        actualPos = newPos
    # head home (10kg)
    wrw += haversine(actualPos, NORTH_POLE) * EMPTY_WEIGHT

    return wrw
    
def closestGift (pos, giftsLeft):
    closest = 0
    minDist = 999999.9
    for g in giftsLeft:
        d = haversine( pos, (giftLat[g], giftLon[g]) )
        if d < minDist:
            closest = g
            minDist = d 
    return closest
            
# ---------------------------------------------    

time0 = time.time()

giftsLeft = range(1,100001)

total = 0.0
round = 0

while len(giftsLeft) > 0:
    # create path
    pathTime0 = time.time() 
    round += 1
    path = []
    weight = 0
    pos = NORTH_POLE
    loading = True
    while loading == True:
        #element = giftsLeft[0]
        element = closestGift(pos, giftsLeft)
        if giftWeight[ element ] + weight <= MAX_WEIGHT:
            path.append(element)
            weight += giftWeight[ element ]
            pos = (giftLat[ element ], giftLon[ element ])
            giftsLeft.remove(element)
            if len(giftsLeft) == 0:
                loading = False
        else:
            loading = False
            # full
    # calc path
    # add to total
    act = wrw(path)
    total += act
    wrwMeanAct = int(act / len(path))
    pathTime = time.time() - pathTime0    
    
    print ('round  :   {}'.format(round))
    print ('time   :   {}'.format(pathTime))
    print ('# gifts:   {}'.format(len(path)))
    print ('weight:    {}'.format(int(weight)))
    print ('giftsLeft: {}'.format(len(giftsLeft)))
    print ('actMeanWRW:   {}'.format(wrwMeanAct))
    print ('totalWRW:     {}'.format(long(total)))
    print ('\n')

percent = total / TOP
print ('Result: ' + str(total))
print ('Result: ' + str(int(percent)))


