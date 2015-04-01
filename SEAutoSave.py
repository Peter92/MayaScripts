import threading, time, math
import pymel.core as pm
import pymel.mayautils as utils
import maya.mel as mel
import os, time
from os.path import isfile, join


class AutoSaveThread(object):
    """Thread to run in the background to auto save the script editor contents."""
    
    #Fixed variables
    printPrefix = 'SE Auto Save: '
    autoSaveName = 'scriptEditorAutoSave'
    intervalName = 'scriptEditorSaveInterval'
    progressName = 'scriptEditorSaveInProgress'
    printName = 'scriptEditorSilentSave'
    locationName = 'scriptEditorSaveLocation'
    
    def __init__( self, wait=0 ):
        """Start off the thread, 'run' does not need to be called.
        
        wait:
            How many seconds to wait before starting the save timer.
        """
        #Set up values
        self.wait = wait
        self.location = pm.optionVar[self.locationName]
        self.enabled=True
        
        #Begin thread
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()
        
    def run(self):
    
        #Wait a short while before starting the execution
        time.sleep( self.wait )
        
        printStuff( "Started at intervals of {} seconds. WARNING: Do not open or close the script editor during saving.".format( pm.optionVar[self.intervalName] ), self.printPrefix )
        alreadySaidItsPaused = False
        
        #Loop until the running state becomes False
        while True:
        
            #Break the loop, this way caused less crashes than 'while pm.optionVar[self.autoSaveName]:'
            runningState = pm.optionVar[self.autoSaveName]
            if not runningState:
                break
            
            #Find if code is paused
            isPaused = runningState == -1
            if not isPaused:
                
                #Print if just unpaused
                if alreadySaidItsPaused:
                    printStuff( "Resuming backup, activating in {0} seconds.".format( interval ), self.printPrefix )
                    alreadySaidItsPaused = False
                    
                #Update progress
                pm.optionVar[self.progressName] = time.time()
                interval = pm.optionVar[self.intervalName]
                intervals = set( i for i in ( 15, 10, 5, 3, 2, 1 ) if i*2 <= interval )
                totalCount = 0
                
                #Count down from interval
                for i in xrange( interval, 0, -1 ):
                    
                    #Check state hasn't been changed to paused or stopped
                    runningState = pm.optionVar[self.autoSaveName]
                    if runningState > 0:
                    
                        #Only print progress if the time matches anything in the list
                        if i in intervals:
                            s = ''
                            if i != 1:
                                s = 's'
                            printStuff( "Activating in {0} second{1}...".format( i, s ), self.printPrefix )
                    else:
                        break
                    time.sleep( 1 )
                    
                #Continue if state is still running
                runningState = pm.optionVar[self.autoSaveName]
                if runningState > 0:
                    
                    #Attempt to save
                    onlySavedBackupFiles = False
                    printStuff( "Saving scripts... Do not open or close the script editor during this time.", self.printPrefix )
                    try:
                        saveScriptEditorFiles( True, self.location )    #Backup files first
                        onlySavedBackupFiles = True
                        saveScriptEditorFiles( False, self.location )   #Overwrite main files
                        onlySavedBackupFiles = False
                        
                    #If script editor window is closed (tabs don't exist)
                    except RuntimeError:
                        printStuff( "Script editor window is possibly closed, trying again in {0} seconds.".format( pm.optionVar[self.intervalName] ), self.printPrefix )
                        
                        #This shouldn't ever happen, but just in case, save the backup files from deletion
                        if onlySavedBackupFiles:
                            MoveBackupScriptsToFolder( pm.optionVar[self.locationName] )
                            moveLocation = pm.optionVar[self.locationName]+'/scriptEditorTemp/{0}'.format( time.time() )
                            printStuff( "Normal files may have become corrupted so backup files have been moved into '{0}'.".format( moveLocation ), self.printPrefix )
                    
                    #If file is read only
                    except WindowsError:
                        printStuff( "Failed to save scripts, one of the files is read only", self.printPrefix )
                    
                    #Other unknown error
                    except:
                        #This also shouldn't happen
                        printStuff( "Failed to save scripts", self.printPrefix )
                    
                    #Successful save
                    else:
                        printStuff( "Successfully saved scripts, saving again in {0} seconds.".format( pm.optionVar[self.intervalName] ), self.printPrefix )
            
            else:
            
                #Only print that the script has been paused once, but keep looping
                if not alreadySaidItsPaused:
                    alreadySaidItsPaused = True
                    printStuff( "Paused by user", self.printPrefix )
                    
                time.sleep(1)
        
        #Print confirmation that loop has been stopped
        pm.optionVar[self.progressName] = False
        printStuff( "Cancelled by user", self.printPrefix )

