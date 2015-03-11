import pymel.core as py
import maya.cmds as cmds
import maya.mel as ml
import random as rd
import sys
import math
from time import time
from decimal import *

def ph_mainCode(postValues):
    
    #animation
    autoMaxDistSpacing = 1 #how far apart the objects will be
    disappear = False #if a 3rd value will be keyed
    disappearSpeed = 8
    
    #colours
    colourExponential = 5 #low value gives greater contrast
    stretchValues = True #setting to false will give a smoother result but not use the full range
    
    #area (doesn't fully work)
    useArea = False
    maxArea = 3
    showCube = False
    
    #directions
    directionRetryValue = 0.35 #1 = always retry
    directionRetryRange = 0.15 #range to add to the retry value
    
    #misc
    autoSeed = True
    newSeed = 1
    groupObjects = True
    
    #display percent
    percentTime = 0.04
    colourPercent = 20 
    deleteCubePercent = 45
    #displayCubeUpdates = True
    cubeUpdateTime = 0.15
  
    #post values
    forkLength = postValues[0]
    keyCube = postValues[1]
    autoSet = postValues[2]
    forks = postValues[3]
    threeDimensions = postValues[4]
    cubeSkip = postValues[5]
    frameSpacing = postValues[6]
    loops = postValues[7]
    animSpacing = postValues[8]
    startingLocX = postValues[9]
    startingLocY = postValues[10]
    startingLocZ = postValues[11]
    maxDistX = postValues[12]
    maxDistY = postValues[13]
    maxDistZ = postValues[14]
    autoMaxDist = postValues[15]
    quickGeneration = postValues[16]
    autoSetMultiplier = postValues[17]
    cubeSize = postValues[18]
    branch = postValues[19]
    mainDirection = postValues[20]
    colourObjects = postValues[21]
    shaderColours = postValues[22]
    colourDetail = postValues[23]
    colourRatio = postValues[24]
    deleteCubes = postValues[25]
    createCurves = postValues[26]
    selectCurves = postValues[27]
    displayCubeUpdates = postValues[28]
    
    #min values
    forkLengthMin = 2
    forksMin = 0
    frameSpacingMin = 0.01
    loopsMin = 1
    maxDistSpacingMin = 1
    percentReductionMax = 0.95
    percentReductionMin = 0.6
    if forks > 0:
        colourExponentialMin = int( ( 1.0 / pow( forks * forkLength , 0.7 ) ) * 1000 )
    else:
        colourExponentialMin = int( ( 1.0 / pow( forkLength , 0.7 ) ) * 1000 )
    if colourExponentialMin < 5:
        colourExponentialMin = 5   
    
    #messages
    global gMainProgressBar
    global msgLevel
    global formatDecimals
    formatDecimals = 2
    msgLevel = 2
    '''
    0 = Key info, seed
    1 = loops
    2 = forks
    3 = points created
    4 = cubes
    '''
    
    ################################################################################################   
    
    #auto set variables
    originalCam = py.lookThru( query = True )
    if deleteCubes == True:
        percentReduction = 1 - deleteCubePercent/100.0
    elif colourObjects == True:
        percentReduction = 1 - colourPercent/100.0
    else:
        percentReduction = 0.99
    shaderColours = shaderColours.replace(' ','').split(',')
    branchMultiple = ( (forkLength+1) * (forks+1) ) / 125.0
    branchAmount = math.log(branchMultiple, 2)/30 + 0.5
    if branchAmount > percentReductionMax:
        branchAmount = percentReductionMax
    elif branchAmount < percentReductionMin:
        branchAmount = percentReductionMin
    
    startTime = time()
    forks = float(forks)
    forkLength = float(forkLength)
    distance = cubeSize/15.0 + cubeSize
    cubeSizeOriginal = cubeSize
    
    if colourObjects == True:
        shaderColours, colourDetail, shaderAmount, shaderName = ph_validateShaderColours(shaderColours,colourDetail)

    if threeDimensions == True:
        degrees = 6
    else:
        degrees = 4
    
    if cubeSkip < 0:
        keyCube == False
        
    if deleteCubes == True:
        keyCube = False
        
    if autoSeed == True:
        newSeed = rd.randint( 0, sys.maxint )
    rd.seed( newSeed )
    
    if threeDimensions == False:
        maxDistY = 0
    
    
    #error messages
    if colourRatio <= 0:
        
        colourRatio = 0.0001
        
    if colourRatio >= 1:
        colourRatio = 0.9999
    
    if colourExponentialMin > colourExponential and colourObjects == True:
        colourExponential = colourExponentialMin
        print "Colour exponential too low, setting it at " + str( int(colourExponentialMin) )
        
    if forkLength < forkLengthMin:
        print "Fork length too low, setting it at " + str(forkLengthMin)
        forkLength = forkLengthMin
        
    if forks < forksMin:
        print "Number of forks too low, setting it at " + str(forksMin)
        forks = forksMin
    
    if loops < loopsMin:
        print "Number of loops too low, setting it at " + str(loopsMin)
        loops = loopsMin
    
    #automatically set key options
    if forks == 0:
        forksTemp = 1
    else:
        forksTemp = forks
    cubeSkipTemp = 0.7 * loops ** 0.1 * forksTemp*forkLength * pow(1.05, pow(forkLength/forksTemp,0.1))
    cubeSkipTemp = cubeSkipTemp * autoSetMultiplier / (600 + (forksTemp + forkLength) * (1.0/degrees) * 20)
    
    if cubeSkipTemp < 1:
        frameSpacingTemp = forksTemp/4.0*((1/cubeSkipTemp)/(degrees * 3))
        if frameSpacingTemp < 1:
            frameSpacingTemp = 1/frameSpacingTemp
        cubeSkipTemp = 0
        frameSpacingTemp = pow( frameSpacingTemp, 0.5 )
        
    else:
        frameSpacingTemp = 1
        
    if autoSet == True:
        cubeSkip = cubeSkipTemp
        frameSpacing = frameSpacingTemp

        if msgLevel > -1:    
            print ""
            print "Set cubeSkip to " + str(cubeSkip)
            print "Set frame spacing to " + str(frameSpacing)
            print ""
    
    #error messages
    else:
        if frameSpacing < frameSpacingMin and keyCube == True :
            print "Frame spacing too low to key, setting it at " + str(frameSpacingMin)
            print ""
            frameSpacing = frameSpacingMin
    
    if loops > 1 and useArea == True:
        useArea = False
        print "Area currently doesn't work with loops, disabling use area"
        print ""
    
    if startingLocX != 0 or startingLocY != 0 or startingLocZ != 0:
        if useArea == True:
            print "Area currently doesn't work with custom starting location, setting starting location to 0"
            startingLocX = 0
            startingLocY = 0
            startingLocZ = 0
    
    if autoMaxDist == True and autoMaxDistSpacing < maxDistSpacingMin:
        print "Spacing between objects too low, setting it at " + str(maxDistSpacingMin)
        autoMaxDistSpacing = maxDistSpacingMin
    
    if useArea == False:
        showCube = False
    
    if showCube == True:
        areaCube = maxArea * 2 * distance + distance
        cmds.polyCube( w = areaCube, h = areaCube , d = areaCube)
    
    if loops > 1:
        approxArea = int( ( loops ** 0.7 ) * ( (forks + forkLength)/ 2.75 + 1.1 ) * autoMaxDistSpacing )
        if autoMaxDist == True:
            maxDistX = approxArea
            maxDistY = approxArea
            maxDistZ = approxArea
        if maxDistX < 0:
            maxDistX = approxArea
        if maxDistY < 0:
            maxDistY = approxArea
        if maxDistZ < 0:
            maxDistZ = approxArea
        if maxDistX == approxArea or maxDistY == approxArea or maxDistZ == approxArea :
            print "Max distance set to " + str(approxArea)
            print ""
    else:
        maxDistX = 0
        maxDistY = 0
        maxDistZ = 0
    
    #check for previous generations
    try:
        cmds.select( 'tempLocator' )
        
    except:
        #reset values
        py.spaceLocator( n = 'tempLocator' )
        py.addAttr( 'tempLocator', shortName = 'progress', longName = 'ProgressBarName', dataType = 'string' )
        py.addAttr( 'tempLocator', shortName = 'cpercent', longName = 'ColourPercent' )
        py.addAttr( 'tempLocator', shortName = 'cstretch', longName = 'ColourStretch' )
        py.addAttr( 'tempLocator', shortName = 'cupdate', longName = 'CubeUpdateTime' )
        py.addAttr( 'tempLocator', shortName = 'pupdate', longName = 'PercentUpdateTime' )
        py.addAttr( 'tempLocator', shortName = 'last', longName = 'LastGeneration' )
        myfile = open( ph_fileName('count') , 'w')
        myfile.write("0")
        myfile.close()
    py.hide()
    
    try:
        prefixOffset = int(ph_readFile( ph_fileName('count') ))
    except:
        prefixOffset = 0
        
    #increment file   
    myfile = open( ph_fileName('count') , 'w')
    myfile.write(""+ str( int(prefixOffset) + loops ) +"")
    myfile.close()
    
    #initialise variables
    currentKey = 0
    highKey = "initialrun"
    totalPoints = 0
    frameNum = py.currentTime(query = True)
    gMainProgressBar = ml.eval('$tmp = $gMainProgressBar');
    py.setAttr('tempLocator.progress',gMainProgressBar)
    py.setAttr('tempLocator.cpercent',colourPercent)
    py.setAttr('tempLocator.cstretch',stretchValues)
    py.setAttr('tempLocator.cupdate',cubeUpdateTime)
    py.setAttr('tempLocator.pupdate',percentTime)
    py.progressBar( gMainProgressBar, edit=True, beginProgress=True, isInterruptable=True, status='Generating forks...', maxValue=100 )
    
    #########################################################################################################
    
    for loop in range(0, loops):
        
        #percentage complete
        percentTimeCurrent = time()
        cubeTimeCurrent = time()
        percentCompleted = float(loop)/loops
        py.progressBar(gMainProgressBar, edit=True, status='Generating forks...', progress=float(ph_decimalConvert(percentCompleted)))
        if displayCubeUpdates == True:
            py.currentTime( currentKey, edit = True, update = True)
        
        #set starting location
        if loops == 1:
            startXLoc = float(startingLocX)
            startYLoc = float(startingLocY)
            startZLoc = float(startingLocZ)
            
        else:
            startXLoc = ( float(startingLocX) + rd.randint(-maxDistX,maxDistX) ) * distance
            startYLoc = ( float(startingLocY) + rd.randint(-maxDistY,maxDistY) ) * distance
            startZLoc = ( float(startingLocZ) + rd.randint(-maxDistZ,maxDistZ) ) * distance
            
        #reset variables
        listOfPoints=[]
        listOfPoints2=[]
        pointInfo=[]
        curveList = []
        i = 0
        cubeSkipCount = 1
        cubeSkipAmount = 0
        cubeLoc = [ startXLoc, startYLoc, startZLoc ]
        cubeSize = cubeSizeOriginal
        loopTime = time()
        py.setAttr('tempLocator.last',(loop + prefixOffset))
        
        #delete temp objects
        try:
            py.delete(generationCam)
            py.delete(motionPath)
            
        except:
            pass
            
        generationCam, motionPath = ph_createTrackingCam(startTime, cubeSize, cubeLoc)
        
    #########################################################################################################
        
        #generate main path
        startKey = py.currentTime(query = True)
        if highKey == "initialrun":
            frameNum = startKey
            highKey = startKey
        else:
            frameNum = rd.uniform( 0, (highKey/frameSpacing) * animSpacing)
            
        if msgLevel > 0:
            print ""
            print "Building loop " + str(loop + 1) + " of " + str(loops)
        if msgLevel > 1:
            print ""
            print "  Building main path"
        
        #create group
        cmds.select( clear = True )
        if groupObjects == True:
            currentGroup = py.group( n = ph_nameLoop(loop + prefixOffset).getNextPrefix() + 'CubeGroup' )
        
        #make first fork
        directionRetry = rd.uniform(directionRetryValue - directionRetryRange, directionRetryValue + directionRetryRange)
        while i in range (0, int(forkLength)):
            
            #slowly reduce size of cubes
            forkPercent = i / forkLength
            reduceSize = cubeSize - branchAmount
            reduceAmount = ( forkPercent * reduceSize ) / 4
            if branch == False:
                reduceAmount = 0
            newSize = cubeSize - reduceAmount
            
            #get colours
            colourValue = 1 - ( forkPercent * (1-branchAmount) )
            
            #create cube
            cubeName = ph_nameLoop(loop + prefixOffset).getNextPrefix() + 'Cube'
            newCube = cmds.polyCube( n = cubeName, w = newSize, d = newSize, h = newSize )
            selection = py.ls( selection=True )
            direction = rd.randint(1,degrees)
            invalid = 0
            
            #get new location of cube
            newLoc, invalid = ph_direction(direction,distance,cubeLoc,listOfPoints,mainDirection,directionRetry,quickGeneration)
            
            #make sure it's not outside bounds
            invalid2 = 0
            if useArea == True:
                if newLoc[0] > maxArea * distance or -newLoc[0] > maxArea * distance or newLoc[1] > maxArea * distance or -newLoc[1] > maxArea * distance or newLoc[2] > maxArea * distance or -newLoc[2] > maxArea * distance: 
                    invalid2 = 1
                    invalid = 1
    
            #stop duplicate cubes
            if invalid == 1:
                invalidCount = 0
                
                #loop to find if there's no new spaces
                for k in range( 0, degrees ):
                    direction = k + 1
                    newLoc, invalid = ph_direction(direction,distance,cubeLoc,listOfPoints,mainDirection,directionRetry,quickGeneration)
        
                    if invalid == 1:
                        invalidCount += 1
                
                #end the loop
                if invalidCount == degrees or invalid2 == 1:
                    i = forkLength
        
                #delete cube
                cmds.delete( newCube )
                
            else:
                
                #move cube
                cmds.move(newLoc[0], newLoc[1], newLoc[2])
                loc = selection[0].getTranslation()
                cubeLoc = [ loc.x, loc.y, loc.z ]
                listOfPoints.append( cubeLoc )
                listOfPoints2.append( cubeLoc )
                frameNum += 1
                totalPoints += 1
                
                currentKey = ( frameNum - cubeSkipAmount ) * frameSpacing
                
                #add attributes
                cubeSel = py.ls( selection = True )
                py.addAttr( cubeSel[0], shortName = 'cv', longName = 'colourValue' )
                py.setAttr( cubeSel[0]+'.colourValue', colourValue )
                
                #key cube creation
                if keyCube == True:
                    
                    #set the keys
                    py.setKeyframe( cubeSel[0].v, time = currentKey - 1, value = 0 )
                    py.setKeyframe( cubeSel[0].v, time = currentKey, value = 1 )
                    if disappear == True:
                        py.setKeyframe( cubeSel[0].v, time = currentKey + disappearSpeed, value = 0 )
                    
                    #store highest value
                    if highKey < currentKey:
                        highKey = currentKey                    
                        
                    #key multiple cubes to same frame
                    if cubeSkipCount >= cubeSkip:
                        cubeSkipCount -= cubeSkip
                    else:
                        cubeSkipCount += 1
                        cubeSkipAmount += 1
    
                    #store fork and current key   
                    storeInfo = [ newLoc[0], newLoc[1], newLoc[2], 0, cubeSize, colourValue, currentKey ]
                    pointInfo.append( storeInfo )  
                    
                else:
                    
                    storeInfo = [ newLoc[0], newLoc[1], newLoc[2], 0, cubeSize, colourValue ]
                    pointInfo.append( storeInfo )   
                
                #add to group
                if groupObjects == True:
                    py.parent( newCube[0], currentGroup )
                
                if msgLevel > 3:
                    print "   Cube created at [" + str(loc.x) + ", " + str(loc.y) + ", " + str(loc.z) + "]"
                
            #percentage complete
            if time() - percentTimeCurrent > percentTime:
                percentTimeCurrent = time()
                percentCompleted = float(loop)/loops+percentReduction*((1.0/loops)*(1.0/(forks+1))*((i+1.0)/forkLength))
                py.progressBar(gMainProgressBar, edit=True, progress=float(ph_decimalConvert(percentCompleted)))
            
            if py.progressBar(gMainProgressBar, query=True, isCancelled=True) == True :
                break
            
            if displayCubeUpdates == True:
                if time() - cubeTimeCurrent > cubeUpdateTime:
                    cubeTimeCurrent = time()
                    py.currentTime( currentKey, edit = True, update = True)
            i += 1
            
        if msgLevel > 2:
            if msgLevel > 3:
                print "    "+ str( totalPoints ) + " points created"
            else:
                print "   "+ str( totalPoints ) + " points created"
            print ""
            
        #create path    
        if len( listOfPoints2 ) > 1 and createCurves == True:
            curveName = cmds.curve( p = listOfPoints2, d = 1 )
            curveList.append( curveName )
            if groupObjects == True:
                py.parent( curveName, currentGroup )
            
        newLength = len( listOfPoints2 )
        if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
            break
            
    #########################################################################################################
                
        #generate forks
        for i in range (0, int(forks)):
            
            #reset variales
            cubeSkipAmount = 0
            frameNum = 0
            
            if msgLevel > 1:
                print "   Building fork " + str(i + 1) + " of " + str(int(forks)) + " (" + str(int(len(listOfPoints)/(time()-startTime))) + " points per second)"
            #select existing cube
            cubeSelectNum = rd.randint(1, len(listOfPoints) - 1 )
            originalFork = pointInfo[cubeSelectNum][3]
            
            #for generations getting smaller
            if branch == True:
                cubeSize = pointInfo[cubeSelectNum][4] * branchAmount
                distance = cubeSize/15.0 + cubeSize
            
            #get frame of cube
            originalKey = pointInfo[cubeSelectNum][-1]
            
            #get colour of cube
            colourStore = pointInfo[cubeSelectNum][5]
            
            #get cube location
            cmds.select( cubeName + str( cubeSelectNum ) )
            loc = py.ls( selection=True )[0].getTranslation()
            cubeLoc = [ loc.x, loc.y, loc.z ]
            listOfPoints2=[cubeLoc]
            j = 0
            
            #reduce gaps towards end of generation
            percentComplete = (i+1)/forks
            changeAtEnd = (pow( forkLength, 0.5 ))/pow( percentComplete, 0.2) - pow( forkLength, 0.5 )
            changeAtEnd = changeAtEnd * frameSpacing * ( degrees / 6 )
            
            #increase gaps towards start of generation
            percentCompleteLow = (forks-i)/forks
            changeAtEndLow = -(pow( forkLength, 0.5 ))/pow( percentCompleteLow, 0.2) + pow( forkLength, 0.5 )
            changeAtEndLow = changeAtEndLow * frameSpacing * ( degrees / 6 )
            
            #calculate key to start fork on
            forkCalc = ((i+2)*newLength)/ (degrees*3.5)
            randomTime = rd.uniform( ( forkCalc * changeAtEndLow ) / 2, forkCalc * changeAtEnd)
            
            #allow for cubeskip and framespacing
            if cubeSkip > 1:
                randomTime = randomTime / cubeSkip
            else:
                randomTime = randomTime * frameSpacing
                
            #for using the old generation
            oldKeyChance = rd.uniform( 0, 1 )
            
            directionRetry = rd.uniform(directionRetryValue - directionRetryRange, directionRetryValue + directionRetryRange)
            while j in range (0, int(forkLength)):
                
                #slowly reduce size of cubes
                forkPercent = j / forkLength
                reduceSize = cubeSize - ( branchAmount * cubeSize )
                reduceAmount = ( forkPercent * reduceSize ) / 3
                
                if branch == False:
                    reduceAmount = 0
                    
                newSize = cubeSize - reduceAmount
                if newSize < 0.001:
                    newSize = 0.001
                    
                #get colours
                colourValue = colourStore - ( forkPercent * (colourStore - ( branchAmount * colourStore )) )
                
                #create cube
                cubeName = ph_nameLoop(loop + prefixOffset).getNextPrefix() + 'Cube'
                newCube = cmds.polyCube( n = cubeName, w = newSize, d = newSize, h = newSize )
                selection = py.ls( selection=True )
                direction = rd.randint(1,degrees)
                invalid = 0
                
                #get new location of cube
                newLoc, invalid = ph_direction(direction,distance,cubeLoc,listOfPoints,mainDirection,directionRetry,quickGeneration)
                
                #make sure it's not outside bounds
                invalid2 = 0
                if useArea == True:
                    if newLoc[0] > maxArea * distance or -newLoc[0] > maxArea * distance or newLoc[1] > maxArea * distance or -newLoc[1] > maxArea * distance or newLoc[2] > maxArea * distance or -newLoc[2] > maxArea * distance: 
                        invalid2 = 1
                        invalid = 1
                
                #stop duplicate cubes
                if invalid == 1:
                    invalidCount = 0
                    
                    #loop to find if there's no new spaces
                    for k in range( 0, degrees ):
                        direction = k + 1
                        newLoc, invalid = ph_direction(direction,distance,cubeLoc,listOfPoints,mainDirection,directionRetry,quickGeneration)
                        
                        if invalid == 1:
                            invalidCount += 1
                
                    #end the loop
                    if invalidCount == degrees or invalid2 == 1:
                        j = forkLength
                        
                    #delete cube
                    cmds.delete( newCube )
                    
                else:
                    
                    #move cube
                    cmds.move(newLoc[0], newLoc[1], newLoc[2])
                    loc = selection[0].getTranslation()
                    cubeLoc = [ loc.x, loc.y, loc.z ]
                    listOfPoints.append( cubeLoc )
                    listOfPoints2.append( cubeLoc )
                    totalPoints += 1
                    frameNum += 1
                    
                    if j == 0:
                        currentKey = originalKey + randomTime
                    else:
                        currentKey = originalKey + (frameNum - cubeSkipAmount ) * frameSpacing + randomTime
                    
                    #add attributes
                    cubeSel = py.ls( selection = True )
                    py.addAttr( cubeSel[0], shortName = 'cv', longName = 'colourValue' )
                    py.setAttr( cubeSel[0]+'.colourValue', colourValue )
                    
                    #key cube creation
                    if keyCube == True:
                        
                        #make sure it doesn't go below the starting key
                        if currentKey < startKey:
                            currentKey = currentKey - randomTime
                            randomTime = startKey
                        
                        #low chance of alternate generation
                        if oldKeyChance > 0.975:
                            
                            oldKey = originalKey + (frameNum - cubeSkipAmount - (((i+2)*len(listOfPoints))/ (degrees*3.5)) ) * frameSpacing
                            m = i
                            while oldKey < originalKey + 1:
                                oldKey = originalKey + (frameNum - cubeSkipAmount - ((m+2)*len(listOfPoints))/ (degrees*3.5)/ ((i+1)**0.25) ) * frameSpacing
                                m = m - 1
                            if oldKey >= originalKey + 1:
                                currentKey = oldKey
                        
                        #set keyframes
                        py.setKeyframe( cubeSel[0].v, time = currentKey - 1, value = 0 )
                        py.setKeyframe( cubeSel[0].v, time = currentKey, value = 1 )
                        if disappear == True:
                            py.setKeyframe( cubeSel[0].v, time = currentKey + disappearSpeed, value = 0 )
                        
                        #store highest value
                        if highKey < currentKey:
                            highKey = currentKey
                        
                        #key multiple cubes to same frame
                        if cubeSkipCount >= cubeSkip:
                            cubeSkipCount -= cubeSkip
                        else:
                            cubeSkipCount += 1
                            cubeSkipAmount += 1
                            
                        #store fork and current key  
                        storeInfo = [ loc.x, loc.y, loc.z, i + 1, cubeSize, colourValue, currentKey ]
                        pointInfo.append( storeInfo )
                        
                    else:
                        
                        storeInfo = [ loc.x, loc.y, loc.z, i + 1, cubeSize, colourValue ]
                        pointInfo.append( storeInfo )
                        
                        
                    #add to group
                    if groupObjects == True:
                        py.parent( newCube[0], currentGroup )
                    
                #percentage complete
                if time() - percentTimeCurrent > percentTime:
                    percentTimeCurrent = time()
                    percentCompleted = float(loop)/loops+percentReduction*((1.0/loops)*((i+1.0)/(forks+1)+((j+0.0)/forkLength)*(1.0/(forks+1))+1.0/(forks+1)-(2.0)/forkLength))
                    py.progressBar(gMainProgressBar, edit=True, progress=float(ph_decimalConvert(percentCompleted)))
                
                if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
                    break    
                
                if displayCubeUpdates == True:
                    if time() - cubeTimeCurrent > cubeUpdateTime:
                        cubeTimeCurrent = time()
                        py.currentTime( currentKey, edit = True, update = True)
                j += 1
                
                if msgLevel > 3:
                        print "    Cube created at [" + str(loc.x) + ", " + str(loc.y) + ", " + str(loc.z) + "]"
            
            i += 1
                
            if msgLevel > 2:
                if msgLevel > 3:
                    print "     "+ str( totalPoints ) + " points created"
                else:
                    print "    "+ str( totalPoints ) + " points created"
                print ""
             
            #create path
            if len( listOfPoints2 ) > 1 and createCurves == True:
                curveName = cmds.curve( p = listOfPoints2, d = 1 )
                curveList.append( curveName )
                if groupObjects == True:
                    py.parent( curveName, currentGroup )
            if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
                break
        
        #skip to next part of code
        py.progressBar(gMainProgressBar, edit=True, endProgress=True)
        py.progressBar(gMainProgressBar, edit=True, beginProgress=True, isInterruptable=True, maxValue=100)
              
        #delete all cubes
        if deleteCubes == True:
            py.progressBar(gMainProgressBar, edit=True, status='Removing cubes...')
            cmds.delete( cubeName )
            for i in range (1, len( listOfPoints )):
                cmds.delete( cubeName + str(i) )
                
                #percentage complete
                if time() - percentTimeCurrent > percentTime:
                    percentTimeCurrent = time()
                    percentCompleted = (float(loop)/loops)+(1.0/loops)*(percentReduction+((deleteCubePercent/100.0)*(float(i)/len(listOfPoints))))
                    py.progressBar(gMainProgressBar, edit=True, progress=float(ph_decimalConvert(percentCompleted)))
                
                if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
                    break
                    
                if displayCubeUpdates == True:
                    if time() - cubeTimeCurrent > cubeUpdateTime:
                        cubeTimeCurrent = time()
                        py.currentTime( currentKey, edit = True, update = True)
        
        #store cube amounts
        #aaaa
        endLetter = str(ph_nameLoop(loop + prefixOffset).getNextPrefix()).capitalize()        
        py.addAttr( currentGroup, shortName = 'num', longName = 'NumberOfCubes' )
        py.setAttr( currentGroup+'.num', totalPoints )
        py.addAttr( currentGroup, shortName = 'branch', longName = 'BranchAmount' )
        py.setAttr( currentGroup+'.branch', branchAmount )
        py.addAttr( currentGroup, shortName = 'expo', longName = 'ColourExponential' )
        py.setAttr( currentGroup+'.expo', colourExponential )
        py.addAttr( currentGroup, shortName = 'forks', longName = 'NumberOfForks')
        py.setAttr( currentGroup+'.forks', forks )
        py.addAttr( currentGroup, shortName = 'length', longName = 'LengthOfForks')
        py.setAttr( currentGroup+'.length', forkLength )
        py.addAttr( currentGroup, shortName = 'key', longName = 'LastFrame')
        py.setAttr( currentGroup+'.key', highKey )
        py.addAttr( currentGroup, shortName = 'id', longName = 'GenerationID')
        py.setAttr( currentGroup+'.id', (loop + prefixOffset) )
       
        #print py.getAttr( 'tempLocator.generationn'+str(ph_nameLoop(loop + prefixOffset).getNextPrefix()).capitalize() )
                   
        #colours
        if colourObjects == True and deleteCubes == False:

            generalList = [loop,loops,(loop + prefixOffset)]
            timeList = [cubeTimeCurrent,percentTimeCurrent,displayCubeUpdates]
            colourList = [shaderName,shaderAmount,colourRatio,colourDetail,shaderColours]
            percentTimeCurrent, cubeTimeCurrent = ph_colourAllObjects(generalList,timeList,colourList)
            
            #create file
            open( ph_fileName('pointinfo') , 'w').close() 
            myfile = open( ph_fileName('pointinfo') , 'w')
            myfile.write(str([generalList,timeList,colourList]))
            myfile.close()
            
        #set time
        if keyCube == True:
            py.playbackOptions( max = highKey * 1.1 )
            py.currentTime( highKey )
        
        if msgLevel > 0:
            print " " + str(totalPoints) + " points created in " + ph_timeOutput(loopTime, time())
        totalPoints = 0
        if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
            break
        
    if msgLevel > -1:
        if msgLevel > 0:
            print ""
            
        print "Seed used was " + str(newSeed)
        print "Total time taken was " + ph_timeOutput(startTime, time())
    
    
    #select curves
    if selectCurves == True:
        
        i = 0
        cmds.select( clear = True )
        for i in range(len(curveList)):
            cmds.select( curveList[i], add = True)
    
    #delete temp objects
    try:
        py.lookThru(originalCam)
        py.delete(generationCam)
        py.delete(motionPath)
        
    except:
        pass
    
    py.progressBar(gMainProgressBar, edit=True, endProgress=True)

