import os

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile
from Keystone.Model.BindFileCollection import BindFileCollection
from Keystone.Model.Keylink import Keylink
from Keystone.Model.SlashCommand import LOAD_FILE_COMMANDS, SlashCommand
from Keystone.Reference.DefaultKeyBindings import DEFAULT_BIND
from Keystone.Utility.KeystoneUtils import GetFileName, GetUniqueFilePath


class Keychain():

    def __init__(self, bindFileCollection: BindFileCollection, key: str, chord: str =""):
        self.Collection = bindFileCollection
        self.Anchor = Keylink(bindFileCollection.File, key, chord)
        self.RootPath = os.path.dirname(self.Anchor.FilePath)
        self.Links = []
        self.Key = key
        self.Chord = chord
        keyChord = Bind(key, chord).GetKeyWithChord()
        for bindFile in bindFileCollection.KeyChains[keyChord]:
            self.Links.append(Keylink(bindFile, key, chord))

    def _changeVar(self, val, chord: bool = False):

        if (chord):
            self.Chord = val
        else:
            self.Key = val

        #note old dict key
        oldKeyChord = self.Anchor.Bind.GetKeyWithChord()

        #set to Anchor
        if (chord):
            self.Anchor.ChangeChord(val)
        else:
            self.Anchor.ChangeKey(val)
        
        #swap in new dict key
        keyChord = self.Anchor.Bind.GetKeyWithChord()
        self.Collection.KeyChains[keyChord] = self.Collection.KeyChains[oldKeyChord]
        del self.Collection.KeyChains[oldKeyChord]

        #set to Links
        for link in self.Links:
            if (chord):
                link.ChangeChord(val)
            else:
                link.ChangeKey(val)

    def ChangeKey(self, key):
        self._changeVar(key)

    def ChangeChord(self, chord):
        self._changeVar(chord, True)

    def Relink(self):
        self.Anchor.ChangeTargetFilePath(self.Links[0].FilePath)
        lastIndex = len(self.Links) - 1
        for idx, link in enumerate(self.Links):
            if (idx == lastIndex):
                target_idx = 0
            else:
                target_idx = idx + 1
            link.ChangeTargetFilePath(self.Links[target_idx].FilePath)

    def Newlink(self, filePath) -> Keylink:
        filePath = os.path.abspath(filePath)
        #create load command
        loadCommand = SlashCommand(name=LOAD_FILE_COMMANDS[0], text="\"%s\"" % filePath)
        loadBind = Bind(self.Key, self.Chord, [loadCommand])
        #create new bind file
        bindFile = BindFile(binds=[loadBind], filePath=filePath)
        return Keylink(bindFile, self.Key, self.Chord)

    def GetNewFileName(self, usedNames = None) -> str:
        names = [GetFileName(link.FilePath) for link in self.Links]
        if (usedNames == None):
            usedNames = names
        else:
            usedNames = names.append(usedNames)
        seed = len(self.Links) + 1
        filePath = os.path.join(self.RootPath, self.Chord + self.Key + "%d" % seed + ".txt")
        filePath = GetUniqueFilePath(filePath, seed, False, usedNames)
        return filePath
