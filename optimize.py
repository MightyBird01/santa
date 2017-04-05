

fileName = '/home/gs/DataScientist/santa/submission-1.csv'

import pandas as pd
from haversine import haversine
import itertools
from random import randint

MAX_WEIGHT = 1000
EMPTY_WEIGHT = 10
NORTH_POLE = (90,0)


def perm (path, lenPerm):
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



def writeFile (fileName):
    fn = fileName.split('.')[0]
    fn = int(fn.split('-')[1]) + 1
    fileName = '/home/gs/DataScientist/santa/submission-' + str(fn) + '.csv'
    file = open (fileName, 'w')
    file.write ('GiftId,TripId\n')
    for p in pathes:
        for e in pathes[p]:
            file.write('{},{}\n'.format(e,p))
    file.close() 

def readFile (fileName):
    global pathes
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
    return 1

def wrw (tripGifts):
    # weighted reindeer weariness
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

def totalWRW():
    tot = 0
    for p in pathes:
        #print (pathes[p])
        tot += wrw(pathes[p])
    return tot

def optimizeSwap(swapLen):
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
    return 1

def clusterTrips():
    tripCluster = {}
    for p in pathes:
        path = pathes[p]
        el = path[0]
        lon = giftLon[el] + 180
        lon = int(lon/10)
        if lon in tripCluster:
            tripCluster[lon].append(p)
        else:
            tripCluster[lon] = [p]
    return tripCluster
    
    
def swap2():
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
    return res

# -----------------------

print ('Read gifts file...')
gifts = pd.read_csv('~/DataScientist/santa/gifts.csv')
print ('done.')

#print (gifts.shape)
#print (gifts.head())

giftLat = {}
giftLon = {}
giftWeight = {}

print ('Create gifts dict...')
for row in gifts.iterrows():
    global giftLat
    global giftLon
    global giftWeight
    id = int(row[1]['GiftId'])
    giftLat[id] = row[1]['Latitude']
    giftLon[id] = row[1]['Longitude']
    giftWeight[id] = row[1]['Weight']
print ('done.')


pathes = {}

readFile(fileName)
initial = totalWRW()
print ('Initial wrw: {}'.format(initial))

tripCluster = clusterTrips()

optimizeSwap(5)


wrwStart = totalWRW()
tot = 0 
for i in range(0,1000):
    if i%100 == 0:
        print('round {}'.format(i))
    s = swap2()
    tot += s
    if s > 0:
        print ('total / imprTot / impr: {} / {:>10} / {:>10}'.format(int(totalWRW()), int(tot), int(s)))
print('\nimprovement total {}'.format(tot))
wrwEnd = totalWRW()
print (wrwStart - wrwEnd)


wrwStart = totalWRW()
imp = swap2()
wrwEnd = totalWRW()
print (wrwStart)
print (imp)
print (wrwEnd)
print (wrwStart - wrwEnd)



# writeFile(fileName)

pathes[1242]

