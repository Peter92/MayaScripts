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
        
class roundToMultiple:
    def __init__( self, multiple, *args ):
        self.returnList = []
        self.multiple = int( multiple )
        self.args = args
        self.mathFunction = math.ceil
    def up( self ):
        return self.round()
    def down( self ):
        self.mathFunction = math.floor
        return self.round()
    def round( self ):
        for n in self.args:
            self.returnList.append( int( self.mathFunction( n/float( self.multiple ) )*self.multiple ) )
        return self.returnList


grid = {}
grid[(0,0)] = 1
grid[(3,-1)] = 1
grid[(9, -2)] = 1

#Convert to octree
xMax = max( grid.keys(), key=itemgetter( 0 ) )[0]
xMin = min( grid.keys(), key=itemgetter( 0 ) )[0]
yMax = max( grid.keys(), key=itemgetter( 1 ) )[1]
yMin = min( grid.keys(), key=itemgetter( 1 ) )[1]
    
#Get maximum depth level
minRange = roundToMultiple( 8, xMin, yMin ).down()
maxRange = roundToMultiple( 8, xMax, yMax ).up()
mainDepthLevel = max( [abs( i ) for i in minRange+maxRange] )
mainDepthLevel = int( math.log( mainDepthLevel/2, 2 ) )
minDepthLevel = -2 #0 has accuracy of 1, -1 of 0.5 etc

#Start octree dictionary
octreeStructure = [( 1, 1 ), ( 1, -1 ), ( -1, 1 ), ( -1, -1 )]
octreeDepthName = "Depth"
octreeDataName = "Data"
octreeData = {"Depth":mainDepthLevel, "Data": dict.fromkeys( octreeStructure, False )}


#originalCoordinates = dict.fromkeys( [tuple( x+0.5 for x in i ) for i in grid.keys()] )
originalCoordinates = dict.fromkeys( grid.keys() )
for relativeCoordinate in originalCoordinates.keys():
    multiplierList = {0: [], 1: []}
    for key in multiplierList:
        maxMultiplier = ( mainDepthLevel-1 )*4
        totalMultiplier = 0
        while maxMultiplier > pow( 2, minDepthLevel )*0.9:
            currentDepthIteration += 1
            #Detect if it should be positive or negative
            currentMultiplier = maxMultiplier
            
            if relativeCoordinate[key] >= totalMultiplier:
                multiplierList[key].append( 1 )
            else:
                multiplierList[key].append( -1 )
                currentMultiplier *= -1
            #Append to total
            totalMultiplier += currentMultiplier
            maxMultiplier /= 2.0
            
    originalCoordinates[relativeCoordinate] = multiplierList


#Write into dictionary
for relativeCoordinate in originalCoordinates:
    
    #Get the coordinates for each depth level
    relativeValues = originalCoordinates[relativeCoordinate]
    relativeCoordinates = zip( relativeValues[0], relativeValues[1] )
    
    #Fill with True
    dictionaryFix = [("Data")]*( len( relativeCoordinates )*2 )
    dictionaryFix[1::2] = relativeCoordinates
    dictionaryFix.append( 1 )
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
