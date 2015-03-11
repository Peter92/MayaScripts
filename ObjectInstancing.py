from time import time
import pymel.core as py
import random as rd
import sys

def buttonPressed(formInfo):
    
    if formInfo == "storedObj":
        getInitialInfo = True
    else:
        getInitialInfo = False
    
    particleRate = win_maxParticleCount.getValue()
    minSlope = win_slopeLimit.getValue()
    minSlopeVariance = win_slopeLimitVar.getValue()
    setBoundingBox = win_boundingBox.getValue()
    maxTilt = win_objTilt.getValue()
    objectScale = win_objScale.getValue()
    objectScaleVariance = win_objScaleW.getValue()
    objectHeightVariance = win_objScaleH.getValue()
    extraHeight = win_posHeight.getValue()
    
    ph_mainCode(extraHeight, particleRate,getInitialInfo,minSlope,minSlopeVariance,setBoundingBox,maxTilt,objectScale,objectScaleVariance,objectHeightVariance)

def ph_displayWindow(displayWindow, displayMessage):
    print displayMessage
    if displayWindow == True:
        py.text(label="  ")
        py.text(label="  ")
        py.text(label="  ")
        py.text(label="  ")
        py.text(label=displayMessage, align = "center")
        py.text(label="  ")   
        py.text(label="  ")
        py.text(label="  ")
        py.text(label="  ")
        py.showWindow()   
        
def ph_timeOutput(startTime, endTime, decimalPoints):

    #calculate decimal points
    if decimalPoints > 0:
        decimals = float( pow( 10, decimalPoints ) )
    else:
        decimals = int( pow( 10, decimalPoints ) )
        
    #calculate seconds and minutes
    seconds = endTime - startTime
    
    #cut decimal points off seconds
    secondsDecimal = int(seconds*decimals)/decimals
    
    #make sure it's correct grammar
    if (decimalPoints == 0) and (secondsDecimal == 1):
        sec = " second"
    else:
        sec = " seconds"
    
    return secondsDecimal, sec

