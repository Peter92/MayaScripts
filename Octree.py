"""
Info
 - Max depth level is fixed
 - Min depth level doesn't matter, just determins the voxel size
 - Maximum coordinates are +-(2^depth-1)
 - Set ID to 0 to remove block, dictionary will automatically clean
 
 - If changed != True, set to true and all branches to true
"""
from codeStuff import TimeOutput
from pprint import PrettyPrinter
pp = PrettyPrinter().pprint
from collections import Counter
import pymel.core as pm
import math, sys
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
            print "Error editing dictionary: {}.".format( sys.exc_info()[1] )
            return
        reducedDictionary = reducedDictionary[i]
    if canOverwriteKeys or ( not canOverwriteKeys and not reducedDictionary.get( listOfValues[-2], None ) ):
        reducedDictionary[listOfValues[-2]] = listOfValues[-1]
        return True
    else:
        return False
def recursiveList( currentInput, combinations, length, returnAll=False ):
    newInputList = []
    for input in currentInput:
        inputWithinRange = len( input ) < length
        if inputWithinRange:
            for combination in combinations:
                newInputList += recursiveList( [input + [input[0], combination]], combinations, length, returnAll )
        if not inputWithinRange or returnAll:
            newInputList.append( input )
    return newInputList
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
#pp().pprint(octreeData)
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

'''
grid = {}
#grid[(2,0,0)] = 2
grid[(0,0,1)] = 2
grid[(1,0,0)] = [3,3]
'''

minDepthLevel = 0

import time
st = time.time()

#Convert to new format that gets rid of even values
def convertCoordinates( dictionaryName, minDepthLevel=0 ):
    newDictionary = {}
    addAmount = pow( 2, minDepthLevel )
    
    for coordinate in dictionaryName.keys():
        
        #Get depth if set
        if type( dictionaryName[coordinate] ) == list:
            coordinateID = dictionaryName[coordinate][0]
            differenceInDepth = dictionaryName[coordinate][1]-minDepthLevel
        else:
            coordinateID = dictionaryName[coordinate]
            differenceInDepth = 0
        
        #Convert larger cubes into multiple small ones
        extraSize = pow( 2, differenceInDepth )/2
        
        x, y, z = coordinate
        rangeX = xrange( int( math.floor( x-extraSize ) ), int( math.ceil( x+extraSize+1 ) ) )
        rangeY = xrange( int( math.floor( y-extraSize ) ), int( math.ceil( y+extraSize+1 ) ) )
        rangeZ = xrange( int( math.floor( z-extraSize ) ), int( math.ceil( z+extraSize+1 ) ) )
        for x in rangeX:
            for y in rangeY:
                for z in rangeZ:
                    newDictionary[tuple( i*2+addAmount*( -1 if i<0 else 1 ) for i in ( x, y, z ) )] = coordinateID
                    
    return newDictionary

    
#grid = grid2
calculatedGrid = convertCoordinates( grid, minDepthLevel )


print "{}: Recalculated coordinates".format( TimeOutput( st, time.time() ) )

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
            
octreeData = {"Depth": maxDepthLevel, "Nodes": dict.fromkeys( octreeStructure, 0 ), "Data": 0}


print "{}: Created octree".format( TimeOutput( st, time.time() ) )

#Convert coordinates into keys
originalCoordinates = dict.fromkeys( calculatedGrid.keys() )
for absoluteCoordinate in originalCoordinates.keys():
    #print calculatedGrid[absoluteCoordinate]
    #Get min depth for block
    individualMinDepth = getMinDepth( minDepthLevel, calculatedGrid[absoluteCoordinate] )
    
    #Find the path down the depth levels
    multiplierList = {0: [], 1: [], 2: []}
    for key in multiplierList.keys():
        maxMultiplier = pow( 2, octreeData["Depth"] )
        totalMultiplier = 0
        while maxMultiplier > pow( 2, individualMinDepth )*0.9:
            #Detect if it should be positive or negative
            currentMultiplier = maxMultiplier
            if absoluteCoordinate[key] > totalMultiplier:
                multiplierList[key].append( 1 )
            elif absoluteCoordinate[key] < totalMultiplier:
                multiplierList[key].append( -1 )
                currentMultiplier *= -1
            else:
                multiplierList[key].append( 1 )
                #print "Something is wrong, coordinate value is even"
            #Append to total
            totalMultiplier += currentMultiplier
            maxMultiplier /= 2.0
            
    originalCoordinates[absoluteCoordinate] = multiplierList
    
print "{}: Converted coordinates into octree format".format( TimeOutput( st, time.time() ) )
    
