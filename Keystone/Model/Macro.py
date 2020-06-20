from Keystone.Model.Bind import Bind, COMMAND_SEPARATOR
from Keystone.Model.SlashCommand import SlashCommand

class Macro():


    def __init__(self, name: str = None, commands: [SlashCommand] = None):

        #Name of Macro
        self.Name = name

        #list of slash commands to concatenate
        self.Commands = commands

    def __repr__(self):
        commands = COMMAND_SEPARATOR.join([str(p) for p in self.Commands])
        if ((self.Name == None) or (self.Name == "")):
            return "/%s" % (commands)
        else:
            return "/macro %s \"%s\"" % (self.Name, commands)