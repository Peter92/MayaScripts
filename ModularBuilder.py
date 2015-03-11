import pymel.core as py
import random as rd
import ast
global tempConnectorName
global connectorStoreName
global precision
locationPrecision = 3
tempConnectorName = 'doorLocator'
connectorStoreName = 'ConnectorList'

'''
To do:
    Nearest neighbour remove
    Update chance
    Object centric deletion
    Rest of code

'''

'''
Data structure:
connectionList[VALUE] = All connections
connectionList[VALUE][0] = All objects in connection
connectionList[VALUE][0][OBJECT] = Individual object info
connectionList[VALUE][0][OBJECT][0] = Object name
connectionList[VALUE][0][OBJECT][1] = Object connection info
connectionList[VALUE][0][OBJECT][1][CONNECTION] = Object connection position info
connectionList[VALUE][0][OBJECT][1][CONNECTION][0] = Object connection location
connectionList[VALUE][0][OBJECT][1][CONNECTION][0][0] = X Object connection location
connectionList[VALUE][0][OBJECT][1][CONNECTION][0][1] = Y Object connection location
connectionList[VALUE][0][OBJECT][1][CONNECTION][0][2] = Z Object connection location
connectionList[VALUE][0][OBJECT][1][CONNECTION][1] = Object connection rotation
connectionList[VALUE][0][OBJECT][1][CONNECTION][1][0] = X Object connection rotation
connectionList[VALUE][0][OBJECT][1][CONNECTION][1][1] = Y Object connection rotation
connectionList[VALUE][0][OBJECT][1][CONNECTION][1][2] = Z Object connection rotation
connectionList[VALUE][0][OBJECT][1][CONNECTION][2] = Object connection size
connectionList[VALUE][0][OBJECT][1][CONNECTION][2][0] = X Object connection size
connectionList[VALUE][0][OBJECT][1][CONNECTION][2][1] = Y Object connection size
connectionList[VALUE][0][OBJECT][1][CONNECTION][2][2] = Z Object connection size
connectionList[VALUE][0][OBJECT][1][CONNECTION][-1] = Individual chance
connectionList[VALUE][0][OBJECT][-1] = Object chance
connectionList[VALUE][-1] = Connection Chance
'''

