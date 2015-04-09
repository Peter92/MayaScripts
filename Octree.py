'''
Info
 - Set ID to 0 to remove block, dictionary will automatically clean
 - Range is -(2^depth)/2-1 to (2^depth)/2 (eg. -256 to 255)
 
 - Point3D and Cube class from mkrieger
'''
from codeStuff import TimeOutput
from pprint import PrettyPrinter
pp = PrettyPrinter().pprint
from collections import Counter
import pymel.core as pm
import math, sys, decimal
from operator import itemgetter
from itertools import product
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
    #Fix if list is only 1 item long
    if len( listOfValues ) < 2:
        return False
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

class Point3D:
    """Representation of a point in 3D space."""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        """Add two points.

        >>> Point3D(1, 2, 3) + Point3D(100, 200, 300)
        Point3D(101, 202, 303)
        """
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point3D(x, y, z)

    def __mul__(self, a):
        """Multiply a point with a number.

        >>> Point3D(1, 2, 3) * 2
        Point3D(2, 4, 6)
        """
        x = self.x * a
        y = self.y * a
        z = self.z * a
        return Point3D(x, y, z)

    def __rmul__(self, a):
        """Multiply a number with a point.

        >>> 2 * Point3D(1, 2, 3)
        Point3D(2, 4, 6)
        """
        return self.__mul__(a)

    def __repr__(self):
        return 'Point3D({p.x}, {p.y}, {p.z})'.format(p=self)
        


class Cube:
    """Representation of a cube."""

    #Directions to all eight corners of a cube
    DIR = [Point3D(*s) for s in product([-1, +1], repeat=3)]

    def __init__(self, center, depth=0):
        if not isinstance(center, Point3D):
            center = Point3D(*center)
        self.center = center
        self.depth = depth

    def __repr__(self):
        return 'Cube(center={c.center}, depth={c.depth})'.format(c=self)

    def _divide(self):
        """Divide into eight cubes of half the size and one level deeper."""
        c = self.center
        a = pow( 2, self.depth )/2.0
        d = self.depth - 1
        return [Cube(c + a/2.0*e, d) for e in Cube.DIR]

    def divide(self, target_depth=0):
        """Recursively divide down to the given depth and return a list of
        all 8^d cubes, where d is the difference between the depth of the
        cube and the target depth, or 0 if the depth of the cube is already
        equal to or less than the target depth.

        >>> c = Cube(center=(0, 0, 0), size=2, depth=1)
        >>> len(c.divide(0))
        8
        >>> len(c.divide(-1))
        64
        >>> c.divide(5)[0] is c
        True
        >>> c.divide(-1)[0].size
        0.5
        """
        if self.depth <= target_depth:
            return [self]
        smaller_cubes = self._divide()
        return [c for s in smaller_cubes for c in s.divide(target_depth)]
    
#pp().pprint(octreeData)
grid = {}
grid[(-1,0,0)] = 1
grid[(0,0,0)] = 1
grid[(1,0,0)] = 1
grid[(0,0,1)] = 1
grid[(1,0,1)] = 1
grid[(0,1,0)] = 1
grid[(0,1,1)] = 1
grid[(1,1,0)] = 1
grid[(1,1,1)] = 1

grid[(2,1,1)] = 5
grid[(10,0,-3)] = [1,1]

grid[(3,0,-1)] = 1
grid[(2,1,0)] = 1
grid[(2,0,1)] = 1
grid[(2,0,0)] = 1
grid[(3,1,1)] = 1
grid[(3,1,0)] = 1
grid[(3,0,1)] = 1
grid[(3,0,0)] = 5 #To demonstrate blocks not grouping if different ID
num = 4
num2 = -1
for x in range( -num, num2+1 ):
    for y in range( -num, num2+1 ):
        for z in range( -num, num2+1 ):
            grid[(x,y,z)] = [1,0]
            


grid = grid2
minDepthLevel = -1
maxDepthGrouping = 100000

import time
st = time.time()


#Convert to new format that gets rid of even values
def convertCoordinates( dictionaryName, minDepthLevel=0 ):
    newDictionary = {}
    addAmount = pow( 2, minDepthLevel )
    addAmount = Point3D( addAmount, addAmount, addAmount )
    
    for coordinate in dictionaryName.keys():
        
        #Get depth if set
        if type( dictionaryName[coordinate] ) == list:
            coordinateID = dictionaryName[coordinate][0]
        else:
            coordinateID = dictionaryName[coordinate]
            
        #newCoordinate = tuple( i*2+addAmount for i in coordinate )
        P3DCoordinate = coordinate*2+addAmount
        newCoordinate = tuple( [P3DCoordinate.x, P3DCoordinate.y, P3DCoordinate.z] )
        newDictionary[newCoordinate] = coordinateID
        
    return newDictionary



