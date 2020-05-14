from tkinter import ttk
import tkinter as tk

from EditSlashCommand import SlashCommandEditor
from FrameListView import FrameListView
from KeyNames import KEY_NAMES
from KeyNames import CHORD_KEYS
from Bind import Bind
from SlashCommand import SlashCommand
from KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneKeyCombo, KeystoneLabel, KeystonePromptFrame, TEXT_FONT
from KeystoneEditFrame import KeystoneEditFrame
from DefaultKeyBindings import DEFAULT_BIND, DEFAULT_COMMAND
from BindFile import GetDefaultBindForKey
from KeystoneTextEntry import KeystoneTextEntry
from KeystoneUtils import GetResourcePath

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
        key = [c for c in list if ((c[0] == keyName) or ((c[1] != '') and (c[1] == keyName)))]
        if (len(key) > 0):
            desc = key[0][2]
            altname = key[0][1]
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
        self.Model.Commands = [SlashCommand(repr=DEFAULT_COMMAND)]
        self.Load(self.Model)
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
            self.TextFrame.grid(row=0, column=0, rowspan="2", columnspan="3", sticky='nsew')
        else:
            self.TextFrame.grid_forget()
            self.KeyFrame.grid(row=0, column=0, sticky='nsew')
            self.UIToTextButton.grid(row=1, column=0, columnspan="3", sticky="nsew", padx="3", pady="3")  
            self.OnShowCommands()

    def Load(self, bind: Bind):
        self.Loading = True
        try:
            self.Model = bind
            if (self._lockKey):
                self.TextEntry.SetText(bind.GetCommands())
            else:
                self.TextEntry.SetText(bind)
            self.SynchTextToUI()
        finally:
            self.Loading=False
        self.SetClean(self)

    def SynchTextToUI(self):
        text = self.TextEntry.GetText()
        if (self._lockKey):
            text = "%s %s" % (self.Model.GetKeyWithChord(), text)
        bind = Bind(repr=text)
        self.Key.set(bind.Key)
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
        self.Model = self.GetBindFromUI()
        return self.Model


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

        #Bind data model
        self.Model = None

        #Indicates keys cannot be edited
        self._lockKey = lockKey

        #layout grid
        self.columnconfigure(0, weight=0, minsize='205')
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        #add controls
        
        self.KeyFrame = KeystoneFrame(self)
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
        if (lockKey):
            keyValue = KeystoneLabel(self.KeyFrame, anchor='nw', textvariable=self.Key, width=5)
            keyValue.grid(row=1, column=1, sticky="nw", padx="3", pady="3")
        else:
            keyBox = KeystoneKeyCombo(self.KeyFrame, textvariable=self.Key, values=" ".join([ c[0] for c in KEY_NAMES]))
            keyBox.grid(row=1, column=1, sticky="nw", padx="3", pady="3")
        self.Key.trace("w", self.SelectKey)
        self.Key.trace("w", self.SetDirty)
        
        self.KeyDescription = tk.StringVar()
        keyDescription = KeystoneLabel(self.KeyFrame, anchor="nw", textvariable=self.KeyDescription, wraplength=200)
        keyDescription.grid(row=2, column=0, columnspan=2,  sticky="nsew", padx="3", pady="3")


        chordLabel = KeystoneLabel(self.KeyFrame, anchor='nw', text="Chord", width=5)
        chordLabel.grid(row=3, column=0, sticky="nw", padx="3", pady="3")
        self.Chord = tk.StringVar()
        if (lockKey):
            chordValue = KeystoneLabel(self.KeyFrame, anchor='nw', textvariable=self.Chord, width=5)
            chordValue.grid(row=3, column=1, sticky="nw", padx="3", pady="3")
        else:
            chordBox = KeystoneKeyCombo(self.KeyFrame, textvariable=self.Chord, values=" ".join([ c[0] for c in CHORD_KEYS]))
            chordBox.grid(row=3, column=1, sticky="n", padx="3", pady="3")
        self.Chord.trace("w", self.SelectChord)
        self.Chord.trace("w", self.SetDirty)
        
        self.ChordDescription = tk.StringVar()
        chordDescription = KeystoneLabel(self.KeyFrame, anchor="nw", textvariable=self.ChordDescription, wraplength=200)
        chordDescription.grid(row=4, column=0, columnspan=2, sticky="nsew", padx="3", pady="3")

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
        
        self.Load(bind)
        self.Dirty.set(dirty)

class EditBindWindow(tk.Toplevel):

    def OnOk(self, *args):
        if (self.Editor.Dirty.get()):
            self.Bind = self.Editor.Get()
            self.ResultCallback(result = True, bind = self.Bind)
            self.destroy()
        else:
            self.OnCancel()

    def OnCancel(self, *args):
        self.ResultCallback(result = False, bind = self.Bind)
        self.destroy()


    def __init__(self, parent, resultCallback, bind: Bind = None, lockKey = False, title = None, dirty = False):

        tk.Toplevel.__init__(self, parent)

        if (title == None):
            if (bind == None):
                title = 'New Bind'
                dirty = True
            else:
                title = bind.GetKeyWithChord()

        if (bind == None):
            bind = Bind(repr=DEFAULT_BIND)

        self.Bind = bind
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
        frame.rowconfigure(0, weight=0)
        frame.rowconfigure(1, weight=1)
        self.Editor = BindEditor(frame, bind, lockKey = lockKey, dirty = dirty)
        self.Editor.grid(column = 1, row = 1, sticky='nsew')
        self.Cancel = KeystoneButton(frame, text="OK", command=self.OnOk)
        self.Cancel.configure(text="Cancel",  command=self.OnCancel)
        self.Cancel.Color('red', 'black')
        self.Cancel.grid(column=0, row=0, sticky='nsew')
        self.OK = KeystoneButton(frame, text="OK", command=self.OnOk)
        self.OK.Color('green', 'black')
        self.OK.grid(column=0, row=1, sticky='nsew')
        frame.grid(column=0, row=0, sticky='nsew')


if (__name__ == "__main__"):
    win = tk.Tk()
    target = Bind(repr="SHIFT+Y em Does this work?$$+say <color #000000><bgcolor #FFFFFF75><border #FF0000><scale 1.0><duration 10>Yay!")
    def callback(result, bind):
        print(result)
        print(bind)
    editor = EditBindWindow(win, callback, target, True)

    tk.mainloop()