def ph_readFile(fileName):
    #create file
    try:
        myfile = open(fileName)
    except:
        open(fileName, 'w').close() 
        myfile = open(fileName)
        
    #read file
    currentValue = myfile.readlines()
    if len(currentValue) == 0:
        currentValue = [False]
    myfile.close()
    return currentValue[0]

def ph_colourAllObjects(generalList,timeList,colourList):
    
    #get values
    loop = generalList[0]
    loops = generalList[1]
    generationNumber = generalList[2]
    cubeTimeCurrent = timeList[0]
    percentTimeCurrent = timeList[1]
    displayCubeUpdates = timeList[2]
    shaderName = colourList[0]
    shaderAmount = colourList[1]
    colourRatio = colourList[2]
    colourDetail = colourList[3]
    shaderColours = colourList[4]
    
    currentGroup = ph_nameLoop(generationNumber).getNextPrefix() + 'CubeGroup'
    numOfCubes = py.getAttr( currentGroup+'.num' )
    branchAmount = py.getAttr( currentGroup+'.branch' )
    colourExponential = py.getAttr( currentGroup+'.expo' )
    forks = py.getAttr( currentGroup+'.forks' )
    forkLength = py.getAttr( currentGroup+'.length' )
    gMainProgressBar = py.getAttr('tempLocator.progress')
    colourPercent = py.getAttr('tempLocator.cpercent')
    stretchValues = py.getAttr('tempLocator.cstretch')
    percentTime = py.getAttr('tempLocator.pupdate')
    cubeUpdateTime = py.getAttr('tempLocator.cupdate')
    currentKey = py.getAttr( currentGroup+'.key' )
    
    smoothOverride = int(forkLength/(4*colourDetail*len(shaderColours)))
    cubesPerColour = ((forks+1)*forkLength)/(colourDetail*len(shaderColours))
    if smoothOverride < 1:
        smoothOverride = 1
    if smoothOverride > int(cubesPerColour/2):
        smoothOverride = int(cubesPerColour/2)
    if smoothOverride > 10:
        smoothOverride = 10
        
    py.progressBar(gMainProgressBar, edit=True, status='Assigning shaders...')
    colourTime = time()
    
        
    cubeName = ph_nameLoop(generationNumber).getNextPrefix() + 'Cube'
    
    #find min and max values
    if stretchValues == True:
        colourNumMax = 0
        colourNumMin = shaderAmount
        if msgLevel > 2:
            print "  Calculating range in colour values"
        for i in range(numOfCubes):
            cube = cubeName
            if i > 0:
                cube += str(i)
            colourValue = py.getAttr( cube+'.colourValue' )
            if colourValue > colourNumMax:
                colourNumMax = colourValue
            elif colourValue < colourNumMin:
                colourNumMin = colourValue
        #calculated after to reduce processing
        colourNumMin = int( colourNumMin * shaderAmount - ( (colourNumMin * shaderAmount) - shaderAmount/2.0 ) / 5 )
        colourNumMax = shaderAmount - int( colourNumMax * shaderAmount - ( (colourNumMax * shaderAmount) - shaderAmount/2.0 ) / colourExponential )
        colourNumHalf = ( shaderAmount + colourNumMin ) / 2.0
        
    if msgLevel > 0:
        print "  Assigning shader to objects"
    
    oldShader = []
       
    for i in range(numOfCubes):
        
        #get cube name
        if i == 0:
            cube = cubeName
        else:
            cube = cubeName + str(i)
        newName = cube + 'Shape'
        
        #calculate colour to assign
        colourValue = py.getAttr( cube+'.colourValue' )
        colourNum = colourValue * shaderAmount - ( (colourValue * shaderAmount) - shaderAmount/2.0 ) / colourExponential
        
        if stretchValues == True:
            #stretch out the values from 0 to max
            if colourNum + 1 == colourNumHalf:
                factor = 0
            elif colourNum + 1 < colourNumHalf:
                factor = ( -colourNumMin / float( colourNum + 1 ) ) * colourNumMin
            elif colourNum + 1 > colourNumHalf:
                factor = ( colourNumMax / float( shaderAmount - colourNum + 1 ) ) * colourNumMax
        else:
            factor = 0
        
        colourNum = int(colourNum + factor)
        
        #fix to stop negative numbers
        if colourNum < 0:
            colourNum = -colourNum
        
        #set ratio of colours
        if colourRatio > 0.5:
            colourNum = int( colourNum + ( shaderAmount - colourNum ) ** ( colourRatio * 2 - 1 ) )
        elif colourRatio < 0.5:
            colourNum = int( colourNum - colourNum ** ( 1 - colourRatio * 2 ) )
        
        colourNum = int(round(colourNum,0))
        
        #stop invalid values
        if colourNum < 0:
            colourNum = 0
        elif colourNum >= shaderAmount:
            colourNum = shaderAmount - 1
            
        py.select( shaderName + str(colourNum), noExpand = True )
        
        #check previous shader
        try:
            oldShader.append(shaderSelect.split('n')[-1])
        except:
            oldShader.append(shaderAmount - 1)
            
        shaderSelect = py.ls( selection = True )[0]
        
        #stop big jumps
        if int(shaderSelect.split('n')[-1]) < int(oldShader[-1]) - 1:
            py.select( shaderName + str(int(oldShader[-1])-1), noExpand = True )
            #overrides initial calculation for extra smoothness
            for i in range(smoothOverride):
                if len(oldShader) > (i+1):
                    if int(oldShader[-1]) != int(oldShader[-2-i]):
                        py.select( shaderName + str(int(oldShader[-1])), noExpand = True )
            shaderSelect = py.ls( selection = True )[0]
          
        #link shader to object
        py.select( newName )
        cubeSelect = py.ls(selection=True)[0].instObjGroups[0]
        py.defaultNavigation( source = shaderSelect, destination = cubeSelect, connectToExisting = True )
        
        #percentage complete
        if time() - percentTimeCurrent > percentTime:
            percentTimeCurrent = time()
            percentCompleted = (float(loop)/loops)+(1.0/loops)*((1-colourPercent/100.0)+((colourPercent/100.0)*((i+1.0)/numOfCubes)))
            py.progressBar(gMainProgressBar, edit=True, progress=float(ph_decimalConvert(percentCompleted)))
                
            if py.progressBar(gMainProgressBar, query=True, isCancelled=True ) == True :
                break
            
        if displayCubeUpdates == True:
            if time() - cubeTimeCurrent > cubeUpdateTime:
                cubeTimeCurrent = time()
                py.currentTime( currentKey, edit = True, update = True)
    
    if msgLevel > 1:
        print "   Shader placement took " + ph_timeOutput(colourTime, time())
    
    return percentTimeCurrent, cubeTimeCurrent
    


