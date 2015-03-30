import threading, time, math
import pymel.core as pm
import maya.utils as utils
import maya.mel as mel
import os, time
from os.path import isfile, join

       
class AutoSaveThread(object):
    printPrefix = 'SE Auto Save: '
    def __init__( self, wait=0, firstRun=False ):
        self.wait = wait
        self.location = AutoSave().location()
        self.enabled=True
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
    def run(self):
        time.sleep( self.wait )
        if firstRun:
            MoveBackupScriptsToFolder( self.location )
        printStuff( "Started at intervals of {} seconds".format( AutoSave().interval() ), AutoSave().silent(), self.printPrefix )
        alreadySaidItsPaused = False
        while AutoSave().enabled():
            AutoSave().progress( time.time() )
            if not AutoSave().paused():
                interval = AutoSave().interval()
                #Update if just stopped being paused
                if alreadySaidItsPaused:
                    printStuff( "Resuming backup, activating in {0} seconds.",format( interval ), AutoSave().silent(), self.printPrefix )
                    alreadySaidItsPaused = False
                intervals = notifySave( interval )
                totalCount = 0
                #Count down from max time
                for i in xrange( interval, 0, -1 ):
                    if AutoSave().enabled() > 0:
                        if i in intervals:
                            if i < 15:
                                s = ''
                                if i != 1:
                                    s = 's'
                                printStuff( "Activating in {0} second{1}...".format( i, s ), AutoSave().silent(), self.printPrefix )
                    else:
                        break
                    time.sleep( 1 )
                if AutoSave().enabled() > 0:
                
                    try:
                        saveScriptEditorFiles( True, self.location )    #Backup files first
                        saveScriptEditorFiles( False, self.location )   #Overwrite main files
                    except:
                        printStuff( "Failed to save scripts", AutoSave().silent() )
                    else:
                        printStuff( "Successfully saved scripts, saving again in {0} seconds".format( AutoSave().interval() ), AutoSave().silent(), self.printPrefix )
            else:
                if not alreadySaidItsPaused:
                    alreadySaidItsPaused = True
                    printStuff( "Paused by user", AutoSave().silent(), self.printPrefix )
                time.sleep(1)
        AutoSave().progress( False )
        printStuff( "Cancelled by user", AutoSave().silent(), self.printPrefix )


def printStuff( stuff, silent, prefix='', suffix='' ):
    if not silent:
        print prefix+stuff+suffix

def notifySave( timing ):
    outputList = set()
    divideAmount = 2.0
    currentNumber = timing/divideAmount
    while currentNumber > 1:
        currentNumber /= divideAmount
        divideAmount = pow( divideAmount, 0.95 )
        outputList.update( [int( math.ceil( currentNumber ) )] )
    outputList = list( outputList )
    outputList.sort()
    outputList += [timing-sum( outputList )]
    outputList.reverse()
    return outputList
    

def saveScriptEditorFiles( backup=False, saveLocation=None ):

    #Needs to be manually set if being run from thread
    if not saveLocation:
        saveLocation = AutoSave().location()
    
    #Get MEL globals
    mel.eval( 'global string $gCommandExecuter[];global string $executerBackupFileName' )
    scriptEditorTabs = mel.eval( '$scriptEditorTabs=$gCommandExecuter' )
    backupFileName = mel.eval( '$backupFileName=$executerBackupFileName' )
    if backup:
        backupFileName += 'Backup'
    
    if pm.optionVar['saveActionsScriptEditor']:
    
        #Get temporary folder location
        saveLocation = saveLocation + "scriptEditorTemp/"
        oldFiles = [f for f in os.listdir( saveLocation ) if os.path.isfile( os.path.join( saveLocation, f ) )]
        
        #Delete old files
        if oldFiles:
            for i in oldFiles:
                if backup and 'backup' in i.lower() or not backup and 'backup' not in i.lower():
                    os.remove( saveLocation+i )
                    
        #Save new files
        for i in range( len( scriptEditorTabs ) ):
            pm.cmdScrollFieldExecuter( scriptEditorTabs[i], storeContents = backupFileName, edit=True )

firstRun = False
try:
    AutoSave()
except:
    firstRun = True

class AutoSave:
    autoSaveName = 'scriptEditorAutoSave'
    intervalName = 'scriptEditorSaveInterval'
    progressName = 'scriptEditorSaveInProgress'
    printName = 'scriptEditorSilentSave'
    locationName = 'scriptEditorSaveLocation'
    def __init__(self):
        if pm.optionVar.get( self.intervalName, None ) == None:
            self.interval(120)
        if pm.optionVar.get( self.progressName, None ) == None:
            self.progress(False)
        if pm.optionVar.get( self.printName, None ) == None:
            self.silent(False)
        self.location(True)
        if pm.optionVar.get( self.autoSaveName, None ) == None:
            self.enabled(False)
    def start( self, timing=None, wait=0, firstRun=False ):
        #Set interval
        if str(timing).isdigit():
            self.interval( timing )
        #Find if previously paused
        wasPaused = False
        if self.paused():
            wasPaused = True
            printStuff( "Resuming backup in {0} seconds".format( self.interval() ), self.silent(), AutoSaveThread.printPrefix )
        self.enabled(True)
        if not self.progress() or time.time()-2 > self.progress() and not wasPaused:
            AutoSaveThread( wait, firstRun )
    def pause(self):
        self.enabled(-1)
    def unpause(self):
        self.enabled(True)
    def stop(self):
        self.progress(False)
        self.enabled(False)
    def paused(self):
        return self.enabled() == -1
    def interval(self,timing=None):
        if timing==None:
            return pm.optionVar[self.intervalName]
        try:
            int(timing)/1
        except:
            pass
        else:
            pm.optionVar[self.intervalName]=max(2,timing)
    def enabled(self,state=None):
        if state==None:
            return pm.optionVar[self.autoSaveName]
        pm.optionVar[self.autoSaveName]=state
    def progress(self,progress=None):
        if progress==None:
            return pm.optionVar[self.progressName]
        pm.optionVar[self.progressName]=progress
    def silent(self,silence=None):
        if silence==None:
            return pm.optionVar[self.printName]
        pm.optionVar[self.printName]=silence
    def location(self,update=None):
        if update==None:
            return pm.optionVar[self.locationName]
        pm.optionVar[self.locationName] = pm.internalVar( userPrefDir=True )


def MoveBackupScriptsToFolder( saveLocation=None ):
    if saveLocation == None:
        saveLocation = AutoSave().location()
    saveLocation += "scriptEditorTemp/"
    newBackupDir = saveLocation+'backup-'+str( int( time.time() ) )+"/"
    fileNames = [f for f in os.listdir( saveLocation ) if os.path.isfile( os.path.join( saveLocation, f ) )]
    for i in fileNames:
        if 'Backup' in i:
            if not os.path.exists( newBackupDir ):
                os.makedirs( newBackupDir )
            os.rename(saveLocation+i, newBackupDir+i.replace( 'Backup', '' ))

#Reset progress in case it wasn't properly stopped on previous run
if firstRun:
    AutoSave().progress(False)
