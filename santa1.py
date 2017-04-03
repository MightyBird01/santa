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
import matplotlib.pyplot as plt

from haversine import haversine
from random import randint

MAX_WEIGHT = 1000
EMPTY_WEIGHT = 1000
NORTH_POLE = (90,0)
LAT_CUTOFF = 80
LON_RANGE = 2.0
LAT_RANGE = 3.0

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


def goingSouth (pos, giftsLeft):
    # find gifts south of pos and close in longitude
    res = []
    for g in giftsLeft:
        if giftLat[g] < pos[0]:
            if ( 
                ( ( abs(giftLon[g] - pos[1]) < LON_RANGE) and 
                  ( abs(giftLat[g] - pos[0]) < LAT_RANGE) )
                or ( (abs(giftLat[g]) > LAT_CUTOFF) and (pos[0] <= 0))):
                res.append(g)
    #print ('{} going south returned elements: {}'.format(pos, len(res)))
    return res


def plotPath (number, path):
    pX = [ giftLon[g] for g in giftsLeft ]    
    pY = [ giftLat[g] for g in giftsLeft ]    
    plt.plot(pX, pY, 'ro', markersize=0.05)
    #plt.plot(gifts['Longitude'], gifts['Latitude'], 'ro', markersize=0.05)
    plt.axis([-180, 180, -90, 90])
    cX = [giftLon[g] for g in path]
    cY = [giftLat[g] for g in path]
    plt.plot(cX, cY, 'b-', linewidth=0.5)
    name = '/home/gs/DataScientist/santa/plots/path' + str(number) + '.png'
    plt.savefig(name, dpi=300)
    plt.close()
    return 1

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
        giftsSouth = goingSouth(pos, giftsLeft)
        if len(giftsSouth) > 0:
            element = closestGift(pos, giftsSouth)
        else:
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
    plotPath (round,path)            
    
    act = wrw(path)
    total += act
    wrwMeanAct = int(act / len(path))
    pathTime = int((time.time() - pathTime0) / .6) / 100
    est = int(total / (100000 - len(giftsLeft)) * 100000 / 1000000000)
    
    print ('round  :      {}'.format(round))
    print ('time   :      {} min'.format(pathTime))
    print ('# gifts:      {}'.format(len(path)))
    print ('path:         {}'.format(path))
    print ('weight:       {}'.format(int(weight)))
    print ('giftsLeft:    {}'.format(len(giftsLeft)))
    print ('actMeanWRW:   {}'.format(wrwMeanAct))
    print ('totalWRW:     {} est in Mrd {}'.format(long(total), est))
    print ('\n')

percent = total / TOP
print ('Result: ' + str(total))
print ('Result: ' + str(int(percent)))




# ---------------------