class selection:
    #AddToSelection
    @classmethod
    def add( self, connectorName, objectInfo, checkConnection ):
        connectionExists = checkConnection[0]
        matchingObjectsIndex = checkConnection[1]
        if connectionExists == False:
            connectionList = infoStore( connectorStoreName )
            #Append to already existing object or create object
            if matchingObjectsIndex >= 0:
                print connectionList[connectorName][0][matchingObjectsIndex][1]
                connectionList[connectorName][0][matchingObjectsIndex][1].append( objectInfo[1][0] )
            else:
                connectionList[connectorName][0].append( objectInfo )
            infoStore( connectorStoreName, connectionList )
            return "Success!"
        else:
            return "Connection already exists here!"
    
    #Remove item from selection
    @classmethod
    def remove( self, connectorName, removeValues, checkConnection, indexValues = -1 ):
        connectionExists = checkConnection[0]
        connectionList = infoStore( connectorStoreName )
        
        #Detect if a certain point is chosen to be removed or if the current position is
        if indexValues != -1:
            connectorName = indexValues[0]
            objectIndex = indexValues[1]
            connectionIndex = indexValues[2]
            #Stop non existing connectors crashing code
            try:
                connectionList[connectorName]
            except:
                connectionList[connectorName] = [ [["temp",[[0,0,0]],0]],0]
            #Translate the index values to their respective items
            objectName = connectionList[connectorName][0][objectIndex][0]
            objectLocation = connectionList[connectorName][0][objectIndex][1][connectionIndex][0]
            objectRotation = connectionList[connectorName][0][objectIndex][1][connectionIndex][1] 
        else:
            #Use the main values
            objectName = removeValues[0]
            objectLocation = removeValues[1][0][0]
            objectRotation = removeValues[1][0][1]
            
        if connectionExists == True:
            numConnectedObjects = len( connectionList[connectorName][0] )
            #Iterate through each object
            for i in range( numConnectedObjects ):
                if objectName == connectionList[connectorName][0][i][0]:
                    numConnections = len( connectionList[connectorName][0][i][1] )
                    #Iterate through each connection
                    for j in range( numConnections ):
                        matchingLocation = connectionList[connectorName][0][i][1][j][0]
                        matchingRotation = connectionList[connectorName][0][i][1][j][1]
                        #Detect which is the clash
                        if objectLocation == matchingLocation and objectRotation == matchingRotation:
                            #Remove individual connection if there is more than one
                            if numConnections > 1:
                                connectionList[connectorName][0][i][1].remove( connectionList[connectorName][0][i][1][j] )
                                infoStore( connectorStoreName, connectionList )
                                return "Success!"
                            else:
                                #Remove whole object if there are no more connections
                                if numConnectedObjects > 1:
                                    connectionList[connectorName][0].remove( connectionList[connectorName][0][i] )
                                    infoStore( connectorStoreName, connectionList )
                                    return "Success!"
                                #Remove whole connector if there are no more objects
                                else:
                                    del connectionList[connectorName]
                                    infoStore( connectorStoreNameconnectorStoreName, connectionList )
                                    return "Success!"
            return "Something went wrong, connection was not deleted."
        return "Connection doesn't exist here yet!"
        
    #Check if connection already exists
    @classmethod
    def exists( self, connectorName, chanceList, objectInfoList ):
        connectionExists = False
        matchingObjectsIndex = -1
        connectionList = infoStore( connectorStoreName )
        #Get values from chance list
        updateChance = chanceList[0]
        chanceOfIndividual = chanceList[1]
        chanceOfObject = chanceList[2]
        chanceOfConnection = chanceList[3]
        #Adjust chance if already exists
        if updateChance == True:
            if connectionList[connectorName][-1] != chanceOfConnection:
                connectionList[connectorName][-1] = chanceOfConnection
        #Iterate through each object for the selected connection(s)
        for i in range( len( connectionList[connectorName][0] ) ):
            #Find if object matches
            if connectionList[connectorName][0][i][0] == objectName:
                matchingObjectsIndex = i
                #Adjust chance if already exists
                if updateChance == True:
                    if connectionList[connectorName][0][i][-1] != chanceOfObject:
                        connectionList[connectorName][0][i][-1] = chanceOfObject
                #Iterate for each connection belonging to the object
                for j in range( len( connectionList[connectorName][0][i][1] ) ):
                    matchingLocation = connectionList[connectorName][0][i][1][j][0]
                    matchingRotation = connectionList[connectorName][0][i][1][j][1]
                    #Detect if connection exists
                    if objectLocation == matchingLocation and objectRotation == matchingRotation:
                        connectionExists = True
                        #Adjust chance if already exists
                        if updateChance == True:
                            if connectionList[connectorName][0][i][1][j][-1] != chanceOfIndividual:
                                connectionList[connectorName][0][i][1][j][-1] = chanceOfIndividual
                        break
        infoStore( connectorStoreName, connectionList )
        return [connectionExists, matchingObjectsIndex]

#Compress something for input/output
class compress:
    #Only import if needed
    import base64
    import zlib
    #Compress value
    @classmethod
    def compress( self, value ):
        return self.base64.b64encode( self.zlib.compress( str( value ), 9 ) )
    #Decompress value
    @classmethod
    def decompress( self, value ):
        return self.zlib.decompress( self.base64.b64decode( value ) )