#Write into dictionary
pathsChanged = set()
for relativeCoordinate in originalCoordinates:
    
    pathsToSimplify = set()
    
    #Get the coordinates for each depth level
    relativeValues = originalCoordinates[relativeCoordinate]
    relativeCoordinates = zip( relativeValues[0], relativeValues[1], relativeValues[2] )
    
    #Get ID
    blockInfo = calculatedGrid[relativeCoordinate]
    infoType = type( blockInfo )
    try:
        if infoType in ( float, int, str ):
            blockID = int( blockInfo )
        else :
            blockID = blockInfo[0]
    except:
        blockID = 0
        
    individualMinDepth = getMinDepth( minDepthLevel, calculatedGrid[relativeCoordinate] )
    
    #Fill recursively with ID
    dictionaryFix = [("Nodes")]*( len( relativeCoordinates )*2 )
    dictionaryFix[1::2] = relativeCoordinates
    #print "Block info: {}".format(blockInfo)
    #Figure out if something already exists
    oldDictionaryValue = dictionaryFix
    while oldDictionaryValue:
        try:
            oldValue = reduce( dict.__getitem__, oldDictionaryValue, octreeData )
        except:
            oldDictionaryValue = oldDictionaryValue[:-2]
        else:
            #Only do something if it's not 0 and is an integer (if dictionary, it's gone up to the maximum depth)
            if oldValue and type( oldValue ) == int:
                
                #print oldValue, oldDictionaryValue
                #print dictionaryFix
                for dictionaryValueToFix in recursiveList( [oldDictionaryValue], octreeStructure, len( dictionaryFix ), True ):
                    #Update dictionary if at the correct length
                    if len(dictionaryValueToFix) == len(dictionaryFix):
                        editDictionary( octreeData, dictionaryValueToFix+[oldValue] )
                        #Append to list to simplify after
                        pathsToSimplify.update( [tuple( dictionaryValueToFix[:-1] )] )
                        pathsChanged.update( [tuple( dictionaryValueToFix[:-1] )] )
                    editDictionary( octreeData, dictionaryValueToFix[:-2]+["Depth",octreeData["Depth"]-len( dictionaryValueToFix )/2+1], False )

            break
    
    pathsChanged.update( [tuple( dictionaryFix[:-1] )] )
    dictionaryFix.append( blockID )
    editDictionary( octreeData, dictionaryFix )
    
    #Fill extra values
    currentDepth = 0
    maxDepth = octreeData["Depth"]-individualMinDepth
    depthDictionaryPath = dictionaryFix[:-1]
    while currentDepth < maxDepth:
        #Fill empty values with 0
        currentDictionaryDepth = reduce( dict.__getitem__, depthDictionaryPath[:-1-currentDepth*2], octreeData )
        for i in octreeStructure:
            if currentDictionaryDepth.get( i, None ) == None:
                #currentDictionaryDepth[i] = 0
                editDictionary( octreeData, depthDictionaryPath[:-1-currentDepth*2]+[i, 0], False )
                
        #Fill in depth
        editDictionary( octreeData, depthDictionaryPath[:-2-currentDepth*2]+["Depth", currentDepth+individualMinDepth], False )
        currentDepth += 1
    
    #Move up a level if all values are 1
    pathsToSimplify.update( [tuple( dictionaryFix[:-2] )] )
    for dictionaryPath in [list( x ) for x in pathsToSimplify]:
        while True:
            allValuesAtDepth = reduce( dict.__getitem__, dictionaryPath, octreeData )
            allPointValues = [allValuesAtDepth.get( coordinate, None ) for coordinate in octreeStructure]
            everythingIsPoint = all( x == allPointValues[0] and str( x ).isdigit() for x in allPointValues )
            if everythingIsPoint:
                editDictionary( octreeData, dictionaryPath[:-1]+[allPointValues[0]] )
                dictionaryPath = dictionaryPath[:-2]
            else:
                break
       
print "{}: Wrote into octree".format( TimeOutput( st, time.time() ) )

#Calculate level of detail information for octree
def summariseLOD( dictionaryName ):
    LODValue = []
    LODRecursionValue = []
    for i in dictionaryName["Nodes"].keys():
        try:
            existingDataValue = dictionaryName["Nodes"][i].get( "Data", None )
        except:
            LODValue.append( dictionaryName["Nodes"][i] )
        else:
            if existingDataValue == None:
                #Node is a dictionary
                LODRecursionValue.append( summariseLOD( dictionaryName["Nodes"][i] ) )
            else:
                #Node is an ID
                LODValue.append( existingDataValue )
    
    valueMode = []           
    if LODValue:
        valueCounter = Counter( LODValue ).most_common()
        valueMode = [i[0] for i in valueCounter if i[1] == valueCounter[0][1]]
            
    for recursionValue in LODRecursionValue:
        if LODValue:
            
            #Find if any of the values in the recursion match the highest values in LODValue
            if any( i in recursionValue for i in valueMode ):
                LODValue += valueMode
                recursionValue = []
        
        #Add the most common value to the list if there were no matches
        if recursionValue:
            LODValue += [Counter( recursionValue ).most_common(1)[0][0]]
    
    dictionaryName["Data"] = Counter( LODValue ).most_common(1)[0][0]
    return LODValue
 
