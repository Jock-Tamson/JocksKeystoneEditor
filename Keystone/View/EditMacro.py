import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Keystone.Model.Macro import Macro
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import DEFAULT_COMMAND
from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.View.EditSlashCommand import SlashCommandEditor
from Keystone.Widget.FrameListView import FrameListView
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneCheckbutton, KeystoneFrame, KeystoneLabel, KeystoneEntry

class EditMacro(KeystoneFrame):

    def Load(self, macro: Macro):
        self.Name.set(macro.Name)
        self.Commands.Load(SlashCommandEditor, macro.Commands, SlashCommand(repr=DEFAULT_COMMAND))

    def Get(self) -> Macro:
        commands = [item.Item.Get() for item in self.Commands.Items]
        if (self.CommandOnly.get()):
            name = None
        else:
            name = self.Name.get()
        return Macro(name, commands)
    
    def __init__(self, parent, macro: Macro):
        KeystoneFrame.__init__(self, parent)

        #StringVar for Name
        self.Name = ""

        #List of commands view frame
        self.Commands = None

        #layout grid
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=7)
        self.rowconfigure(0, weight=1)

        #add controls
        
        self.NameFrame = KeystoneFrame(self)
        self.NameFrame.columnconfigure(1, weight=1)
        self.NameFrame.columnconfigure(2, weight=0)
        self.NameFrame.rowconfigure(4, weight=1)
        self.NameFrame.grid(row=0, column=0, sticky='nsew') 

        self.CommandsFrame=KeystoneFrame(self)
        self.CommandsFrame.columnconfigure(0, weight=1)
        self.CommandsFrame.grid(row=0, column=2, sticky='nsew', padx="3", pady="3")
        
        self.Commands = FrameListView(self.CommandsFrame)
        self.Commands.grid(row=0, column=0, sticky='new')

        nameLabel = KeystoneLabel(self.NameFrame, anchor='nw', text="Name", width=5)
        nameLabel.grid(row=1, column=0, sticky="nw", padx="3", pady="3")
        self.Name = tk.StringVar()
        self.NameBox = KeystoneEntry(self.NameFrame, textvariable=self.Name)
        self.NameBox.grid(row=1, column=1, sticky="nsew", padx="3", pady="3")

        self.CommandOnly = tk.BooleanVar(value=False)
        self.CommandOnlyCheck = KeystoneCheckbutton(self.NameFrame, variable=self.CommandOnly)
        self.CommandOnlyCheck.grid(row=2, column=0, sticky="ne", padx="3", pady="3")
        commandOnlyLabel = KeystoneLabel(self.NameFrame, anchor='nw', text='Copy command only')
        commandOnlyLabel.grid(row=2, column=1, sticky="nw", padx="3", pady="3")
        
        self.Load(macro)

class EditMacroWindow(tk.Toplevel):

    def OnCopy(self, *args):
        macro = self.Editor.Get()
        self.clipboard_clear()
        command = macro.__repr__()
        self.clipboard_append(macro.__repr__())

        messagebox.showinfo("Copy to City of Heroes",  
            "The command:\n\n" +
            "%s\n\n" % str(command) +
            "has been copied to  the clipboard.\n\n" +
            "Paste and execute this command in the game to create the macro")

    def OnClose(self, *args):
        self.destroy()


    def __init__(self, parent, macro: Macro = None):

        tk.Toplevel.__init__(self, parent)
        self.attributes("-topmost", 1)

        self.title("Create a Macro")
        icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            self.iconbitmap(icon)
        self.protocol("WM_DELETE_WINDOW", self.OnClose)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = KeystoneFrame(self)
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1, minsize='205')
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)

        if (macro == None):
            macro = Macro("Name", [SlashCommand(repr="powexec_name power")])
        self.Editor = EditMacro(frame, macro)
        self.Editor.grid(column = 1, row = 0, rowspan=2, sticky='nsew')
        self.Close = KeystoneButton(frame)
        self.Close.configure(text="Close",  command=self.OnClose)
        self.Close.Color('red', 'black')
        self.Close.grid(column=0, row=1, sticky='nsew')
        self.Copy = KeystoneButton(frame, text="Copy to Clipboard", command=self.OnCopy)
        self.Copy.Color('green', 'black')
        self.Copy.grid(column=0, row=0, sticky='nsew')
        frame.grid(column=0, row=0, sticky='nsew')