def printWrapper( input ):
    """Wrapper to be used with executeDeferred."""
    pm.mel.mprint( input+'\n' )

def printStuff( stuff, prefix='', suffix='' ):
    """Print function to use the wrapper."""
    if not pm.optionVar[AutoSaveThread.printName]:
        utils.executeDeferred( printWrapper, str( prefix )+str( stuff )+str( suffix ) )


def saveScriptEditorFiles( backup=False, saveLocation=None ):
    """Modification of the inbuilt MEL code syncExecuterBackupFiles(),
    to allow for backup files to be created separately, and not be 
    deleted when overwriting the main files.
    
    backup:
        changes the fileNames it will save and delete, always run the
        backup first, since if it crashes, the main files are still 
        intact.
         - Boolean
    
    saveLocation:
        Will automatically set itself to the correct value if left empty, 
        only needs to be given when being used inside a thread.
         - String:
            "C:/Users/(name)/Documents/Maya/(version)/prefs/"
            pymel.core.internalVar( userPrefDir=True )
    """
    
    #Needs to be manually set if being run from thread
    if not saveLocation:
        saveLocation = pm.optionVar[AutoSaveThread.locationName]
        
    #Get MEL global variables
    mel.eval( 'global string $gCommandExecuter[]' )
    mel.eval( 'global string $executerBackupFileName' )
    scriptEditorTabs = mel.eval( '$scriptEditorTabs=$gCommandExecuter' )
    backupFileName = mel.eval( '$backupFileName=$executerBackupFileName' )
    if backup:
        backupFileName += 'Backup'
    
    #Continue if saving is enabled in preferences
    saveScriptEditor = pm.optionVar['saveActionsScriptEditor']
    if saveScriptEditor and scriptEditorTabs:
    
        #Get folder location and list of files
        saveLocation = saveLocation + "scriptEditorTemp/"
        oldFiles = [f for f in os.listdir( saveLocation )
                    if os.path.isfile( os.path.join( saveLocation, f ) )]
        
        #Delete old files
        if oldFiles:
            for i in oldFiles:
                validBackup = backup and 'backup' in i.lower()
                validMain = not backup and 'backup' not in i.lower()
                if validBackup or validMain:
                    try:
                        os.remove( saveLocation+i )
                    except:
                        printStuff( "Couldn't remove file: {0}".format( saveLocation+i ) )
                    
        #Save new files
        for i in range( len( scriptEditorTabs ) ):
            pm.cmdScrollFieldExecuter( scriptEditorTabs[i], 
                                       storeContents=backupFileName, 
                                       edit=True )
                                       
    #Fix to stop scripts deleting before opening editor for the first time
    elif not scriptEditorTabs:
        raise RuntimeError()


firstRun = False
try:
    AutoSave()
except:
    firstRun = True