summariseLOD( octreeData )

print "{}: Calculated level of detail".format( TimeOutput( st, time.time() ) )

#Calculate points
def formatOctree( dictionaryValue, minDepthLevel, absoluteMinDepth=None, startingCoordinates=[0, 0, 0] ):
    
    allPoints = {}
    currentDepth = dictionaryValue["Depth"]
    depthMultiplier = pow( 2, currentDepth )
    #Amount to add to the position, addToNegative to connect at the axis
    addToNegative = 0
    if minDepthLevel > 0:
        addToNegative = 1-pow( 2, ( minDepthLevel ) )
        addAmount = 1-pow( 2, ( minDepthLevel-1 ) )
    else:
        depthIncrement = minDepthLevel+1
        addAmount = pow( 2, minDepthLevel )/2.0 
        while depthIncrement < 0:
            addAmount += pow( 2, depthIncrement )/2.0
            depthIncrement += 1
    differenceInDepth = currentDepth-minDepthLevel

    #Fix for things separating on the axis if using LOD values
    movementAppendAmount = 0
    if absoluteMinDepth != None and absoluteMinDepth > minDepthLevel:
        movementAppendAmount = pow( 2, minDepthLevel )/2.0
        if absoluteMinDepth-1 != minDepthLevel:
            movementAppendAmount = -movementAppendAmount
            
                
    for key in dictionaryValue["Nodes"].keys():
        newCoordinate = [depthMultiplier*i for i in key]
        newCoordinate[0] += startingCoordinates[0]
        newCoordinate[1] += startingCoordinates[1]
        newCoordinate[2] += startingCoordinates[2]
        newDictionaryValue = dictionaryValue["Nodes"][key]
        
        if newDictionaryValue:
            
            valueID = None
            if type( newDictionaryValue ) == dict:
                #Don't look below the minimum depth
                if newDictionaryValue["Depth"] < absoluteMinDepth and absoluteMinDepth != None:
                    valueID = newDictionaryValue["Data"]
                else:
                    #Recursively loop down
                    allPoints.update( formatOctree( newDictionaryValue, minDepthLevel, absoluteMinDepth, newCoordinate ) )
                    valueID = None
            elif str( newDictionaryValue ).isdigit():
                #If it's a number
                valueID = newDictionaryValue
            
                
            if valueID:
                
                cubeSize = 2**currentDepth
                #Increment position if conditions are met
                if ( currentDepth and minDepthLevel >= 0 ) or ( currentDepth <= 0 and minDepthLevel < 0 ):
                    moveCubeAmount = addAmount
                    
                #Fix for strange behaviour when minDepthLevel = -1
                elif differenceInDepth > 0:
                    moveCubeAmount = 1
                    #Fix for stranger behaviour when it's also a big generation
                    if differenceInDepth > 1:
                        moveCubeAmount -= 0.25
                else:
                    moveCubeAmount = 0
                
                    
                totalMovement = tuple( x+(movementAppendAmount-addToNegative if x<0 else -movementAppendAmount) for x in ( ( i+(1 if i<0 else -1) )/2+moveCubeAmount for i in newCoordinate ) )
                
                allPoints[totalMovement] = [cubeSize, valueID]
                
    return allPoints

newList = formatOctree( octreeData, minDepthLevel, 1 )

print "{}: Formatted octree into usable points".format( TimeOutput( st, time.time() ) )
import zlib, base64, cPickle
with open( "C:/test.txt", "w" ) as txt:
    txt.write( cPickle.dumps( newList ) )

if True:
    for coordinates in newList.keys():
        cubeSize = newList[coordinates][0]
        blockID = newList[coordinates][1]
        newCube = pm.polyCube( h=cubeSize, w=cubeSize, d=cubeSize )[0]
        pm.move( newCube, coordinates )
        pm.addAttr( newCube, shortName = 'id', longName = "blockID" , attributeType = "byte" )
        pm.setAttr( "{0}.id".format( newCube ), blockID )

    print "{}: Drew cubes".format( TimeOutput( st, time.time() ) )


inputLength = len( cPickle.dumps( grid ) )
octreeLength = len( cPickle.dumps( octreeData ) )
print "Length of input:  {0}".format( inputLength )
print "Length of octree: {0}".format( octreeLength )
print "{0}% efficiency".format( round( float( inputLength )/octreeLength, 2 )*100 )
print "Length of output:  {0}".format( len( cPickle.dumps( newList ) ) )

