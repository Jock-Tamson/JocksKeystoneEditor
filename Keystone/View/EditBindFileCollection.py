import os as os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Model.BindFileCollection import NEW_FILE, KEY_CHAINS, ROOT, BindFileCollection
from Keystone.Model.Keychain import BOUND_FILES, Keychain, NONE, KEY, CHORD, PATH, REPR
from Keystone.View.BindFileCollectionView import EDITOR, BindFileCollectionView, SELECTED_TAG
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
        hasChildren = ( not (self.viewFrame.Dictionary[KEY_CHAINS] == NONE))
        self.ShowTree.set(hasChildren)
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

    def OnShowTree(self, *args):
        value = self.ShowTree.get()
        if (value and (self._showingTree != True)):
            self.Pane.insert(0, self.viewFrame)
            self._showingTree = True
        elif ((not value) and (self._showingTree != False)):
            self.Pane.forget(self.viewFrame)
            self._showingTree = False

    def Reset(self):
        if (self.editor != None):
            self.editor.grid_forget()
        self.EditedItems = None
        self.FilePath = None
        self.viewFrame.Reset()
        self.ShowTree.set(False)

    def Load(self, bindFileCollection):
        self.Reset()
        self.FilePath = bindFileCollection.FilePath
        self.viewFrame.Load(bindFileCollection)
        self.viewFrame.SelectRoot()
        hasChildren = ( not (self.viewFrame.Dictionary[KEY_CHAINS] == NONE))
        self.ShowTree.set(hasChildren)
        if ((self.FilePath != None) and os.path.exists(self.FilePath)):              
            self.SetClean(self)
        else:
            self.SetDirty(self)

    def Get(self):
        return self.viewFrame.GetCollection()

    def New(self, defaults: bool = False):
        editor = EditBindFile(self.editFrame)
        editor.New(defaults)
        bindFile = editor.Get()
        collection = BindFileCollection(None, bindFile)
        self.Load(collection)

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
            self.master.update()
            fileName = filedialog.askopenfilename(**options)
            self.master.update()

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
            self.master.update()
            filePath = filedialog.asksaveasfilename(**options)
            self.master.update()
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

    def ImportBinds(self, filePath):

        if (self.editor == None):
            return
        importCollection = BindFileCollection()
        importCollection.Deserialize(filePath)
        boundFiles = importCollection.GetBoundFiles()
        if (((self.editor.FilePath == None) or (self.editor.FilePath == NEW_FILE)) and (len(boundFiles) > 0)):
            response = messagebox.askokcancel('Path Needed For Linked Files',
                'You must choose a target path for this file to set paths for linked files.\n'+
                'The paths will be set, but no files will be saved yet.')
            if (not response):
                return
            options = {}
            options['initialfile'] = "keybinds.txt"
            options['title'] = "Select Target Destination for Linked Files"
            options['filetypes'] = (("Keybind Files", "*.txt"), ("All Files", "*.*"))
            options['defaultextension'] = "txt"
            self.master.update()
            pointPath = filedialog.asksaveasfilename(**options)
            self.master.update()
            if (pointPath == ''):
                return False          
            self.FilePath = pointPath
        else:
            pointPath = self.editor.FilePath

        importCollection.RepointFilePaths(pointPath)
        if (pointPath != None):
            self.editor.FilePath = pointPath
            self.editor.PathLabel.configure(text=self.editor.FilePath)
            self.FilePath = self.editor.FilePath 
            self.viewFrame.Directory = os.path.dirname(self.editor.FilePath)
            self.viewFrame.Dictionary[PATH] = self.editor.FilePath

        boundFiles = importCollection.GetBoundFiles()
        if (len(boundFiles) > 0):
            #put them in the orphange so refresh can find them
            orphans = [{PATH : boundFile.FilePath, REPR : boundFile.__repr__(), EDITOR : None, SELECTED_TAG : False} for boundFile in boundFiles]
            self.viewFrame.GetOrphanage(True, orphans)

        for bind in importCollection.File.Binds:
            self.editor.NewBindCallback(True, bind)

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

        self._showingTree = None
        self.ShowTree = tk.BooleanVar(value=False)
        self.ShowTree.trace("w", self.OnShowTree)

        self.Reset()