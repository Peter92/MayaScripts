import threading
import time
import pymel.core as pm
import maya.utils as utils
import maya.mel as mel
 
class ThreadingExample(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True # Daemonize thread
        thread.start() # Start the execution
    def run(self):
        print "Backup started"
        while AutoSave:
            if self.interval>5:
                time.sleep(self.interval-4)
                print('Saving in 4 seconds')
                time.sleep(4)
            else:
                time.sleep(self.interval)
            mel.eval( 'syncExecuterBackupFiles()' )
        print "Backup stopped"
    
    def stop(self):
        self.a = False

global AutoSave
AutoSave = True

ThreadingExample(10)
