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
        {}
        """
        self.dict = {}
        self._encode_dict()
        
    def clear(self):
        """Delete the dictionary.
        
        >>> SceneScript().clear()
        
        Stored information doesn't exist, so raises a KeyError
        >>> SceneScript.decode(pm.fileInfo[SceneScript.dict_name])
        Traceback (most recent call last):
        KeyError: 'scripts'
        """
        del pm.fileInfo[self.dict_name]
        
    def add(self, name, script):
        """Add new script to the dictionary.
        
        SceneScript().add(name, script):
            name: Name the script will be saved under.
            script: The script in a text format.
        
        >>> SceneScript().add("MyScript", "print 5")
        """
        self.dict[str(name)] = {}
        self.dict[str(name)]["script"] = str(script)
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
                    del self.dict[str(i)]
            self._encode_dict()
    
    def scripts(self):
        """Return a list of scripts.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript().scripts()
        ['MyScript']
        """
        return self.dict.keys()
    
    def get(self, script):
        """Return the code for a script.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript().get("MyScript")
        'print 5'
        """
        return self.dict[script]['script']
    
    def __getitem__(self, script):
        """Return the code for a script.
        
        >>> SceneScript().add("MyScript", "print 5")
        >>> SceneScript()["MyScript"]
        'print 5'
        """
        return self.dict[script]['script']
    
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
        exec(self.dict[script]["script"], new_globals)
        
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
        if not isinstance(callbackCommandObjects.get(script, None), list):
            callbackCommandObjects[script] = []
        
        #Make sure all are enclosed in quotations
        new_script = self._enclose(script)
        str_values = self._enclose(script)
        if args:
            str_values += ', ' + self._enclose(*args)
        if kwargs:
            str_values += ', ' + ', '.join(k+'='+str(v) for k,v in kwargs.iteritems())
        
        #Register callback
        callback_object = OpenMaya.MSceneMessage().addCallback( callbackID, self._callback_wrapper, str_values )
        
        #Write to dictionary
        callbackCommandObjects[script].append(callback_object)
        
        return callback_object
    
    def removeCallback(self, script):
        """Remove all callbacks relating to a script.
        
        >>> SceneScript().removeCallback("MyScript")
        """
        if callbackCommandObjects.get(script, None):
            for i in range(len(callbackCommandObjects[script])):
                self._del_callback(callbackCommandObjects[script][i])
            del callbackCommandObjects[script]
    
    def removeAllCallbacks(self):
        """Remove all custom callbacks.
        
        >>> SceneScript().removeAllCallbacks()
        """
        for script in callbackCommandObjects:
            self.removeCallback(i)
    
    def _del_callback(self, PyCObject):
        """Delete a callback object.
        
        Create PyCObject
        >>> SceneScript().add("MyScript", "def test(x): print x, 'scene saved'")
        >>> test_callback = SceneScript().addCallback(OpenMaya.MSceneMessage.kAfterSave, "MyScript", "test(y)", y=100)
        
        Remove callback
        >>> SceneScript().removeCallback(test_callback)
        """
        OpenMaya.MSceneMessage().removeCallback( PyCObject )
    
    def _callback_wrapper(self, input, *args):
        """Wrapper to unpack the args and kwargs."""
        unpacked = "SceneScript().run({})".format(input)
        exec(unpacked)
