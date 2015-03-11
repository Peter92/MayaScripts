import pymel.core as py
import random as rd
import ast
from fractions import Fraction


modifyList = True #actions that update the list
getConnectedEdge = False #get information from selection

addEdgeToList = True #add or remove from list
chanceEdge = 50 #chance of occurance
chanceObject = 50
sortList = True #sorts the list

edgeToDefine = ['x']
nameOfEdge = 'test3'

#initialise stuff
debugInfo = True
selectedObjects = py.ls( selection = True )

#create store
try:
    py.select( 'infoStore' )
except:
    py.spaceLocator( n = 'infoStore' )
    py.addAttr( 'infoStore', shortName = 'progress', longName = 'ProgressBarName', dataType = 'string' )
    py.addAttr( 'infoStore', shortName = 'sides', longName = 'EdgeList', dataType = 'string' )
    py.addAttr( 'infoStore', shortName = 'locations', longName = 'ObjectLocationList', dataType = 'string' )
    py.addAttr( 'infoStore', shortName = 'objects', longName = 'ObjectInfo', dataType = 'string' )
    py.setAttr( 'infoStore.sides', '[]' )
    py.setAttr( 'infoStore.objects', '[]' )
    py.setAttr( 'infoStore.locations', '[]' )
py.hide( 'infoStore')
allEdges = ast.literal_eval( py.getAttr( 'infoStore.sides' ) )

#convert - to number
for i in range( len( edgeToDefine ) ):
    if '-' in edgeToDefine[i]:
        edgeToDefine[i] = str(edgeToDefine[i]).replace('-','')+str(2)

'''
if getConnectedEdge == True:
    #list connections
    for objSelNum in range( len( selectedObjects ) ):
        objSel = str( selectedObjects[objSelNum] )
        connectedEdges = []
        #get connections to object
        for i in range( len( allEdges ) ):
            for j in range( len( allEdges[i][1] ) ):
                if objSel == allEdges[i][1][j][0]:
                    connectedEdges.append( [allEdges[i][0][0],float( allEdges[i][0][1] )] )
        #get percentage chance
        totalRandom = 0
        for i in range( len( connectedEdges ) ):
            totalRandom += connectedEdges[i][1]
        for i in range( len( connectedEdges ) ):
            connectedEdges[i].append( float( connectedEdges[i][1]/totalRandom ) )
            if i > 0:
                previousValue = float( connectedEdges[i-1][2] )
            else:
                previousValue = 0
            connectedEdges[i].append( previousValue + float( connectedEdges[i][1]/totalRandom ) )
        #calculate edge to use
        randomNum = rd.uniform( 0, 1 )
        for i in range( len( connectedEdges ) ):
            if randomNum > connectedEdges[i][3]:
                pass
            else:
                selectedEdge = connectedEdges[i][0]
                print 5
                break
        #get sides of object assigned to edge
        for i in range( len( allEdges ) ):
            if allEdges[i][0][0] == selectedEdge:
                numberOfCombinations = 0
                individualChance = []
                totalChance = 0
                for j in range( len( allEdges[i][1] ) ):
                    numberOfCombinations += len( allEdges[i][1][j][1] )
                    for k in range( len( allEdges[i][1][j][1] ) ):
                        totalChance += float( allEdges[i][1][j][2] )
                #increment the chance
                increment = 0
                for j in range( len( allEdges[i][1] ) ):
                    for k in range( len( allEdges[i][1][j][1] ) ):
                        if increment > 0:
                            previousValue = float( individualChance[increment-1] )
                        else:
                            previousValue = 0
                        increment += 1
                        individualChance.append( previousValue + float( allEdges[i][1][j][2]/totalChance ) )
                #calculate object and side to use
                randomNum = rd.uniform( 0, 1 )
                for j in range( len( individualChance ) ):                
                    if randomNum > individualChance[j]:
                        pass
                    else:
                        selectedSideIndex = j
                        break
                #loop to get object and value from index
                increment = 0
                for j in range( len( allEdges[i][1] ) ):
                    for k in range( len( allEdges[i][1][j][1] ) ):
                        if increment == selectedSideIndex:
                            objInfo = allEdges[i][1][j]
                            objName = objInfo[0]
                            objSide = objInfo[1][k]
                            if debugInfo == True:
                                print "Random number " + str( randomNum ) + " chose object '" + str( objName ) + "' for side " + str( objSide )
                                print
                        increment += 1
                            '''
    
