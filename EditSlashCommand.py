from tkinter import filedialog, ttk
import tkinter as tk
from tkinter.colorchooser import askcolor

import os

from ColorPicker import ColorPicker
from DefaultKeyBindings import DEFAULT_BIND
from KeystoneUtils import AverageRGBValues, GetFileName, RemoveOuterQuotes, TriggerOpenLinkedFileCallback
from CommandReference import LIST_OF_SLASH_COMMANDS
from SlashCommand import SlashCommand, IsLoadFileCommand
from KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel, KeystoneCombo, KeystoneRadio, KeystoneEntry, TEXT_FONT, FONT_SIZE
from KeystoneEditFrame import KeystoneEditFrame
from KeystoneTextEntry import KeystoneTextEntry


class SlashCommandEditor(KeystoneEditFrame):

    COMMAND_BACKGROUND = 'lightskyblue'

    def ResetFormat(self):
        self.ColorEntry.ColorEntryText.set("")
        self.BackgroundEntry.ColorEntryText.set("")
        self.BorderEntry.ColorEntryText.set("")
        self.TransparencyEntryText.set("")
        self.ScaleEntryText.set("")
        self.RepeatText.set("")
        self.DurationText.set("")


    def SelectCommand(self, *args):
        command = [c for c in LIST_OF_SLASH_COMMANDS if (c[0] == self.CommandName.get())]
        if (len(command) > 0):
            if (self.TextPrompt != command[0][1]):
                #reset text if prompt is different
                self.TextPrompt = command[0][1]
                self.ResetFormat()
                self.TextEntry.SetText(self.TextPrompt)           
            description = command[0][2]
            self.DescriptionText.set(description)   
            self.IsLoadFileCommand.set(IsLoadFileCommand(command[0][0]))    
        else:
            self.DescriptionText.set("")

    def FormatText(self, *args):
        foreground = self.ColorEntry.ColorEntryText.get()
        if (foreground == ""):
            foreground="Black"
        background = self.BackgroundEntry.ColorEntryText.get()
        transparency = self.TransparencyEntryText.get()
        if (background == ""):
            background="White"
        elif(not (transparency == "")):
            background = AverageRGBValues(background, self.COMMAND_BACKGROUND, int(transparency))
        border = self.BorderEntry.ColorEntryText.get()
        if (border == ""):
            border="White"
        scale = self.ScaleEntryText.get()
        if (scale == ""):
            scale = 1.0
        else:
            try:
                scale = float(scale)
                if (scale > 4.0):
                    scale = 4.0
                    self.ScaleEntryText.set("4.0")
                elif(scale < 0):
                    scale = 0
                    self.ScaleEntryText.set("0")
            except:
                scale = 1.0
                self.ScaleEntryText.set("")
        duration = self.DurationText.get()
        if (duration != ""):
            try:
                duration = int(duration)
                if(duration < 0):
                    duration = 0
                    self.DurationText.set("0")
            except:
                self.DurationText.set("")
        self.TextEntry.configure(background=background, foreground=foreground, highlightbackground=border, highlightthickness=2, font=(TEXT_FONT, int(FONT_SIZE * scale)))
        self.SetDirty()

    def Load(self, command: SlashCommand):
        self.Loading = True
        try:
            self.BrowseButton.grid_forget()
            self.Model = command
            self.CommandName.set(command.Name)
            self.TextEntry.SetText(command.Text)
            if (command.Repeat):
                self.RepeatText.set(command.REPEAT_STR)
            elif (command.Toggle):
                self.RepeatText.set(command.TOGGLE_STR)
            self.ColorEntry.ColorEntryText.set(command.TextColor)
            self.BackgroundEntry.ColorEntryText.set(command.TextBackgroundColor)
            self.BorderEntry.ColorEntryText.set(command.TextBorderColor)
            self.TransparencyEntryText.set(command.TextBackgroundTransparency)
            self.ScaleEntryText.set(command.TextScale)
            self.DurationText.set(command.TextDuration)
        finally:
            self.Loading = False
        self.SetClean(self)

    def Get(self) -> SlashCommand:
        self.Model.Name = self.CommandName.get()
        self.Model.Text = self.TextEntry.GetText()
        repeat = self.RepeatText.get()
        if (repeat == self.Model.REPEAT_STR):
            self.Model.Repeat = True
            self.Model.Toggle = False
        elif (repeat == self.Model.TOGGLE_STR):
            self.Model.Repeat = False
            self.Model.Toggle = True
        else:
            self.Model.Repeat = False
            self.Model.Toggle = False
        self.Model.TextColor = self.ColorEntry.ColorEntryText.get()
        self.Model.TextBackgroundColor = self.BackgroundEntry.ColorEntryText.get()
        self.Model.TextBorderColor = self.BorderEntry.ColorEntryText.get()
        self.Model.TextBackgroundTransparency = self.TransparencyEntryText.get()
        self.Model.TextScale = self.ScaleEntryText.get()
        self.Model.TextDuration = self.DurationText.get()
        return self.Model

    _lockShowFormat = False

    def LockShowFormat(self, *args):
        self._lockShowFormat = True

    def UnlockShowFormat(self, *args):
        self._lockShowFormat = False

    def BindWidgetToShowFormat(self, widget):
        widget.bind('<FocusIn>', self.ShowFormat)
        widget.bind('<FocusOut>', self.HideFormat)
        widget.bind('<Enter>', self.UnlockShowFormat)

    def ShowFormat(self, *args):
        self.rowconfigure(2, weight=1)
        self.FormatFrame.grid(row=1, column=0, sticky='nsew')
        self.DescriptionFrame.grid(row=2, column=0, sticky='nsew')

    def HideFormat(self, *args):
        if (not self._lockShowFormat):
            self.rowconfigure(2, weight=0)
            self.FormatFrame.grid_forget()
            self.DescriptionFrame.grid_forget()

    def OnSetIsLoadFileCommand(self, *args):
        value = self.IsLoadFileCommand.get()
        if (value):
            self.BrowseButton.grid(row=0, column=2, sticky='nsw')
            self.NewButton.grid(row=0, column=3, sticky='nse')
        else:
            self.BrowseButton.grid_forget()
            self.NewButton.grid_forget()

    def OnBrowseButton(self):
        options = {}
        filePath =  RemoveOuterQuotes( self.TextEntry.GetText() )
        options['initialfile'] = GetFileName(filePath)
        options['initialdir'] = os.path.dirname(filePath)
        options['title'] = "Select Keybind File"
        options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
        options['defaultextension'] = "txt"
        options['multiple'] = False
        filePath = filedialog.askopenfilename(**options)
        if (filePath != ''):
            self.TextEntry.SetText("\"%s\"" % (filePath))
            TriggerOpenLinkedFileCallback(filePath)

    def OnNewButton(self):
        options = {}
        filePath =  RemoveOuterQuotes( self.TextEntry.GetText() )
        options['initialfile'] = GetFileName(filePath)
        options['initialdir'] = os.path.dirname(filePath)
        options['title'] = "Create Keybind File"
        options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
        options['defaultextension'] = "txt"
        filePath = filedialog.asksaveasfilename(**options)
        if (filePath != ''):
            self.TextEntry.SetText("\"%s\"" % (filePath))        
            file = open(filePath, "w+")
            try:
                file.write(DEFAULT_BIND)
            finally:
                file.close()
            TriggerOpenLinkedFileCallback(filePath)

    def __init__(self, parent, command: SlashCommand):
        KeystoneEditFrame.__init__(self, parent)

        #Frame for formatting controls
        self.FormatFrame = None

        #Frame for decscription
        self.DescriptionFrame = None

        #StringVar for command name
        self.CommandName = None

        #text entry object
        self.TextEntry = None

        #color entry objects
        self.ColorEntry = None
        self.BackgroundEntry = None
        self.BorderEntry = None

        #StringVar for transparency
        self.TransparencyEntryText = None

        #StringVar for scale
        self.ScaleEntryText = None

        #StringVar for repeat selection
        self.RepeatText = None

        #StringVar for duration
        self.DurationText = None

        #StringVar for power description text
        self.DescriptionText = None

        #The text prompt for the last selected command, e.g. "power" for powexec_name
        self.TextPrompt = None

        #SlashCommand class data model
        self.Model = None

        #layout grid and frames
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        commandFrame = KeystoneFrame(self)
        commandFrame.grid(row=0, column=0, sticky='nsew')
        commandFrame.columnconfigure(0, weight=0)
        commandFrame.columnconfigure(1, weight=1)
        commandFrame.columnconfigure(2, weight=0)
        commandFrame.columnconfigure(3, weight=0)
        self.FormatFrame = formatFrame = KeystoneFrame(self)
        self.DescriptionFrame = descriptionFrame = KeystoneFrame(self)

        #add controls
        self.CommandName = tk.StringVar()
        commandBox = KeystoneCombo(commandFrame, textvariable=self.CommandName, values=" ".join([ c[0] for c in LIST_OF_SLASH_COMMANDS]), postcommand=self.LockShowFormat)
        commandBox.grid(row=0, column=0, sticky="w", padx="3", pady="3")
        self.CommandName.trace("w", self.SelectCommand)
        self.CommandName.trace("w", self.SetDirty)

        self.TextEntry = KeystoneTextEntry(commandFrame)
        self.TextEntry.grid(row=0, column=1, sticky="nsew", padx="3", pady="3")     
        self.TextEntry.bind("<Key>", self.SetDirty)

        self.BrowseButton = KeystoneButton(commandFrame, text=" ... ", command=self.OnBrowseButton)
        self.NewButton = KeystoneButton(commandFrame, text="New", command=self.OnNewButton)
        self.IsLoadFileCommand = tk.BooleanVar()
        self.IsLoadFileCommand.set(False)
        self.IsLoadFileCommand.trace("w", self.OnSetIsLoadFileCommand)

        label = KeystoneLabel(formatFrame, text="Repeat Mode", anchor='n')
        label.grid(row=0, column=0, pady="3")
        repeatModes = [("Once", ""), ("Repeat [%s]" % command.REPEAT_STR, command.REPEAT_STR), ("Toggle [%s]" %command.TOGGLE_STR , command.TOGGLE_STR)]
        self.RepeatText = tk.StringVar()
        for idx, (text, mode) in enumerate(repeatModes):
            b = KeystoneRadio(formatFrame, text=text, value=mode, variable=self.RepeatText)
            b.grid(row=1+idx, column=0, sticky='w')
        self.RepeatText.set("")
        self.RepeatText.trace("w", self.SetDirty)

        editLabels = ["Text Color", "Background Color", "Transparency", "Border Color", "Scale", "Duration"]
        for idx, text in enumerate(editLabels):
            label = KeystoneLabel(formatFrame, text=text, anchor='n', width=30)
            if (idx < 3):
                row = 1
            else:
                row = 3
            label.grid(row=row, column=1+(idx % 3))

        self.ColorEntry = ColorPicker(formatFrame)
        self.ColorEntry.Combo.configure(postcommand=self.LockShowFormat)
        self.ColorEntry.grid(row=0, column=1, padx="3", pady="3")
        self.ColorEntry.ColorEntryText.trace("w", self.FormatText)

        self.BackgroundEntry = ColorPicker(formatFrame)
        self.BackgroundEntry.Combo.configure(postcommand=self.LockShowFormat)
        self.BackgroundEntry.grid(row=0, column=2, padx="3", pady="3")
        self.BackgroundEntry.ColorEntryText.trace("w", self.FormatText)

        self.TransparencyEntryText = tk.StringVar()
        self.TransparencyEntry = KeystoneCombo(formatFrame, textvariable=self.TransparencyEntryText, values=" ".join([str(p) for p in range(0,101)]), width=3, postcommand=self.LockShowFormat)
        self.TransparencyEntry.grid(row=0, column=3)
        self.TransparencyEntryText.trace("w", self.FormatText)

        self.BorderEntry = ColorPicker(formatFrame)
        self.BorderEntry.Combo.configure(postcommand=self.LockShowFormat)
        self.BorderEntry.grid(row=2, column=1, padx="3", pady="3")
        self.BorderEntry.ColorEntryText.trace("w", self.FormatText)

        self.ScaleEntryText = tk.StringVar()
        scaleEntry = KeystoneEntry(formatFrame, textvariable=self.ScaleEntryText, width=5)
        scaleEntry.grid(row=2, column=2)
        self.ScaleEntryText.trace("w", self.FormatText)

        self.DurationText = tk.StringVar()
        durationEntry = KeystoneEntry(formatFrame, textvariable=self.DurationText, width=5)
        durationEntry.grid(row=2, column=3)
        self.DurationText.trace("w", self.FormatText)

        self.DescriptionText = tk.StringVar()
        description = KeystoneLabel(descriptionFrame, anchor="nw", textvariable=self.DescriptionText, wraplength=800)
        description.grid(sticky="nsew", padx="3", pady="3")

        #load model
        self.Load(command)

        #bind to hide format and desc
        self.BindWidgetToShowFormat(self)

        
if (__name__ == "__main__"):
    win = tk.Tk()
    target = SlashCommand(repr="+say <color #000000><bgcolor #FFFFFF75><border #FF0000><scale 1.0><duration 10>Yay!")
    editor = SlashCommandEditor(win, target)
    s = ttk.Style()
    s.configure('My.TFrame', background='red')
    editor.configure(style="My.TFrame")
    editor.pack(anchor='n', fill='both', expand=True, side='left')

    tk.mainloop()