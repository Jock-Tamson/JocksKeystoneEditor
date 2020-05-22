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
from Keystone.Model.Keylink import Keylink
from Keystone.Model.Keychain import Keychain
from Keystone.View.EditSlashCommand import SlashCommandEditor
from Keystone.View.EditBind import EditBindWindow
from Keystone.View.EditBindFile import EditBindFile
from Keystone.View.BindFileCollectionView import BindFileCollectionView
from Keystone.View.EditKeylink import EditKeylink
from Keystone.View.EditKeychain import EditKeychain
from Keystone.Windows.KeystoneWalkthroughPages import ShowIntroWalkthrough
from Keystone.Windows.BindFileEditorWindow import BindFileEditorWindow
from Keystone.Utility.KeystoneUtils import GetResourcePath

class TestKeystoneWalthroughPages(unittest.TestCase):

    def test_ShowIntroWalkthrough(self):
        win = tk.Tk()
        imgPath = GetResourcePath('.\\Resources\\LeadBrick1.jpg')
        self.Image = ImageTk.PhotoImage(Image.open(imgPath))
        ShowIntroWalkthrough(win, image=self.Image)

        #tk.mainloop()
        win.destroy()

class TestEditSlashCommand(unittest.TestCase):

    def test_EditSlashCommand(self):
        win = tk.Tk()
        command = SlashCommand(repr="+say <color #000000><bgcolor #FFFFFF75><bordercolor #FF0000><scale 1.0><duration 10>Yay!")
        target = SlashCommandEditor(win, command)
        s = ttk.Style()
        s.configure('My.TFrame', background='red')
        target.configure(style="My.TFrame")
        target.pack(anchor='n', fill='both', expand=True, side='left')
        actual = target.Get()
        self.assertEqual(actual.__repr__(), command.__repr__())
        #tk.mainloop()
        win.destroy()

class TestEditBind(unittest.TestCase):

    def test_EditBind(self):
        win = tk.Tk()
        expected = Bind(repr="CONTROL+JOYSTICK2_RIGHT em Does this work?$$+say <color black><bgcolor #FFFFFF75><bordercolor red><scale 1.0><duration 10>Yay!")
        def callback(result, bind):
            self.assertEqual(result, True)
            self.assertEqual(bind.__repr__(), expected.__repr__())
        editor = EditBindWindow(win, callback, expected, True)
        editor.Editor.SetDirty()
        #tk.mainloop()
        editor.OnOk()

class TestEditBindFile(unittest.TestCase):

    def test_EditBindFile(self):
        win = tk.Tk()
        file = ReadBindsFromFile("./TestReferences/keybinds.txt")
        binds = EditBindFile(win, file, showUploadBindButton=True)

        win.columnconfigure(0, weight=1)
        win.rowconfigure(0, weight=1)
        binds.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

        actual = binds.Get()

        self.assertEqual(actual.__repr__(), file.__repr__())

       # tk.mainloop()
        win.destroy()
        
class TestBindFileCollectionView(unittest.TestCase):

    def test_EditBindFileCollectionView(self):
        
        win = tk.Tk()
        viewFrame = BindFileCollectionView(win)
        viewFrame.pack(fill=tk.BOTH, expand=True)
        #viewFrame.New()
        viewFrame.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')

        #tk.mainloop()
        win.destroy()

class TestEditKeyLink(unittest.TestCase):

    def test_EditKeyLink(self):
        
        win = tk.Tk()
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        keychain = Keychain(collection, "I")
        bindFile = ReadBindsFromFile("./TestReferences/Field Test/I1.txt")
        target = Keylink(bindFile, "I")
        editor = EditKeylink(win, target, keychain)
        editor.pack(anchor='n', fill='both', expand=True, side='left')

        #tk.mainloop()
        win.destroy()

class TestEditKeyChain(unittest.TestCase):

    def test_EditKeyChain(self):
        
        win = tk.Tk()
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        editor = EditKeychain(win, target)
        editor.pack(anchor='n', fill='both', expand=True, side='left')

        #tk.mainloop()
        win.destroy()

class TestBindFileEditorWindow(unittest.TestCase):

    def test_BindFileEditorWindow(self):

        win = BindFileEditorWindow()

        #tk.mainloop()
        win.destroy()

if __name__ == "__main__":
    unittest.main()
