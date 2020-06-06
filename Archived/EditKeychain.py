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
        
class TestKeychain(unittest.TestCase):

    def test_init(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        actual = len(target.Links)
        expected = 2
        self.assertEqual(actual, expected, "Unexpected Links length")
        actual = target.Links[1].TargetFilePath
        expected = target.Links[0].FilePath
        self.assertEqual(actual, expected, "Unexpected file paths")
        actual = target.Anchor.FilePath
        expected = os.path.abspath(refFilePath)
        self.assertEqual(actual, expected, "Unexpected anchor file path")

    def test_ChangeKey(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        expected = "J"
        target.ChangeKey(expected)
        actual = target.Key
        self.assertEqual(actual, expected, "Unexpected changed Key")
        actual = target.Anchor.Key
        self.assertEqual(actual, expected, "Unexpected changed Key in anchor")
        for idx, link in enumerate(target.Links):
            actual = link.Key
            self.assertEqual(actual, expected, "Unexpected changed Key in Link " + str(idx))
        self.assertTrue("J" in collection.KeyChains)
        self.assertFalse("I" in collection.KeyChains)

    def test_ChangeChord(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        expected = "SHIFT"
        target.ChangeChord(expected)
        actual = target.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord")
        actual = target.Anchor.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord in anchor")
        for idx, link in enumerate(target.Links):
            actual = link.Chord
            self.assertEqual(actual, expected, "Unexpected changed Chord in Link " + str(idx))
        self.assertTrue("SHIFT+I" in collection.KeyChains)
        self.assertFalse("I" in collection.KeyChains)

    def test_NewLink(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        chain = Keychain(collection, "I")
        newFilePath = "./TestReferences/Field Test/I3.txt"
        target = chain.Newlink(newFilePath)
        actual = target.FilePath
        expectedPath = os.path.abspath(newFilePath)
        self.assertEqual(actual, expectedPath, "Unexpected FilePath")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        actual = target.Bind.__repr__()
        expected = "I \"bind_load_file \"%s\"\"" % expectedPath
        self.assertEqual(actual, expected, "Unexptected Bind")
        actual = target.Command.__repr__()
        expected = "bind_load_file \"%s\"" % expectedPath
        self.assertEqual(actual, expected, "Unexpected Command")
        actual = target.TargetFilePath
        self.assertEqual(actual, expectedPath, "Unexpected TargetFilePath")

    def test_Relink(self):

        def _testLinks():
            for idx, testCase in enumerate(expected):
                expectedFilePath = os.path.abspath(testCase[0])
                expectedTargetFilePath = os.path.abspath(testCase[1])
                actualFilePath = target.Links[idx].FilePath
                actualTargetFilePath = target.Links[idx].TargetFilePath
                self.assertEqual(actualFilePath, expectedFilePath, "Unexpected FilePath in link " + str(idx))
                self.assertEqual(actualTargetFilePath, expectedTargetFilePath, "Unexpected TargetFilePath in link " + str(idx))

        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        newFilePath = "./TestReferences/Field Test/I3.txt"
        newLink = target.Newlink(newFilePath)
        target.Links.insert(1, newLink)
        target.Relink()
        expectedTargetFilePath = os.path.abspath("./TestReferences/Field Test/I1.txt")
        actualTargetFilePath = target.Anchor.TargetFilePath
        self.assertEqual(actualTargetFilePath, expectedTargetFilePath)
        expected = (
            ("./TestReferences/Field Test/I1.txt", "./TestReferences/Field Test/I3.txt"),
            ("./TestReferences/Field Test/I3.txt", "./TestReferences/Field Test/I2.txt"),
            ("./TestReferences/Field Test/I2.txt", "./TestReferences/Field Test/I1.txt")
        )
        _testLinks()
        
        newFilePath = "./TestReferences/Field Test/I4.txt"
        newLink = target.Newlink(newFilePath)
        target.Links.insert(0, newLink)
        target.Relink()
        expectedTargetFilePath = os.path.abspath("./TestReferences/Field Test/I4.txt")
        actualTargetFilePath = target.Anchor.TargetFilePath
        self.assertEqual(actualTargetFilePath, expectedTargetFilePath)
        expected = (
            ("./TestReferences/Field Test/I4.txt", "./TestReferences/Field Test/I1.txt"),
            ("./TestReferences/Field Test/I1.txt", "./TestReferences/Field Test/I3.txt"),
            ("./TestReferences/Field Test/I3.txt", "./TestReferences/Field Test/I2.txt"),
            ("./TestReferences/Field Test/I2.txt", "./TestReferences/Field Test/I4.txt")
        )
        _testLinks()

    def test_GetNewFileName(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.GetNewFileName()
        expected = os.path.abspath("./TestReferences/Field Test/I3.txt")
        self.assertEqual(actual, expected)
