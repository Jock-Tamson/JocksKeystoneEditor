import os as os

from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Utility.KeystoneUtils import GetUniqueFilePath, RemoveOuterQuotes

NEW_FILE = "<New File>"

def GetKeyChains(bindFile: BindFile, path: str, result):

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

    path = os.path.abspath(path)
    for bind in bindFile.GetLoadFileBinds():
        for command in bind.GetLoadFileCommands():
            boundPath = command.GetTargetFile()
            if (boundPath == path):
                continue
            boundKey = bind.GetKeyWithChord()
            boundFile = ReadBindsFromFile(boundPath)
            if ( not addBoundFile(boundKey, boundFile)):
                continue

            GetKeyChains(boundFile, boundPath, result)

class BindFileCollection():

    def Load(self, filePath: str):
        self.FilePath = filePath
        self.File = ReadBindsFromFile(filePath)
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

    def RepointFilePaths(self, newFilePath: str, overwrite: bool = False):
        if (self.File.FilePath == None):
            return
        currentFilePath = os.path.abspath(self.File.FilePath)
        newFilePath = os.path.abspath(newFilePath)
        if (currentFilePath == newFilePath):
            return
        currentDirectory = os.path.dirname(currentFilePath)
        newDirectory = os.path.dirname(newFilePath)

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
