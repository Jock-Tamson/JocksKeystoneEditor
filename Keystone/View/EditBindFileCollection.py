import os as os
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Model.BindFileCollection import NEW_FILE, KEY_CHAINS, ROOT, BindFileCollection
from Keystone.Model.Keychain import BOUND_FILES, Keychain, NONE, KEY, CHORD, PATH, REPR
from Keystone.View.BindFileCollectionView import EDITOR, BindFileCollectionView
from Keystone.View.EditBindFile import EditBindFile
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystonePanedWindow
from Keystone.Widget.KeystoneTree import (CHAIN_TAG, EDITED_TAG, FILE_TAG,
                                          KeystoneTree)
from Keystone.Utility.KeystoneUtils import SetOpenLinkedFileCallback


class EditBindFileCollection(KeystoneEditFrame):

    def SetEditedItem(self, *args):
        editor = args[0]
        item = self.viewFrame.GetEditedItem(editor)
        self.viewFrame.SetEdited(item, True)
        if (self.EditedItems == None):
            self.EditedItems = [editor]
        elif (not (editor in self.EditedItems)):
            self.EditedItems.append(editor)
        self.SetDirty()

    def ClearEditedItem(self, *args):
        editor = args[0]
        item = self.viewFrame.GetEditedItem(editor)
        self.viewFrame.SetEdited(item, False)
        if (self.EditedItems != None):
            if (editor in self.EditedItems):
                self.EditedItems.remove(editor)
                if (len(self.EditedItems) == 0):
                    self.EditedItems = None
                    self.SetClean()

    def selectItem(self, *args):
        self.selectedItem = self.viewFrame.Tree.focus()
        if (self.selectedItem == self.lastItem):
            return
        if (not self.viewFrame.Tree.HasTag(self.selectedItem, FILE_TAG)):
            self.lastItem = None
            if (self.editor != None):
                self.editor.grid_forget()
                self.editor = None
            return
        self.lastItem = self.selectedItem

        fileTag = self.viewFrame.Tree.GetTags(self.selectedItem)[1]
        editor = self.viewFrame.GetEditor(fileTag)
        if (self.editor != None):
            self.editor.grid_forget()
        if (editor != None):
            self.editor = editor
        else:
            bindFile = self.viewFrame.Get(fileTag)
            self.editor = EditBindFile(self.editFrame, bindFile)
            self.editor.OnSetDirty.append(self.SetEditedItem)
            self.editor.OnSetClean.append(self.ClearEditedItem)
            self.viewFrame.SetEditor(fileTag, self.editor)

        self.editor.grid(row=0, column=0, sticky='nsew')

    def Reset(self):
        if (self.editor != None):
            self.editor.grid_forget()
        self.EditedItems = None
        self.FilePath = None
        self.viewFrame.Reset()

    def Load(self, bindFileCollection):
        self.Reset()
        self.FilePath = bindFileCollection.FilePath
        self.viewFrame.Load(bindFileCollection)

        children = self.viewFrame.Tree.GetAllChildren() 
        if (len(children) > 1):
            self.Pane.insert(0, self.viewFrame)
        else:
            self.Pane.forget(self.viewFrame)

        self.viewFrame.Tree.selection_set(children[0])
        self.viewFrame.Tree.focus(children[0])

    def Get(self):
        return self.viewFrame.GetCollection()

    def New(self, defaults: bool = False):
        editor = EditBindFile(self.editFrame)
        editor.New(defaults)
        bindFile = editor.Get()
        collection = BindFileCollection(None, bindFile)
        self.Load(collection)
        self.viewFrame.Dictionary[EDITOR] = editor
        self.SetEditedItem(editor)

    def Open(self, fileName = None):
        if (fileName == None):
            options = {}
            filePath = self.FilePath
            if (filePath != None):
                options['initialfile'] = filePath
                options['initialdir'] = os.path.dirname(filePath)
            options['title'] = "Open Keybind File"
            options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
            options['defaultextension'] = "txt"
            options['multiple'] = False
            fileName = filedialog.askopenfilename(**options)

        if (fileName != ''):
            self.Reset()
            collection = BindFileCollection()
            collection.Load(fileName)
            self.Load(collection)

    def Save(self, promptForPath: bool = False):

        if (self.viewFrame.Dictionary == None):
            return

        currentFilePath = self.FilePath
        if ( promptForPath or (currentFilePath== None)):        
            options = {}
            options['initialfile'] = "keybinds.txt"
            options['title'] = "Save Keybind File As"
            options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
            options['defaultextension'] = "txt"
            filePath = filedialog.asksaveasfilename(**options)
            if (filePath == ''):
                return
        else:
            filePath = currentFilePath

        self.FilePath = os.path.abspath(filePath)

        collection = self.Get()           
        collection.Save(filePath)
        self.Reset()
        self.Load(collection)

        if (self.SaveCallback != None):
            self.SaveCallback(self)

    def __init__(self, parent, saveCallback = None):

        KeystoneEditFrame.__init__(self, parent)

        self.lastItem = None
        self.editor = None
        self.selectedItem = None
        self.EditedItems = None
        self.SaveCallback = saveCallback

        self.Pane = KeystonePanedWindow(self, orient=tk.HORIZONTAL)
        self.Pane.pack(fill=tk.BOTH, expand=1)

        self.viewFrame = BindFileCollectionView(self.Pane)
        self.viewFrame.Tree.OnSelect.append(self.selectItem)
        self.Pane.add(self.viewFrame)
    
        self.editFrame = KeystoneFrame(self.Pane, style='editStyle.TFrame', width=1000)
        self.editFrame.columnconfigure(0, weight=1)
        self.editFrame.rowconfigure(0, weight=1)
        self.Pane.add(self.editFrame)

        self.Reset()