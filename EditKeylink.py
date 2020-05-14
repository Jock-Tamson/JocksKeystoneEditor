from tkinter import ttk
import tkinter as tk
import os
import datetime

from BindFile import ReadBindsFromFile
from BindFileCollection import BindFileCollection
from EditBindFile import EditBindFile
from Keylink import Keylink
from KeystoneEditFrame import KeystoneEditFrame
from KeystoneFormats import KeystoneEntry, KeystoneLabel, KeystoneButton
from KeystoneUtils import GetDirPathFromRoot, GetUniqueFilePath
from Keychain import Keychain

class EditKeylink(KeystoneEditFrame):

    def OnEdit(self):
        if (self.Editing):
            self.NameEdit.grid_forget()
            self.NameLabel.grid(row=0, column=1, sticky='nsew')
            self.Editing = False
        else:
            self.NameEdit.grid(row=0, column=1, sticky='nsew')
            self.NameLabel.grid_forget()
            self.Editing = True

    def __init__(self, parent, link: Keylink, keychain: Keychain):

        KeystoneEditFrame.__init__(self, parent)
        self.Keychain = keychain
        self.RootPath = os.path.dirname(keychain.RootPath)
        if (link == None):
            #new link
            filePath = self.Keychain.GetNewFileName()
            self.Link = keychain.Newlink(filePath)
        else:
            self.Link = link

        #layout grid and frames
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)

        self.FileName = tk.StringVar()
        self.NameEdit = KeystoneEntry(self, textvariable=self.FileName)
        self.NameLabel = KeystoneLabel(self, textvariable=self.FileName)
        name = GetDirPathFromRoot(self.RootPath, self.Link.FilePath)
        self.FileName.set(name)
        self.FileName.trace("w", self.OnSetDirty)
        self.NameLabel.grid(row=0, column=1, sticky='nsew')

        self.Button = KeystoneButton(self, text="...",  width=3, command=self.OnEdit)
        self.Button.grid(row=0, column=0, sticky="nsew") 

        self.Editing = False
    
if (__name__ == "__main__"):
    win = tk.Tk()
    refFilePath = "./TestReferences/Field Test/keybinds.txt"
    collection = BindFileCollection(refFilePath)
    keychain = Keychain(collection, "I")
    bindFile = ReadBindsFromFile("./TestReferences/Field Test/I1.txt")
    target = Keylink(bindFile, "I")
    editor = EditKeylink(win, target, keychain)
    editor.pack(anchor='n', fill='both', expand=True, side='left')

    tk.mainloop()