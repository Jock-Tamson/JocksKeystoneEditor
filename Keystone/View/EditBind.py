import tkinter as tk
from tkinter import ttk

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import GetDefaultBindForKey
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import DEFAULT_BIND, DEFAULT_COMMAND
from Keystone.Reference.KeyNames import CHORD_KEYS, KEY_NAMES
from Keystone.Utility.KeystoneUtils import MatchKeyName, FormatKeyWithChord, GetResourcePath
from Keystone.View.EditSlashCommand import SlashCommandEditor
from Keystone.Widget.FrameListView import FrameListView
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import (BACKGROUND, FOREGROUND, TEXT_FONT, KeystoneButton, KeystoneFrame,
                             KeystoneKeyCombo, KeystoneLabel,
                             KeystonePromptFrame)
from Keystone.Widget.KeystoneTextEntry import KeystoneTextEntry


class BindEditor(KeystoneEditFrame):

    DELETE_TEXT = 'UNBIND'
    DELETE_COLOR = 'black'
    DELETE_TEXT_COLOR = 'red'
    DELETE_STYLE = tk.FLAT

    ASSIGN_TEXT = 'BIND'
    UNASSIGN_TEXT = 'Unassign Bind'
    UNASSIGN_MESSAGE= 'Include no assignment?  Use "nop" to  assign a key to do nothing.  Use /unbind <key> to restore a default in the UI'
    DEFAULT_TEXT = 'Default Bind'
    DEFAULT_COLOR = 'yellow'
    DEFAULT_TEXT_COLOR = 'black'
    CANCEL_TEXT = 'Cancel'
    ASSIGN_COLOR = 'black'
    ASSIGN_TEXT_COLOR = 'green'

    def SetKeyDescription(self, keyVar: tk.StringVar, descVar: tk.StringVar, list):
        keyName = keyVar.get()
        key = MatchKeyName(keyName, list)
        if (key != None):
            desc = key[2]
            altname = key[1]
            if ((desc=='')and(altname != '')):
                desc = altname
            descVar.set(desc)
        else:
            descVar.set('')

    def SelectKey(self, *args):
        self.SetKeyDescription(self.Key, self.KeyDescription, KEY_NAMES)

    def SelectChord(self, *args):
        self.SetKeyDescription(self.Chord, self.ChordDescription, CHORD_KEYS)

    def AssignCommand(self, *args):
        model = Bind(key=self.Key.get(), chord = self.Chord.get(), commands = [SlashCommand(repr=DEFAULT_COMMAND)])
        self.Load(model)
        self.SetDirty()

    def UnassignCommand(self, *args):
        text=args[0]
        if (text == self.UNASSIGN_TEXT):
            self.ShowCommands.set(False)
            self.SetDirty()
        elif (text == self.DEFAULT_TEXT):
            bind = GetDefaultBindForKey(self.Key.get(), self.Chord.get())
            self.Commands.Load(SlashCommandEditor, bind.Commands, SlashCommand(repr=DEFAULT_COMMAND))
            self.ShowCommands.set(True)
            self.SetDirty()
        else:#Cancel
            self.ShowCommands.set(True)

    def OnDelete(self, *args):
        self.CommandsFrame.grid_forget()
        self.Delete.grid_forget()
        buttons = [self.UNASSIGN_TEXT, self.DEFAULT_TEXT, self.CANCEL_TEXT]
        colors = [[self.DELETE_TEXT_COLOR, self.DELETE_COLOR], [self.DEFAULT_COLOR, self.DEFAULT_TEXT_COLOR], [self.ASSIGN_TEXT_COLOR, self.ASSIGN_COLOR]]
        results = [self.UNASSIGN_TEXT, self.DEFAULT_TEXT, self.CANCEL_TEXT]
        commands = [self.UnassignCommand, self.UnassignCommand, self.UnassignCommand]
        unassignPrompt = KeystonePromptFrame(self, self.UNASSIGN_MESSAGE, buttons = buttons, colors=colors, results=results, commands=commands)
        unassignPrompt.grid(row=0, column=1, sticky='nsew')

    def OnShowCommands(self, *args):
        show = self.ShowCommands.get()
        if (show):
            self.Assign.grid_forget()
            self.Delete.grid(row = 0, column=1, sticky='nsw')
            self.CommandsFrame.grid(row=0, column=2, sticky='nsew', padx="3", pady="3")
        else:
            self.Assign.grid(row = 0, column=1, sticky='nsw')
            self.CommandsFrame.grid_forget()
            self.Delete.grid_forget()

    def OnShowTextEditor(self, *args):
        show = self.ShowTextEditor.get()
        if (show):
            self.Assign.grid_forget()
            self.Delete.grid_forget()
            self.KeyFrame.grid_forget()
            self.CommandsFrame.grid_forget()
            self.UIToTextButton.grid_forget()
            self.UnlockKeysButton.grid_forget()
            self.TextFrame.grid(row=0, column=0, rowspan="2", columnspan="3", sticky='nsew')
        else:
            self.TextFrame.grid_forget()
            self.KeyFrame.grid(row=0, column=0, sticky='nsew')  
            if (self._lockKey):
                self.UIToTextButton.grid(row=1, column=1, columnspan="2", sticky="nsew", padx="3", pady="3")
                self.UnlockKeysButton.grid(row=1, column=0, sticky="sw")
            else:
                self.UIToTextButton.grid(row=1, column=0, columnspan="3", sticky="nsew", padx="3", pady="3")
            self.OnShowCommands()
    
    def UnlockKeys(self, unlock=True):
        if unlock:
            self._lockKey = False
            self.KeyBox.grid(row=1, column=1, sticky="nsew", padx="3", pady="3")
            self.ChordBox.grid(row=3, column=1, sticky="nsew", padx="3", pady="3")
            self.KeyValue.grid_forget()
            self.ChordValue.grid_forget()
            self.UnlockKeysButton.grid_forget()
        else:
            self._lockKey = True
            self.KeyBox.grid_forget()
            self.ChordBox.grid_forget()
            self.KeyValue.grid(row=1, column=1, sticky="nsew", padx="3", pady="3")
            self.ChordValue.grid(row=3, column=1, sticky="nsew", padx="3", pady="3")

    def Load(self, bind: Bind):
        self.Loading = True
        try:
            if (self._lockKey):
                self.TextEntry.SetText(bind.GetCommands())
            else:
                self.TextEntry.SetText(bind.__repr__())
            self.SynchTextToUI()
        finally:
            self.Loading=False
        self.SetClean(self)

    def SynchTextToUI(self):
        key = self.Key.get()
        chord = self.Chord.get()
        text = self.TextEntry.GetText()
        if (self._lockKey):
            text = "%s %s" % (FormatKeyWithChord(key, chord), text)
        bind = Bind(repr=text)
        if (key != bind.Key):
            self.Key.set(bind.Key)
        if (chord != bind.Chord):
            self.Chord.set(bind.Chord)
        if (bind.Commands != None):        
            self.Commands.Load(SlashCommandEditor, bind.Commands, SlashCommand(repr=DEFAULT_COMMAND))
            self.ShowCommands.set(True)
        else:
            self.ShowCommands.set(False)
        self.ShowTextEditor.set(False)

    def SynchUIToText(self):
        bind = self.GetBindFromUI()
        if (self._lockKey):
            self.TextEntry.SetText(bind.GetCommands())
        else:
            self.TextEntry.SetText(bind)
        self.ShowTextEditor.set(True)

    def GetBindFromUI(self)->Bind:
        bind = Bind()
        if (self.ShowCommands.get()):
            bind.Commands = [item.Item.Get() for item in self.Commands.Items]
        else:
            bind.Commands = None
        bind.Key = self.Key.get()
        bind.Chord = self.Chord.get()
        return bind


    def Get(self) -> Bind:
        if (self.ShowTextEditor.get()):
            self.SynchTextToUI()
        model = self.GetBindFromUI()
        return model


    def __init__(self, parent, bind: Bind, lockKey = False, dirty = False):
        KeystoneEditFrame.__init__(self, parent)

        #StringVar for Key
        self.Key = None

        #StringVar for Chord
        self.Chord = None

        #StringVar for Key Description
        self.KeyDescription = None

        #StringVar for Chord Description
        self.ChordDescription = None

        #List of commands view frame
        self.Commands = None

        #Indicates keys cannot be edited
        self._lockKey = lockKey

        #layout grid
        self.columnconfigure(0, weight=1, minsize=200)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=7)
        self.rowconfigure(0, weight=1)

        #add controls
        
        self.KeyFrame = KeystoneFrame(self)
        self.KeyFrame.columnconfigure(1, weight=1)
        self.KeyFrame.columnconfigure(2, weight=0)
        self.KeyFrame.rowconfigure(4, weight=1)

        self.CommandsFrame=KeystoneFrame(self)
        self.CommandsFrame.columnconfigure(0, weight=1)
        
        self.Commands = FrameListView(self.CommandsFrame)
        self.Commands.OnSetDirty.append(self.SetDirty)
        self.Commands.grid(row=0, column=0, sticky='new')

        self.TextFrame = KeystoneFrame(self)
        self.TextFrame.rowconfigure(0, weight=1, minsize='55')
        self.TextFrame.columnconfigure(0, weight=1, minsize='405')

        self.Delete = tk.Button(self, text=self.DELETE_TEXT, background=self.DELETE_COLOR, foreground=self.DELETE_TEXT_COLOR, font=(TEXT_FONT, 7, "bold"), relief=self.DELETE_STYLE, width=1, wraplength=1, command=self.OnDelete)
        
        self.Assign = tk.Button(self, text=self.ASSIGN_TEXT, background=self.ASSIGN_COLOR, foreground=self.ASSIGN_TEXT_COLOR, font=(TEXT_FONT, 7, "bold"), relief=self.DELETE_STYLE, width=1, wraplength=1, command=self.AssignCommand)


        self.UIToTextButton = KeystoneButton(self, text="Edit As Text", command=self.SynchUIToText)

        keyLabel = KeystoneLabel(self.KeyFrame, anchor='nw', text="Key", width=5)
        keyLabel.grid(row=1, column=0, sticky="nw", padx="3", pady="3")
        self.Key = tk.StringVar()
        self.KeyValue = KeystoneLabel(self.KeyFrame, anchor='nw', textvariable=self.Key, width=5)
        self.KeyBox = KeystoneKeyCombo(self.KeyFrame, textvariable=self.Key, values=" ".join([ c[0] for c in KEY_NAMES]))
        self.Key.trace("w", self.SelectKey)
        
        self.KeyDescription = tk.StringVar()
        keyDescription = KeystoneLabel(self.KeyFrame, anchor="nw", textvariable=self.KeyDescription, wraplength=200)
        keyDescription.grid(row=2, column=0, columnspan=2,  sticky="nsew", padx="3", pady="3")

        self.Key.set(bind.Key)
        self.Key.trace("w", self.SetDirty)

        chordLabel = KeystoneLabel(self.KeyFrame, anchor='nw', text="Chord", width=5)
        chordLabel.grid(row=3, column=0, sticky="nw", padx="3", pady="3")
        self.Chord = tk.StringVar()
        self.ChordValue = KeystoneLabel(self.KeyFrame, anchor='nw', textvariable=self.Chord, width=5)
        self.ChordBox = KeystoneKeyCombo(self.KeyFrame, textvariable=self.Chord, values=" ".join([ c[0] for c in CHORD_KEYS]))
        self.Chord.trace("w", self.SelectChord)
        
        self.ChordDescription = tk.StringVar()
        chordDescription = KeystoneLabel(self.KeyFrame, anchor="nw", textvariable=self.ChordDescription, wraplength=200)
        chordDescription.grid(row=4, column=0, columnspan=2, sticky="nsew", padx="3", pady="3")
      
        self.Chord.set(bind.Chord)
        self.Chord.trace("w", self.SetDirty)

        self.UnlockKeysButton = KeystoneButton(self, text="Change Assigned Key", command=self.UnlockKeys)
        self.UnlockKeysButton.Color(FOREGROUND, BACKGROUND)

        self.ShowCommands = tk.BooleanVar()
        self.ShowCommands.trace("w", self.OnShowCommands)

        self.TextEntry = KeystoneTextEntry(self.TextFrame, height=5)
        self.TextEntry.grid(row=0, column=0, sticky="nsew", padx="3", pady="3")     
        self.TextEntry.bind("<Key>", self.SetDirty)

        self.ShowTextEditor = tk.BooleanVar()
        self.ShowTextEditor.set(False)
        self.ShowTextEditor.trace("w", self.OnShowTextEditor)

        self.TextToUIButton = KeystoneButton(self.TextFrame, text="Editor", command=self.SynchTextToUI)
        self.TextToUIButton.grid(row=1, column=0, sticky="nsew", padx="3", pady="3")  

        self.OnShowTextEditor()
        self.UnlockKeys(not lockKey)
        
        self.Load(bind)
        self.Dirty.set(dirty)