def ph_mainCode(extraHeight, particleRate,getInitialInfo,minSlope,minSlopeVariance,setBoundingBox,maxTilt,objectScale,objectScaleVariance,objectHeightVariance):
    
    displayWindow = True
    windowError = py.window(title="Notice",  mxb=False, s=False)
    errorLayout = py.rowColumnLayout(numberOfColumns=3, parent = windowError)
    
    #initialise varibables
    originalTime = py.currentTime( query = True)
    deleteCount = 0
    decimalPoints = 2
    
    #file validation
    storeSelection = py.ls( selection = True )
    
    try:
        validFile = True
        myfile = open('storedobjects.txt')
        objectList = myfile.readlines()
        myfile.close()
        py.select( clear = True )
        for i in range( len( objectList ) ):
            py.select( objectList[i], add = True )
        1/len(objectList)
        
    except:
        validFile = False
    

    #get original selection    
    py.select( clear = True )
    for i in range(len(storeSelection)):
        py.select( storeSelection[i], add = True )
        
        #deselect non polygons
        if type(storeSelection[i]) != py.nodetypes.Transform:
            py.select( storeSelection[i], deselect = True)
            
        #deselect objects in the text file
        if getInitialInfo == False:
            for j in range(len(objectList)):
                selectionEdit = storeSelection[i] + objectList[j][-2] + objectList[j][-1]
                if objectList[j] == selectionEdit:
                    py.select( storeSelection[i], deselect = True )
                
    storeSelection = py.ls( selection = True )
        
    startTime = time()
    listOfPoints = []
    totalNum = 0
    
    if len(storeSelection) == 0:
        displayMessage = "Nothing is selected. Please select an object and try again."  
        ph_displayWindow(displayWindow, displayMessage)
    
    elif getInitialInfo == True:
        
        #write to file
        selection = py.ls( selection = True )
        myfile = open('storedobjects.txt','w')
        for i in range(len(selection)):
            myfile.write(""+selection[i]+"\r\n")
        myfile.close()
        if len(selection) > 0:
            print str(len(selection)) + " object(s) successfully stored."
            if displayWindow == True:
                py.text(label="  ")
                py.text(label="  ")
                py.text(label="  ")
                py.text(label="  ")
                py.text(label=str(len(selection)) + " object(s) successfully stored.", align = "center")
                py.text(label="  ")   
                py.text(label="  ")
                py.text(label="  ")
                py.text(label="  ")
                py.showWindow()
        
        else:
            displayMessage = "Please select the objects you wish to store."
            ph_displayWindow(displayWindow, displayMessage)
            
        for i in range(len(storeSelection)):
            py.select( storeSelection[i], add = True )
            
    elif validFile == False:
        displayMessage = "Error with stored list. Please choose new object(s) to duplicate."
        ph_displayWindow(displayWindow, displayMessage)
        
    elif len(objectList) == 0:
        displayMessage = "No objects stored. Please choose new object(s) to duplicate."
        ph_displayWindow(displayWindow, displayMessage)
        
    else:
        for loops in range(len(storeSelection)):
            
            particleID = []
            particleLoc = []
            particleVelocity = []
            
            #get information about selected object
            py.select( storeSelection[loops], r = True )
            originalObj = py.ls( selection = True )
            originalObjLoc = originalObj[0].getTranslation()
            originalObjX = originalObjLoc.x
            originalObjY = originalObjLoc.y
            originalObjZ = originalObjLoc.z
            
            #duplicate object to work on
            tempObj = py.instance(originalObj)
            
            #make emitter
            particleEmitter = py.emitter( n='tempEmitter', type ='surface', r = particleRate * 24, sro = 0, speed = 0.0001 )
            particles = py.particle( n='emittedParticles' )
            py.connectDynamic( 'emittedParticles', em='tempEmitter' )
            py.setAttr( particles[1] + '.seed[0]', rd.randint(0, sys.maxint) )
            
            #get list from file
            myfile = open('storedobjects.txt')
            objectList = myfile.readlines()
            objectListCopy = []
            myfile.close()
            
            for i in range( len(objectList) ):
                copyObj = py.duplicate( objectList[i] )
                objectListCopy.append( copyObj )
            
            #fixes the seed always being 0
            py.currentTime( originalTime + 1 , edit = True, update = True)
            py.currentTime( originalTime, edit = True, update = True)
            py.currentTime( originalTime + 1 , edit = True, update = True)
            numOfParticles = particles[1].num()
            
            for i in range(numOfParticles):
            
                #get particle info
                particleInfo = particles[1].Point( 'emittedParticles', i )
                particleID.append( particleInfo )
                particleLoc.append( particleInfo.position )
                particleVelocity.append( particleInfo.velocity )
                
            for i in range(len(particleID)):
                
                #place objects
                randomNum = rd.randint(0, len(objectListCopy) - 1)
                instanceObj = objectListCopy[randomNum]
                dupObj = py.instance( instanceObj )
                yDir = particleVelocity[i][1] * 10000
                
                #get height of object
                py.select( instanceObj, r = True )
                py.scale(1,1,1)
                height = py.ls (selection = True)[0].getBoundingBox().height()
                
                #reselect instance
                py.select( dupObj[0], r = True )
                py.move( dupObj[0], particleLoc[i][0], particleLoc[i][1] + extraHeight, particleLoc[i][2] )
                py.rotate( dupObj[0], rd.uniform(-maxTilt, maxTilt), rd.randint(0, 360), rd.uniform(-maxTilt, maxTilt), os=True)
                scaleX = rd.uniform(objectScale - objectScaleVariance, objectScale + objectScaleVariance)
                scaleY = rd.uniform(objectScale - (objectHeightVariance/2), objectScale + objectHeightVariance)
                scaleZ = rd.uniform(objectScale - objectScaleVariance, objectScale + objectScaleVariance)
                py.scale( dupObj[0], scaleX, scaleY, scaleZ)
                
                if yDir <= rd.uniform(minSlope - minSlopeVariance, minSlope + minSlopeVariance):
                    py.delete( dupObj )
                    deleteCount = deleteCount + 1
                else:
                    listOfPoints.append( dupObj )
        
                #display percent completed
                maxValue = int(pow(len(particleID), 0.5))
                if float(i/maxValue) == float(i)/maxValue:
                    print str(int((float(i)*100/len(particleID))*100.0)/100.0) + "% completed"
                    
            totalNum = totalNum + numOfParticles
            
            #delete temp objects
            py.select( tempObj, 'tempEmitter', 'emittedParticles' )
            py.delete()
            py.currentTime( originalTime, edit = True, update = True)
            for i in range( len(objectListCopy )):
                py.delete(objectListCopy[i][0])
                    
        
    #place objects in display layer
    py.select( clear = True )
    if len( listOfPoints ) > 0:
        if setBoundingBox == True:
            displayLayerName = 'duplicatedObjectsBB'
        else:
            displayLayerName = 'duplicatedObjectsMesh'
            
        #add to display layer
        try:
            for i in range( len( listOfPoints )):
                py.editDisplayLayerMembers( displayLayerName, listOfPoints[i] )
        
        #create display layer first
        except:
            py.createDisplayLayer( noRecurse=True, name=displayLayerName )
            for i in range( len( listOfPoints )):
                py.editDisplayLayerMembers( displayLayerName, listOfPoints[i] )
                
            #display objects as bounding box
            if setBoundingBox == True:
                py.setAttr( displayLayerName + '.levelOfDetail', 1 )
            py.setAttr( displayLayerName + '.color', 17 ) 
        
        #add to group
        for i in range( len( listOfPoints )):
            py.select( listOfPoints[i][0], add = True )
        py.group(n = 'duplicatedObjectsGroup' )
    
    
        #output time taken
        endTime = time()
        ph_timeOutput(startTime, endTime, decimalPoints)
        secondsDecimal, sec = ph_timeOutput(startTime, endTime, decimalPoints)
        displayMessage = str( totalNum - deleteCount ) + " objects created in " + str(secondsDecimal) + str(sec)
        ph_displayWindow(displayWindow, displayMessage)    
    
    #select original selection
    py.select( clear = True )
    for i in range(len(storeSelection)):
        py.select( storeSelection[i], add = True )
    