def recursiveCoordinate( coordinate, coordinateInfo, minDepthLevel, octreeStructure ):
    
    newDictionary = {}
    
    if type( coordinateInfo ) != list:
        coordinateInfo = [coordinateInfo,minDepthLevel]
   
    coordinateDepth = coordinateInfo[1]
    
    if coordinateDepth > minDepthLevel:
        coordinateInfo[1] -= 1
        moveAmount = pow( 2, minDepthLevel-2 )
        for i in octreeStructure:
            newCoordinate = [i[j]*moveAmount+coordinate[j] for j in xrange( 3 )]
            newDictionary.update( recursiveCoordinate( newCoordinate, coordinateInfo, minDepthLevel, octreeStructure ) )
            
    else:
        newDictionary[tuple( coordinate )] = coordinateInfo
    
    return newDictionary

newGrid = {}
for coordinate in grid:
    try:
        if type( grid[coordinate] ) == list:
            cubeID = grid[coordinate][0]
            cubeDepth = grid[coordinate][1]
        else:
            cubeID = grid[coordinate]
            cubeDepth = minDepthLevel
    except:
        cubeID = 0
        cubeDepth = minDepthLevel
    
    #Round to the nearest point and floor if the depth level is lower than min depth level
    #Fixes if cube exactly matches octree but is the wrong depth, as it would think there was an extra layer
    nearestRound = 1/pow( 2.0, minDepthLevel )
    coordinate = [math.floor( x*nearestRound )/nearestRound for x in coordinate]
    
    Point3DGrid = {c.center: [cubeID, minDepthLevel] for c in Cube( coordinate, cubeDepth ).divide( minDepthLevel )}
    newGrid.update( Point3DGrid )
    
    #newGrid.update( recursiveCoordinate( coordinate, grid[coordinate], minDepthLevel, octreeStructure ) )
print "Number of points calculated: {0}".format( len( newGrid.keys() ) )

calculatedGrid = convertCoordinates( newGrid, minDepthLevel )
#calculatedGrid = grid

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
            
octreeData = {"Depth": maxDepthLevel, "Nodes": dict.fromkeys( octreeStructure, 0 ), "Data": 0, "Counter": 0}


print "{}: Created octree".format( TimeOutput( st, time.time() ) )