def ph_timeOutput(startTime, endTime):

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
    
def ph_direction(direction,distance,cubeLoc,listOfPoints,mainDirection,directionRetry,quickGeneration):
    invalid = 0
    
    #stop generation in certain direction
    if mainDirection == 'left' or mainDirection == '-x':
        while direction == 1:
            direction = rd.randint(1,6)
        while direction != 2 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    elif mainDirection == 'right' or mainDirection == 'x':
        while direction == 2:
            direction = rd.randint(1,6)
        while direction != 1 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    elif mainDirection == 'backwards' or mainDirection == '-z':
        while direction == 3:
            direction = rd.randint(1,6)
        while direction != 4 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    elif mainDirection == 'forwards' or mainDirection == 'z':
        while direction == 4:
            direction = rd.randint(1,6)
        while direction != 3 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    elif mainDirection == 'down' or mainDirection == '-y':
        while direction == 5:
            direction = rd.randint(1,6)
        while direction != 6 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    elif mainDirection == 'up' or mainDirection == 'y':
        while direction == 6:
            direction = rd.randint(1,6)
        while direction != 5 and rd.uniform(0,1) < directionRetry:
            direction = rd.randint(1,6)
        if directionRetry < 0 and rd.uniform(-1,0) > directionRetry:
            direction = rd.randint(1,6)
    
    #store the new location
    if direction == 1:
        newLoc = [distance + cubeLoc[0], cubeLoc[1], cubeLoc[2]]
    elif direction == 2:
        newLoc = [-distance + cubeLoc[0], cubeLoc[1], cubeLoc[2]]
    elif direction == 3:
        newLoc = [cubeLoc[0], cubeLoc[1], distance + cubeLoc[2]]
    elif direction == 4:
        newLoc = [cubeLoc[0], cubeLoc[1], -distance + cubeLoc[2]]
    elif direction == 5:
        newLoc = [cubeLoc[0], distance + cubeLoc[1], cubeLoc[2]]
    elif direction == 6:
        newLoc = [cubeLoc[0], -distance + cubeLoc[1], cubeLoc[2]]
    
    #check if exists
    if quickGeneration == True:
        for i in range(len(listOfPoints)-1):
            if newLoc == listOfPoints[i]:
                invalid = 1
    else:
        accuracy = 2
        a = pow(10.0,accuracy)
        check = '['+str(int(newLoc[0]*a)/a)+','+str(int(newLoc[1]*a)/a)+','+str(int(newLoc[2]*a)/a)+']'
        for i in range(len(listOfPoints)-1):
            if '['+str(int(listOfPoints[i][0]*a)/a)+','+str(int(listOfPoints[i][1]*a)/a)+','+str(int(listOfPoints[i][2]*a)/a)+']' == check:
                invalid = 1
    
    return newLoc, invalid

