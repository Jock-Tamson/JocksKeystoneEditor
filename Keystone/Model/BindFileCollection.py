import os as os
import json as json
import tempfile

from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Utility.KeystoneUtils import GetUniqueFilePath, RemoveOuterQuotes, RemoveStartAndEndDirDelimiters

NEW_FILE = "<New File>"
ROOT = "root"
BOUND_FILES = "bound_files"
PATH = "path"
REPR = "repr"

def GetKeyChains(bindFile: BindFile, path: str, result, boundFiles = None):

    def addBoundFile(keyToAdd: str, fileToAdd: BindFile) -> bool:
        if keyToAdd in result:
            pathToAdd = os.path.abspath(fileToAdd.FilePath)
            if (not [b.FilePath for b in result[keyToAdd]].__contains__(pathToAdd)):
                result[keyToAdd].append(fileToAdd)
            else:
                return False
        else:
            result[keyToAdd] = [fileToAdd]
        return True

    if (path == None):
        path = ""
    else:
        path = os.path.abspath(path)
        
    for bind in bindFile.GetLoadFileBinds():
        for command in bind.GetLoadFileCommands():
            boundPath = command.GetTargetFile()
            if (boundPath == path):
                continue
            boundKey = bind.GetKeyWithChord()
            if (boundFiles == None):
                boundFile = ReadBindsFromFile(boundPath)
            else:
                match = [b for b in boundFiles if b.FilePath == boundPath]
                if (len(match) > 0):
                    boundFile = match[0]
                else:
                    continue
            if ( not addBoundFile(boundKey, boundFile)):
                continue

            GetKeyChains(boundFile, boundPath, result, boundFiles)

class BindFileCollection():

    def Load(self, filePath: str, bindFile = None):
        self.FilePath = filePath
        if (bindFile == None):
            bindFile = ReadBindsFromFile(filePath)
        self.File = bindFile
        GetKeyChains(self.File, filePath, self.KeyChains)

    def New(self, defaults: bool = False):
            self.FilePath = None
            self.File = NewBindFile(defaults)

    def GetBoundFiles(self):
        result = []
        for keyBind, boundFiles in self.KeyChains.items():
            for boundFile in boundFiles:
                result.append(boundFile)
            keyBind = keyBind #makes warnings happy
        return result

    def Serialize(self, filePath):
        self.RepointFilePaths("C:\\keybinds.txt", True)
        file_dict = {ROOT : self.File.__repr__()}
        bound_files = []
        for boundFile in self.GetBoundFiles():
            bound_file_dict = {}
            bound_file_dict[PATH] = boundFile.FilePath.replace("C:", ROOT)
            bound_file_dict[REPR] = boundFile.__repr__()
            bound_files.append(bound_file_dict)
        file_dict[BOUND_FILES] = bound_files
        with open(filePath, "w+") as json_file:
            json.dump(file_dict, json_file)


    def Deserialize(self, filePath):
        with open(filePath, "r") as json_file:
            data = json.load(json_file)
        self.FilePath = "C:\\keybinds.txt"
        self.File = BindFile(repr=data[ROOT])
        self.File.FilePath = self.FilePath
        boundFiles = []
        for boundFileEntry in data[BOUND_FILES]:
            boundFile = BindFile(repr=boundFileEntry[REPR])
            boundFile.FilePath = boundFileEntry[PATH].replace(ROOT, "C:")
            boundFiles.append(boundFile)
        self.KeyChains = {}
        GetKeyChains(self.File, self.FilePath, self.KeyChains, boundFiles)


    def RepointFilePaths(self, newFilePath: str, overwrite: bool = False):
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


    def __init__(self, filePath: str = ''):

        self.FilePath = None
        self.File = None
        self.KeyChains = {}
        if os.path.exists(filePath):
            self.Load(filePath)