class tempConnector:
    #Check if temporary connector exists
    @classmethod
    def check( self ):  
        try:
            connectorSelection = py.ls( tempConnectorName )[0]
            return True
        except:
            return False
    #Get size of connector
    @classmethod
    def size( self ):
        connectorRotation = position.get( tempConnectorName )[1]
        py.rotate( tempConnectorName, ( 0, 0, 0 ) )
        connectorBoundingBox = py.ls( tempConnectorName )[0].getBoundingBox()
        py.rotate( tempConnectorName, connectorRotation )
        connectorWidth = round( connectorBoundingBox.width(), locationPrecision )
        connectorHeight = round( connectorBoundingBox.height(), locationPrecision )
        connectorDepth = round( connectorBoundingBox.depth()/3.625, locationPrecision )
        return [ connectorWidth, connectorHeight, connectorDepth ]
    
    #(Re)create connector
    @classmethod
    def create( self, startLocation = [0,0,0] ):
        try:
            py.delete( tempConnectorName )
        except:
            pass
        py.polyCube( n = tempConnectorName, height = 100, width = 100, depth = 10, subdivisionsWidth = 3, subdivisionsHeight = 3 )
        py.setAttr( tempConnectorName + '.rz', lock = True, keyable = False, channelBox = False )
        py.scale( tempConnectorName + '.f[4]', ( 0.25, 0.25, 0.25 ) )
        py.polyExtrudeFacet( tempConnectorName + '.f[4]', localTranslateZ = 10 )
        py.polyExtrudeFacet( tempConnectorName + '.f[4]', localScale = ( 1.25, 1.25, 1.25 ) )
        py.polyExtrudeFacet( tempConnectorName + '.f[4]', localTranslateZ = 20 )
        py.scale( tempConnectorName + '.f[4]', ( 0, 0, 1 ) )
        py.polyExtrudeFacet( tempConnectorName + '.f[32]', localScale = ( 0.3, 0.27, 1 ) )
        py.polyExtrudeFacet( tempConnectorName + '.f[32]', localTranslateZ = 3 )
        py.polyExtrudeFacet( tempConnectorName + '.f[32]', localScale = ( 1.25, 1.25, 1.25 ) )
        py.polyExtrudeFacet( tempConnectorName + '.f[32]', localTranslateZ = 5 )
        py.scale( tempConnectorName + '.f[32]', ( 0, 1, 0 ) )
        py.move( tempConnectorName + '.f[32]', ( 0, 0, 6.15 ), r = True )
        py.xform( tempConnectorName, pivots = ( 0, -50, -5 ) )
        py.move( tempConnectorName, startLocation )
        py.select( tempConnectorName )

#Temporary output
class output:
    #Temporary output
    @classmethod
    def connector( self ):
        connectionList = infoStore( connectorStoreName )
        #Count all percentages
        chanceOfConnectionTotal = 0
        chanceOfObjectTotal = {}
        chanceOfIndividualTotal = {}
        for connectorName in connectionList:
            chanceOfConnectionTotal += connectionList[connectorName][-1]
            chanceOfObjectTotal[connectorName] = 0
            for i in range( len(connectionList[connectorName][0]) ):
                chanceOfObjectTotal[connectorName] += connectionList[connectorName][0][i][-1]
                chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][i][0]] = 0
                for j in range( len( connectionList[connectorName][0][i][1] ) ):
                    chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][i][0]] += connectionList[connectorName][0][i][1][j][-1]
        #Output values
        for connectorName in connectionList:
            connectionPercentage = ( 100 * connectionList[connectorName][-1] ) / chanceOfConnectionTotal
            print connectorName + ": " + str( connectionPercentage ) + "% (" + str(connectionList[connectorName][1]) +  ")"
            for i in range( len(connectionList[connectorName][0]) ):
                objectPercentage = ( 100 * connectionList[connectorName][0][i][-1] ) / chanceOfObjectTotal[connectorName]
                print " " + str( i ) + ": " + str( connectionList[connectorName][0][i][0] ) + ": " + str( objectPercentage ) + "% (" + str( connectionList[connectorName][0][i][-1] ) + ")"
                for j in range( len( connectionList[connectorName][0][i][1] ) ):
                    individualPercentage = ( 100 * connectionList[connectorName][0][i][1][j][-1] ) / chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][i][0]]
                    positionAppend = ""
                    for k in range( len( connectionList[connectorName][0][i][1][j] ) - 1 ):
                        if k!= 0:
                            positionAppend += ", "
                        coordinates = connectionList[connectorName][0][i][1][j][k]
                        positionAppend += str( coordinates )
                    print "  " + str( j ) + ": " + positionAppend + ": " + str( individualPercentage ) + "% (" + str( connectionList[connectorName][0][i][1][j][-1] ) + ")"
    @classmethod
    def object( self ):
        objectList = sortByObject()
        #Count all percentages
        chanceOfConnectionTotal = {}
        chanceOfIndividualTotal = {}
        for objectName in objectList:
            chanceOfConnectionTotal[objectName] = 0
            for i in range( len( objectList[objectName] ) ):
                chanceOfConnectionTotal[objectName] += objectList[objectName][i][-1]
                chanceOfIndividualTotal[objectName + "." + objectList[objectName][i][0]] = 0
                for j in range( len( objectList[objectName][i][1] ) ):
                    chanceOfIndividualTotal[objectName + "." + objectList[objectName][i][0]] += objectList[objectName][i][1][j][-1]
        #Output values
        for objectName in objectList:
            print objectName + ":"
            for i in range( len( objectList[objectName] ) ):
                connectionPercentage = ( 100 * objectList[objectName][i][-1] ) / chanceOfConnectionTotal[objectName]
                print " " + str( i ) + ": " + objectList[objectName][i][0] + ": " + str( connectionPercentage ) + "% (" + str( objectList[objectName][i][-1] ) + ")"
                for j in range( len( objectList[objectName][i][1] ) ):
                    individualPercentage = ( 100 * objectList[objectName][i][1][j][-1] ) / chanceOfIndividualTotal[objectName + "." + objectList[objectName][i][0]]
                    positionAppend = ""
                    for k in range( len( objectList[objectName][i][1][j] ) - 1 ):
                        if k != 0:
                            positionAppend += ", "
                        positionAppend += str( objectList[objectName][i][1][j][k] )
                    print "  " + str( j ) + ": " + str( positionAppend ) + ": " + str( individualPercentage ) + "% (" + str( objectList[objectName][i][1][j][-1] ) + ")"
                    