def ph_validateShaderColours(shaderColours,colourDetail):
    #stop invalid colours from increasing smoothness
    shaderColours.reverse()
    invalidColours = ph_createShader(1,shaderColours,True)
    if len(shaderColours) == 1:
        colourDetail = 1
    shaderAmount = (len(shaderColours) - invalidColours) * colourDetail
    if shaderAmount == 0:
        shaderColours = ['grey']
        colourDetail = 1
        shaderAmount = 1
        print "No valid colours, setting shader to " + shaderColours[0]
    
    #create shaders
    shaderName = ph_createShader(shaderAmount,shaderColours)
    
    return shaderColours, colourDetail, shaderAmount, shaderName
    
    
def ph_setColours():
    
    #store colour values
    colourLightRed = [1,0.5,0.5,'lightred','lrd']
    colourRed = [1,0,0,'red','rd']
    colourDarkRed = [0.5,0,0,'darkred','drd']
    
    colourLightGreen = [0.5,1,0.5,'lightgreen','lgrn']
    colourGreen = [0,1,0,'green','grn']
    colourDarkGreen = [0,0.5,0,'darkgreen','dgrn']
    
    colourLightBlue = [0.5,0.5,1,'lightblue','lblu']
    colourBlue = [0,0,1,'blue','blu']
    colourDarkBlue = [0,0,1.5,'darkblue','dblu']
    
    colourLightYellow = [1,1,0.5,'lightyellow','lylw']
    colourYellow = [1,1,0,'yellow','ylw']
    colourDarkYellow = [0.5,0.5,0,'darkyellow','dlw']
    
    colourLightMagenta = [1,0.5,1,'lightmagenta','lmgt']
    colourMagenta = [1,0,1,'magenta','mgt']
    colourDarkMagenta = [0.5,0,0.5,'darkmagenta','dmgt']
    
    colourLightCyan = [0.5,1,1,'lightcyan','lcyn']
    colourCyan = [0,1,1,'cyan','cyn']
    colourDarkCyan = [0,1,1,'darkcyan','dcyn']
    
    colourLightOrange = [1,0.7,0,'lightorange','lorg']
    colourOrange = [1,0.5,0,'orange','org']
    colourDarkOrange = [1,0.3,0,'darkorange','dorg']
    
    colourLightPurple = [0.7,0,0.7,'lightpurple','lprpl']
    colourPurple = [0.5,0,0.5,'purple','prpl']
    colourDarkPurple = [0.3,0,0.3,'darkpurple','dprpl']
    
    colourLightGrey = [0.7,0.7,0.7,'lightgrey','lgry']
    colourGrey = [0.5,0.5,0.5,'grey','gry']
    colourDarkGrey = [0.3,0.3,0.3,'darkgrey','dgry']
    
    colourLightBrown = [0.4,0.3,0,'lightbrown','lbrn']
    colourBrown = [0.3,0.2,0,'brown','brn']
    colourDarkBrown = [0.2,0.1,0,'darkbrown','dbrn']
    
    colourWhite = [1,1,1,'white','wit']
    colourBlack = [0,0,0,'black','blk']
    
    colourStore = []
    colourStore.append(colourLightRed)
    colourStore.append(colourRed)
    colourStore.append(colourDarkRed)
    colourStore.append(colourLightGreen)
    colourStore.append(colourGreen)
    colourStore.append(colourDarkGreen)
    colourStore.append(colourLightBlue)
    colourStore.append(colourBlue)
    colourStore.append(colourDarkBlue)
    colourStore.append(colourLightYellow)
    colourStore.append(colourYellow)
    colourStore.append(colourDarkYellow)
    colourStore.append(colourLightMagenta)
    colourStore.append(colourMagenta)
    colourStore.append(colourDarkMagenta)
    colourStore.append(colourLightCyan)
    colourStore.append(colourCyan)
    colourStore.append(colourDarkCyan)
    colourStore.append(colourLightOrange)
    colourStore.append(colourOrange)
    colourStore.append(colourDarkOrange)
    colourStore.append(colourLightGrey)
    colourStore.append(colourGrey)
    colourStore.append(colourDarkGrey)
    colourStore.append(colourLightBrown)
    colourStore.append(colourBrown)
    colourStore.append(colourDarkBrown)
    colourStore.append(colourBlack)
    colourStore.append(colourWhite)
    
    return colourStore

def ph_setViewport():
    py.runtime.ActivateViewport20()
    py.setAttr( 'hardwareRenderingGlobals.ssaoEnable', 1 )
    py.setAttr( 'hardwareRenderingGlobals.multiSampleEnable', 1 )
    py.setAttr( 'hardwareRenderingGlobals.motionBlurEnable', 1 )
    py.runtime.DisplayWireframe(all=True)
        

def ph_createShader(max,colourInputTemp,validate=False):
    colourStore = ph_setColours()
    
    #remove any spaces
    colourInput = []
    for i in range(len(colourInputTemp)):
        colourInput.append( str(colourInputTemp[i]) )
    
    #match colour name with list, store shader name
    colourList = []
    shaderName = ''
    surfaceShaderName = 'surface'
    
    #match colours to values
    numColours = 0
    
    for i in range(len(colourInput)):
        for j in range(len(colourStore)):
            if str(colourInput[i].lower()) == str(colourStore[j][3]).lower():
                
                numColours += 1
                
                #store colour values
                colourList.append([colourStore[j][0],colourStore[j][1],colourStore[j][2]])
                
                #create names
                addLetter = colourStore[j][4]
                try:
                    shaderName = addLetter + str(shaderName)[0].capitalize()+str(shaderName)[1-len(shaderName):len(shaderName)]
                except:
                    shaderName = addLetter + str(shaderName).capitalize()
                surfaceShaderName = addLetter + addLetter + str(surfaceShaderName)[0].capitalize()+str(surfaceShaderName)[1-len(surfaceShaderName):len(surfaceShaderName)]
    
    if validate == True:
        return len(colourInput) - numColours
    else:
        #check for already existing materials
        try:
            1/numColours
            valid = True
            
        except:
            valid = False
           
        if valid == True:
            #fix for single colours
            firstValue = colourList[0]
            colourList.append(firstValue)
            colourList.append([0,0,0])
            
            shaderName = shaderName + str(max) + 'n'
            surfaceShaderName = surfaceShaderName + str(max) + 'n'
            print 'Shader name: ' + shaderName
            
            #check if exists
            print
            try:
                py.select( shaderName + '0' )
                exists = True
                print " Shader already exists"
                
            except:
                exists = False
                print " Shader doesn't exist"
            
            if exists == False:
                
                newTime = time()
                for i in range(max):
                
                    #temporary values to work with increments
                    maxNew= numColours + max - 2
                    if numColours > 1:
                        maxTemp = maxNew/(numColours-1.0)
                    else:
                        maxTemp = maxNew/(numColours)
                
                    #calculate numbers to use
                    count = 0
                    percentage = i/(maxTemp-1.0)
                    while percentage >= 1:
                        count += 1
                        percentage -= 1
                    
                    #calculate colour values
                    percentage = (i-(maxTemp*count)+count)/(maxTemp-1.0)
                    
                    redValue = colourList[count][0] - (colourList[count][0]-colourList[count+1][0]) * percentage
                    greenValue = colourList[count][1] - (colourList[count][1]-colourList[count+1][1]) * percentage
                    blueValue = colourList[count][2] - (colourList[count][2]-colourList[count+1][2]) * percentage
                    
                    #create shader
                    newShader = py.shadingNode("lambert", asShader=True, name = shaderName + str(i))
                    newShader.color.set([redValue,greenValue,blueValue], type = "double3")
                    
                    #link with surfaceshader
                    newSurfaceShader = py.sets( renderable=True, noSurfaceShader=True, empty=True, name=surfaceShaderName + str(i) )
                    py.connectAttr(newShader.outColor,newSurfaceShader.surfaceShader)
                    
                    if msgLevel > 3:
                        print '   Creating shader (' + str(i+1) + ' of ' + str(max) + ')'
                        
                    elif msgLevel > 2:
                        if i == 0:
                            print '   Creating shader (' + str(i+1) + ' of ' + str(max) + ')'
                        elif time() - 0.5 > newTime:
                            print '   Creating shader (' + str(i+1) + ' of ' + str(max) + ')'
                            newTime = time()
                        elif i == max - 1:
                            print '   Creating shader (' + str(i+1) + ' of ' + str(max) + ')'
                    
                    elif msgLevel > 0:
                        if i == 0:
                            print '   Creating shaders'
        print
        return shaderName


def ph_createTrackingCam(startTime,cubeSize,startingLoc):
    
    #get time
    sceneStartTime = py.playbackOptions( q = True, ast = True)
    if startTime > sceneStartTime:
        startTime = sceneStartTime
       
    #set variables
    fullCircle = math.radians(360)
    spirals = 2
    height = 150
    size = 14 * cubeSize ** 0.75
    accuracy = 5 #number of points per calculation
    endLoops = 300 #number of circles to build at end
    
    #calculate number of steps
    steps = spirals*8*accuracy
    
    #check accuracy value
    if accuracy < 1:
        accuracy = 1
    else:
        accuracy = int(accuracy)
    
    #build spiral
    spiralPoints=[]   
    for j in range(0, steps + 1):
        
        #get floating point values for j
        m = float(j)
        i = m
        if m < 0:
            i = -1/(m-1)
        if m == 0:
            i = 0.5
           
        #calculation
        spiralStepNum = (i/steps)
        locx = math.sin(spiralStepNum * fullCircle * spirals) * (size+spiralStepNum*200) * size ** 0.5
        locz = math.cos(spiralStepNum * fullCircle * spirals) * (size+spiralStepNum*200) * size ** 0.5
        
        #store values
        heightValue = i*height/steps
        pointInfo = [ locx, heightValue, locz ]
        spiralPoints.append( pointInfo )
    
    highNum = spiralPoints[-1][0]
    tempSpiralPoints = []
    for j in range(0, steps):
        
        #get floating point values for j
        m = float(j)
        i = m
        if m < 0:
            i = -1/(m-1)
        if m == 0:
            i = 0.5
            
        #calculation
        circleStepNum = (i/steps)
        locx = math.sin(circleStepNum * fullCircle * spirals) * (size+spiralStepNum*200) * size ** 0.5
        locz = math.cos(circleStepNum * fullCircle * spirals) * (size+spiralStepNum*200) * size ** 0.5
    
        #store values
        pointInfo = [ locx, height, locz ]
        tempSpiralPoints.append( pointInfo )
        
    #repeat circles
    for i in range(0,endLoops):
        for j in range(len(tempSpiralPoints)):
            spiralPoints.append(tempSpiralPoints[j])
    
    #set up objects
    cam = py.camera(n='generationCam', focalLength = 20)
    camPath = cmds.curve( p = spiralPoints, n='camMotionPath' )
    py.move( camPath, [startingLoc[0]-(45 * cubeSize ** 0.75), (20 * cubeSize ** 0.75)/2 + startingLoc[1], startingLoc[2]])
    py.rotate( camPath, [0,rd.uniform(-20,20),rd.uniform(-15,0)])
    py.move( 'tempLocator', [startingLoc[0],startingLoc[1],startingLoc[2]], absolute = True )
    py.select( cam[0] )
    py.select( camPath, add = True)
    
    #build motion path
    pathAnim = py.pathAnimation( fractionMode = True, bank = False, follow = True, followAxis = 'x', upAxis = 'y', worldUpType = 'vector', worldUpVector = [0,1,0], startTimeU = startTime, endTimeU = 8589934 )
    py.selectKey(pathAnim + '_uValue')
    py.keyTangent( pathAnim + '_uValue', e = True, a = True, t = (startTime,startTime), outWeight = 70000 )
    py.lookThru( cam[0] )
    
    #set to look at centre
    py.cycleCheck( e = False )
    py.disconnectAttr( pathAnim + '.rotateX', cam[0] + '.rotateX' )
    py.setAttr( cam[0] + '.rotateX', -7.5 )
    py.disconnectAttr( pathAnim + '.rotateZ', cam[0] + '.rotateZ' )
    py.setAttr( cam[0] + '.rotateZ', 0 )
    py.aimConstraint( 'tempLocator', cam[0], o = (0,-90,0) )
    
    py.hide( cam[0], camPath )
        
    return cam[0],camPath

    #file names
