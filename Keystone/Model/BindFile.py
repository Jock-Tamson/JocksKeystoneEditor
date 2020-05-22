import os

from Keystone.Model.Bind import Bind
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import (DEFAULT_BIND,
                                                   DEFAULT_COMMAND,
                                                   DEFAULT_KEY_BINDINGS)
from Keystone.Utility.KeystoneUtils import (GetFileName, GetUniqueFilePath,
                                            MatchKeyName)


#object for a set of keybinds to save or load from a file
class BindFile():

    LINE_SEPARATOR = "\n"

    #parse a file read in as a single string
    def Parse(self, repr: str):
        parts = repr.split(self.LINE_SEPARATOR)
        self.Binds = [Bind(repr=p) for p in parts if (p != "")]

    #init from a list of Bind objects or a representive string
    #if repr is set binds is ignored
    def __init__(self, binds: [Bind] = None , repr:str = "", filePath:str = None):

        self.Binds = None

        self.FilePath = None
        
        if (repr == ""):
            self.Binds = binds
        else:
            self.Parse(repr=repr)
        self.FilePath = filePath

    def __repr__(self):
        return self.LINE_SEPARATOR.join([str(b) for b in self.Binds])

    #Overwrite or create a file from the binds in the object
    def WriteBindsToFile(self, filePath: str = None):
        if (filePath == None):
            filePath = self.FilePath
        if (filePath == None):
            return
        directory = os.path.dirname(filePath)
        if (not os.path.exists(directory)):
            os.makedirs(directory, exist_ok=True)
        file = open(filePath, "w+")
        try:
            file.write(self.__repr__())
        finally:
            file.close()
        self.FilePath = filePath

    def GetLoadFileBinds(self):
        return [b for b in self.Binds if b.IsLoadFileBind()]

    def RepointFilePaths(self, newFilePath: str, overwrite: bool = False):
        currentFilePath = os.path.abspath(self.FilePath)
        newFilePath = os.path.abspath(newFilePath)
        if (currentFilePath == newFilePath):
            return #No change, exit
        if ((not overwrite) and (os.path.exists(newFilePath))):
            newFilePath = GetUniqueFilePath(newFilePath)
        self.FilePath = newFilePath
        currentDirectory = os.path.dirname(currentFilePath)
        newDirectory = os.path.dirname(newFilePath)
        for bind in self.GetLoadFileBinds():
            for command in bind.GetLoadFileCommands():
                currentTargetPath = command.GetTargetFile()
                if (currentTargetPath == currentFilePath):
                    command.SetTargetFile(newFilePath)
                else:
                    newTargetPath = currentTargetPath.replace(currentDirectory, newDirectory)
                    if ((not overwrite) and (os.path.exists(newTargetPath))):
                        newTargetPath = GetUniqueFilePath(newTargetPath)
                    command.SetTargetFile(newTargetPath)

    def GetBindForKey(self, key, chord = ""):
        quickMatch = [b for b in self.Binds if ((b.Key == key) and ((chord == None) or (b.Chord == chord)))]
        if (len(quickMatch) > 0):
            return quickMatch
        dummyForConversion = Bind(key=key, chord=chord)
        defaultedName = dummyForConversion.GetKeyWithChord(defaultNames=True)
        return [b for b in self.Binds if (defaultedName == b.GetKeyWithChord(defaultNames=True))]


#Load a BindFile object from a text file
def ReadBindsFromFile(filePath: str) -> BindFile:
    file = open(filePath)
    try:
        text = file.read()
    finally:
      file.close()
    return BindFile(repr=text, filePath = filePath)

#Create a new bind file from defaults
def NewBindFile(defaults: bool = False) -> BindFile:
    
    if (defaults):
        repr = DEFAULT_KEY_BINDINGS
    else:
        repr = DEFAULT_BIND
    return BindFile(repr=repr)

def GetDefaultBindForKey(key, chord = "") -> Bind:
    bindFile = NewBindFile(defaults=True)
    binds = bindFile.GetBindForKey(key, chord)
    if (len(binds) > 0):
        return binds[0]
    else:
        return Bind(key, chord, [SlashCommand(repr=DEFAULT_COMMAND)])