if modifyList == True:
    for objSel in range( len( selectedObjects ) ):
        edgeToAdd = [[nameOfEdge,chanceEdge],[[str(selectedObjects[objSel]),edgeToDefine,chanceObject]]]
        #get previous value and update
        edgeAlreadyExists = -1
        objectExistsHere = -1
        objectExists = False
        for i in range( len( allEdges ) ):
            edgeInfo = allEdges[i][0]
            objInfo = allEdges[i][1]
            if edgeInfo[0] == edgeToAdd[0][0]: #check if edge name exists
                edgeAlreadyExists = i #index of edge name
                for j in range( len( objInfo ) ): #count number of existing values
                    if objInfo[j][0] == edgeToAdd[1][0][0]: #check if object is in edge name
                        objectExistsHere = j #index of object
                        for m in range( len( objInfo[j][1] ) ): #loop through each matching axis
                            for n in range( len( edgeToAdd[1][0][1] ) ): #loop for each selected axis
                                if objInfo[j][1][m] == edgeToAdd[1][0][1][n]:
                                    objectExists = True
        if debugInfo == True:
            print "Object name: " + str(edgeToAdd[1][0][0])
            print "Edge index: " + str(edgeAlreadyExists)
            print "Object index: " + str(objectExistsHere)
            print "Entry exists: " + str(objectExists)
            print
        #add to list
        addEdges = edgeToAdd[1][0][1]
        if len( allEdges ) == 0:
            allEdges.append( edgeToAdd )
        elif ( objectExists == False or len( edgeToAdd[1][0][1] ) > 1 ) and addEdgeToList == True :
            existingEdges = allEdges[edgeAlreadyExists][1][objectExistsHere][1]
            if edgeAlreadyExists > -1:
                if objectExistsHere > -1:
                    matchingValues = []
                    #check for matching letters
                    for i in range( len( addEdges ) ):
                        for j in range( len( existingEdges ) ):
                            alreadyExists = False
                            for m in range( len( matchingValues ) ):
                                if addEdges[i] == matchingValues[m]:
                                    alreadyExists = True
                            if addEdges[i] == existingEdges[j] and alreadyExists == False:
                                matchingValues.append( addEdges[i] )
                    #subtract matching letters and add to list
                    for i in range( len( addEdges ) ):
                        currentEdge = addEdges[i]
                        addToList = True
                        for j in range( len( matchingValues ) ):
                            if addEdges[i] == matchingValues[j]:
                                addToList = False
                        if addToList == True:
                            allEdges[edgeAlreadyExists][1][objectExistsHere][1].append( addEdges[i] )
                elif objectExists == False:
                    allEdges[edgeAlreadyExists][1].append( edgeToAdd[1][0] ) #add object
            elif objectExists == False:
                allEdges.append( edgeToAdd ) #add edge
                
        #remove from list
        if objectExists == True and addEdgeToList == False:
            if edgeAlreadyExists > -1:
                if objectExistsHere > -1:
                    objectList = allEdges[edgeAlreadyExists][1]
                    objectEdges = objectList[objectExistsHere][1]
                    edgesToRemove = edgeToAdd[1][0][1]
                    removeEdges = []
                    #check to make sure letters still exist
                    for i in range( len( objectEdges ) ):
                        for j in range( len( edgesToRemove ) ):
                            alreadyExists = False
                            for k in range( len( removeEdges ) ):
                                if objectEdges[i] == removeEdges[k]:
                                    alreadyExists = True
                            if objectEdges[i] == edgesToRemove[j] and alreadyExists == False:
                                removeEdges.append( edgesToRemove[j] )
                    if len( objectEdges ) > len( edgesToRemove ): #remove individual letter
                        for i in range( len( removeEdges ) ):
                            allEdges[edgeAlreadyExists][1][objectExistsHere][1].remove( removeEdges[i] )
                    else:
                        if len( objectList ) > 1: #remove whole object
                            objectList.remove( objectList[objectExistsHere] )
                        else: #remove entire edge
                            allEdges.remove( allEdges[edgeAlreadyExists] )
        
    #sort list
    if sortList == True:
        allEdges.sort()
        for i in range( len( allEdges ) ):
            allEdges[i][1].sort()
            for j in range( len( allEdges[i][1] ) ):
                allEdges[i][1][j][1].sort()
    
    
    #calculate percentages
    edgeProbability = 0
    totalProbability = 0
    edgeChance = float( allEdges[i][0][1] )
    for i in range( len( allEdges ) ):
        edgeProbability += edgeChance
        totalProbability += edgeChance * len( allEdges[i][1] )
    for i in range( len( allEdges ) ):
        #store as exact values
        individualEdgeProb = Fraction( edgeChance ) / Fraction( edgeProbability )
        edgeProbSeparated = [individualEdgeProb.numerator,individualEdgeProb.denominator]
        individualTotalProb = Fraction( edgeChance * len( allEdges[i][1] )) / Fraction( totalProbability )
        totalProbSeparated = [individualTotalProb.numerator,individualTotalProb.denominator]
        probabilityInfo = [edgeProbSeparated, totalProbSeparated]
        if len( allEdges[i] ) == 2:
            allEdges[i].append( probabilityInfo )
        else:
            allEdges[i][2] = probabilityInfo
            
    #store list
    py.setAttr( 'infoStore.sides', str( allEdges ) )




#calculate probability
totalProbability = 0
for i in range( len( allEdges ) ):
    totalProbability += float(allEdges[i][0][1])

#display text
if debugInfo == True:
    for i in range( len( allEdges ) ):
        edgeInfo = allEdges[i][0]
        objInfo = allEdges[i][1]
        outputText = "'" + str(edgeInfo[0]) + "' (" + str( round( edgeInfo[1]/totalProbability, 2 ) ) + "% probability) is applied to '"
        for j in range( len( objInfo ) ):
            outputText += objInfo[j][0] + "' for side"
            objSides = objInfo[j][1]
            if len( objSides ) > 1:
                outputText += "s"
            for m in range( len( objSides ) ):
                outputText += " " + str( objSides[m] ).replace( "x2", "-x" ).replace( "y2", "-y" )
                if m == len( objSides )-2:
                    outputText += " and"
                if m < len( objSides )-2:
                    outputText += ","
            if j == len( objInfo )-2:
                outputText += " and '"
            if j < len( objInfo )-2:
                outputText += ", '"
        print outputText


py.select( selectedObjects )