def ph_fileName(type):
    
    generationCountFile = 'generation_count'
    pointInfoStore = 'generation_pointinfo'
    
    if str(type).lower() == 'count':
        return generationCountFile
    elif str(type).lower() == 'pointinfo':
        return pointInfoStore
        
class ph_nameLoop:
    
    def __init__(self,startAt=0):
        self.letters = list('abcdefghijklmnopqrstuvwxyz')
        self.currentNumber = startAt
    
    def getNextPrefix(self):
        
        remainder = self.currentNumber
        iteration = 1
        iterationSize = len(self.letters)
        while remainder>=iterationSize:
            remainder -= iterationSize
            iterationSize *= len(self.letters)
            iteration  += 1
            
        result = ''
        for i in range(iteration):
            result = self.letters[remainder % len(self.letters)]+result
            remainder =remainder / len(self.letters)
            
        self.currentNumber +=1
            
        return result

class listGroups():
    
    windowName = "groupUI"
    
    @classmethod
    def display(cls):
        
        try:
            py.deleteUI(cls.windowName, window=True)
            py.windowPref(cls.windowName, remove=True )
        except:
            pass
            
        outlinerFilter = py.itemFilter(byName = '*CubeGroup')
        
        #count cameras
        ignore = ['Shape','translate','rotate','scale','visibility']
        allObjects = py.ls()
        numberOfGroups = 0
        for i in range( len(allObjects) ):
            if 'CubeGroup' in str(allObjects[i]):
                invalid = 0
                for ignoreName in ignore:
                    if ignoreName in str(allObjects[i]):
                        invalid += 1
                if invalid == 0:
                    numberOfGroups += 1
                    
        if numberOfGroups == 0:
            numberOfGroups += 1
        
        #display window
        winGroups = py.window(cls.windowName, title="Available groups")
        height = (15/numberOfGroups) + 75 + (25 * numberOfGroups) ** 0.975
        if height > 600:
            height = 600
        py.frameLayout( labelVisible=False, h = height )
        panel = py.outlinerPanel()
        outliner = py.outlinerPanel(panel, query=True,outlinerEditor=True)
        py.outlinerEditor( outliner, edit=True, showShapes=False, showAttributes=False, showConnected=False, showDagOnly=True, ignoreDagHierarchy=False, displayMode = 'List', filter = outlinerFilter )
        py.showWindow()

