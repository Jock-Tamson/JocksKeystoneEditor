import os as os
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Model.BindFileCollection import NEW_FILE, KEY_CHAINS, ROOT, BindFileCollection
from Keystone.Model.Keychain import BOUND_FILES, Keychain, NONE, KEY, CHORD, PATH, REPR
from Keystone.View.BindFileCollectionView import BindFileCollectionView
from Keystone.View.EditBindFile import EditBindFile
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystonePanedWindow
from Keystone.Widget.KeystoneTree import (CHAIN_TAG, EDITED_TAG, FILE_TAG,
                                          KeystoneTree)
from Keystone.Utility.KeystoneUtils import SetOpenLinkedFileCallback


class EditBindFileCollection(KeystoneEditFrame):

    def SetEditedItem(self, *args):
        tags = self.selectedItem['tags']
        if (tags[0] != FILE_TAG):
            return
        fileTag = tags[1]
        if (self.EditedItems == None):
            self.EditedItems = [self.editor]
        else:
            self.EditedItems.append(self.editor)
        self.viewFrame.SetEdited(fileTag, len(self.EditedItems) - 1)
        self.SetDirty()

    def ClearEditedItem(self, *args):
        editor = args[0]
        index = [idx for idx, e in enumerate(self.EditedItems) if e == editor][0]
        chainIndex = None
        fileIndex = None
        if self.viewFrame.Dictionary[EDITED_TAG] == index:
            chainIndex = -1
            fileIndex = -1
        elif self.viewFrame.Dictionary[KEY_CHAINS] != NONE:
            for c, keyChain in enumerate(self.viewFrame.Dictionary[KEY_CHAINS]):
                boundFiles = keyChain[BOUND_FILES]
                if (boundFiles == NONE):
                    continue
                for f, boundFile in enumerate(boundFiles):
                    if (boundFile[EDITED_TAG] == index):
                        chainIndex = c
                        fileIndex = f
                        break
                if (chainIndex != None):
                    break
        fileTag = self.viewFrame.BuildFileTag(chainIndex, fileIndex)
        self.viewFrame.SetEdited(fileTag, -1)

    def selectItem(self, *args):
        self.selectedItem = self.viewFrame.Tree.item(self.viewFrame.Tree.focus())
        tags = self.selectedItem['tags']
        if (tags == ''):
            self.lastItem = None
            if (self.editor != None):
                self.editor.grid_forget()
                self.editor = None
            return
        if (tags == self.lastItem):
            return
        self.lastItem = tags
        if (tags[0] == FILE_TAG):
            fileTag = tags[1]
            editorIndex = self.viewFrame.GetEditorIndex(fileTag)
            if (self.editor != None):
                self.editor.grid_forget()
            if (editorIndex >= 0):
                self.editor = self.EditedItems[editorIndex]
            else:
                bindFile = self.viewFrame.Get(fileTag)
                self.editor = EditBindFile(self.editFrame, bindFile)
                self.editor.OnSetDirty.append(self.SetEditedItem)
                self.editor.OnSetClean.append(self.ClearEditedItem)
        elif (tags[0] == CHAIN_TAG):
            self.lastItem = None
            if (self.editor != None):
                self.editor.grid_forget()
                self.editor = None
            return
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
        if (self.viewFrame.Dictionary == None):
            return None
        keyChains = []
        if (self.viewFrame.Dictionary[KEY_CHAINS] != NONE):
            for keyChain in self.viewFrame.Dictionary[KEY_CHAINS]:
                keyChains.append(Keychain(repr=keyChain.__repr__()))
        root = BindFile(filePath=self.viewFrame.Dictionary[PATH], repr=self.viewFrame.Dictionary[ROOT])
        collection = BindFileCollection(filePath = self.FilePath, bindFile=root, keyChains = keyChains)
        return collection

    def New(self, defaults: bool = False):
        bindFile = NewBindFile(defaults)
        collection = BindFileCollection(None, bindFile)
        self.Load(collection)
        self.EditedItems = [EditBindFile(self.editFrame, bindFile = bindFile)]
        self.viewFrame.SetEdited(self.viewFrame.BuildFileTag(-1, -1), 0)
        self.SetDirty()

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

        for idx, editor in enumerate(self.EditedItems):
            item = self.viewFrame.Tree.item(self.viewFrame.GetEditedItem(idx))
            fileTag = item['tags'][1]
            self.viewFrame.CommitRepr(fileTag, editor.Get().__repr__())

        collection = self.Get()
            
        collection.Save(filePath)
        self.Load(collection)

        if (self.SaveCallback != None):
            self.SaveCallback(self)

    def _openLinkedFileCallback(self, path, bind, source):
        pass

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
        self.viewFrame.Tree.bind('<<TreeviewSelect>>', self.selectItem)
        self.Pane.add(self.viewFrame)
    
        self.editFrame = KeystoneFrame(self.Pane, style='editStyle.TFrame', width=1000)
        self.editFrame.columnconfigure(0, weight=1)
        self.editFrame.rowconfigure(0, weight=1)
        self.Pane.add(self.editFrame)
        
        SetOpenLinkedFileCallback(self._openLinkedFileCallback)

        self.Reset()