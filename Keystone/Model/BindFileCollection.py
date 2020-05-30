import ast
import os as os
import json as json
import tempfile

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Model.Keychain import Keychain, BOUND_FILES, NONE, PATH, REPR

from Keystone.Utility.KeystoneUtils import GetUniqueFilePath, RemoveOuterQuotes, RemoveStartAndEndDirDelimiters

NEW_FILE = "<New File>"
ROOT = "root"
DESCRIPTION = 'description'
KEY_CHAINS = 'key_chains'



def getBoundFiles(path, bind: Bind, foundFiles, boundFiles):
    for command in bind.GetLoadFileCommands():
        boundPath = command.GetTargetFile()
        if (os.path.realpath (boundPath) == os.path.realpath (path)):
            continue
        if (boundFiles == None):
            if (os.path.exists(boundPath)):
                boundFile = ReadBindsFromFile(boundPath)
            else:
                continue
        else:
            match = [b for b in boundFiles if os.path.realpath (b.FilePath) == os.path.realpath (boundPath)]
            if (len(match) > 0):
                boundFile = match[0]
            elif (os.path.exists(boundPath)):
                boundFile = ReadBindsFromFile(boundPath)
            else:
                continue
        match = [b for b in foundFiles if os.path.realpath (b.FilePath) == os.path.realpath (boundFile.FilePath)]
        if (len(match) > 0):
            continue
        foundFiles.append(boundFile.Clone())
        for chainBind in boundFile.GetLoadFileBinds():
                for foundFile in getBoundFiles(path, chainBind, foundFiles, boundFiles):
                    match = [b for b in foundFiles if os.path.realpath (b.FilePath) == os.path.realpath (boundFile.FilePath)]
                    if (len(match) > 0):
                        continue
                    foundFiles.append(foundFile)
        
    return foundFiles

def GetKeyChains(bindFile: BindFile, path: str, boundFiles = None):

    result = []   

    if (path == None):
        path = ""
    else:
        path = os.path.abspath(path) 
    for bind in bindFile.GetLoadFileBinds():
        chainFiles = getBoundFiles(path, bind, [], boundFiles)
        if (len(chainFiles) > 0):
            result.append(Keychain(key=bind.Key, chord=bind.Chord, boundFiles=chainFiles))

    if (len(result) == 0):
        result = None

    return result

class BindFileCollection():

    def Load(self, filePath: str, bindFile = None, boundFilesSource = None):
        self.FilePath = filePath
        if (bindFile == None):
            bindFile = ReadBindsFromFile(filePath)
        self.File = bindFile
        if ((boundFilesSource != None) and (len(boundFilesSource) == 0)):
            boundFilesSource = None
        self.KeyChains = GetKeyChains(self.File, filePath, boundFilesSource)

    def New(self, defaults: bool = False):
            self.FilePath = None
            self.File = NewBindFile(defaults)

    def GetBoundFiles(self):
        result = []
        if self.KeyChains == None:
            return result
        for keyChain in self.KeyChains:
            if keyChain.BoundFiles == None:
                continue
            for boundFile in keyChain.BoundFiles:
                result.append(boundFile)
        return result

    def Serialize(self, filePath):
        clone = self.Clone()
        clone.RepointFilePaths("C:\\keybinds.txt", True)
        file_dict = clone.GetDictionary()
        with open(filePath, "w+") as json_file:
            json.dump(file_dict, json_file)

    def Deserialize(self, filePath):
        with open(filePath, "r") as json_file:
            data = json.load(json_file)
        self.LoadDictionary(data, serialization = True)

    def RepointFilePaths(self, newFilePath: str, overwrite: bool = False):

        if (newFilePath == None):
            self.File.FilePath = None

            boundFiles = self.GetBoundFiles()
            for boundFile in boundFiles:
                boundFile.FilePath = None

            return

        if (self.File.FilePath == None):
            return
        currentFilePath = os.path.abspath(self.File.FilePath)
        newFilePath = os.path.abspath(newFilePath)
        if (currentFilePath == newFilePath):
            return
        currentDirectory = RemoveStartAndEndDirDelimiters(os.path.dirname(currentFilePath))
        newDirectory = RemoveStartAndEndDirDelimiters(os.path.dirname(newFilePath))

        self.File.RepointFilePaths(newFilePath, overwrite)

        boundFiles = self.GetBoundFiles()
        for boundFile in boundFiles:
            currentFilePath = os.path.abspath(boundFile.FilePath)
            newFilePath = currentFilePath.replace(currentDirectory, newDirectory)
            if ((not overwrite) and (os.path.exists(newFilePath))):
                newFilePath = GetUniqueFilePath(newFilePath)
            boundFile.RepointFilePaths(newFilePath, overwrite)

    def Save(self, filePath: str = None, overwrite: bool = False):
        if (filePath == None):
            filePath = self.File.FilePath
        currentFilePath = self.File.FilePath

        if (filePath != currentFilePath):
            self.RepointFilePaths(filePath, overwrite)

        self.File.WriteBindsToFile(filePath)

        boundFiles = self.GetBoundFiles()
        for boundFile in boundFiles:
            boundFile.WriteBindsToFile()


    def __init__(self, filePath: str = '', bindFile: BindFile = None, keyChains:[Keychain] = None, description = None, repr=''):

        if (repr != ''):
            self.Parse(repr)
        else:
            self.FilePath = filePath
            self.File = bindFile
            self.KeyChains = None
            self.Description = description

    def LoadDictionary(self, data, serialization = False):
        if serialization:
            self.FilePath = "C:\\keybinds.txt"
        else:
            path = data[PATH]
            if path == NEW_FILE:
                self.FilePath = None
            else:
                self.FilePath = data[PATH]
        description = data[DESCRIPTION]
        if (description == NONE):
            self.Description = None
        else:
            self.Description = description
        self.File = BindFile(repr=data[ROOT])
        self.File.FilePath = self.FilePath
        keyChains = data[KEY_CHAINS]
        if (keyChains == None):
            self.KeyChains = None
        else:
            self.KeyChains = []
            for entry in keyChains:
                if serialization:
                    for boundFile in entry[BOUND_FILES]:
                        boundFile[PATH] = boundFile[PATH].replace(ROOT, "C:")
                self.KeyChains.append(Keychain(repr=entry.__repr__()))

    def GetDictionary(self, serialization = False):
        data = {}
        if self.FilePath == None:
            data[PATH] = NEW_FILE
        else:
            data[PATH] = self.FilePath
        if self.Description == None:
            data[DESCRIPTION] = None
        else:
            data[DESCRIPTION] = self.Description
        data[ROOT] = self.File.__repr__()
        if self.KeyChains == None:
            data[KEY_CHAINS] = NONE
        else:
            keyChains = []
            for keyChain in self.KeyChains:
                chain_dict = keyChain.GetDictionary()
                if (serialization):
                    for entry in chain_dict[BOUND_FILES]:
                        entry[PATH] = entry[PATH].replace("C:", ROOT)
                keyChains.append(chain_dict)
            data[KEY_CHAINS] = keyChains
        return data

    def Parse(self, repr: str):
        data = ast.literal_eval(repr)
        self.LoadDictionary(data)

    def __repr__(self)->str:
        return self.GetDictionary().__repr__()

    def Clone(self):
        return BindFileCollection(repr=self.__repr__())
