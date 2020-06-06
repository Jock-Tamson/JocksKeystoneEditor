import json
import os
import tkinter as tk
from tkinter import ttk

from Keystone.Model.BindFileCollection import DESCRIPTION
from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel, TEXT_FONT, LARGE_FONT_SIZE
from Keystone.Widget.KeystoneMoreLabel import KeystoneMoreLabel
from Keystone.Widget.ScrollingFrame import ScrollingFrame

ImportWindow = None

class SelectKeybindImportWindow(tk.Toplevel):

    def OnImportCallback(self, fileName, *args):
        if (self.ImportCallback != None):
            filePath = os.path.join(self.ResourceDir, fileName)
            self.ImportCallback(self, filePath)

    def __init__(self, parent, resourceDir = None, importCallback = None, *args, **kwargs):

        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.maxsize(900, 700)
        self.attributes("-toolwindow", 1)

        icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            self.iconbitmap(icon)

        self.title("Some Key Binds...")

        #setup grid

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.scroll = ScrollingFrame(self)
        self.scroll.grid(row=0, column=0, sticky='nsew')
        self.frame = KeystoneFrame(self.scroll.scrollwindow)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.columnconfigure(0)
        self.frame.columnconfigure(1)
        self.frame.columnconfigure(2, weight=1)
        row = 0


        self.frame.grid(row=0, column=0, sticky='nsew')

        #get list of kst files from Resources
        if (resourceDir == None):
            self.ResourceDir = os.path.abspath(GetResourcePath('.\\Resources\\'))
        else:
            self.ResourceDir = resourceDir
        self.fileList =  [ f for f in os.listdir(self.ResourceDir) if f.endswith(".kst")]
        self.buttons= []
        self.labels = []
        self.descriptions = []
        for filename in self.fileList :
            filePath = os.path.join(self.ResourceDir, filename)
            with open(filePath, "r") as json_file:
                data = json.load(json_file)
            self.buttons.append(KeystoneButton(self.frame, text="Import", command= lambda row = row: self.OnImportCallback(self.fileList[row])))
            self.buttons[-1].Color('yellow', 'black')
            self.buttons[-1].grid(row=row, column=0, sticky='nw', padx=3, pady=3)
            self.labels.append(KeystoneLabel(self.frame, text=filename))
            self.labels[-1].grid(row=row, column=1, sticky='new', padx=3, pady=3)
            self.descriptions.append(KeystoneMoreLabel(self.frame, text=data[DESCRIPTION]))
            self.descriptions[-1].grid(row=row, column=2, sticky='nsew')
            row = row + 1

        self.ImportCallback = importCallback


def _onCloseImportWindow(*args):
    global ImportWindow
    ImportWindow.destroy()
    ImportWindow = None

def ShowSelectKeybindImportWindow(parent, resourceDir = None, importCallback = None, *args, **kwargs):

    global ImportWindow
    if (ImportWindow == None):
        ImportWindow = SelectKeybindImportWindow(parent, resourceDir, importCallback, *args, **kwargs)
        ImportWindow.protocol("WM_DELETE_WINDOW", _onCloseImportWindow)