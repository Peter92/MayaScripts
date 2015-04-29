import pymel.core as pm
from maya import OpenMaya
import cPickle, base64, re
from maya.utils import executeInMainThreadWithResult as execute
global callbackCommandObjects
first_run = False
try:
    callbackCommandObjects.keys()
except:
    callbackCommandObjects = {}
    first_run = True
    
def get_unique_id(f_name):
    """Randomly generate ID for computer."""
    try:
        with open(f_name, 'r') as f:
            id = str(f.read())
        if len(id) == 64:
            return id
        else:
            raise IOError("id format not valid")
    except IOError:
        import os, binascii
        with open(f_name, 'w') as f:
            id = binascii.hexlify(os.urandom(32))
            f.write(id)
        return get_unique_id(f_name)
        
class SceneScript(object):
    """Save scripts in the scene file."""

    dict_name = "scripts"
    def __init__(self, **kwargs):
        """Initialise the dictionary."""
        
        #Set variables to default values if fileInfo record doesn't exist
        if pm.fileInfo.get(self.dict_name, None) is None:
            self.reset()
        else:
            self.dict = self.decode(pm.fileInfo[self.dict_name])
            
        #Add kwargs to dictionary
        for k, v in kwargs.iteritems():
            self.add(k, v)
    
    def registerSceneCallbacks(self, *args):
        """
        Automatically register stored callbacks. 
        Set this command to run when the scene loads.
        """
        #Remove all callbacks created by code before registering more
        self.unregisterAllCallbacks(self)
        
        #Update dictionary since it will belong to old scene
        self.dict = SceneScript().dict
        
        #Iterate through all items and add as callback
        if self.dict.get('callbacks', None):
            for script in self.dict['callbacks']:
                if self.dict['callbacks'].get(script, None):
                    for id in self.dict['callbacks'][script]:
                        self._str_callback(script, id)
                        
    @classmethod
    def UID(self):
        return get_unique_id('SceneScripts.uid')
            
    @classmethod
    def encode(self, input):
        """Encode an input.
        
        SceneScript.encode(input):
            input: String to encode
        
        >>> SceneScript.encode({})
        'KGRwMQou'
        """
        return base64.b64encode(cPickle.dumps(input))
    
    @classmethod
    def decode(self, input):
        """Decode an input.
        
        SceneScript.decode(input):
            input: Encoded string (picked and converted to base64)
        
        >>> SceneScript.decode('KGRwMQou')
        {}
        """
        return cPickle.loads(base64.b64decode(input))
    
    def _encode_dict(self):
        """Store self.dict in the Maya file."""
        pm.fileInfo[self.dict_name] = self.encode(self.dict)
        
    def reset(self):
        """Empty the dictionary and reset to default.
        
        >>> SceneScript().reset()
        
        Stored information is an encoded empty dictionary
        >>> SceneScript.decode(pm.fileInfo[SceneScript.dict_name])
        {}
        """
        self.dict = {}
        self.removeAllCallbacks()
        self._encode_dict()
        
    def clear(self):
        """Delete the dictionary.
        
        >>> SceneScript().clear()
        
        Stored information doesn't exist, so raises a KeyError
        >>> SceneScript.decode(pm.fileInfo[SceneScript.dict_name])
        Traceback (most recent call last):
        KeyError: 'scripts'
        """
        self.removeAllCallbacks()
        del pm.fileInfo[self.dict_name]
        
    def add(self, name, script):
        """Add new script to the dictionary.
        
        SceneScript().add(name, script):
            name: Name the script will be saved under.
            script: The script in a text format.
        
        >>> SceneScript().add("MyScript", "print 5")
        """
        if str(name) not in self.dict:
            self.dict[str(name)] = {}
        self.dict[str(name)]['script'] = str(script)
        self._encode_dict()
        
    def remove(self, *args, **kwargs):
        """Remove script from the dictionary.
        
        SceneScript.remove(name):
            name (args): Names of the scripts to remove
            all (kwargs['all']): If all scripts should be removed
        
        >>> SceneScript().remove('MyScript')
        >>> SceneScript().remove('MyScript1', 'MyScript2')
        >>> SceneScript().remove(all=True)
        """
        
        if kwargs.get('all', None):
            #Remove all scripts
            self.reset()
            
        else:
            #Remove individual scripts
            for i in args:
                if self.dict.get(str(i), None) is not None:
                    self.removeCallback(str(i))
                    del self.dict[str(i)]
            self._encode_dict()
    
    def rename(self, original, new):
        """Rename a script.
        Will only run if the original name exists and new name doesnt.
        Returns True if something was renamed, False otherwise.
        
        SceneScript().rename(original_name, new_name)
            original_name: Name of the script to rename
            new_name: Name to change it to
        
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> print SceneScript().keys()
        ['MyScript']
        
        >>> SceneScript().rename('MyScript', 'MyNewScript')
        True
        
        >>> print SceneScript().keys()
        ['MyNewScript']
        
        >>> SceneScript().rename('MyScript', 'MyNewScript')
        False
        """
        if original in self.dict and new not in self.dict:
            self.dict[str(new)] = self.dict[original]
            del self.dict[original]
            self._encode_dict()
            return True
        return False
    
    def keys(self):
        return self.dict.keys()
        
    def __getitem__(self, script):
        """Return the code for a script.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript()["MyScript"]
        'print 5'
        """
        return self.dict[script]['script']
    get = __getitem__
    
    def run(self, script, *args, **kwargs):
        """Execute a script.
        
        SceneScript().run(name, command, variables):
            name: Name of the script to run
            command: Execute function commands, seperate them by commas
            variables: Pass variables to the script (otherwise it will try use global ones)
        
        Execute a simple line of code
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript().run("MyScript")
        5
        
        Execute a function with a return
        >>> SceneScript().add("MyScript", "def test(x): return x*5")
        >>> SceneScript().run("MyScript", "test(10)", "test('c')")
        [50, 'ccccc']
        
        Pass a variable to a function command
        >>> SceneScript().run("MyScript", 'test(a+b)', a=10, b=-50)
        [-200]
        
        Execute a function without a return
        >>> SceneScript().add("MyScript", "def test(x): print x*5")
        >>> SceneScript().run("MyScript", "test(10)", "test('c')")
        50
        ccccc
        [None, None]
        
        Pass a variable
        >>> SceneScript().add("MyScript", "print x")
        >>> SceneScript().run("MyScript", x=20)
        20
        """
        #Create a local version globals()
        new_globals = globals().copy()
        new_globals.update(kwargs)
        
        #Run the code
        exec(self.dict[script]['script'], new_globals)
        
        #Run individual commands and append outputs to a list
        all_outputs = []
        for i in args:
            if i:
                try:
                    exec('script_output='+str(i), new_globals)
                    all_outputs.append(new_globals['script_output'])
                #SyntaxError if it won't return a value, eg. script_output=print 5
                except SyntaxError:
                    exec(str(i), new_globals)
        if all_outputs:
            return all_outputs
    
    @classmethod
    def _enclose(self, input):
        """Enclose the input in quotations.
        
        >>> SceneScript._enclose("test")
        "'test'"
        
        >>> SceneScript._enclose(["test1", 'test2', 100])
        ["'test1'", "'test2'", '100']
        """
        
        #Convert to list
        was_list = True
        if not isinstance(input, (list, tuple)):
            input = [input]
            was_list = False
        input = list(input)
        
        #Iterate through each item
        for i in range(len(input)):
            word = input[i]
            #Make sure it is a string, otherwise ignore
            if isinstance( word, str ):
                if word[0] == word[-1]:
                    while word[0] in ("'", '"'):
                        word = word[1:-1]
                input[i] = "'"+word+"'"
            else:
                input[i] = str(word)
        
        #Get first element if it wasn't originally a list or tuple
        if not was_list:
            input = input[0]
            
        return input
    
    
    
    
    def removeOwnership(self, script=None, callbackID=None):
        """Remove ownership of callbacks, which will stop them activating.
        Leave empty for all, or specify which ones.
        
        SceneScript().removeOwnership(script, callbackID)
            script: Names of scripts to deactivate (optional)
            callbackID: IDs of callbacks for a script (optional)
            
        Create PyCObject
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(10)")
        
        Remove ownsership
        >>> SceneScript().removeOwnership('MyScript')
        """
        self.claimOwnership(script, callbackID, unregister=True)
    
    def claimOwnership(self, script=None, callbackID=None, **kwargs):
        """Claim ownership of callbacks, which is needed to activate them.
        Leave empty for all, or specify which ones.
        
        SceneScript().claimOwnership(script, callbackID)
            script: Names of scripts to activate (optional)
            callbackID: IDs of callbacks for a script (optional)
        
        Create unregistered PyCObject
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(10)", register=False)
        
        Claim ownership
        >>> SceneScript().claimOwnership()
        """
        
        
        #What to set ID to
        if kwargs.get('unregister', None):
            userID = None
        else:
            userID = SceneScript.UID()
        
        #Build list of scripts to register ownership
        if script is None:
            listOfScripts = self.dict.keys()
        elif not isinstance(script, (list, tuple)):
            listOfScripts = [script]
            
        
        #Build ID list
        if callbackID is None:
            pass
        elif not isinstance(callbackID, (list, tuple)):
            listOfIDs = [callbackID]
            
        for script in listOfScripts:
            if self.dict.get(script, None):
                
                #If ID is empty, build it with all values
                if callbackID is None:
                    if self.dict[script].get('callbacks', None):
                        listOfIDs = self.dict[script]['callbacks'].keys()
                    else:
                        listOfIDs = []
                
                #Iterate through all the IDs and set user ID
                for id in listOfIDs:
                    self.dict[script]['callbacks'][id][2] = userID
                
        self._encode_dict()
    
                        
    
    def _str_callback(self, script, id):
        """Wrapper for if the callback information is in the correct format."""
        
        if script in self.dict:
            self._reg_callback(script, id)
    
    def _reg_callback(self, script, id):
        """Register a callback matching the script and ID."""
        
        callback_data = self.dict[script]['callbacks'][id]
        
        #Make sure session dictionary is a dictionary
        if not isinstance(callbackCommandObjects.get(script, None), dict):
            callbackCommandObjects[script] = {}
        
        if SceneScript.UID() == callback_data[2]:
            
            self.unregisterCallback(script, id)
            '''
            #Remove existing callback if exists
            if callbackCommandObjects[script].get(id) is not None:
                self._del_callback(callbackCommandObjects[script][id])
                del callbackCommandObjects[script][id]
                '''
            if callbackCommandObjects.get(script) is None:
                callbackCommandObjects[script] = {}
                
            #Register callback
            callback_object = OpenMaya.MSceneMessage().addCallback(callback_data[0], self._callback_wrapper, callback_data[1])
            
            #Write to session dictionary
            callbackCommandObjects[script][id] = callback_object
            
            return callback_object
        
    
    def addCallback(self, callbackID, script, *args, **kwargs):
        """Add a callback to the scene store.
        Use 'register=False' to stop the script automatically calling when the scene loads.
        
        Add script
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        
        Register as callback
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(y)", y=100)
        
        Remove callback
        >>> SceneScript()._del_callback(test_callback)
        """
        
        if script in self.dict:
            
            #Get user ID
            if kwargs.get('register') == False:
                userID = None
            else:
                userID = SceneScript.UID()
            try:
                del kwargs['register']
            except KeyError:
                pass
                
            #Make sure all are enclosed in quotations
            str_values = self._enclose(script)
            if args:
                str_values += ', ' + ', '.join(self._enclose(args))
            if kwargs:
                str_values += ', ' + ', '.join(k+'='+str(v) for k,v in kwargs.iteritems())
            
            #Get next script ID
            if not isinstance( self.dict[script].get('callbacks', None), dict):
                self.dict[script]['callbacks'] = {}
            try:
                newID = max(self.dict[script]['callbacks'].keys())+1
            except ValueError:
                newID = 0
            
                
            self.dict[script]['callbacks'][newID] = [callbackID, str_values, userID]
            self._encode_dict()
            
            #Register callback
            callbackData = self._reg_callback(script, newID)
            return callbackData
            
        else:
            raise KeyError("script name '{}' doesn't exist".format(script))
    
    def unregisterCallback(self, script, callbackID=None):
        """Unregister callback, but do not delete from stored information.
        Skip if element doesn't exist.
        
        >>> SceneScript().unregisterCallback("MyScript")
        """
        
        #Remove stored callback
        if callbackCommandObjects.get(script, None):
            callbackIDs = callbackCommandObjects[script].keys()
            if callbackID:
                callbackIDs = [callbackID]
            for i in callbackIDs:
                try:
                    self._del_callback(callbackCommandObjects[script][i])
                    del callbackCommandObjects[script][i]
                except (RuntimeError, KeyError):
                    pass
            #Remove listing if it contains nothing
            if not callbackCommandObjects[script].keys():
                del callbackCommandObjects[script]
        
    
    def removeCallback(self, script, callbackID=None):
        """Remove all callbacks relating to a script.
        Skip if element doesn't exist.
        
        >>> SceneScript().removeCallback("MyScript")
        """
        
        self.unregisterCallback(script, callbackID)
        
        #Delete callback info from stored list
        if self.dict.get(script, None):
            if self.dict[script].get('callbacks', None):
                #Remove an individual ID
                if callbackID is not None and self.dict[script]['callbacks']:
                    del self.dict[script]['callbacks'][callbackID]
                #Delete everything relating to a script
                elif callbackID is None:
                    del self.dict[script]['callbacks']
                self._encode_dict()
    
    def unregisterAllCallbacks(self, *args):
        """Unregister all custom callbacks."""
        allCallbacks = callbackCommandObjects.copy()
        for script in allCallbacks:
            self.unregisterCallback(script)
    
    def removeAllCallbacks(self):
        """Remove all custom callbacks.
        
        >>> SceneScript().removeAllCallbacks()
        """
        allCallbacks = callbackCommandObjects.copy()
        for script in allCallbacks:
            self.removeCallback(script)
        for script in self.dict:
            self.dict[script]['callbacks'] = {}
        self._encode_dict()
    
    def _del_callback(self, PyCObject):
        """Delete a callback object.
        
        Create PyCObject
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(y)", y=100)
        
        Remove callback
        >>> SceneScript().removeCallback(test_callback)
        """
        OpenMaya.MSceneMessage().removeCallback(PyCObject)
    
    def _callback_wrapper(self, input, *args):
        """Wrapper to unpack the args and kwargs from a string."""
        unpacked = "SceneScript().run({})".format(input)
        exec(unpacked)
    
    def _callback_list(self):
        """Build dictionary of callback commands."""
        allCallbacks = {}
        allCallbacks[0] = 'kSceneUpdate'
        allCallbacks[1] = 'kBeforeNew'
        allCallbacks[2] = 'kAfterNew'
        allCallbacks[3] = 'kBeforeImport'
        allCallbacks[4] = 'kAfterImport'
        allCallbacks[5] = 'kBeforeOpen'
        allCallbacks[6] = 'kAfterOpen'
        allCallbacks[7] = 'kBeforeFileRead'
        allCallbacks[8] = 'kAfterFileRead'
        allCallbacks[9] = 'kBeforeExport'
        allCallbacks[10] = 'kAfterExport'
        allCallbacks[11] = 'kBeforeSave'
        allCallbacks[12] = 'kAfterSave'
        allCallbacks[13] = 'kBeforeReference'
        allCallbacks[14] = 'kAfterReference'
        allCallbacks[15] = 'kBeforeRemoveReference'
        allCallbacks[16] = 'kAfterRemoveReference'
        allCallbacks[17] = 'kBeforeImportReference'
        allCallbacks[18] = 'kAfterImportReference'
        allCallbacks[19] = 'kBeforeExportReference'
        allCallbacks[20] = 'kAfterExportReference'
        allCallbacks[21] = 'kBeforeUnloadReference'
        allCallbacks[22] = 'kAfterUnloadReference'
        allCallbacks[23] = 'kBeforeSoftwareRender'
        allCallbacks[24] = 'kAfterSoftwareRender'
        allCallbacks[25] = 'kBeforeSoftwareFrameRender'
        allCallbacks[26] = 'kAfterSoftwareFrameRender'
        allCallbacks[27] = 'kSoftwareRenderInterrupted'
        allCallbacks[28] = 'kMayaInitialized'
        allCallbacks[29] = 'kMayaExiting'
        allCallbacks[30] = 'kBeforeNewCheck'
        allCallbacks[31] = 'kBeforeOpenCheck'
        allCallbacks[32] = 'kBeforeSaveCheck'
        allCallbacks[33] = 'kBeforeImportCheck'
        allCallbacks[34] = 'kBeforeExportCheck'
        allCallbacks[35] = 'kBeforeLoadReference'
        allCallbacks[36] = 'kAfterLoadReference'
        allCallbacks[37] = 'kBeforeLoadReferenceCheck'
        allCallbacks[38] = 'kBeforeReferenceCheck'
        allCallbacks[39] = 'kBeforePluginLoad'
        allCallbacks[40] = 'kAfterPluginLoad'
        allCallbacks[41] = 'kBeforePluginUnload'
        allCallbacks[42] = 'kAfterPluginUnload'
        allCallbacks[43] = 'kBeforeCreateReference'
        allCallbacks[44] = 'kAfterCreateReference'
        allCallbacks[45] = 'kExportStarted'
        allCallbacks[46] = 'kBeforeLoadReferenceAndRecordEdits'
        allCallbacks[47] = 'kAfterLoadReferenceAndRecordEdits'
        allCallbacks[48] = 'kBeforeCreateReferenceAndRecordEdits'
        allCallbacks[49] = 'kAfterCreateReferenceAndRecordEdits'
        allCallbacks[50] = 'kLast'
        return allCallbacks
    
    def listCallbacks(self):
        """Print a list of all usable callback commands."""
        allCallbacks = self._callback_list()
        for i in allCallbacks:
            print "{}: {}".format(i, allCallbacks[i])
    
    def convertCallbackID(self, ID):
        """Return the name of a callback ID.
        
        >>> SceneScript().convertCallbackID(5)
        'kBeforeOpen'
        """
        return self._callback_list()[ID]
    
    def scripts(self, *args):
        """Print the contents stored in the file."""
        allCallbacks = self._callback_list()
        for script in self.dict:
            print "{}:".format(script)
            #Print the script contents
            print "  Script: {}".format(('\n'+self.dict[script]['script']).replace("\n","\n    >>> "))
            #Print the script callbacks]
            if self.dict.get(script, None):
                if self.dict[script].get('callbacks', None):
                    print "  Callbacks:"
                    for id in self.dict[script]['callbacks']:
                        contents=self.dict[script]['callbacks'][id]
                        print "    ID {}:".format(id)
                        if contents[2] != SceneScript.UID() and False:
                            contents[2] = str(contents[2])
                            contents[2] += " (no match - will not register callback)"
                        print "      User ID: {}".format(contents[2])
                        if contents[2] != SceneScript.UID():
                            print "        - Warning: will not register callback, ID doesn't match"
                        callbackName = ' '.join(re.findall('[A-Z][a-z]*', allCallbacks[contents[0]]))
                        print "      Callback {}: {}".format(contents[0], callbackName)
                        args_kwargs = contents[1].split(", ")
                        args = []
                        kwargs = []
                        #Separate args and kwargs
                        for i in args_kwargs[1:]:
                            is_arg = True
                            for letter in i:
                                if letter in ("'",'"'):
                                    break
                                elif letter in ("="):
                                    is_arg = False
                                    break
                            if is_arg:
                                args.append(i)
                            else:
                                kwargs.append(i)
                        if args:
                            print "      Commands: {}".format(", ".join(args))
                        if kwargs:
                            print "      Variables: {}".format(", ".join(kwargs))
            print "Personal ID: {}".format(SceneScript.UID())


if first_run:
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kBeforeOpen, SceneScript().unregisterAllCallbacks)
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kBeforeNew, SceneScript().unregisterAllCallbacks)
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kMayaExiting, SceneScript().unregisterAllCallbacks)
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kMayaInitialized, SceneScript().registerSceneCallbacks)
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kAfterOpen, SceneScript().registerSceneCallbacks)
    OpenMaya.MSceneMessage().addCallback(OpenMaya.MSceneMessage.kAfterNew, SceneScript().registerSceneCallbacks)
