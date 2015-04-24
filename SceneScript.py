import pymel.core as pm
from maya import OpenMaya
import cPickle, base64
from maya.utils import executeInMainThreadWithResult as execute
global callbackCommandObjects
try:
    callbackCommandObjects.keys()
except:
    callbackCommandObjects = {}
class SceneScript(object):
    """Save scripts in the scene file."""

    dict_name = "scripts"
    def __init__(self, **kwargs):
        """Initialise the dictionary."""
        if pm.fileInfo.get(self.dict_name, None) is None:
            self.reset()
        else:
            self.dict = self.decode(pm.fileInfo[self.dict_name])
        #Add kwargs to dictionary
        for k, v in kwargs.iteritems():
            self.add(k, v)
    
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
        {'callbacks': {}, 'script': {}}
        """
        self.dict = {}
        self.dict['script'] = {}
        self.dict['callbacks'] = {}
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
        self.dict['script'][str(name)] = str(script)
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
                if self.dict['script'].get(str(i), None) is not None:
                    del self.dict['script'][str(i)]
            self._encode_dict()
    
    def scripts(self):
        """Return a list of scripts.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript().scripts()
        ['MyScript']
        """
        return self.dict['script'].keys()
    
    def __getitem__(self, script):
        """Return the code for a script.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript()["MyScript"]
        'print 5'
        """
        return self.dict['script'][script]
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
        exec(self.dict['script'][script], new_globals)
        
        #Run individual commands and append outputs to a list
        all_outputs = []
        for i in args:
            if i:
                exec('script_output='+str(i), new_globals)
                all_outputs.append(new_globals['script_output'])
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
    
    def addCallback(self, callbackID, script, *args, **kwargs):
        """Add a script to run on an event.
        
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(y)", y=100)
        
        Remove callback
        >>> SceneScript()._del_callback( test_callback )
        """
        if script in self.dict['script']:
            
            #Make sure all are enclosed in quotations
            str_values = self._enclose(script)
            print args
            if args:
                str_values += ', ' + ', '.join(self._enclose(args))
            if kwargs:
                str_values += ', ' + ', '.join(k+'='+str(v) for k,v in kwargs.iteritems())
            
            #Write to self.dict
            if not isinstance(callbackCommandObjects.get(script, None), dict):
                callbackCommandObjects[script] = {}
            if not isinstance( self.dict['callbacks'].get(script, None), dict):
                self.dict['callbacks'][script] = {}
            try:
                newID = max(self.dict['callbacks'][script].keys())+1
            except ValueError:
                newID = 0
            self.dict['callbacks'][script][newID] = [callbackID, str_values]
            self._encode_dict()
            
            #Register callback
            callback_object = OpenMaya.MSceneMessage().addCallback(callbackID, self._callback_wrapper, str_values)
            
            #Write to session dictionary callbackCommandObjects = {}
            callbackCommandObjects[script][newID] = callback_object
            
            return callback_object
        else:
            raise KeyError("script name '{}' doesn't exist".format(script))
    
    def removeCallback(self, script, callbackID=None):
        """Remove all callbacks relating to a script.
        Skip if element doesn't exist.
        
        >>> SceneScript().removeCallback("MyScript")
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
                except RuntimeError:
                    pass
            #Remove listing if it contains nothing
            if not callbackCommandObjects[script].keys():
                del callbackCommandObjects[script]
        
        #Delete callback info from stored list
        if self.dict['callbacks'].get(script):
            #Remove an individual ID
            if callbackID is not None and self.dict['callbacks'][script]:
                del self.dict['callbacks'][script][callbackID]
            #Delete everything relating to a script
            elif callbackID is None:
                del self.dict['callbacks'][script]
            self._encode_dict()
    
    def removeAllCallbacks(self):
        """Remove all custom callbacks.
        
        >>> SceneScript().removeAllCallbacks()
        """
        allCallbacks = callbackCommandObjects.copy()
        for script in allCallbacks:
            self.removeCallback(script)
        self.dict['callbacks'] = {}
    
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
        """Wrapper to unpack the args and kwargs."""
        unpacked = "SceneScript().run({})".format(input)
        exec(unpacked)
    
    def _callback_list(self):
        """Build dictionary of callback commands."""
        allCallbacks = {}
        allCallbacks[0] = 'SceneUpdate'
        allCallbacks[1] = 'BeforeNew'
        allCallbacks[2] = 'AfterNew'
        allCallbacks[3] = 'BeforeImport'
        allCallbacks[4] = 'AfterImport'
        allCallbacks[5] = 'BeforeOpen'
        allCallbacks[6] = 'AfterOpen'
        allCallbacks[7] = 'BeforeFileRead'
        allCallbacks[8] = 'AfterFileRead'
        allCallbacks[9] = 'BeforeExport'
        allCallbacks[10] = 'AfterExport'
        allCallbacks[11] = 'BeforeSave'
        allCallbacks[12] = 'AfterSave'
        allCallbacks[13] = 'BeforeReference'
        allCallbacks[14] = 'AfterReference'
        allCallbacks[15] = 'BeforeRemoveReference'
        allCallbacks[16] = 'AfterRemoveReference'
        allCallbacks[17] = 'BeforeImportReference'
        allCallbacks[18] = 'AfterImportReference'
        allCallbacks[19] = 'BeforeExportReference'
        allCallbacks[20] = 'AfterExportReference'
        allCallbacks[21] = 'BeforeUnloadReference'
        allCallbacks[22] = 'AfterUnloadReference'
        allCallbacks[23] = 'BeforeSoftwareRender'
        allCallbacks[24] = 'AfterSoftwareRender'
        allCallbacks[25] = 'BeforeSoftwareFrameRender'
        allCallbacks[26] = 'AfterSoftwareFrameRender'
        allCallbacks[27] = 'SoftwareRenderInterrupted'
        allCallbacks[28] = 'MayaInitialized'
        allCallbacks[29] = 'MayaExiting'
        allCallbacks[30] = 'BeforeNewCheck'
        allCallbacks[31] = 'BeforeOpenCheck'
        allCallbacks[32] = 'BeforeSaveCheck'
        allCallbacks[33] = 'BeforeImportCheck'
        allCallbacks[34] = 'BeforeExportCheck'
        allCallbacks[35] = 'BeforeLoadReference'
        allCallbacks[36] = 'AfterLoadReference'
        allCallbacks[37] = 'BeforeLoadReferenceCheck'
        allCallbacks[38] = 'BeforeReferenceCheck'
        allCallbacks[39] = 'BeforePluginLoad'
        allCallbacks[40] = 'AfterPluginLoad'
        allCallbacks[41] = 'BeforePluginUnload'
        allCallbacks[42] = 'AfterPluginUnload'
        allCallbacks[43] = 'BeforeCreateReference'
        allCallbacks[44] = 'AfterCreateReference'
        allCallbacks[45] = 'ExportStarted'
        allCallbacks[46] = 'BeforeLoadReferenceAndRecordEdits'
        allCallbacks[47] = 'AfterLoadReferenceAndRecordEdits'
        allCallbacks[48] = 'BeforeCreateReferenceAndRecordEdits'
        allCallbacks[49] = 'AfterCreateReferenceAndRecordEdits'
        allCallbacks[50] = 'Last'
        return allCallbacks
    
    def listCallbacks(self):
        """Print the contents stored in the file."""
        allCallbacks = self._callback_list()
        for script in self.dict['callbacks']:
            print "{}:".format(script)
            #Print the script contents
            print "  Script:"
            print "    {}".format(self.get(script).replace("\n","\n    "))
            #Print the script callbacks
            if self.dict['callbacks'][script]:
                print "  Callbacks:"
                for id in self.dict['callbacks'][script]:
                    contents=self.dict['callbacks'][script][id]
                    print "    ID {}:".format(id)
                    print "      Callback: {} ({})".format(contents[0], self.convertCallbackID(contents[0]))
                    args_kwargs = contents[1].split(", ")
                    args = []
                    kwargs = []
                    #Separate args and kwargs
                    for i in args_kwargs:
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
    
    def convertCallbackID(self, ID):
        """Return the name of a callback ID."""
        return self._callback_list()[ID]