class userInterface(object):
    
    #set up user interface
    windowName = "generationUI"
    
    @classmethod
    def display(cls):

        if py.window(cls.windowName, exists=True):
            py.deleteUI(cls.windowName, window=True)
        
        displayHiddenValues = False
        
        main_window = py.window(cls.windowName, title="Generation", rtf=True, mxb=False, sizeable=False )
        py.rowColumnLayout(numberOfColumns=1)
        helpForkLength = "Sets the maximum number of points to be created for each fork."
        helpNumForks = "Sets the number of forks to generate."
        help3DGeneration = "Enables generation in the Y axis."
        helpDeleteCubes = "Deletes all cubes on completion, reducing the memory usage of the scene."
        helpQuickGeneration = "Disable if there's a problem with cubes overlapping."
        helpReduceSize = "Sets the cubes to reduce size as it gets further into the generation."
        helpGenerate = "Starts a generation."
        helpAnimation = "Sets the cubes to appear over time."
        helpAutoSet = "Automatically set animation values based on other variables."
        helpCubeSkip = "Sets the number of cubes to appear for each frame."
        helpFrameSpacing = "Sets the amount of frames between each key."
        helpAnimMultiplier = "Sets the maximum time between which loops will be animated."
        helpLoops = "For use if multiple generations are needed."
        helpNumLoops = "Sets the number of times to run the generation."
        helpAutoDistance = "Automatically calculates the area to generate loops in."
        helpUserDistance = "Sets the areas maximum +/- values to generate loops in."
        helpColours = "Enables the generation of colours."
        helpEnterColours = "Type in colours separated by commas, light and dark variations are accepted."
        helpSmoothness = "Determines the number of smoothing steps between each colour."
        helpRatio = "Weights values towards one end of the range."
        helpUpdateShader = "Places new shaders over the previous generation"
        helpStartingLoc = "Choose point to start generation."
        helpGetLoc = "Sets the starting location to that of the current selection."
        helpCubeSize = "Sets the size of cubes"
        helpMinPos = "Sets the minimum location on a fork where a new fork can be created."
        helpDirection = "Choose a direction for the generation to follow."
        colourList = ph_setColours()
        cls.textTip = py.text(label=userInterface.tipList(), align = "left") 
        py.popupMenu( button = 2, postMenuCommand = "userInterface.nextTip()"  ) 
        mainLayout = py.rowColumnLayout(numberOfColumns=5 )
        py.text(label='  ')  
        py.text(label='---------------------------main---------------------------', align="left", enable = False) 
        py.text(label='      ')  
        py.text(label='--------------------------animation--------------------------', align="left", enable = False) 
        py.text(label='  ')  
        py.text(label=' ')  
        py.text( label = "   Set length of forks ", align = "left" )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpForkLength )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.sliderForkLength = py.floatSliderGrp(parent=mainLayout, field = True, enable=True, min = 2, max = 1000, fmn = 2, fmx = sys.maxint, pre = 0, changeCommand = 'userInterface.calculateIncrease()')
        cls.sliderForkLength.setValue(300) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpForkLength )
        py.text(label=' ')
        cls.checkboxAnim = py.checkBox(parent=mainLayout, label="Create animation", value=True, changeCommand="userInterface.animCheckbox()", align="right")
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAnimation )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkboxAnimAutoSet = py.checkBox(parent=mainLayout, label="Automatically set values", value=True, changeCommand="userInterface.autoSetCheckbox()")
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAutoSet )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text( label = "   Set number of forks ", align = "left" )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpNumForks )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.sliderForkNum = py.floatSliderGrp(parent=mainLayout, field = True, enable=True, min = 0, max = 500, fmn = 1, fmx = sys.maxint, pre = 0, changeCommand = 'userInterface.calculateIncrease()')
        cls.sliderForkNum.setValue(50) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpNumForks )
        py.text(label=' ')  
        cls.textAutoSet = py.text(label='Multiplier for automatically set values  ', align = "right")  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAutoSet )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkbox3D = py.checkBox(parent=mainLayout, label="3D generation", value=True, align="right", changeCommand="userInterface.threeDimensions()", height = 22)
        py.popupMenu( button = 2 ) 
        py.menuItem( label=help3DGeneration )
        cls.tempText3D = py.text(label='0', visible = displayHiddenValues)  
        cls.sliderAnimAutoSet = py.floatSliderGrp(parent=mainLayout, field = True, enable=True, min = 0.001, max = 4, fmn = 0.001, fmx = sys.maxint, pre = 3)
        cls.sliderAnimAutoSet.setValue(1) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAutoSet )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkboxQuickGeneration = py.checkBox(parent=mainLayout, label="Quick generation", value=True, align="right", height = 22)
        py.popupMenu( button = 2 ) 
        cls.menuQuickGeneration = py.menuItem( label=helpQuickGeneration )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkboxBranch = py.checkBox(parent=mainLayout, label="Reduce in size", value=True, align="right", height = 22, changeCommand="userInterface.selectCurves2D()")
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpReduceSize )
        py.text(label=' ')  
        cls.textCubeSkip = py.text(label='Amount of cubes to update per frame ', align="right", enable = False)
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpCubeSkip )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.textQuickGeneration = py.text(label=' ', align = "left", enable = False)  
        userInterface.calculateIncrease()
        py.text(label=' ')   
        cls.sliderCubeSkip = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = 1, max = 20, fmn = 1, fmx = 100, pre = 1)
        cls.sliderCubeSkip.setValue(3)
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpCubeSkip )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.button = py.button( label = "Generate", command = py.Callback( userInterface.buttonPressed, "generate" ) )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpGenerate )
        py.popupMenu( button = 3 ) 
        cls.checkboxDeleteCubes = py.menuItem( label='Delete cubes', checkBox=False, command = "userInterface.deleteCubeCheckbox()" )
        cls.checkboxCreateCurves = py.menuItem( label='Create curves', checkBox=False, command = "userInterface.createCurves()")
        cls.checkboxSelectCurves = py.menuItem( label='Select curves', checkBox=True, enable=False )
        py.menuItem( d=True )
        cls.checkboxPreview = py.menuItem( label='Preview generation (slower)', checkBox = True, command = "userInterface.previewGeneration('main')" )
        cls.checkboxEnableGrid = py.menuItem( label='Enable grid', checkBox = py.grid( query = True, toggle = True ), command = "userInterface.toggleGrid()" )
        cls.checkboxViewport = py.menuItem( label='High quality viewport', command = "userInterface.setViewport()" )
        py.text(label=' ')  
        cls.textFrameSpacing = py.text(label='Number of frames between each update ', align="right", enable = False) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpFrameSpacing )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')    
        py.text(label=' ')  
        cls.sliderFrameSpacing = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = 1, max = 4, fmn = 1, fmx = 100, pre = 1)
        cls.sliderFrameSpacing.setValue(1) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpFrameSpacing )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label='---------------------------loops--------------------------', align="left", enable = False)  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkboxLoops = py.checkBox(parent=mainLayout, label="Enable loops", value=False, changeCommand="userInterface.enableLoops()", align="right")
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpLoops )
        py.text(label=' ')  
        cls.textAnimSpacing = py.text(label='Multiplier for animation spacing between loops ', align="right", enable = False)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAnimMultiplier )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ') 
        cls.sliderAnimSpacing = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = 0.001, max = 4, fmn = 0.001, fmx = sys.maxint, pre = 3)
        cls.sliderAnimSpacing.setValue(1) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAnimMultiplier )
        py.text(label=' ')  
        py.text(label=' ') 
        cls.textNumLoops = py.text(label='   Set number of loops ', align="left", enable = False)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpNumLoops )
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        py.text(label=' ')  
        cls.sliderLoops = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = 1, max = 20, fmn = 1, fmx = sys.maxint, pre = 0)
        cls.sliderLoops.setValue(1)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpNumLoops )
        py.text(label=' ')  
        py.text(label='-----------------------------misc----------------------------', align="left", enable = False)   
        py.text(label=' ')  
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ')  
        py.text(label='Starting location X ', align="right")  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.checkboxAutoDistance = py.checkBox(parent=mainLayout, label="Auto set distance (or set any value below to -1)", value=True, changeCommand="userInterface.setDistance()", align="right", enable = False)
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpAutoDistance )
        py.text(label=' ')  
        cls.sliderStartX = py.floatSliderGrp(parent=mainLayout, field = True, min = -1000, max = 1000, fmn = -sys.maxint, fmx = sys.maxint, pre = 2)
        cls.sliderStartX.setValue(0) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ')  
        py.text(label=' ') 
        cls.textSizeX = py.text(label='                                 Size X', align="left", enable = False) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance )
        py.text(label=' ')  
        py.text(label='Starting location Y ', align="right") 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ')  
        py.text(label=' ')  
        cls.sliderSizeX = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = -1, max = 1500, fmn = -1, fmx = sys.maxint, pre = 0)
        cls.sliderSizeX.setValue(500) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance )
        py.text(label=' ')  
        cls.sliderStartY = py.floatSliderGrp(parent=mainLayout, field = True, min = -1000, max = 1000, fmn = -sys.maxint, fmx = sys.maxint, pre = 2)
        cls.sliderStartY.setValue(0)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ')  
        py.text(label=' ') 
        cls.textSizeY = py.text(label='                                 Size Y', align="left", enable = False)
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance )
        py.text(label=' ')         
        py.text(label='Starting location Z ', align="right") 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ')  
        py.text(label=' ') 
        cls.sliderSizeY = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = -1, max = 1500, fmn = -1, fmx = sys.maxint, pre = 0)
        cls.sliderSizeY.setValue(500) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance )
        py.text(label=' ') 
        cls.sliderStartZ = py.floatSliderGrp(parent=mainLayout, field = True, min = -1000, max = 1000, fmn = -sys.maxint, fmx = sys.maxint, pre = 2)
        cls.sliderStartZ.setValue(0)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpStartingLoc )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.textSizeZ = py.text(label='                                 Size Z', align="left", enable = False) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        cls.sliderSizeZ = py.floatSliderGrp(parent=mainLayout, field = True, enable = False, min = -1, max = 1500, fmn = -1, fmx = sys.maxint, pre = 0)
        cls.sliderSizeZ.setValue(500) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUserDistance)
        py.text(label=' ') 
        cls.selectButton = py.button( label = 'Get location/size of selection' )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpGetLoc )
        py.popupMenu( button = 1 ) 
        py.menuItem( label='Get location', command="userInterface.getSelectionLoc()" )
        py.menuItem( d=True )
        py.menuItem( label='Get size', command="userInterface.getSelectionSize()" )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        cls.directionTempText = py.text(label='', visible = displayHiddenValues) 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label='----------------------------colours---------------------------', align="left", enable = False)   
        py.text(label=' ') 
        cls.directionButton = py.button( label = 'Choose direction of generation (default)' )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpDirection )
        py.popupMenu( button = 1 ) 
        py.radioCollection()
        cls.dropDownX = py.menuItem( label='Right (x)', radioButton=True, command="userInterface.directionX()")
        cls.dropDownXm = py.menuItem( label='Left (-x)', radioButton=True, command="userInterface.directionXm()" )
        cls.dropDownY = py.menuItem( label='Up (y)', radioButton=True, command="userInterface.directionY()" )
        cls.dropDownYm = py.menuItem( label='Down (-y)', radioButton=True, command="userInterface.directionYm()" )
        cls.dropDownZ = py.menuItem( label='Forwards (z)', radioButton=True, command="userInterface.directionZ()" )
        cls.dropDownZm = py.menuItem( label='Backwards (-z)', radioButton=True, command="userInterface.directionZm()" )
        py.menuItem( d=True )
        cls.manualLocation = py.menuItem( label='Custom (0.0, 0.0, 0.0)', radioButton=True, command="userInterface.customDirection(0,'')")
        #loops for each amount
        directions = ['x','y','z']
        amounts = [0.01,0.05,0.1,0.2,0.5,1.0]
        for j in range(len(directions)):
            py.menuItem( label=directions[j], subMenu=True  )
            for i in range( -len(amounts), len(amounts) ):
                if i < 0:
                    py.menuItem( label='+ ' + str(amounts[-i-1]), command="userInterface.customDirection('"+str(amounts[-i-1])+"','"+directions[j]+"')" )
                else:
                    if i == 0:
                        py.menuItem( d=True )
                    py.menuItem( label='- ' + str(amounts[i]), command="userInterface.customDirection('-"+str(amounts[i])+"','"+directions[j]+"')" )
            py.setParent( '..', menu=True )
        py.menuItem( d=True )
        py.menuItem( label='None', radioButton=True, command="userInterface.directionNone()" )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.checkboxColours = py.checkBox(parent=mainLayout, label="Enable colours", value=True, changeCommand="userInterface.enableColours()", align="right")
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpColours )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label='Size of cube ', align="right") 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpCubeSize )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourText = py.text(label='   Enter colours', align = 'left') 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpEnterColours )
        py.text(label=' ') 
        cls.sliderSize = py.floatSliderGrp(parent=mainLayout, field = True, min = 1, max = 10, fmn = 1, fmx = sys.maxint, pre = 0)
        cls.sliderSize.setValue(1)  
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpCubeSize )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourTextField = py.textField( text = 'black, white')
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpEnterColours )
        py.popupMenu( button = 3 ) 
        
        #calculate sub menu
        actualColourList = []
        numColours = []
        for i in range(len(colourList)):
            solidColour = colourList[i][3].replace('light','').replace('dark','')
            if solidColour == colourList[i][3]:
                otherShades = 0
                try:
                    if colourList[i-1][3].replace('light','') == solidColour:
                        otherShades += 1
                    if colourList[i+1][3].replace('dark','') == solidColour:
                        otherShades += 1
                except:
                    pass
                    
                numColours.append( otherShades )
                actualColourList.append( colourList[i][3] )
                
        #create menu
        py.menuItem( label = 'Clear', command='userInterface.clearColour()' )
        py.menuItem( d=True )
        for i in range(len(actualColourList)):
            
            if numColours[i] > 0:
                py.menuItem( label = actualColourList[i].capitalize(), subMenu = True )
            for j in range(len(colourList)):
                if actualColourList[i] == colourList[j][3].replace('light','').replace('dark',''):
                    
                    #set colours to light/dark/normal
                    if numColours[i] > 0:
                        if colourList[j][3].replace('dark','') != colourList[j][3]:
                            newName = "Dark"
                        elif colourList[j][3].replace('light','') != colourList[j][3]:
                            newName = "Light"
                        else:
                            newName = "Normal"
                    else:
                        newName = colourList[j][3].capitalize()
                    py.menuItem( label = newName, command='userInterface.addColour("'+colourList[j][3]+'")' )
            py.setParent( '..', menu=True )
        py.menuItem( d=True )
        py.menuItem( label = 'Groups', subMenu = True )
        #add to these manually
        py.menuItem( label = 'Black/White', command='userInterface.clearColour(), userInterface.addColour("black, white")' )
        py.menuItem( label = 'Black/Green/White', command='userInterface.clearColour(), userInterface.addColour("black, green, white")' )
        py.menuItem( label = 'Black/Cyan/White', command='userInterface.clearColour(), userInterface.addColour("black, cyan, white")' )
        py.menuItem( label = 'Black/Magenta/White', command='userInterface.clearColour(), userInterface.addColour("black, magenta, white")' )
        py.menuItem( label = 'Red/Yellow', command='userInterface.clearColour(), userInterface.addColour("red, yellow")' )
        py.menuItem( label = 'Red/Yellow/Green', command='userInterface.clearColour(), userInterface.addColour("red, yellow, green")' )
        py.menuItem( label = 'Blue/Green', command='userInterface.clearColour(), userInterface.addColour("blue, green")' )
        py.menuItem( label = 'Blue/White', command='userInterface.clearColour(), userInterface.addColour("blue, white")' )
        py.menuItem( label = 'Orange/Magenta', command='userInterface.clearColour(), userInterface.addColour("orange, magenta")' )
        py.menuItem( label = 'Cyan/Magenta', command='userInterface.clearColour(), userInterface.addColour("cyan, magenta")' )
        py.menuItem( label = 'Magenta/Yellow', command='userInterface.clearColour(), userInterface.addColour("cyan, magenta")' )
        py.menuItem( label = 'Magenta/Cyan/Blue', command='userInterface.clearColour(), userInterface.addColour("magenta, cyan, blue")' )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label='Set minimum position of new forks (%)', align = 'right', enable = False) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpMinPos )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourDetailText = py.text(label='   Set smoothness of colour blending', align = 'left') 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpSmoothness )
        py.text(label=' ') 
        cls.minPosition = py.floatSliderGrp(parent=mainLayout, field = True, min = 0, max = 100, fmn = 0, fmx = 100, pre = 2, enable = False)
        cls.minPosition.setValue(0) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpMinPos )
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourDetail = py.floatSliderGrp(parent=mainLayout, field = True, min = 5, max = 25, fmn = 1, fmx = sys.maxint, pre = 0)
        cls.colourDetail.setValue(10) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpSmoothness )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourWeightsText = py.text(label='   Set ratio of colours', align = 'left') 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpRatio )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        cls.colourWeights = py.floatSliderGrp(parent=mainLayout, field = True, min = 0.001, max = 0.999, fmn = 0.001, fmx = 0.999, pre = 3)
        cls.colourWeights.setValue(0.5) 
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpRatio )
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        py.text(label=' ') 
        cls.shaderButton = py.button( label = "Update shaders (right click for selection)", command = py.Callback( userInterface.buttonPressed, "colours" ) )
        py.popupMenu( button = 2 ) 
        py.menuItem( label=helpUpdateShader )
        py.popupMenu( button = 3 ) 
        cls.listAllGroups = py.menuItem( label = 'Show list of cube groups', command = "listGroups.display()" )
        py.menuItem( d=True )
        cls.checkboxUpdateShaders = py.menuItem( label = 'Preview generation (slower)', checkBox=True, command = "userInterface.previewGeneration('colours')")
        cmds.showWindow(cls.windowName)
        
    @classmethod   
    #get size of selection
    def getSelectionSize(cls):
        
        sel = py.ls(selection = True)
        numSelected = len(sel)
        
        #validation
        for i in range (0, numSelected ):
            try:
                sel[i].getBoundingBox()
            except:
                numSelected = 0
                
        if numSelected > 0:
            totalSize = 0
            for i in range (0, numSelected ):
                objBB = sel[i].getBoundingBox()
                objWidth = objBB.width()
                objHeight = objBB.height()
                objDepth = objBB.depth()
                totalSize += (objWidth+objHeight+objDepth)/3
            totalSize = int(totalSize/numSelected)
            print "Set size to " + str(totalSize)
            py.floatSliderGrp(cls.sliderSize, edit=True).setValue(totalSize/numSelected)
                
    @classmethod   
    def getSelectionLoc(cls):
        
        #set variables to inf and -inf
        objXMin=1e1000
        objXMax=-1e1000
        objYMin=1e1000
        objYMax=-1e1000
        objZMin=1e1000
        objZMax=-1e1000
        
        sel = py.ls(selection = True)
        numSelected = len(sel)
        
        #validation
        for i in range (0, numSelected ):
            try:
                sel[i].getBoundingBox()
            except:
                numSelected = 0
                
        if numSelected > 0:
            for i in range (0, numSelected ):
               
                #get bounding box and position information
                objBB = sel[i].getBoundingBox()
                objWidth = objBB.width()
                objHeight = objBB.height()
                objDepth = objBB.depth()
                objLoc = sel[i].getTranslation()
           
                #determine max values
                if objXMin > objLoc.x - (objWidth / 2):
                    objXMin = objLoc.x - (objWidth / 2)
                if objYMin > objLoc.y - (objHeight / 2):
                    objYMin = objLoc.y - (objHeight / 2)
                if objZMin > objLoc.z - (objDepth / 2) :
                    objZMin = objLoc.z - (objDepth / 2)
                   
                if objXMax < objLoc.x + (objWidth / 2):
                    objXMax = objLoc.x + (objWidth / 2)
                if objYMax < objLoc.y + (objHeight / 2):
                    objYMax = objLoc.y + (objHeight / 2)
                if objZMax < objLoc.z + (objDepth / 2):
                    objZMax = objLoc.z + (objDepth / 2)
                    
                xLoc = int( (( objXMax + objXMin ) / 2)*100 )/100.0
                yLoc = int( (( objYMax + objYMin ) / 2)*100 )/100.0
                zLoc = int( (( objZMax + objZMin ) / 2)*100 )/100.0
                
                py.floatSliderGrp(cls.sliderStartX, edit=True).setValue(xLoc)
                py.floatSliderGrp(cls.sliderStartY, edit=True).setValue(yLoc)
                py.floatSliderGrp(cls.sliderStartZ, edit=True).setValue(zLoc)
            print "Set location to " + str(xLoc) + ', ' + str(yLoc) + ', ' + str(zLoc)
        
        else:
            print "Nothing is selected"

        
    @classmethod   
    def buttonPressed(cls, submit):
       
        if submit == "colours":
            selection = py.ls(selection = True)
            py.select(clear = True)
            #colourLists = eval(ph_readFile( ph_fileName('pointinfo') ))
            shaderColours, colourDetail, shaderAmount, shaderName = ph_validateShaderColours(cls.colourTextField.getText().replace(' ','').split(','),int(cls.colourDetail.getValue()))
            
            timeList = [0,0,py.menuItem(cls.checkboxUpdateShaders, query=True, checkBox=True)]
            colourList = [shaderName,shaderAmount,1 - cls.colourWeights.getValue(),int(cls.colourDetail.getValue()),shaderColours]
            
            #calculate if the stored information is wrong, or if invalid items are selected
            valid = 0
            valid2 = 1
            validAmount = [0,1]
            for i in range(len(selection)):
                validAmount = [validAmount[0],1]
                try:
                    generalList = [0,1,int(py.getAttr( selection[i]+'.id' ))]
                except:
                    validAmount = [validAmount[0],0]
                if validAmount[1] == 1:
                    try:
                        ph_colourAllObjects(generalList,timeList,colourList)
                        validAmount = [1,validAmount[1]]
                    except:
                        if validAmount[0] <= 0:
                            validAmount = [-1,validAmount[1]]
                          
            if validAmount[0] == -1:
                print "Error with stored information. Please run a new generation."
            elif validAmount[0] == 0:
                print "No valid groups selected, running on latest generation."
                try:
                    generalList = [0,1,int(py.getAttr('tempLocator.last'))]
                    ph_colourAllObjects(generalList,timeList,colourList)
                except:
                    print "Problem with latest generation. Please run a new one."
            py.select(selection)
                
        if submit == "generate":
            
            if cls.checkboxLoops.getValue() == False:
                loops = 1
            else:
                loops = int(cls.sliderLoops.getValue())
                
            postValues = []
            postValues.append(cls.sliderForkLength.getValue()) #forkLength
            postValues.append(cls.checkboxAnim.getValue()) #keyCube
            postValues.append(cls.checkboxAnimAutoSet.getValue()) #autoSet
            postValues.append(cls.sliderForkNum.getValue()) #forks
            postValues.append(cls.checkbox3D.getValue()) #threeDimensions
            postValues.append(cls.sliderCubeSkip.getValue()) #cubeSkip
            postValues.append(cls.sliderFrameSpacing.getValue()) #frameSpacing
            postValues.append(loops) #loops
            postValues.append(cls.sliderAnimSpacing.getValue()) #animSpacing
            postValues.append(cls.sliderStartX.getValue()) #startingLocX
            postValues.append(cls.sliderStartY.getValue()) #startingLocY
            postValues.append(cls.sliderStartZ.getValue()) #startingLocZ
            postValues.append(cls.sliderSizeX.getValue()) #maxDistX
            postValues.append(cls.sliderSizeY.getValue()) #maxDistY
            postValues.append(cls.sliderSizeZ.getValue()) #maxDistZ
            postValues.append(cls.checkboxAutoDistance.getValue()) #autoMaxDist
            postValues.append(cls.checkboxQuickGeneration.getValue()) #quickGeneration
            postValues.append(cls.sliderAnimAutoSet.getValue()) #autoSetDistance
            postValues.append(cls.sliderSize.getValue()) #cubeSize
            postValues.append(cls.checkboxBranch.getValue()) #branch
            postValues.append(cls.directionTempText.getLabel()) #mainDirection
            postValues.append(cls.checkboxColours.getValue()) #colourObjects
            postValues.append(cls.colourTextField.getText()) #shaderColours
            postValues.append(int(cls.colourDetail.getValue())) #colourDetail
            postValues.append(1 - cls.colourWeights.getValue()) #colourRatio
            postValues.append(py.menuItem(cls.checkboxDeleteCubes, query=True, checkBox=True)) #deleteCubes
            postValues.append(py.menuItem(cls.checkboxCreateCurves, query=True, checkBox=True)) #createCurves
            postValues.append(py.menuItem(cls.checkboxSelectCurves, query=True, checkBox=True)) #selectCurves
            postValues.append(py.menuItem(cls.checkboxPreview, query=True, checkBox=True)) #previewAnimation
            
            ph_mainCode(postValues)
    
    @classmethod
    def setViewport(cls):
        ph_setViewport()
    
    @classmethod
    def previewGeneration(cls,generation):
        if generation == 'main':
            py.menuItem(cls.checkboxUpdateShaders, edit=True, checkBox = py.menuItem(cls.checkboxPreview, query=True, checkBox=True) )
        elif generation == 'colours':
            py.menuItem(cls.checkboxPreview, edit=True, checkBox = py.menuItem(cls.checkboxUpdateShaders, query=True, checkBox=True) )
        
    @classmethod
    def toggleGrid(cls):
        py.grid( toggle = (py.grid( toggle=True, query = True) == 0))
        
    #grey out options
    @classmethod
    def calculateIncrease(cls):
        forks = py.floatSliderGrp(cls.sliderForkNum, query=True, value=True)
        forkLength = py.floatSliderGrp(cls.sliderForkLength, query=True, value=True)
        if forks == 0:
            forks = 1
        totalAmount = ( forks * forkLength ) / 500
        increaseSpeed = totalAmount * ( 1 + 1/totalAmount )
        increaseDecimal = int(increaseSpeed*10)/10.0
        if len(str(int(increaseDecimal))) > 1:
            increaseDecimal = int(increaseDecimal)
        py.text(cls.textQuickGeneration, edit=True, label = " Quick generation can be up to " + str(increaseDecimal) + "x faster" )
    
    @classmethod
    def enableColours(cls):
        #animation auto set checkbox
        enableValue = py.checkBox(cls.checkboxColours, query=True, value=True)
        py.floatSliderGrp(cls.colourDetail, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.colourWeights, edit=True, enable=enableValue)
        py.text(cls.colourText, edit=True, enable=enableValue) 
        py.text(cls.colourDetailText, edit=True, enable=enableValue) 
        py.text(cls.colourWeightsText, edit=True, enable=enableValue) 
        py.textField(cls.colourTextField, edit=True, enable=enableValue) 
        py.button(cls.shaderButton, edit=True, enable=enableValue)
    
    @classmethod
    def threeDimensions(cls):
        #3d checkbox
        enableValue = py.checkBox(cls.checkbox3D, query=True, value=True)
        py.menuItem( cls.dropDownY, enable=enableValue, edit=True )
        py.menuItem( cls.dropDownYm, enable=enableValue, edit=True )
        if enableValue == False:
            if py.menuItem( cls.dropDownY, query=True, rb = True ):
                py.text(cls.directionTempText, edit=True, label = 'disabledUp') 
                py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (up)' )
            if py.menuItem( cls.dropDownYm, query=True, rb = True ):
                py.text(cls.directionTempText, edit=True, label = 'disabledDown') 
                py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (down)' )
        else:
            if py.text(cls.directionTempText, query=True, label=True) == 'diabledUp':
                py.text(cls.directionTempText, edit=True, label = 'up') 
            elif py.text(cls.directionTempText, query=True, label=True) == 'diabledDown':
                py.text(cls.directionTempText, edit=True, label = 'down') 
        
        userInterface.selectCurves2D()

    @classmethod
    def selectCurves2D(cls):
        #select use curves
        enableValue = py.checkBox(cls.checkbox3D, query=True, value=True)
        if enableValue == True:
            enableValue = False
        elif py.checkBox(cls.checkboxBranch, query=True, value=True) == False:
            enableValue = True
            
        if enableValue == True and int(py.text(cls.tempText3D, query=True, label=True)) != 2:
            py.text(cls.tempText3D, edit=True, label=1) 
            
        if int(py.text(cls.tempText3D, query=True, label=True)) == 1:
            py.menuItem( cls.checkboxCreateCurves, edit=True, checkBox=enableValue )
        
    @classmethod
    def animCheckbox(cls):
        #create animation checkbox
        enableValue = py.checkBox(cls.checkboxAnim, query=True, value=True)
        autoSet = py.checkBox(cls.checkboxAnimAutoSet, query=True, value=True)
        py.checkBox(cls.checkboxAnimAutoSet, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.sliderAnimAutoSet, edit=True, enable = enableValue)
        py.floatSliderGrp(cls.sliderFrameSpacing, edit=True, enable = enableValue)
        py.floatSliderGrp(cls.sliderCubeSkip, edit=True, enable = enableValue)
        
        if py.checkBox(cls.checkboxLoops, query=True, value=True) == True:
            py.floatSliderGrp(cls.sliderAnimSpacing, edit=True, enable=enableValue)
            py.text(cls.textAnimSpacing, edit=True, enable=enableValue) 
            
        if autoSet == False:
            py.text(cls.textCubeSkip, edit=True, enable=enableValue)
            py.text(cls.textFrameSpacing, edit=True, enable=enableValue) 
            
            if enableValue == True:
                py.floatSliderGrp(cls.sliderAnimAutoSet, edit=True, enable = False)
                py.floatSliderGrp(cls.sliderFrameSpacing, edit=True, enable = True)
                py.floatSliderGrp(cls.sliderCubeSkip, edit=True, enable = True)
        
        else:
            py.text(cls.textAutoSet, edit=True, enable=enableValue) 
            if enableValue == True:
                py.floatSliderGrp(cls.sliderAnimAutoSet, edit=True, enable = True)
                py.floatSliderGrp(cls.sliderFrameSpacing, edit=True, enable = False)
                py.floatSliderGrp(cls.sliderCubeSkip, edit=True, enable = False)
        
        
    @classmethod
    def autoSetCheckbox(cls):
        #animation auto set checkbox
        enableValue = py.checkBox(cls.checkboxAnimAutoSet, query=True, value=True)
        py.text(cls.textAutoSet, edit=True, enable=enableValue) 
        py.floatSliderGrp(cls.sliderAnimAutoSet, edit=True, enable=enableValue)
        if enableValue == False:
            enableValue = True
        else:
            enableValue = False        
        py.text(cls.textCubeSkip, edit=True, enable=enableValue) 
        py.text(cls.textFrameSpacing, edit=True, enable=enableValue) 
        py.floatSliderGrp(cls.sliderFrameSpacing, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.sliderCubeSkip, edit=True, enable=enableValue)
        
    @classmethod
    def enableLoops(cls):
        #loops checkbox
        enableValue = py.checkBox(cls.checkboxLoops, query=True, value=True)
        py.text(cls.textNumLoops, edit=True, enable=enableValue) 
        py.floatSliderGrp(cls.sliderLoops, edit=True, enable=enableValue)
        if py.checkBox(cls.checkboxAutoDistance, query=True, value=True) == False:
            py.checkBox(cls.checkboxAutoDistance, edit=True, enable=enableValue, value=False)
            py.text(cls.textSizeX, edit=True, enable=enableValue) 
            py.text(cls.textSizeY, edit=True, enable=enableValue) 
            py.text(cls.textSizeZ, edit=True, enable=enableValue) 
            py.floatSliderGrp(cls.sliderSizeX, edit=True, enable=enableValue)
            py.floatSliderGrp(cls.sliderSizeY, edit=True, enable=enableValue)
            py.floatSliderGrp(cls.sliderSizeZ, edit=True, enable=enableValue)
        else:
            py.checkBox(cls.checkboxAutoDistance, edit=True, value=True, enable=enableValue)
        
        if py.checkBox(cls.checkboxAnim, query=True, value=True) == True:
            py.floatSliderGrp(cls.sliderAnimSpacing, edit=True, enable=enableValue)
            py.text(cls.textAnimSpacing, edit=True, enable=enableValue) 
        
        
    @classmethod 
    def setDistance(cls):
        #auto set loop distance checkbox
        enableValue = py.checkBox(cls.checkboxAutoDistance, query=True, value=True)
        if enableValue == False:
            enableValue = True
        else:
            enableValue = False
        py.text(cls.textSizeX, edit=True, enable=enableValue) 
        py.text(cls.textSizeY, edit=True, enable=enableValue) 
        py.text(cls.textSizeZ, edit=True, enable=enableValue) 
        py.floatSliderGrp(cls.sliderSizeX, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.sliderSizeY, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.sliderSizeZ, edit=True, enable=enableValue)
        
    @classmethod 
    def nextTip(cls):
        py.text( cls.textTip, edit=True, label=userInterface.tipList()) 
        
        
    @classmethod 
    def createCurves(cls):
        enableValue = py.menuItem(cls.checkboxCreateCurves, query=True, checkBox=True)
        py.menuItem(cls.checkboxSelectCurves, edit=True, enable=enableValue)
        py.text(cls.tempText3D, edit=True, label=2) 
    
    @classmethod 
    def deleteCubeCheckbox(cls):
        #delete cubes checkbox
        enableValue = py.menuItem(cls.checkboxDeleteCubes, query=True, checkBox=True)
        animEnabled = py.checkBox(cls.checkboxAnim, query=True, value=True)
        animAutoSet = py.checkBox(cls.checkboxAnimAutoSet, query=True, value=True)
        colourEnabled = py.checkBox(cls.checkboxColours, query=True, value=True)
        
        if colourEnabled == True:
            py.floatSliderGrp(cls.colourDetail, edit=True, enable=enableValue)
            py.floatSliderGrp(cls.colourWeights, edit=True, enable=enableValue)
            py.text(cls.colourText, edit=True, enable=enableValue) 
            py.text(cls.colourDetailText, edit=True, enable=enableValue) 
            py.text(cls.colourWeightsText, edit=True, enable=enableValue) 
            py.textField(cls.colourTextField, edit=True, enable=enableValue) 
        
        if enableValue == False:
            enableValue = True
        else:
            enableValue = False
        py.checkBox(cls.checkboxAnim, edit=True, enable=enableValue)
        py.checkBox(cls.checkboxColours, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.colourDetail, edit=True, enable=enableValue)
        py.floatSliderGrp(cls.colourWeights, edit=True, enable=enableValue)
        py.text(cls.colourText, edit=True, enable=enableValue) 
        py.text(cls.colourDetailText, edit=True, enable=enableValue) 
        py.text(cls.colourWeightsText, edit=True, enable=enableValue) 
        py.textField(cls.colourTextField, edit=True, enable=enableValue) 
        
        if colourEnabled == False:
            py.floatSliderGrp(cls.colourDetail, edit=True, enable=False)
            py.floatSliderGrp(cls.colourWeights, edit=True, enable=False)
            py.text(cls.colourText, edit=True, enable=False) 
            py.text(cls.colourDetailText, edit=True, enable=False) 
            py.text(cls.colourWeightsText, edit=True, enable=False) 
            py.textField(cls.colourTextField, edit=True, enable=False) 
        
        if animEnabled == True and enableValue == True:
            checkBoxAuto = True
        else:
            checkBoxAuto = False
            
        py.checkBox(cls.checkboxAnimAutoSet, edit=True, enable=checkBoxAuto)
        if animAutoSet == True:
            py.floatSliderGrp(cls.sliderAnimAutoSet, edit=True, enable = enableValue)
            py.text(cls.textAutoSet, edit=True, enable=enableValue) 
        else:
            py.floatSliderGrp(cls.sliderFrameSpacing, edit=True, enable = enableValue)
            py.floatSliderGrp(cls.sliderCubeSkip, edit=True, enable = enableValue)
            py.text(cls.textCubeSkip, edit=True, enable=enableValue)
            py.text(cls.textFrameSpacing, edit=True, enable=enableValue)
            
        if py.checkBox(cls.checkboxLoops, query=True, value=True) == True and animEnabled == True:
            py.text(cls.textAnimSpacing, edit=True, enable=enableValue)
            py.floatSliderGrp(cls.sliderAnimSpacing, edit=True, enable=enableValue)
    
    @classmethod
    def clearColour(cls):
        py.textField(cls.colourTextField, edit=True, text='') 
        
    @classmethod
    def addColour(cls, colour):
        #adds colour to text field
        originalColours = py.textField(cls.colourTextField, query=True, text=True) 
        
        #remove any spaces at end
        newColours = ""
        numSpaces = 0
        for i in range(len(originalColours)):
            if originalColours[-i-1] == " ":
                numSpaces += 1
            else:
                break
        for i in range(len(originalColours)-numSpaces):
            newColours += originalColours[i]
            
        #add colour to box
        if colour.replace('dark','') != colour:
            colour = "dark " + colour.replace('dark','')
        elif colour.replace('light','') != colour:
            colour = "light " + colour.replace('light','')
            
        if newColours != "":
            if newColours[-1] != ",":
                newColours += ', ' + colour
            else: newColours+= ' ' + colour
        else:
            newColours = colour
        py.textField(cls.colourTextField, edit=True, text = newColours) 

    @classmethod
    def customDirection(cls, amount, direction):
        originalDirection = py.menuItem( cls.manualLocation, query=True, label = True ).replace('Custom (','').replace(')','').split(', ')
        x = Decimal(originalDirection[0])
        y = Decimal(originalDirection[1])
        z = Decimal(originalDirection[2])
        if direction == 'x':
            x += Decimal(amount)
            if x > 1:
                x = 1.0
            if x < -1:
                x = -1.0
        if direction == 'y':
            y += Decimal(amount)
            if y > 1:
                y = 1.0
            if y < -1:
                y = -1.0
        if direction == 'z':
            z += Decimal(amount)
            if z > 1:
                z = 1.0
            if z < -1:
                z = -1.0
        newValue = [x,y,z]
        
        py.menuItem( cls.manualLocation, edit=True, radioButton = True, label='Custom ('+str(newValue[0])+', '+str(newValue[1])+', '+str(newValue[2])+')')
        py.text(cls.directionTempText, visible = True, edit=True, label = 'this doesnt work yet '+'['+str(newValue[0])+', '+str(newValue[1])+', '+str(newValue[2])+']') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (custom)' )
        
        
    @classmethod
    def directionX(cls):
        py.text(cls.directionTempText, edit=True, label = 'x') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (right)' )
    @classmethod
    def directionXm(cls):
        py.text(cls.directionTempText, edit=True, label = '-x') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (left)' )
    @classmethod
    def directionY(cls):
        py.text(cls.directionTempText, edit=True, label = 'y') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (up)' )
    @classmethod
    def directionYm(cls):
        py.text(cls.directionTempText, edit=True, label = '-y') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (down)' )
    @classmethod
    def directionZ(cls):
        py.text(cls.directionTempText, edit=True, label = 'z') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (forwards)' )
    @classmethod
    def directionZm(cls):
        py.text(cls.directionTempText, edit=True, label = '-z') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (backwards)' )
    @classmethod
    def directionNone(cls):
        py.text(cls.directionTempText, edit=True, label = '') 
        py.button( cls.directionButton, edit=True, label = 'Choose direction of generation (default)' )
    
    @classmethod
    def tipList(cls):
        sentencePrefix = "&nbsp;Tip: "
        sentenceList = []
        sentenceList.append( sentencePrefix + "A large number of short forks will create a tightly packed shape, whereas a low number of very long forks<br/>&nbsp;will create something more complex." )
        sentenceList.append( sentencePrefix + "For a much more complex shape, try higher values such as 4000x100. A number may be input manually if<br>&nbsp;it's outside the range." )
        sentenceList.append( sentencePrefix + "Large generations can take a while use a lot of RAM. Be careful when setting the values high, as it will<br/>&nbsp;increase the save file by a large amount." )
        sentenceList.append( sentencePrefix + "If something is not clear, middle click the field to view more information." )
        sentenceList.append( sentencePrefix + "When inputting colours, right click to bring up a full list." )
        sentenceList.append( sentencePrefix + "Disabling quick generation will improve checks to stop overlapping, at a cost to performance. It is advised<br>&nbsp;to keep this enabled unless making a 2D generation." )
        sentenceList.append( sentencePrefix + "Right click the generation button for a few display options." )
        sentenceList.append( sentencePrefix + "Enabling the high quality checkbox will turn on Viewport 2.0 with SSAO, MSAA and motion blur." )
        sentenceList.append( sentencePrefix + "If the wrong shaders are chosen, it is possible to assign new ones if the group is selected." )
        sentenceEnd = "<br/>&nbsp;&nbsp;<font size='2' color='grey'>Load the script editor to view progress details.</font><br/><br/>"
        return sentenceList[ int(rd.randint(0,len(sentenceList) - 1)) ] + sentenceEnd
  
