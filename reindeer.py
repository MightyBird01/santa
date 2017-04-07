# -*- coding: utf-8 -*-
"""
Created on Fri Apr  7 07:37:14 2017

@author: gs
"""


import pandas as pd
import time
import matplotlib.pyplot as plt

from haversine import haversine
from random import randint

MAX_WEIGHT = 1000
EMPTY_WEIGHT = 10
NORTH_POLE = (90,0)
STOP_FILE_NAME = 'stop.txt'

LAT_CUTOFF = 80
LON_RANGE = 2.0
LAT_RANGE = 3.0
RAW_MAX_DIST = 2


giftLat = {}
giftLon = {}
giftWeight = {}


def readGifts():
    global giftLat
    global giftLon
    global giftWeight
    print ('Read gifts file...')
    gifts = pd.read_csv('gifts.csv')
    print ('done.')
    print ('Create gift dicts...')
    for row in gifts.iterrows():
        id = int(row[1]['GiftId'])
        giftLat[id] = row[1]['Latitude']
        giftLon[id] = row[1]['Longitude']
        giftWeight[id] = row[1]['Weight']
    print ('done.')
    return 1

def createNextFileName(fileName):
    fn = fileName.split('.')[0]
    fn = int(fn.split('-')[1]) + 1
    fileName = 'submission-' + str(fn) + '.csv'
    return fileName

def writeSubmissionFile (fileName, pathes):
    file = open (fileName, 'w')
    file.write ('GiftId,TripId\n')
    for p in pathes:
        for e in pathes[p]:
            file.write('{},{}\n'.format(e,p))
    file.close() 

def readSubmissionFile (fileName):
    # takes name and returns pathes dict
    pathes = {}
    print ('Read trips file...')
    trips = pd.read_csv(fileName)
    print ('done.')
    print ('Create trip dict...')
    for row in trips.iterrows():
        gift = int(row[1]['GiftId'])
        trip = int(row[1]['TripId'])
        if trip in pathes:
            pathes[trip].append(gift)
        else:
            pathes[trip] = [gift]
    print ('done.')
    return pathes

def stopSignal():
    res = False
    with open(STOP_FILE_NAME, 'r') as f:
        lines = f.readlines()
        l = lines[0]
        if 'stop' in l:
            res = True
    return res

# ----------------------------------------------------------------------
    
def wrw (tripGifts):
    # weighted reindeer weariness
    # takes list of giftIds
    wrw = 0.0
    actualWeight = EMPTY_WEIGHT
    actualPos = NORTH_POLE
    # calc starting weight
    for g in tripGifts:
        actualWeight += giftWeight[g]
    #print ('initialWeight: {}'.format(actualWeight))
    # follow path, add wrw, remove weight
    #print ('initial weight = {}'.format(actualWeight))
    for g in tripGifts:
        newPos = (giftLat[g], giftLon[g])
        #print ('newpos: {}'.format(newPos))
        dist = haversine(actualPos, newPos)
        #print ('dist: {}'.format(dist))
        wrw += dist * actualWeight
        actualWeight -= giftWeight[g]
        actualPos = newPos
    # head home (10kg)
    #print ('end weight = {}'.format(actualWeight))
    wrw += haversine(actualPos, NORTH_POLE) * EMPTY_WEIGHT

    return wrw

def tripWeight (tripGifts):
    res = 0.0
    for g in tripGifts:
        res += giftWeight[g]
    return res

def totalWRW(pathes):
    # takes pathes dict and returns sum of wrw
    tot = 0
    for p in pathes:
        #print (pathes[p])
        tot += wrw(pathes[p])
    return tot


# --------------------------------------------------------------------

def closeGiftsRaw(pos, giftsLeft):
    # return list of ids of potentially close elements based on grid
    lat = pos[0]
    lon = pos[1]
    res = []
    for g in giftsLeft:
        la1 = giftLat[g]
        lo1 = giftLon[g]
        if ((abs(lat-la1) < RAW_MAX_DIST) and (abs(lon-lo1) < RAW_MAX_DIST)):
            res.append(g)
    #print ('raw number: {}'.format(len(res)))
    return res
    
    
def closestGift (pos, giftsLeft):
    # return closest gift as id
    closest = 0
    minDist = 999999.9
    for g in giftsLeft:
        d = haversine( pos, (giftLat[g], giftLon[g]) )
        if d < minDist:
            closest = g
            minDist = d 
    return closest

def closestGiftWeighted (pos, giftsLeft, pathLen):
    # return closest gift weighted as id
    closest = 0
    minDist = 9999999.9
    pathLen += 10 # do not overrate
    for g in giftsLeft:
        #d = haversine( pos, (giftLat[g], giftLon[g]) ) / ((giftWeight[g] / WEIGHT_FACTOR) / pathLen)
        d = haversine( pos, (giftLat[g], giftLon[g]) ) - (giftWeight[g] + pathLen) * WEIGHT_FACTOR
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

# --------------------------------------------------------------------


def plotPath (number, path, giftsLeft):
    pX = [ giftLon[g] for g in giftsLeft ]    
    pY = [ giftLat[g] for g in giftsLeft ]    
    plt.plot(pX, pY, 'ro', markersize=0.05)
    #plt.plot(gifts['Longitude'], gifts['Latitude'], 'ro', markersize=0.05)
    plt.axis([-180, 180, -90, 90])
    cX = [giftLon[g] for g in path]
    cY = [giftLat[g] for g in path]
    plt.plot(cX, cY, 'b-', linewidth=0.5)
    name = 'plots/path' + str(number) + '.png'
    plt.savefig(name, dpi=300)
    plt.close()
    return 1