class AutoSave:
    """Control the auto save thread. Setting values in this will edit the
    prefs dictionary (pymel.core.optionVar), so values will be persistent
    between sessions.
    
    Functions:
        start( interval=0 ) - start thread
        pause() - pause/unpause execution
        paused() - return if paused
        stop() - stop thread
        interval() - how many seconds between saves
        enabled() - current state of thread
        progress() - current progress of thread
        location() - location of script editor files
        silent() - if messages should be disabled
    """
    def __init__(self):
        """Auto set values if they don't exist yet."""
        #Set interval at 2 minutes
        if pm.optionVar.get( AutoSaveThread.intervalName, None ) == None:
            self.interval(120)
        #Set current progress to False
        if pm.optionVar.get( AutoSaveThread.progressName, None ) == None:
            self.progress(False)
        #Set silent mode to False
        if pm.optionVar.get( AutoSaveThread.printName, None ) == None:
            self.silent(False)
        #Set the script editor location
        self.location(True)
        #Set state of the thread to 'stopped'
        if pm.optionVar.get( AutoSaveThread.autoSaveName, None ) == None:
            self.enabled(False)
            
    def start( self, timing=None, wait=0 ):
        """Start or unpause the thread, and change the interval.
        
        timing:
            Uses AutoSave().interval() to change the interval to the provided
            value for conveniance.
             - Integer above 2
        
        wait:
            The number of seconds to wait before the thread will begin.
             - Integer above 0
        """
        #Set interval
        if str(timing).isdigit():
            self.interval( timing )
            
        #Find if previously paused
        wasPaused = False
        if self.paused():
            wasPaused = True
        
        #Start the thread
        self.enabled(True)
        if ( not self.progress() or time.time()-2 > self.progress() ) and not wasPaused:
            AutoSaveThread( wait )
            
    def pause(self):
        """Stop the thread from saving anything, but keep it running."""
        #Pause
        if self.enabled() == 1:
            self.enabled(-1)
            
        #Unpause
        if self.enabled() == -1:
            self.enabled(1)        
            
    def stop(self):
        """End the thread."""
        self.progress(False)
        
    def paused(self):
        """If the thread is currently paused."""
        return self.enabled() == -1
        
    def interval(self,timing=None):
        """Set or return the interval between saving.
        
        timing:
            Number of seconds between saving attempts. If left empty,
            returns the current set value.
             - Integer above 2
        """
        #Return current interval
        if timing==None:
            return pm.optionVar[AutoSaveThread.intervalName]
            
        #Check if it is a number
        try:
            int(timing)/1
        except:
            pass
        else:
            #Make sure it is above 2 seconds
            pm.optionVar[AutoSaveThread.intervalName]=max(2,timing)
            
    def enabled(self,state=None):
        """Set or return the current state of the thread. 1 or True is active,
        0 or False is stopped, and -1 is paused.
        
        state:
            Set the state of the thread. If left empty, returns the current 
            state.
             - Integer (1, 0, -1)
        """
        #Return current state
        if state==None:
            return pm.optionVar[AutoSaveThread.autoSaveName]
        
        #Set state
        pm.optionVar[AutoSaveThread.autoSaveName]=state
        
    def progress(self,progress=None):
        """Similar to the states, but used to check the thread is still
        active, and not just in an active state because of an improper
        shutdown. If it has not been updated in the last 2 seconds and
        AutoSave().start() is called, it is presumed the thread is not
        active.
        
        progress:
            Set the time of the latest thread activity. If left empty,
            returns the last time it was updated. Set to 0 to mark the
            thread as stopped.
             - Integer
        """
        #Return progress
        if progress==None:
            return pm.optionVar[AutoSaveThread.progressName]
         
        #Set progress
        pm.optionVar[AutoSaveThread.progressName]=progress
        
        #Update state if progress is False
        if progress==False:
            self.enabled(False)
            
    def silent(self,silence=None):
        """If all print messages should be disabled. Currently not recommended
        due to crashing if loading/closing the script editor during saving.
        
        silence:
            Choose if script should run silently. If left empty, returns the
            current setting.
             - Boolean
        """
        #Return if code should be silent
        if silence==None:
            return pm.optionVar[AutoSaveThread.printName]
        
        #Set if code should be silent
        pm.optionVar[AutoSaveThread.printName]=silence
        
        
    def location(self,update=None):
        """Location of the script editor files.
        
        update:
            Refresh the location. If left empty, return the stored location.
             - Boolean
        """
        #Return location of script editor files
        if update==None:
            return pm.optionVar[AutoSaveThread.locationName]
        
        #Refresh location of script editor files
        pm.optionVar[AutoSaveThread.locationName] = pm.internalVar( userPrefDir=True )


def MoveBackupScriptsToFolder( saveLocation=None ):
    """Move any files containing 'backup' in the name to a timestamped folder.
    
    saveLocation:
        Will automatically set itself to the correct value if left empty, 
        only needs to be given when being used inside a thread.
         - String:
            "C:/Users/(name)/Documents/Maya/(version)/prefs/"
            pm.internalVar( userPrefDir=True )
    """
    #Automatically set location
    if saveLocation == None:
        saveLocation = pm.optionVar[AutoSaveThread.locationName]
    
    #Get current folder and new folder names
    saveLocation += "scriptEditorTemp/"
    newBackupDir = saveLocation+'backup-'+str( int( time.time() ) )+"/"
    
    #Get list of files
    fileNames = [f for f in os.listdir( saveLocation ) if os.path.isfile( os.path.join( saveLocation, f ) )]
    for i in fileNames:
        if 'Backup' in i:
        
            #Make folder if it doesn't exist
            if not os.path.exists( newBackupDir ):
                os.makedirs( newBackupDir )
                
            #Move file
            os.rename(saveLocation+i, newBackupDir+i.replace( 'Backup', '' ))

#Reset progress in case it wasn't properly stopped on previous run
if firstRun:
    AutoSave().progress(False)
    MoveBackupScriptsToFolder( pm.optionVar[AutoSaveThread.locationName] )
