import os

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile
from Keystone.Utility.KeystoneUtils import GetFileName, RemoveOuterQuotes


class Keylink():

    def __init__(self, bindFile: BindFile, key: str, chord: str = ""):
        self.File = bindFile
        self.FilePath = os.path.abspath(bindFile.FilePath)
        self.Key = key
        self.Chord = chord
        self.Bind = None
        for bind in [b for b in bindFile.Binds if ((b.Key == key) and (b.Chord == chord))]:
            self.Bind = bind
        self.Command = None
        for command in [c for c in self.Bind.Commands if c.IsLoadFileCommand()]:
            self.Command = command
        targetFilePath = (RemoveOuterQuotes(self.Command.Text))
        if targetFilePath == "":
            self.TargetFilePath = ""
        else:
            self.TargetFilePath = os.path.abspath(targetFilePath)

    def ChangeKey(self, key):
        self.Key = key
        self.Bind.Key = key

    def ChangeChord(self, chord):
        self.Chord = chord
        self.Bind.Chord = chord

    def ChangeFilePath(self, filePath):
        self.FilePath = filePath
        self.File.FilePath = filePath

    def ChangeTargetFilePath(self, targetFilePath):
        self.TargetFilePath = os.path.abspath(targetFilePath)
        self.Command.Text = "\"" + self.TargetFilePath + "\""
