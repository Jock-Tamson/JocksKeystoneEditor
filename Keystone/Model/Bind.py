from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.KeyNames import CHORD_KEYS, KEY_NAMES
from Keystone.Utility.KeystoneUtils import FormatKeyWithChord, MatchKeyName, RemoveOuterQuotes

#object for a keybind of 1 or more commands
class Bind():

    COMMAND_SEPARATOR = "$$"
    PADDED_COMMAND_SEPARATOR = "%s " % COMMAND_SEPARATOR
    UNBOUND = "UNBOUND"

    #Parse key and command list from representative string
    def Parse(self, repr: str):

        #split on space a take firt part as key second part as commands
        repr = repr.lstrip()
        parts = repr.split(" ", 1)
        commands = RemoveOuterQuotes(parts[1])

        #split key and chord on +
        if (parts[0].__contains__("+")):
            parts = parts[0].split("+", 1)
            self.Chord = parts[0].strip()
            self.Key = parts[1].strip()
        else:
            self.Key = parts[0].strip()

        if ((commands == "") or (commands == self.UNBOUND)):
            self.Commands = None
        else:
            #split on command separator and send parts to SlashCommand init
            parts = [p.lstrip() for p in commands.split(self.COMMAND_SEPARATOR)]
            if (commands.__contains__(self.PADDED_COMMAND_SEPARATOR)):
                self.COMMAND_SEPARATOR = self.PADDED_COMMAND_SEPARATOR
            self.Commands = [SlashCommand(repr = p) for p in parts]


    #init with name of key to bind and list of SlashCommands to concatente or from a string representation
    #setting repr will override commands
    def __init__(self, key: str = "", chord: str = "", commands: [SlashCommand] = None, repr: str = ""):

        #Name of the key to bind with the slash command(s). See https://paragonwiki.com/wiki/List_of_Key_Names
        self.Key = ""

        #Name of the chord key to bind with the slash command(s), e.g. CTRL in CTRL+W
        self.Chord = ""

        #List of SlashCommands to concatenate with the bind.  
        self.Commands = None
        
        if (repr == ""):
            self.Key = key
            self.Chord = chord
            self.Commands = commands
        else:
            self.Parse(repr=repr)

        self._lastKey = None
        self._lastChord = None
        self._defaultedKey = self.GetDefaultedKeyName()
        self._defaultedChord = self.GetDefaultedChordName()

    def IsLoadFileBind(self)->bool:
        return (self.GetLoadFileCommands().__len__() > 0)

    def GetLoadFileCommands(self):
        if (self.Commands == None):
            return []
        else:
            return [p for p in self.Commands if p.IsLoadFileCommand() ]

    def GetDefaultedKeyName(self)->str:
        if (self._lastKey != self.Key):
            self._lastKey = self.Key
            match = MatchKeyName(self.Key, KEY_NAMES)
            if (match == None):
                self._defaultedKey = self.Key
            else:
                self._defaultedKey =  match[0]
        return self._defaultedKey

    def GetDefaultedChordName(self)->str:
        if (self._lastChord != self.Chord):
            self._lastChord = self.Chord
            match = MatchKeyName(self.Chord, CHORD_KEYS)
            if (match == None):
                self._lastChord = self.Chord
            else:
                self._lastChord =  match[0]
        return self._lastChord


    def GetKeyWithChord(self, defaultNames = False):
        if (defaultNames):
            key = self.GetDefaultedKeyName()
            chord = self.GetDefaultedChordName()
        else:
            key = self.Key
            chord = self.Chord
        return FormatKeyWithChord(key, chord)
        
    def GetCommands(self):
        if (self.Commands == None):
            return self.UNBOUND
        else:
            commands = self.COMMAND_SEPARATOR.join([str(p) for p in self.Commands])
            return "\"%s\"" % (commands)

    def __repr__(self):
        key = self.GetKeyWithChord()
        commands = self.GetCommands()
        return "%s %s" % (key, commands)

    def Clone(self):
        return Bind(repr=self.__repr__())
