from Keystone.Model.Bind import Bind, COMMAND_SEPARATOR
from Keystone.Model.SlashCommand import SlashCommand

class Macro():


    def __init__(self, name: str = "", commands: [SlashCommand] = None):

        #Name of Macro
        self.Name = name

        #list of slash commands to concatenate
        self.Commands = commands

    def __repr__(self):
        commands = COMMAND_SEPARATOR.join([str(p) for p in self.Commands])
        return "/macro %s \"%s\"" % (self.Name, commands)