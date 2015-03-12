import pymel.core as py
import math
from operator import itemgetter
class EditError( Exception ):
    pass
def editDictionary( dictionaryName, listOfValues, canOverwriteKeys=True ):
    reducedDictionary = dictionaryName
    for i in listOfValues[:-2]:
        if type( reducedDictionary ) != dict and canOverwriteKeys:
            reducedDictionary = {}
        try:
            if reducedDictionary.get( i, None ) == None:
                canOverwriteKeys = True
                raise EditError()
            elif type( reducedDictionary[i] ) != dict:
                raise EditError()
        except EditError:
            reducedDictionary[i] = {}
        except:
            print "Something went wrong"
            return
        reducedDictionary = reducedDictionary[i]
    if canOverwriteKeys or ( not canOverwriteKeys and not reducedDictionary.get( listOfValues[-2], None ) ):
        reducedDictionary[listOfValues[-2]] = listOfValues[-1]
        return True
    else:
        return False
        
def roundToMultiple( multiple, *args ):
    maxPower = 0
    for i in args:
        if i:
            try:
                closestPower = int( math.ceil( math.log( abs( i ), multiple ) ) )
            except:
                closestPower = 0
        else:
            closestPower = 0
        if closestPower > maxPower:
            maxPower = closestPower
    return maxPower

grid = {}
grid[(0,1,0)] = 1
grid[(0,0,0)] = 1
grid[(3,5,-1)] = 1
grid[(10,-5,-3)] = 1

#Get maximum depth level
xMax = max( grid.keys(), key=itemgetter( 0 ) )[0]
xMin = min( grid.keys(), key=itemgetter( 0 ) )[0]
yMax = max( grid.keys(), key=itemgetter( 1 ) )[1]
yMin = min( grid.keys(), key=itemgetter( 1 ) )[1]
zMax = max( grid.keys(), key=itemgetter( 2 ) )[2]
zMin = min( grid.keys(), key=itemgetter( 2 ) )[2]
minDepthLevel = 0
maxDepthLevel = roundToMultiple( 3, xMax, xMin, yMax, yMin, zMax, zMin )

#Start octree dictionary
octreeRange = ( 1, 0, -1 )
octreeStructure = set()
for x in octreeRange:
    for y in octreeRange:
        for z in octreeRange:
            octreeStructure.add( ( x, y, z ) )
octreeDepthName = "Depth"
octreeDataName = "Data"
octreeData = {"Depth":mainDepthLevel, "Data": dict.fromkeys( octreeStructure, False )}


originalCoordinates = dict.fromkeys( grid.keys() )
for absoluteCoordinate in originalCoordinates.keys():
    print absoluteCoordinate
    multiplierList = dict.fromkeys( range( 3 ), list() )
    for key in multiplierList:
        maxMultiplier = 3**maxDepthLevel
        totalMultiplier = 0
        while maxMultiplier > pow( 3, minDepthLevel )*0.9:
            #Detect if it should be positive or negative
            currentMultiplier = maxMultiplier
            if relativeCoordinate[key] > totalMultiplier:
                multiplierList[key].append( 1 )
            elif relativeCoordinate[key] < totalMultiplier:
                multiplierList[key].append( -1 )
                currentMultiplier *= -1
            else:
                multiplierList[key].append( 0 )
            print currentMultiplier
            #Append to total
            totalMultiplier += currentMultiplier
            maxMultiplier /= 3.0
        print multiplierList
        print
