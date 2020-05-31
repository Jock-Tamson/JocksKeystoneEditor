import ast

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile

KEY = "key"
CHORD = "chord"
BOUND_FILES = "bound_files"
PATH = "path"
REPR = "repr"
NONE = "none"

class Keychain():

    def __init__(self, repr: str = "", key: str = "", chord: str = "", boundFiles: [BindFile] = None):
        if (repr != ""):
            self.Parse(repr)
        else:
            self.parserBind = Bind(key=key, chord=chord)
            self.Key = self.parserBind.GetDefaultedKeyName()
            self.Chord = self.parserBind.GetDefaultedChordName()
            self.BoundFiles = boundFiles

    def Parse(self, repr: str):
        keychainDict = ast.literal_eval(repr)
        self.parserBind = Bind(key=keychainDict[KEY], chord=keychainDict[CHORD])
        self.Key = self.parserBind.GetDefaultedKeyName()
        self.Chord = self.parserBind.GetDefaultedChordName()
        boundFilesRepr = keychainDict[BOUND_FILES]
        if boundFilesRepr == NONE:
            boundFiles = None
        else:
            boundFiles = []
            for boundFileEntry in boundFilesRepr:
                boundFile = BindFile(repr=boundFileEntry[REPR])
                boundFile.FilePath = boundFileEntry[PATH]
                boundFiles.append(boundFile)
        self.BoundFiles = boundFiles
    
    def GetKeyWithChord(self):
        return self.parserBind.GetKeyWithChord(defaultNames=True)

    #Dictionary structure
    #KEY - Key for bind in root file
    #CHORD - Chord for bind in root file
    #BOUND_FILES- Array of dictionaries for bound files
        #PATH - Path from load command
        #REPR - repr string of loaded bind file

    def GetDictionary(self):
        keychainDict = {}
        keychainDict[KEY] = self.Key
        keychainDict[CHORD] = self.Chord
        if self.BoundFiles == None:
            keychainDict[BOUND_FILES] = NONE
        else:
            bound_files = []
            for boundFile in self.BoundFiles:
                bound_file_dict = {}
                bound_file_dict[PATH] = boundFile.FilePath
                bound_file_dict[REPR] = boundFile.__repr__()
                bound_files.append(bound_file_dict)
            keychainDict[BOUND_FILES] = bound_files
        return keychainDict


    def __repr__(self)->str:
        keychainDict = self.GetDictionary()
        return keychainDict.__repr__()

    def Clone(self):
        return Keychain(repr=self.__repr__())