class EditBindWindow(tk.Toplevel):

    def OnOk(self, *args):
        if (self.Editor.Dirty.get()):
            try:
                bind = self.Editor.Get()
                self.ResultCallback(result = True, bind = bind)
            finally:
                self.destroy()
        else:
            self.OnCancel()

    def OnCancel(self, *args):
        try:
            self.ResultCallback(result = False, bind = None)
        finally:
            self.destroy()


    def __init__(self, parent, resultCallback, bind: Bind = None, lockKey = False, title = None, dirty = False):

        tk.Toplevel.__init__(self, parent)
        self.attributes("-topmost", 1)

        if (title == None):
            if (bind == None):
                title = 'New Bind'
                dirty = True
            else:
                title = bind.GetKeyWithChord()

        self.Title = title
        self.ResultCallback = resultCallback

        self.title(title)
        icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            self.iconbitmap(icon)
        self.protocol("WM_DELETE_WINDOW", self.OnCancel)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        frame = KeystoneEditFrame(self)
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1, minsize='205')
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=0)

        if (bind == None):
            self.Editor = BindEditor(frame, Bind(repr=DEFAULT_BIND), lockKey = lockKey, dirty = dirty)           
        else:
            self.Editor = BindEditor(frame, bind, lockKey = lockKey, dirty = dirty)
        self.Editor.grid(column = 1, row = 0, rowspan=2, sticky='nsew')
        self.Cancel = KeystoneButton(frame, text="OK", command=self.OnOk)
        self.Cancel.configure(text="Cancel",  command=self.OnCancel)
        self.Cancel.Color('red', 'black')
        self.Cancel.grid(column=0, row=1, sticky='nsew')
        self.OK = KeystoneButton(frame, text="OK", command=self.OnOk)
        self.OK.Color('green', 'black')
        self.OK.grid(column=0, row=0, sticky='nsew')
        frame.grid(column=0, row=0, sticky='nsew')