class position:
    #Return location and rotation of selected object
    @classmethod
    def get( self, objectSelection ):
        #turn string object to transform
        if type( objectSelection ) != py.nodetypes.Transform:
            objectSelection = py.ls( objectSelection )[0]
        objectLocation = objectSelection.getTranslation()
        objectRotation = objectSelection.getRotation()
        return [ objectLocation, objectRotation ]
    #Get connector position relative to selected object
    @classmethod
    def relative( self, objectSelection ):
        objectInfo = self.get( objectSelection )
        connectorInfo = self.get( tempConnectorName )
        finalLocationX = round( connectorInfo[0][0] - objectInfo[0][0], locationPrecision )
        finalLocationY = round( connectorInfo[0][1] - objectInfo[0][1], locationPrecision )
        finalLocationZ = round( connectorInfo[0][2] - objectInfo[0][2], locationPrecision )
        finalRotationX = round( connectorInfo[1][0] - objectInfo[1][0], locationPrecision )
        finalRotationY = round( connectorInfo[1][1] - objectInfo[1][1], locationPrecision )
        finalRotationZ = round( connectorInfo[1][2] - objectInfo[1][2], locationPrecision )
        return [ [finalLocationX, finalLocationY, finalLocationZ], [finalRotationX, finalRotationY, finalRotationZ] ]

def timeOutput(startTime, endTime):
    try:
        formatDecimals
    except:
        formatDecimals = 2
    #calculate decimal points
    if formatDecimals > 0:
        decimals = float( pow( 10, formatDecimals ) )
    else:
        decimals = int( pow( 10, formatDecimals ) )
    #calculate seconds and minutes
    seconds = endTime - startTime
    #cut decimal points off seconds
    secondsDecimal = int(seconds*decimals)/decimals
    #make sure it's correct grammar
    if (formatDecimals == 0) and (secondsDecimal == 1):
        sec = " second"
    else:
        sec = " seconds"
    return str( secondsDecimal ) + sec

def infoStore( storeName, storeValue = False ):
    storeName = str( storeName )
    #Create info store if it doesn't exist
    try:
        py.ls( 'infoStore' )[0]
    except:
        originalSelection = py.ls( selection = True )
        py.spaceLocator( n = 'infoStore' )
        py.addAttr( 'infoStore', shortName = 'progress', longName = 'ProgressBarName', dataType = 'string' )
        py.select( originalSelection )
        py.hide( 'infoStore')
    #Get value from info store or create new attribute
    try:
        storedValue = ast.literal_eval( py.getAttr( 'infoStore.' + storeName ) )
    except:
        py.addAttr( 'infoStore', longName = storeName, dataType = 'string' )
        py.setAttr( 'infoStore.' + storeName, '{}' )
        storedValue = ast.literal_eval( py.getAttr( 'infoStore.' + storeName ) )
    #Write values to info store
    if storeValue != False:
        py.setAttr( 'infoStore.' + storeName, str( storeValue ) )
    return storedValue