#Convert coordinates into keys
originalCoordinates = dict.fromkeys( calculatedGrid.keys() )
for absoluteCoordinate in originalCoordinates.keys():
    
    #Find the path down the depth levels
    multiplierList = {0: [], 1: [], 2: []}
    for key in multiplierList.keys():
        maxMultiplier = pow( 2, octreeData["Depth"] )
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
                #If it is neither, negative should hopefully stop potential errors
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
                        
                    inputDepth = octreeData["Depth"]-len( dictionaryValueToFix )/2+1
                    editDictionary( octreeData, dictionaryValueToFix[:-2]+["Depth",inputDepth], False )

            break
    
    pathsChanged.update( [tuple( dictionaryFix[:-1] )] )
    dictionaryFix.append( blockID )
    editDictionary( octreeData, dictionaryFix )
    
    #Fill extra values
    currentDepth = 0
    maxDepth = octreeData["Depth"]-minDepthLevel
    depthDictionaryPath = dictionaryFix[:-1]
    while currentDepth < maxDepth:
        #Fill empty values with 0
        currentDictionaryDepth = reduce( dict.__getitem__, depthDictionaryPath[:-1-currentDepth*2], octreeData )
        for i in octreeStructure:
            if currentDictionaryDepth.get( i, None ) == None:
                #currentDictionaryDepth[i] = 0
                editDictionary( octreeData, depthDictionaryPath[:-1-currentDepth*2]+[i, 0], False )
                
        #Fill in depth
        editDictionary( octreeData, depthDictionaryPath[:-2-currentDepth*2]+["Depth", currentDepth+minDepthLevel], False )
        currentDepth += 1
    
    #Move up a level if all values are 1
    pathsToSimplify.update( [tuple( dictionaryFix[:-2] )] )
    for dictionaryPath in [list( x ) for x in pathsToSimplify]:
        
        
        while True:
            
            #Get all values
            allValuesAtDepth = reduce( dict.__getitem__, dictionaryPath[:-1], octreeData )
            allPointValues = [allValuesAtDepth["Nodes"].get( coordinate, None ) for coordinate in octreeStructure]
            
            #Find if all 8 coordinates are the same
            everythingIsPoint = all( x == allPointValues[0] for x in allPointValues ) and str( allPointValues[0] ).isdigit()
            
            #Find current depth as to not group past the max amount
            currentDepth = allValuesAtDepth["Depth"]
            
            if everythingIsPoint and currentDepth < maxDepthGrouping:
                
                #Edit dictionary
                editDictionary( octreeData, dictionaryPath[:-1]+[allPointValues[0]] )
                dictionaryPath = dictionaryPath[:-2]
                
            else:
                
                #Can no longer group
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
def formatOctree( dictionaryValue, minDepthLevel, absoluteMinDepth=None, startingCoordinates=( 0, 0, 0 ) ):
        
    #Get dictionary information
    allPoints = {}
    currentDepth = dictionaryValue["Depth"]
    
    cubeSize = pow( 2, currentDepth )
    depthMultiplier = pow( 2, currentDepth )
    
    #Set value to reverse the original coordinate conversion
    if not currentDepth:
        addAmount = 0
    else:
        if minDepthLevel > 0:
            addAmount = -pow( 2, ( minDepthLevel-1 ) )
        elif currentDepth > 0:
            addAmount = -0.5
        #Fix for everything being offset by 0.5 when min depth level is anything under 0
        elif minDepthLevel < 0:
            addAmount = -0.5
        else:
            addAmount = -pow( 2, minDepthLevel-1 )
            
    for coordinate in dictionaryValue["Nodes"]:
        nodeData = dictionaryValue["Nodes"].get( coordinate, 0 )
        
        #Calculate new coordinates
        newCoordinate = [depthMultiplier*i for i in coordinate]
        newCoordinate = tuple( newCoordinate[i]+startingCoordinates[i] for i in xrange( 3 ) )
        
        #Detect what type nodeData is
        if type( nodeData ) == dict:
            
            #Don't look below the minimum depth
            if nodeData["Depth"] < absoluteMinDepth and absoluteMinDepth != None:
                valueID = nodeData["Data"]
            else:
                #Recursively loop down
                newDictionaryValue = dictionaryValue["Nodes"][coordinate]
                allPoints.update( formatOctree( newDictionaryValue, minDepthLevel, absoluteMinDepth, newCoordinate ) )
                valueID = None
                
        else:
            valueID = nodeData
            
        #Add to list
        if valueID:
            totalMovement = tuple( i/2+addAmount for i in newCoordinate )
            #totalMovement = tuple( i/2+addAmount*(1 if i<0 else 1) for i in newCoordinate )
            allPoints[totalMovement] = [valueID, currentDepth]
        
    return allPoints
    
    
newList = formatOctree( octreeData, minDepthLevel )
#newList = {}
print "{}: Formatted octree into usable points".format( TimeOutput( st, time.time() ) )
import zlib, base64, cPickle
with open( "C:/test.txt", "w" ) as txt:
    txt.write( cPickle.dumps( newList ) )

if True:
    for coordinates in newList.keys():
        blockID, depthLevel = newList[coordinates]
        cubeSize = pow( 2, depthLevel )
        newCube = pm.polyCube( h=cubeSize, w=cubeSize, d=cubeSize )[0]
        pm.move( newCube, coordinates )
        pm.addAttr( newCube, shortName = 'id', longName = "blockID" , attributeType = "byte" )
        pm.setAttr( "{}.id".format( newCube ), blockID )
        pm.polyEditUV( '{}.map[:]'.format( newCube ), su=cubeSize*6, sv=cubeSize*8 )

    print "{}: Drew cubes".format( TimeOutput( st, time.time() ) )

inputLength = len( cPickle.dumps( grid ) )
octreeLength = len( cPickle.dumps( octreeData ) )
print "Length of input:  {0}".format( inputLength )
print "Length of octree: {0}".format( octreeLength )
print "{0}% efficiency".format( round( float( inputLength )/octreeLength, 2 )*100 )
print "Length of output:  {0}".format( len( cPickle.dumps( newList ) ) )
print "Max depth: {0}".format( octreeData["Depth"] )

