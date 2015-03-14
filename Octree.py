import pymel.core as pm
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
    
    
import time
st = time.time()
grid = {}
grid[(0,0,0)] = 1
grid[(0,0,1)] = 1
grid[(1,0,0)] = 1
grid[(1,0,1)] = 1
grid[(0,1,0)] = 1
grid[(0,1,1)] = 1
grid[(1,1,0)] = 1
grid[(1,1,1)] = 1
grid[(3,0,-1)] = 1
grid[(10,0,-3)] = 1

grid[(2,1,1)] = 1
grid[(2,1,0)] = 1
grid[(2,0,1)] = 1
grid[(2,0,0)] = 1
grid[(3,1,1)] = 1
grid[(3,1,0)] = 1
grid[(3,0,1)] = 1
grid[(3,0,0)] = 5 #To demonstrate blocks not grouping if different ID

minDepthLevel = 0


#Convert to new format that gets rid of even values
def convertCoordinates( dictionaryName, minDepthLevel=0 ):
    newDictionary = {}
    addAmount = pow( 2, minDepthLevel )
    for coordinate in dictionaryName.keys():
        newDictionary[tuple( i*2+addAmount*(-1 if i<0 else 1) for i in coordinate )] = dictionaryName[coordinate]
    return newDictionary
    
#grid = cPickle.loads(zlib.decompress(base64.b64decode(urllib.urlopen("http://pastee.co/OQ5POF/raw").read()))); minDepthLevel = 0
calculatedGrid = convertCoordinates( grid, minDepthLevel )

#Get maximum depth level
xMax = max( calculatedGrid.keys(), key=itemgetter( 0 ) )[0]
xMin = min( calculatedGrid.keys(), key=itemgetter( 0 ) )[0]
yMax = max( calculatedGrid.keys(), key=itemgetter( 1 ) )[1]
yMin = min( calculatedGrid.keys(), key=itemgetter( 1 ) )[1]
zMax = max( calculatedGrid.keys(), key=itemgetter( 2 ) )[2]
zMin = min( calculatedGrid.keys(), key=itemgetter( 2 ) )[2]
maxDepthLevel = roundToMultiple( 2, xMax, xMin, yMax, yMin, zMax, zMin )

#Start octree dictionary
octreeRange = ( 1, -1 )
octreeStructure = set()
for x in octreeRange:
    for y in octreeRange:
        for z in octreeRange:
            octreeStructure.add( ( x, y, z ) )
octreeDepthName = "Depth"
octreeDataName = "Data"
octreeData = {"Depth":maxDepthLevel, "Data": dict.fromkeys( octreeStructure, False )}


originalCoordinates = dict.fromkeys( calculatedGrid.keys() )
for absoluteCoordinate in originalCoordinates.keys():
    #Find the path down the depth levels
    multiplierList = {0: [], 1: [], 2: []}
    for key in multiplierList.keys():
        maxMultiplier = pow( 2, maxDepthLevel )
        totalMultiplier = 0
        while maxMultiplier > pow( 2, minDepthLevel )*0.9:
            #Detect if it should be positive or negative
            currentMultiplier = maxMultiplier
            if absoluteCoordinate[key] > totalMultiplier:
                multiplierList[key].append( 1 )
            elif absoluteCoordinate[key] < totalMultiplier:
                multiplierList[key].append( -1 )
                currentMultiplier *= -1
            else:
                multiplierList[key].append( 1 )
                print "Something is wrong, coordinate value is even"
            #Append to total
            totalMultiplier += currentMultiplier
            maxMultiplier /= 2.0
            
    originalCoordinates[absoluteCoordinate] = multiplierList
    
