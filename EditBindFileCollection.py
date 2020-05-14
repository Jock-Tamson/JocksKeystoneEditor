from tkinter import ttk
import tkinter as tk
import os as os
from tkinter import filedialog

from BindFileCollectionView import BindFileCollectionView
from BindFile import ReadBindsFromFile
from BindFileCollection import BindFileCollection, NEW_FILE
from EditBindFile import EditBindFile
from EditKeychain import EditKeychain
from Keychain import Keychain
from KeystoneFormats import KeystoneFrame, KeystonePanedWindow
from KeystoneTree import KeystoneTree, EDITED_TAG, FILE_TAG, CHAIN_TAG
from KeystoneEditFrame import KeystoneEditFrame

class EditBindFileCollection(KeystoneEditFrame):

    def SetEditedItem(self, *args):
        tags = self.selectedItem['tags']
        selectedFilePath = tags[1]
        if (self.EditedItems == None):
            self.EditedItems = {selectedFilePath : self.editor}
        else:
            self.EditedItems[selectedFilePath] = self.editor
        if (not (EDITED_TAG in tags)):
            tags.append(EDITED_TAG)
        self.viewFrame.Tree.item(self.viewFrame.Tree.focus(), tags=tags)
        self.SetDirty()

    def ClearEditedItem(self, *args):
        editor = args[0]
        filePath = editor.Model.FilePath
        items = self.viewFrame.Tree.GetAllTaggedChildren(filePath)
        for item in items:
            tags = self.viewFrame.Tree.item(item)['tags']
            if (EDITED_TAG in tags):
                tags.remove(EDITED_TAG)
            if ((self.EditedItems != None) and (filePath in self.EditedItems)):
                del self.EditedItems[filePath] 
                if (len(self.EditedItems) == 0):
                    self.EditedItems = None
                    self.SetClean()
            self.viewFrame.Tree.item(item, tags=tags)

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
            selectedFilePath = tags[1]
            if (self.editor != None):
                self.editor.grid_forget()
            if (self.EditedItems != None) and (selectedFilePath in self.EditedItems):
                self.editor = self.EditedItems[selectedFilePath]
            else:
                if (selectedFilePath == self.viewFrame.Collection.FilePath):
                    bindFile = self.viewFrame.Collection.File
                else:
                    bindFile = [b for b in self.viewFrame.Collection.GetBoundFiles() if b.FilePath == selectedFilePath][0]
                self.editor = EditBindFile(self.editFrame, bindFile)
                self.editor.OnSetDirty.append(self.SetEditedItem)
                self.editor.OnSetClean.append(self.ClearEditedItem)
        elif (tags[0] == CHAIN_TAG):
            key = tags[1]
            keyChain = Keychain(self.viewFrame.Collection, key)
            self.editor = EditKeychain(self.editFrame, keyChain)
        self.editor.grid(row=0, column=0, sticky='nsew')

    def Reset(self):
        if (self.editor != None):
            self.editor.grid_forget()
        self.EditedItems = None
        self.viewFrame.Reset()

    def Load(self, path):
        self.Reset()
        self.viewFrame.Load(path)

    def New(self, defaults: bool = False):
        self.Reset()
        self.viewFrame.New(defaults)
        self.EditedItems = {NEW_FILE : EditBindFile(self.editFrame, self.viewFrame.Collection.File)}
        self.SetDirty()

    def Open(self):
        options = {}
        if (self.viewFrame.Collection != None):
            filePath = self.viewFrame.Collection.File.FilePath
        else:
            filePath = None
        if (filePath != None):
            options['initialfile'] = filePath
            options['initialdir'] = os.path.dirname(filePath)
        options['title'] = "Open Keybind File"
        options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
        options['defaultextension'] = "txt"
        options['multiple'] = False
        fileName = filedialog.askopenfilename(**options)
        if (fileName != ''):
            self.Load(path=fileName)

    def Save(self, promptForPath: bool = False):
        if (self.viewFrame.Collection == None):
            return
        currentFilePath = self.viewFrame.Collection.File.FilePath
        if ( promptForPath or (currentFilePath == None)):        
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
        
        filePath = os.path.abspath(filePath)
        if (filePath == currentFilePath):
            if ((self.EditedItems != None) and (len(self.EditedItems) > 0)):
                openEditors = [editor for path, editor in self.EditedItems.items()]
                for editor in openEditors:
                    editor.OnSave()
        else:
            if ((self.EditedItems != None) and (len(self.EditedItems) > 0)):
                openEditors = [editor for path, editor in self.EditedItems.items()]
                for editor in openEditors:
                    editor.Get()
            self.viewFrame.Collection.Save(filePath)
            self.Load(filePath)
            

    def __init__(self, parent):

        KeystoneEditFrame.__init__(self, parent)

        self.lastItem = None
        self.editor = None
        self.selectedItem = None
        self.EditedItems = None

        pane = KeystonePanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=1)

        self.viewFrame = BindFileCollectionView(pane)
        self.viewFrame.Tree.bind('<<TreeviewSelect>>', self.selectItem)
        pane.add(self.viewFrame)
    
        self.editFrame = KeystoneFrame(pane, style='editStyle.TFrame', width=1000)
        self.editFrame.columnconfigure(0, weight=1)
        self.editFrame.rowconfigure(0, weight=1)
        pane.add(self.editFrame)
    
if (__name__ == "__main__"):
    win = tk.Tk()
    editor = EditBindFileCollection(win)
    #editor.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')
    editor.New(defaults=True)
    editor.pack(fill=tk.BOTH, expand=1)

    tk.mainloop()