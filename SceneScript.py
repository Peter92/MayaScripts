import pymel.core as pm
from maya import OpenMaya
import cPickle, base64
class SceneScript(object):
    """Save scripts in the scene file."""
    
    dict_name = "scripts"
    def __init__(self):
        """Initialise the dictionary."""
        #Create dictionary
        if pm.fileInfo.get(self.dict_name, None) is None:
            self.reset()
        else:
            self.dict = self.decode(pm.fileInfo[self.dict_name])
    
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
        
        >>> SceneScript().remove("MyScript")
        
        >>> SceneScript().remove("MyScript1", "MyScript2")
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
        
        Execute a function without a return
        >>> SceneScript().add("MyScript", "def test(x): y=x*5")
        >>> SceneScript().run("MyScript", "test(10)")
        [None]
        
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