#Write into dictionary
for relativeCoordinate in originalCoordinates:
    
    #Get the coordinates for each depth level
    relativeValues = originalCoordinates[relativeCoordinate]
    relativeCoordinates = zip( relativeValues[0], relativeValues[1], relativeValues[2] )
    
    #Fill with True
    dictionaryFix = [("Data")]*( len( relativeCoordinates )*2 )
    dictionaryFix[1::2] = relativeCoordinates
    dictionaryFix.append( calculatedGrid[relativeCoordinate] )
    editDictionary( octreeData, dictionaryFix )
    
    #Fill empty values with False
    currentDepth = 0
    maxDepth = octreeData["Depth"]-minDepthLevel
    while currentDepth < maxDepth:
        depthDictionaryPath = dictionaryFix[:-1]
        currentDictionaryDepth = reduce( dict.__getitem__, depthDictionaryPath[:-1-currentDepth*2], octreeData )
        for i in octreeStructure:
            if currentDictionaryDepth.get( i, None ) == None:
                currentDictionaryDepth[i] = False
                editDictionary( octreeData, depthDictionaryPath[:-1-currentDepth*2]+[i, False], False )
        #Fill in depth
        editDictionary( octreeData, depthDictionaryPath[:-2-currentDepth*2]+["Depth", currentDepth+minDepthLevel], False )
        currentDepth += 1
            
    #Move up a level if all values are 1
    dictionaryPath = dictionaryFix[:-2]
    while True:
        allValuesAtDepth = reduce( dict.__getitem__, dictionaryPath, octreeData )
        allPointValues = [allValuesAtDepth.get( coordinate, None ) for coordinate in octreeStructure]
        everythingIsPoint = all( x == allPointValues[0] and str( x ).isdigit() for x in allPointValues )
        if everythingIsPoint:
            editDictionary( octreeData, dictionaryPath[:-1]+[allPointValues[0]] )
            dictionaryPath = dictionaryPath[:-2]
        else:
            break


#Calculate points
def formatOctree( dictionaryValue, minDepthLevel, startingCoordinates=[0, 0, 0] ):
    allPoints = {}
    currentDepth = dictionaryValue["Depth"]
    depthMultiplier = pow( 2, currentDepth )
    #Amount to add to the position
    if minDepthLevel > 0:
        addAmount = 1-pow( 2, ( minDepthLevel-1 ) )
    else:
        depthIncrement = minDepthLevel+1
        addAmount = pow( 2, minDepthLevel )/2.0 
        while depthIncrement < 0:
            addAmount += pow( 2, depthIncrement )/2.0
            depthIncrement += 1
    differenceInDepth = currentDepth-minDepthLevel
    for key in dictionaryValue["Data"].keys():
        newCoordinate = [depthMultiplier*i for i in key]
        newCoordinate[0] += startingCoordinates[0]
        newCoordinate[1] += startingCoordinates[1]
        newCoordinate[2] += startingCoordinates[2]
        newDictionaryValue = dictionaryValue["Data"][key]
        
        if newDictionaryValue and str( newDictionaryValue ).isdigit():
            cubeSize = 2**currentDepth
            #Increment position if conditions are met
            if ( currentDepth and minDepthLevel >= 0 ) or ( currentDepth <= 0 and minDepthLevel < 0 ):
                moveCubeAmount = addAmount
            #Fix for strange behaviour when minDepthLevel = -1
            elif differenceInDepth > 0:
                moveCubeAmount = 1
                #Fix for stranger behaviour when minDepthLevel = -1 and it's a big generation
                if differenceInDepth > 1:
                    moveCubeAmount -= 0.25
            else:
                moveCubeAmount = 0
            
            totalMovement = tuple( ( i+(1 if i<0 else -1) )/2+moveCubeAmount for i in newCoordinate )
            allPoints[totalMovement] = [cubeSize, newDictionaryValue]
        elif type( newDictionaryValue ) == dict:
            allPoints.update( formatOctree( newDictionaryValue, minDepthLevel, newCoordinate ) )
    return allPoints

newList = formatOctree( octreeData, minDepthLevel )

import zlib, base64, cPickle
inputLength = len( cPickle.dumps( grid ) )
octreeLength = len( cPickle.dumps( octreeData ) )
print "Length of input:  {0}".format( inputLength )
print "Length of octree: {0}".format( octreeLength )
print "{0}% efficiency".format( round( float( inputLength )/octreeLength, 2 )*100 )
print "Length of output:  {0}".format( len( cPickle.dumps( newList ) ) )

print time.time()-st


for coordinates in newList.keys():
    cubeSize = newList[coordinates][0]
    blockID = newList[coordinates][1]
    newCube = pm.polyCube( h=cubeSize, w=cubeSize, d=cubeSize )[0]
    pm.move( newCube, coordinates )
    pm.addAttr( newCube, shortName = 'id', longName = "blockID", attributeType = "byte" )
    pm.setAttr( "{0}.id".format( newCube ), blockID )