#Create dictionary
def initialise( connectorName, objectInfoList ):
    #Find if dictionary exists
    try:
        connectionList = infoStore( connectorStoreName )
    except:
        connectionList = {}
    #Find if dictionary value exists
    try:
        firstRun = False
        connectionList[connectorName]
    except:
        firstRun = True
        connectionList[connectorName] = [[ objectInfoList ], chanceOfConnection]
        infoStore( connectorStoreName, connectionList )
    return firstRun

def sortByObject( originalObjectName = False ):
    connectionList = infoStore( connectorStoreName )
    objectList = {}
    for connection in connectionList:
        for i in range( len(connectionList[connection][0]) ):
            objectName = connectionList[connection][0][i][0]
            if objectName == originalObjectName or originalObjectName == False:
                connectionChance = connectionList[connection][-1]
                addToList = [connection, [], connectionChance]
                try:
                    objectList[objectName].append( addToList )
                except:
                    objectList[objectName] = [ addToList ]
                for j in range( len( connectionList[connection][0][i][1] ) ):
                    objectList[objectName][-1][1].append( connectionList[connection][0][i][1][j] )
    return objectList
    
    
#Adding items
connectorName = 'test'
addToList = True

#Removing items
removeFromList = False
removeCustomPoint = False
removeValues = ['test', 0, 3]

#Set chance
chanceOfIndividual = 50
chanceOfObject = 500
chanceOfConnection = 10
updateChance = True

#Update chance of custom point



if tempConnector.check() == False:
    try:
        startLocation = position.get( py.ls( selection = True )[0] )[0]
        tempConnector.create( startLocation )
    except:
        tempConnector.create()
    #create pCube1 and pCube2
    #infoStore( connectorStoreName, compress.decompress( 'eNqlkb0OwjAMhF8lW5b0ZCdxflh5jKoLUnckyoR4d5xUILGUAstZsaXP58vNLvNlsQczjqM9H6+nma1rj8AoQZwZIkRazQKqYdIhCzhnbQlSLVo5gVLuIyKQM68C0q402SRGVOIGKkisxAgfyhava8eupv1qekgRJEqqiCE0oHrNoe/ohKfsYE+tp9ID8t8ltHvXh1w8ao3OFIR21FBQWf7A/fBxb2HcH3C/dlw=' ) )
    #temp = 'eNqNjrEKwzAMRH/FmxdbSBdbcbr2M4yXQvZC06n032srpGTMokN34uk+fltfm7+5Wqt/3t+PVXwYSwRlleDyTJxycFEw0TJJ6ykTByfFpI9hCe/mIeZmi2qcE4nixMognFBxuYKyaRd7UfyLssETQbXDCijpAef+DlJIGFcftOG17w8i9jxl'
else:
    pass
    #put code here
    

#Get selected object information
objectName = str( py.ls( selection = True )[0] )
objectPosition = position.relative( objectName )
objectPosition.append( tempConnector.size() )
objectPosition.append( chanceOfIndividual )
objectLocation = objectPosition[0]
objectRotation = objectPosition[1]
objectSize = objectPosition[2]

#Other things
chanceList = [updateChance, chanceOfIndividual, chanceOfObject, chanceOfConnection]
objectInfoList = [objectName, [objectPosition], chanceOfObject]
if removeCustomPoint == False:
    removeValues = -1
    