def ph_decimalConvert(value):
    value = str(int(value*pow(10,formatDecimals+2))/pow(10.0,formatDecimals))
    decimals = value.split('.')[1]
    if len(decimals) < formatDecimals:
        for i in range(formatDecimals-len(decimals)):
            value += '0'
    return value

userInterface.display()
'''
v0.1
Generates 2D line in random directions
Draws curve down the line
Set distance between points

v0.15
Generates forks starting from any point in the first line
Extra list added for each fork to have it's own curve

v0.2
Rewrote code to allow for overlap checking
Added in an extra few lines to allow 3D generation

v0.25
Added playback options, to see the generation of the lines
Added delete cube option

v0.3
Added option to keep generation within an area
Stops the loop if the cube can't go anywhere
Turned cube movement into a function

v0.4
Added minimum generation values with error messages
Added keying options
Set end time to the last calculation

v0.45
Merged the playback and keying options
Set end time to the highest calculation
Added in a workaround to stop large values appearing before frame 0

v0.46
Fixed workaround to work with the cubeSkip option

v0.48
Fixed workaround to work with extreme values
Attempted rewriting the area code to optimise it (theoretically should have worked, but didn't)
Merged primary and secondary fork lengths

v0.5
Added in calculation to automatically generate timing based on the inputs
Rewrote workaround code again to work with more extreme values
Added option to set seed

v0.6
Added option for loops
Loops are generated at random time offsets
Each loop has a different prefix, up to a maximum of 12356630 (can be increased easily if needed)

v0.7
Rewrote keying options
Area disables if using loops
Added levels of message output
Added option to automatically set the area new objects will be created in
Amount of loops changes speed of animation

v0.8
Merged new keying with old keying to get better result
Improved auto keying options
Added time offset on new fork creation
Made the time offset decrease in maximum value as the generation nears the end

v0.81
Edited the time offset to allow the opposite negative values
Removed option of playback during generation

v0.85
Added option to set size of cube
Fixed the auto spacing calculation for multiple loops to work with different sizes

v0.9
Grouped objects
Added option to offset the prefix by a certain amount

v0.95
Added code to allow multiple generations in the same scene 

v1.0
Designed a basic user interface
Curves will no longer be created for single points
Starting key now based on the current position of time slider

v1.03
Fixed grouping code
Output grouping messages

v1.05
Added checkbox to group objects
Added randomly chosen tips to user interface
Fixed the start time of the animation
Disabled decimal points for generation

v1.1
Optimised grouping
Optimised keying
Added option to make cubes only appear for a certain number of frames

v1.2
Added option to allow the cubes to decrease in size
Set each fork to slowly decrease in length based on the amount

v1.3
Fixed decreasing sizes to work with lower values
Outputs time taken
Optimised location lookup
Fixed branching to work with loops
Switched the grouping checkbox to branching
Added code to automatically set branching values

v1.4
Wrote code to create sequence of colours
Added validation to check for existing materials
Modified branching code to work with colours
Assign colours to cubes

v1.42
User can choose colour

v1.45
Any number of colours can now be chosen
Fixed single colours not working
Ignores invalid values
Added validation to stop user submitting empty values
Fixed to work with loops and delete cube option

v1.5
Added option to max out the range of values
Added option to change the ratio of colours
Added option to choose direction of generation
Calculates minimum values for colour exponential value
Updated colour detail to change based on number of colours

v1.55
Optimised prefix calculation
Allows for the auto set loop distance to be set for individual directions
Updated user interface to select directions
If one colour is chosen, only creates a single shader
Invalid colour values now don't influence the smoothness

v1.6
Added option to get the location of selected objects
Added validation to stop invalid objects from crashing the code
Improved the check for already existing cubes to work after the reduce size option was added
Fixed starting location to be accurate
Fixed colours to work with different cube sizes
Maxing out the range of colour values no longer crashes code when setting ratio

v1.65
Added help messages to UI
Separated create shader function to allow other use of colours
Right clicking on colour input displays list of colours to enter
Added script to create appropiate submenus

v1.7
Added variable to make direction more weighted
Updated to allow it to work in reverse
Added maximum range to randomise it for each fork
Turning generation to 2d now disables up and down directions
Fixed the check to stop two cubes being placed in the same spot
Added option to use older less accurate placement for speed increase
Displays an estimated speed increase from the quick generation

v1.75
Option to set up viewport added (viewport 2.0 + ssao + motion blur + msaa)
Calculates overall percent complete
Percent updated to include assigning colours
Option to skip curve creation added
Percent code rewrote to allow for future additions
Percent updated to include deleting the cubes

v1.8
Displays percentage in lower left box
Allows cancellation of code
Cancelling code will now cause jump to next section
Added display options to right click menu of generate
Added clear command to right click menu of entering colours

v1.85
Added code to stop quick transitions in colour
Changed to run multiple times in a loop
Put in check to stop values too high
Added colour groups to dropdown menu
Disabling 3D will tick the create curve checkbox acordingly unless the user sets something
Viewport set code changed from checkbox to run when clicked
Added custom direction selection options to user interface

v1.9
Created a camera which will follow a circle motion path around the generation
Circle now changed to a spiral going outwards
Option for multiple circle loops at the end added so camera won't stop
Unlinks the X rotation and points towards the centre
Added option to toggle the grid
Tracking now works on individual loops
Improved camera tracking code to work with most sizes
Moved key cube code to allow the camera to update when not using an animation
Fixed camera tracking to always point towards object

v1.95
Moved prefix calculation into different function
Moved colour assigning into different function
Created file reading function
Store values for colour creation inside file
Colour can now be re-assigned after a generation
Added preview generation option into user interface

2.0
Locator stores number of cubes per generation
Cubes contain colour information for remapping colours
Improved efficiency so groups store all generation info and locator stores global info
Stored colour value within each cube
Replaced update shader code to work with any of the generations
Added option to list all cube groups
Set variable height based on amount of groups
Added validation messages for if updating colour does not work
Succesfully added loops to change colour on multiple generations at once


To do:
    match smoothness with smoothoverride
    >Store fork completion percent
    >Create new fork only when over 50%

--------------------------------------------------
'''