global win
try:
    win.delete()
except:
    pass

win = py.window(title="Instance objects",  mxb=False, s=False)
win_layout1 = py.rowColumnLayout(numberOfColumns=1)
py.text(label="This will generate multiple instances of geometry to place on an object. Possible uses could include designing<br> a forest or field.<br><font size='2' color = 'grey'>Note: Due to current limitations of the code, pivots are reset when instancing. If using paint effects, please draw them at<br/> the centre of the scene to make sure they are accurately placed.", align = "left")  
win_layout = py.rowColumnLayout(numberOfColumns=4 )
py.text(label='  ')  
py.text(label=' ')  
py.text(label='      ')  
py.text(label=' ')  
py.text(label=' ')  
py.text( label = "   Select object(s) to be instanced ", align = "left" )
py.text(label=' ')  
py.text(label='Maximum duplicate object count  ', align = "right")  
py.text(label=' ')  
win_storeObj = py.button( label="Store object(s)", parent = win_layout, command = py.Callback( buttonPressed, "storedObj" ) )
py.text(label=' ')  
win_maxParticleCount = py.floatSliderGrp( field = True, parent = win_layout, min = 10, max = 10000, fmn = 0, fmx = 10000000, pre = 0)
win_maxParticleCount.setValue(1000) 
py.text(label=' ')  
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ') 
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ') 
py.text(label='Sloping limit (0 = vertical, 1 = horizontal)  ', align = "right") 
py.text(label=' ')  
py.text(label='   Select object(s) to run code on', align = "left") 
py.text(label=' ') 
win_slopeLimit = py.floatSliderGrp( field = True, parent = win_layout, min = 0, max = 1, fmn = -1, fmx = 1, pre = 2)
win_slopeLimit.setValue(0.75)
py.text(label=' ')  
win_distribute = py.button( label = "Scatter", parent = win_layout, command = py.Callback( buttonPressed, "executeScript" ) )
py.text(label=' ') 
py.text(label='Sloping limit variance  ', align = "right") 
py.text(label=' ')  
win_boundingBox = py.checkBox( label = "Display objects as bounding box", value=True, parent = win_layout ) 
py.text(label=' ') 
win_slopeLimitVar = py.floatSliderGrp( field = True, parent = win_layout, min = 0, max = 0.5, fmn = 0, fmx = 1, pre = 2)
win_slopeLimitVar.setValue(0.1) 
py.text(label=' ')  
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ')  
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ') 
py.text(label='Object scale  ', align = "right")  
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ') 
win_objScale = py.floatSliderGrp( field = True, parent = win_layout, min = 0.01, max = 5, fmn = 0.01, fmx = 100, pre = 2)
win_objScale.setValue(1) 
py.text(label=' ')  
py.text(label='  Maximum tilt angle  ', align = "left") 
py.text(label=' ') 
py.text(label='Object width variance  ', align = "right")  
py.text(label=' ')  
win_objTilt = py.floatSliderGrp( field = True, parent = win_layout, min = 0, max = 10, fmn = 0, fmx = 90, pre = 1)
win_objTilt.setValue(2) 
py.text(label=' ') 
win_objScaleW = py.floatSliderGrp( field = True, parent = win_layout, min = 0.01, max = 1, fmn = 0, fmx = 10, pre = 2)
win_objScaleW.setValue(0.05) 
py.text(label=' ')  
py.text(label='  Height position adjustment (use if object is too low)', align = "left") 
py.text(label=' ') 
py.text(label='Object height variance  ', align = "right") 
py.text(label=' ')   
win_posHeight = py.floatSliderGrp( field = True, parent = win_layout, min = -100, max = 100, fmn = -100000, fmx = 100000, pre = 3)
win_posHeight.setValue(0) 
py.text(label=' ') 
win_objScaleH = py.floatSliderGrp( field = True, parent = win_layout, min = 0.01, max = 1, fmn = 0, fmx = 10, pre = 2)
win_objScaleH.setValue(0.1) 
py.text(label=' ')  
py.text(label=' ') 
py.text(label=' ') 
py.text(label=' ') 
py.showWindow()