'''
connectionList = infoStore( connectorStoreName )
newConnectionIndex = selectRandomConnection( str( objectName ).split( '_' )[0] )
newObjectInfo = connectionList[newConnectionIndex[0]][0][newConnectionIndex[1]]
selectedConnection = newObjectInfo[1][newConnectionIndex[2]]


#Get coordinates of pivot
pivotOrigin = [newConnectionIndex[3][0][0],newConnectionIndex[3][0][1]-selectedConnection[2][1]/2,newConnectionIndex[3][0][2]-selectedConnection[2][2]/2]
defaultPivot = py.xform( objectName, query = True, pivots = True )
py.xform( objectName, pivots = pivotOrigin )
objectInfo = position.get( objectName )
objectPosition = objectInfo[0]
objectRotation = objectInfo[1]
pivotRelative = py.xform( objectName, query = True, pivots = True )
pivotOrigin = [ objectPosition[0] + pivotRelative[0], objectPosition[1] + pivotRelative[1], objectPosition[2] + pivotRelative[2] ]
py.xform( objectName, pivots = [defaultPivot[0], defaultPivot[1], defaultPivot[2]] )

#Create new object and move to new location
newObject = py.instance( newObjectInfo[0], name = newObjectInfo[0] + str( "_" ) )
newRotation = selectedConnection[1]

pivotInfo = [selectedConnection[0][0],selectedConnection[0][1]-selectedConnection[2][1]/2,selectedConnection[0][2]-selectedConnection[2][2]/2]

defaultPivot = py.xform( objectName, query = True, pivots = True )
py.xform( newObject, pivots = pivotInfo )

py.move ( pivotOrigin[0] - pivotInfo[0], pivotOrigin[1] - pivotInfo[1], pivotOrigin[2] - pivotInfo[2], newObject, absolute = True )
py.rotate ( newObject, 0, 180 - newRotation[1] - objectRotation[1], 0, relative = True )
'''


#Set up dictionary
firstRun = initialise( connectorName, objectInfoList )

#Find if item to add already exists
checkConnection = selection.exists( connectorName, chanceList, objectInfoList)

#Add to selection
if addToList == False:
    print "Adding connection to list..."
    print selection.add( connectorName, objectInfoList, checkConnection )

#Remove from selection
if removeFromList == True:
    print "Removing connection from list..."
    print selection.remove( connectorName, objectInfoList, checkConnection, removeValues )

#Pick connector
#Get pivot point
#Set pivot point

          

'''
objectInfoList = [objectName, [objectPosition], chanceOfObject]

initialise( connectorName, objectInfoList ) = True if new dictionary is created, False if not

timeOutput( startTime, endTime ) = text

#CLASSES
selection
    -exists( connectorName, chanceList, objectInfoList ) = [exists, object index = -1]
    -add( connectorName, objectInfoList, checkConnection ) = text
    -remove( connectorName, objectInfoList, checkConnection, removeValues ) = text
compress
    -compress( value ) = compressed text
    -decompress( value ) = decompressed text
output
    -connector
    -object


#Find compatible connection to object
selectRandomConnector( objectName ) = Get a single connector from the selected object
    return connectorName
selectRandomConnection( objectName ) = Get the index values of a new point that selected object can connect to
    return [connectorName, objectIndex, connectionIndex]
    
position.flip( rotation ) = Return mirrored rotation around horizontal axis
    return [x,y,z]
    
#Storing and sorting
infoStore( storeName, valuesToUpdate = False ) = Update list of all values
    return dictionary if valuesToUpdate is False
sortByObject( objectName = False ) = Sort connection list to have objects as index values
    return dictionary

#Getting object information
position.get( objectSelection ) = Return absolute location and rotation of object
position.relative( objectSelection ) = Return relative location and rotation of object
    return [location, rotation]

#Select new path
selectNewConnection( objectName ) = Pick connection coming from object based on percentage
    return connector name

#Updating selection
selection.exists( connectorName, chanceList, objectInfoList )
    return [exists, object index]
selection.add( connectorName, objectInfoList, checkConnection ) = Add object to connection list
selection.remove( connectorName, objectInfoList, checkConnection, removeValues ) = Remove object or values from connection list
    return text

#Output  
output.connector() = Output list of connections
output.object()( objectName = False ) Output list of connections, resorted with objects as index

'''
output.connector()
class copyObject:
    #Duplicate object
    @classmethod
    def copy( self, location ):
        pass
    #Update pivot
    @classmethod
    def pivot( self, location ):
        pass
    #Flip rotation horizontally
    @classmethod
    def flip( self, inputRotation ):
        outputRotationX = -inputRotation[0]
        outputRotationY = inputRotation[1] + 180
        outputRotationZ = inputRotation[2] % 360
        return [ outputRotationX, outputRotationY, outputRotationZ ]


