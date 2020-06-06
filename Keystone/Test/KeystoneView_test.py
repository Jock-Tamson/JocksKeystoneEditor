import os
import inspect
import tkinter as tk
import unittest
from tkinter import ttk

from PIL import Image, ImageTk

from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import ReadBindsFromFile
from Keystone.Model.BindFileCollection import BindFileCollection
from Keystone.Model.Keychain import Keychain
from Keystone.Reference.ImportExportWalkthrough import IMPORT_EXPORT_WALKTHROUGH
from Keystone.Reference.CollectionsAndKeyChainsWalkthrough import COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH, COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH_END_PAGES
from Keystone.View.EditSlashCommand import SlashCommandEditor
from Keystone.View.EditBind import EditBindWindow
from Keystone.View.EditBindFile import EditBindFile
from Keystone.View.BindFileCollectionView import BindFileCollectionView
from Keystone.View.EditBindFileCollection import EditBindFileCollection
from Keystone.Windows.KeystoneWalkthroughPages import ShowWalkthrough
from Keystone.Windows.BindFileEditorWindow import BindFileEditorWindow
from Keystone.Windows.KeystoneAbout import ShowHelpAbout
from Keystone.Windows.SelectKeybindImportWindow import ShowSelectKeybindImportWindow
from Keystone.Utility.KeystoneUtils import GetResourcePath

SET_TO_SHOW_WINDOWS = False

class TestKeystoneWalthroughPages(unittest.TestCase):

    def test_ShowIntroWalkthrough(self):
        if SET_TO_SHOW_WINDOWS:
            win = tk.Tk()
            ShowWalkthrough(win)
            tk.mainloop()

    def test_ShowImportWalkthrough(self):
        if SET_TO_SHOW_WINDOWS:
            win = tk.Tk()
            ShowWalkthrough(win, walkthrough=IMPORT_EXPORT_WALKTHROUGH)
            tk.mainloop()

    def test_ShowCollectionWalkthrough(self):
        if SET_TO_SHOW_WINDOWS:
            win = tk.Tk()
            ShowWalkthrough(win, walkthrough=COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH, endPages=COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH_END_PAGES)
            tk.mainloop()

class TestEditSlashCommand(unittest.TestCase):

    def test_EditSlashCommand(self):
        win = tk.Tk()
        command = SlashCommand(repr="+say <color black><bgcolor #FFFFFF75><bordercolor red><scale 1.0><duration 10>Yay!")
        target = SlashCommandEditor(win, command)
        s = ttk.Style()
        s.configure('My.TFrame', background='red')
        target.configure(style="My.TFrame")
        target.pack(anchor='n', fill='both', expand=True, side='left')
        actual = target.Get()
        self.assertEqual(actual.__repr__(), command.__repr__())
        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()

class TestEditBind(unittest.TestCase):

    def test_EditBind(self):
        win = tk.Tk()
        expected = Bind(repr="CONTROL+JOYSTICK2_RIGHT em Does this work?$$+say <color black><bgcolor #FFFFFF75><bordercolor red><scale 1.0><duration 10>Yay!")
        def callback(result, bind):
            print(bind)
            self.assertEqual(result, True)
            self.assertEqual(bind.__repr__(), expected.__repr__())
        editor = EditBindWindow(win, callback, expected, True)
        editor.Editor.SetDirty()
        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            editor.OnOk()

class TestEditBindFile(unittest.TestCase):

    def test_EditBindFile(self):
        win = tk.Tk()
        bindFile = ReadBindsFromFile("./TestReferences/keybinds.txt")
        binds = EditBindFile(win, bindFile, showUploadBindButton=True)

        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)
        binds.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

        actual = binds.Get()

        self.assertEqual(len(actual.Binds), len(bindFile.Binds))
        for bind in bindFile.Binds:
            found = actual.GetBindForKey(bind.Key, bind.Chord)
            self.assertEqual(len(found) , 1, "Did not find bind " + str(bind))
            self.assertEqual(bind.GetCommands(), found[0].GetCommands())
            


        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()
        
class TestBindFileCollectionView(unittest.TestCase):

    def test_EditBindFileCollectionView(self):
        
        win = tk.Tk()
        viewFrame = BindFileCollectionView(win)
        viewFrame.pack(fill=tk.BOTH, expand=True)
        #viewFrame.New()
        collection = BindFileCollection()
        collection.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')
        viewFrame.Load(collection)

        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()
        
class TestEditBindFileCollection(unittest.TestCase):

    def test_EditBindFileCollection(self):
        
        win = tk.Tk()
        target = EditBindFileCollection(win)
        target.pack(fill=tk.BOTH, expand=True)
        #viewFrame.New()
        collection = BindFileCollection()
        collection.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')
        target.Load(collection)

        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()

    def test_EditBindFileCollectionSingleFile(self):
        
        win = tk.Tk()
        target = EditBindFileCollection(win)
        target.pack(fill=tk.BOTH, expand=True)
        target.Open(fileName = '.\\TestReferences\\keybinds.txt')

        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()

    def test_EditBindFileCollectionNew(self):
        
        win = tk.Tk()
        target = EditBindFileCollection(win)
        target.pack(fill=tk.BOTH, expand=True)
        target.New(defaults=False)

        if SET_TO_SHOW_WINDOWS:
            tk.mainloop()
        else:
            win.destroy()

class TestBindFileEditorWindow(unittest.TestCase):

    def test_BindFileEditorWindow(self):

        if SET_TO_SHOW_WINDOWS:
            BindFileEditorWindow()

            tk.mainloop()

class TestKeystoneAbout(unittest.TestCase):

    def test_KeystoneAboutself(self):
        if SET_TO_SHOW_WINDOWS:
            win = tk.Tk()
            ShowHelpAbout(win)

            tk.mainloop()

class TestSelectKeybindImportWindow(unittest.TestCase):

    def test_ShowSelectKeybindImportWindow(self):
        if SET_TO_SHOW_WINDOWS:
            win = tk.Tk()

            def callback(selector, filePath):
                print(filePath)

            ShowSelectKeybindImportWindow(win, importCallback=callback)

            tk.mainloop()

if __name__ == "__main__":
    unittest.main()