# --------------------------------------------------------------------


def perm (path, lenPerm):
    # takes list of giftIds and permutation length
    # returns list of all possible pathes
    positions = range(0,len(path)-lenPerm+1)
    #print (positions)
    result = []
    for i in positions:
        first = path[0:i]
        middle = path[i:i+lenPerm]
        last = path[i+lenPerm:len(path)]
        #print (first, middle, last)
        perms = list(itertools.permutations(middle, lenPerm))
        for p in perms:
            l = first + list(p) + last
            result.append(l)
    return (result)

def optimizeSwap(swapLen, pathes):
    saved = 0
    for p in pathes:
        betterSolutionFound = True
        while betterSolutionFound == True:
            betterSolutionFound = False
            print ('\nchecking path {}'.format(p))
            l = perm(pathes[p], swapLen)
            print ('number perms: {}'.format(len(l)))
            lowest = wrw(pathes[p])
            startWRW = lowest
            lowestPath = pathes[p]
            for p2 in l:
                w = wrw(p2)
                if w < lowest:
                    lowest = w
                    lowestPath = p2
    
            if lowest < startWRW:
                betterSolutionFound = True
                pathes[p] = lowestPath
                print ('Reduction path {}: {}'.format(p, int(startWRW-lowest)))
                saved += (startWRW-lowest)
                print ('optimized so far: {}'.format(int(saved)))
    print ('\noptimized total: {}\n'.format(int(saved)))
    return pathes



def clusterTrips():
    tripCluster = {}
    for p in pathes:
        path = pathes[p]
        el = path[0]
        lon = giftLon[el] + 180 + CLUSTER_OFFSET
        lon = int(lon/10) % 36
        if lon in tripCluster:
            tripCluster[lon].append(p)
        else:
            tripCluster[lon] = [p]
    return tripCluster
    
    
def swap2(tripCluster, pathes):
    # cluster 0-35
    c = randint(0,35)
    #print ('cluster: {}'.format(c))
    # 2 trips
    trip1 = 0
    trip2 = 0
    res = 0
    while trip1 == trip2:
        # trip positions in cluster
        possibleTrips = tripCluster[c]
        lpt = len(possibleTrips)
        trip1 = randint(0,lpt-1)
        trip2 = randint(0,lpt-1)
    trip1 = tripCluster[c][trip1]
    trip2 = tripCluster[c][trip2]
    # trip ids in pathes
    #print ('trip 1 id: {}'.format(trip1))
    #print ('trip 2 id: {}'.format(trip2))

    tripPath1 = pathes[trip1]
    tripPath2 = pathes[trip2]
    #print ('trip 1 path: {}'.format(tripPath1))
    #print ('trip 2 path: {}'.format(tripPath2))
    #print ('trip 1 path len: {}'.format(len(tripPath1)))
    #print ('trip 2 path len: {}'.format(len(tripPath2)))
    weight1 = tripWeight(tripPath1)
    weight2 = tripWeight(tripPath2)
    #print ('old weight: {} {}'.format(weight1, weight2))
    oldWRW1 = wrw(tripPath1)
    oldWRW2 = wrw(tripPath2)
    # 2 elements
    giftId1 = tripPath1[randint(0,len(tripPath1)-1)]
    giftId2 = tripPath2[randint(0,len(tripPath2)-1)]
    #print ('gift 1 id: {}'.format(giftId1))
    #print ('gift 2 id: {}'.format(giftId2))
    # gift ids

    basePath1 = tripPath1[:]
    basePath1.remove(giftId1)
    basePath2 = tripPath2[:]
    basePath2.remove(giftId2)
    #print ('base path 1: {}'.format(basePath1))
    #print ('base path 2: {}'.format(basePath2))
    #print ('base 1 path len: {}'.format(len(basePath1)))
    #print ('base 2 path len: {}'.format(len(basePath2)))
    # pathes without selected elements (giftIDs)

    if ((tripWeight(basePath1+[giftId2]) <= MAX_WEIGHT) and (tripWeight(basePath2+[giftId1]) <= MAX_WEIGHT)):
        #print ('weight would be ok...')
        bestPath1wrw = 999999999.9
        bestPath1 = []
        for i in range(0,len(basePath1)+2):
            newPath = basePath1[:]
            newPath.insert(i,giftId2)
            newWRW = wrw(newPath)
            if newWRW < bestPath1wrw:
                #print ('new 1 path len: {}'.format(len(newPath)))
                bestPath1wrw = newWRW
                bestPath1 = newPath[:]

        bestPath2wrw = 999999999.9
        bestPath2 = []
        for i in range(0,len(basePath2)+2):
            newPath = basePath2[:]
            newPath.insert(i,giftId1)
            newWRW = wrw(newPath)
            if newWRW < bestPath2wrw:
                #print ('new 2 path len: {}'.format(len(newPath)))
                bestPath2wrw = newWRW
                bestPath2 = newPath[:]

        if (bestPath1wrw+bestPath2wrw) < (oldWRW1 + oldWRW2 - 1):
            #print('swap2 improvement found: {}'.format(int(oldWRW1+oldWRW2-bestPath1wrw-bestPath2wrw)))
            res = oldWRW1+oldWRW2-bestPath1wrw-bestPath2wrw
            pathes[trip1] = bestPath1
            pathes[trip2] = bestPath2
    return res, pathes

