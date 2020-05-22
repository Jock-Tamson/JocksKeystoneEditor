import os
import tkinter as tk
from tkinter import ttk

from Keystone.Model.BindFileCollection import BindFileCollection
from Keystone.Model.Keychain import Keychain
from Keystone.Reference.KeyNames import CHORD_KEYS, KEY_NAMES
from Keystone.View.EditKeylink import EditKeylink
from Keystone.Widget.FrameListView import FrameListView
from Keystone.Widget.KeystoneFormats import (KeystoneFrame, KeystoneKeyCombo,
                                             KeystoneLabel)
from Keystone.Widget.ScrollingFrame import ScrollingFrame
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame


class LinkListItem(EditKeylink):

    def __init__(self, parent, args):
        EditKeylink.__init__(self, parent, args["link"], args["keychain"])

class EditKeychain(KeystoneEditFrame):

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

    def __init__(self, parent, keychain: Keychain):
        KeystoneEditFrame.__init__(self, parent)   

        self.Keychain = keychain


        #layout grid and frames
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        keyFrame = KeystoneFrame(self)
        keyFrame.grid(row=0, column=0, sticky='nsew')      
        
        keyLabel = KeystoneLabel(keyFrame, anchor='nw', text="Key", width=5)
        keyLabel.grid(row=0, column=0, sticky="nw", padx="3", pady="3")
        self.Key = tk.StringVar()
        keyBox = KeystoneKeyCombo(keyFrame, textvariable=self.Key, values=" ".join([ c[0] for c in KEY_NAMES]))
        keyBox.grid(row=0, column=1, sticky="nw", padx="3", pady="3")
        self.Key.trace("w", self.SelectKey)
        self.Key.trace("w", self.SetDirty)
        
        self.KeyDescription = tk.StringVar()
        keyDescription = KeystoneLabel(keyFrame, anchor="nw", textvariable=self.KeyDescription, wraplength=200)
        keyDescription.grid(row=1, column=0, columnspan=2,  sticky="nsew", padx="3", pady="3")


        chordLabel = KeystoneLabel(keyFrame, anchor='nw', text="Chord", width=5)
        chordLabel.grid(row=0, column=2, sticky="nw", padx="3", pady="3")
        self.Chord = tk.StringVar()
        chordBox = KeystoneKeyCombo(keyFrame, textvariable=self.Chord, values=" ".join([ c[0] for c in CHORD_KEYS]))
        chordBox.grid(row=0, column=3, sticky="n", padx="3", pady="3")
        self.Chord.trace("w", self.SelectChord)
        self.Chord.trace("w", self.SetDirty)
        
        self.ChordDescription = tk.StringVar()
        chordDescription = KeystoneLabel(keyFrame, anchor="nw", textvariable=self.ChordDescription, wraplength=200)
        chordDescription.grid(row=1, column=2, columnspan=2, sticky="nsew", padx="3", pady="3")

        scrollingFrame = ScrollingFrame(self)
        scrollingFrame.grid(row=2, column=0, columnspan=5, sticky='nsew')

        self.view = FrameListView(scrollingFrame.scrollwindow)
        self.view.pack(fill=tk.BOTH, expand=1)
        self.Load(keychain)
        self.view.OnSetDirty.append(self.SetDirty)

    def Load(self, keychain: Keychain):
        self.Key.set(keychain.Key)
        self.Chord.set(keychain.Chord)
        self.view.Load(LinkListItem, [{"link" : link, "keychain": keychain} for link in keychain.Links], {"link" : None, "keychain": keychain})
    
if (__name__ == "__main__"):
    win = tk.Tk()
    refFilePath = "./TestReferences/Field Test/keybinds.txt"
    collection = BindFileCollection(refFilePath)
    target = Keychain(collection, "I")
    editor = EditKeychain(win, target)
    editor.pack(anchor='n', fill='both', expand=True, side='left')

    tk.mainloop()
