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


import random
maxNum = 30
minNum = 0
exponentialNum = 0.5
grid = {}
for i in range( 400 ):
    x = int(random.randint(minNum,maxNum)**exponentialNum)
    y = int(random.randint(minNum,maxNum)**exponentialNum)
    z = int(random.randint(minNum,maxNum)**exponentialNum)
    grid[(x,y,z)] = 1
    
minDepthLevel = 0

#Convert to new format that gets rid of even values
def convertCoordinates( dictionaryName, minDepthLevel=0 ):
    newDictionary = {}
    addAmount = pow( 2, minDepthLevel )
    for coordinate in dictionaryName.keys():
        newDictionary[tuple( i*2+addAmount for i in coordinate )] = dictionaryName[coordinate]
    return newDictionary
grid = convertCoordinates( grid, minDepthLevel )

#Get maximum depth level
xMax = max( grid.keys(), key=itemgetter( 0 ) )[0]
xMin = min( grid.keys(), key=itemgetter( 0 ) )[0]
yMax = max( grid.keys(), key=itemgetter( 1 ) )[1]
yMin = min( grid.keys(), key=itemgetter( 1 ) )[1]
zMax = max( grid.keys(), key=itemgetter( 2 ) )[2]
zMin = min( grid.keys(), key=itemgetter( 2 ) )[2]
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


originalCoordinates = dict.fromkeys( grid.keys() )
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
    dictionaryFix.append( grid[relativeCoordinate] )
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


#Calculate placement of cubes
def drawCubes( dictionaryValue, minDepthLevel=0, startingCoordinates=[0, 0, 0] ):
    currentDepth = dictionaryValue["Depth"]
    depthMultiplier = pow( 2, currentDepth )
    #Amount to add to the movement of a cube
    depthIncrement = minDepthLevel+1
    addAmount = pow( 2, minDepthLevel )/2.0
    while depthIncrement < 0:
        addAmount += pow( 2, depthIncrement )/2.0
        depthIncrement += 1
    for key in dictionaryValue["Data"].keys():
        newCoordinate = [depthMultiplier*i for i in key]
        newCoordinate[0] += startingCoordinates[0]
        newCoordinate[1] += startingCoordinates[1]
        newCoordinate[2] += startingCoordinates[2]
        #newCoordinate = [x+y+z for x, y, z in zip( newCoordinate, startingCoordinates )]
        newDictionaryValue = dictionaryValue["Data"][key]
        if newDictionaryValue and str( newDictionaryValue ).isdigit():
            cubeSize = 2**currentDepth
            newCube = py.polyCube( h=cubeSize, w=cubeSize, d=cubeSize )[0]
            moveCubeAmount = 0
            #Increment move amount if conditions are met
            if ( currentDepth and minDepthLevel >= 0 ) or ( currentDepth <= 0 and minDepthLevel < 0 ):
                moveCubeAmount = addAmount
            py.move( newCube, [(i-1)/2+moveCubeAmount for i in newCoordinate] )
            py.addAttr( newCube, shortName = 'id', longName = "blockID", attributeType = "byte" )
            py.setAttr( "{0}.id".format( newCube ), newDictionaryValue )
        elif type( newDictionaryValue ) == dict:
            drawCubes( newDictionaryValue, minDepthLevel, newCoordinate )



#Use test value for a bigger cube
#editDictionary( octreeData, ["Data",(-1,-1,-1),1] )
drawCubes( octreeData, minDepthLevel )