class newConnection:
    #Pick empty connection from object
    def connector( self, object, selectedConnection = False ):
        if selectedConnection != False:
            pass #Use selected connection
        else:
            pass #Pick random connection
        connectorName = -1
        coordinates = -1
        return [connectorName, coordinates]
    #Pick new connection from connector
    def connection( self, connection = -1 ):
        pass








#Get percentage of connections from object
def selectRandomConnector( objectName ):
    connectionsFromObject = sortByObject(objectName)[objectName]
    chanceOfConnectionTotal = 0
    connectionRandom = rd.uniform( 0, 100 )
    connectionPercentageIncrement = 0
    #Count total amount
    for i in range( len( connectionsFromObject ) ):
        chanceOfConnectionTotal += connectionsFromObject[i][-1]
    #Calculate percentage of connector
    for i in range( len( connectionsFromObject ) ):
        connectionPercentage = ( 100.0 * connectionsFromObject[i][-1] ) / chanceOfConnectionTotal
        connectionPercentageIncrement += connectionPercentage
        #Select random item
        if connectionPercentageIncrement > connectionRandom:
            selectedConnector = connectionsFromObject[i][0]
            connectionsFromConnector = connectionsFromObject[i][1]
            break
    
    #Select connection from self
    chanceOfIndividualTotal = 0
    for i in range( len( connectionsFromConnector ) ):
        chanceOfIndividualTotal += connectionsFromConnector[i][-1]
    individualSelfRandom = rd.uniform( 0, 100 )
    individualPercentageIncrement = 0
    for i in range( len( connectionsFromConnector ) ):
        individualPercentage = ( 100.0 * connectionsFromConnector[i][-1] ) / chanceOfIndividualTotal
        individualPercentageIncrement += individualPercentage
        #Select random item
        if individualPercentageIncrement > individualSelfRandom:
            selectedSelfConnection = connectionsFromConnector[i]
            selectedSelfConnectionIndex = i
            break
            
    return [selectedConnector, selectedSelfConnection]
    
    
def selectRandomConnection( objectName ):
    connectionList = infoStore( connectorStoreName )
    #Count all percentages
    chanceOfConnectionTotal = 0
    chanceOfObjectTotal = {}
    chanceOfIndividualTotal = {}
    for connectorName in connectionList:
        chanceOfConnectionTotal += connectionList[connectorName][-1]
        chanceOfObjectTotal[connectorName] = 0
        for i in range( len(connectionList[connectorName][0]) ):
            chanceOfObjectTotal[connectorName] += connectionList[connectorName][0][i][-1]
            chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][i][0]] = 0
            for j in range( len( connectionList[connectorName][0][i][1] ) ):
                chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][i][0]] += connectionList[connectorName][0][i][1][j][-1]
    randomConnector = selectRandomConnector( objectName )
    connectorName = randomConnector[0]
    selfConnection = randomConnector[1]
    #Select random object
    objectRandom = rd.uniform( 0, 100 )
    objectPercentageIncrement = 0
    for i in range( len(connectionList[connectorName][0]) ):
        objectPercentage = ( 100.0 * connectionList[connectorName][0][i][-1] ) / chanceOfObjectTotal[connectorName]
        objectPercentageIncrement += objectPercentage
        #Select random item
        if objectPercentageIncrement > objectRandom:
            selectedObject = connectionList[connectorName][0][i][0]
            selectedObjectIndex = i
            break
    #Select connection from object
    individualRandom = rd.uniform( 0, 100 )
    individualPercentageIncrement = 0
    for i in range( len( connectionList[connectorName][0][selectedObjectIndex][1] ) ):
        individualPercentage = ( 100.0 * connectionList[connectorName][0][selectedObjectIndex][1][i][-1] ) / chanceOfIndividualTotal[connectorName + "." + connectionList[connectorName][0][selectedObjectIndex][0]]
        individualPercentageIncrement += individualPercentage
        #Select random item
        if individualPercentageIncrement > individualRandom:
            selectedConnection = connectionList[connectorName][0][selectedObjectIndex][1][i]
            selectedConnectionIndex = i
            break
    #Return values
    return [connectorName, selectedObjectIndex, selectedConnectionIndex, selfConnection]
