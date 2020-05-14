from SlashCommand import SlashCommand
from KeystoneUtils import RemoveOuterQuotes

#object for a keybind of 1 or more commands
class Bind():

    COMMAND_SEPARATOR = "$$"
    PADDED_COMMAND_SEPARATOR = "%s " % COMMAND_SEPARATOR

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

    def IsLoadFileBind(self)->bool:
        return (self.GetLoadFileCommands().__len__() > 0)

    def GetLoadFileCommands(self):
        if (self.Commands == None):
            return []
        else:
            return [p for p in self.Commands if p.IsLoadFileCommand() ]

    def GetKeyWithChord(self):
        if (self.Chord == ""):
            key = self.Key
        else:
            key = "%s+%s" % (self.Chord, self.Key)
        return key

    def GetCommands(self):
        if (self.Commands == None):
            return "UNBOUND"
        else:
            commands = self.COMMAND_SEPARATOR.join([str(p) for p in self.Commands])
            return "\"%s\"" % (commands)

    def __repr__(self):
        key = self.GetKeyWithChord()
        commands = self.GetCommands()
        return "%s %s" % (key, commands)

