import os as os
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFile import ReadBindsFromFile
from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection
from Keystone.Model.Keychain import Keychain
from Keystone.View.BindFileCollectionView import BindFileCollectionView
from Keystone.View.EditBindFile import EditBindFile
from Keystone.View.EditKeychain import EditKeychain
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystonePanedWindow
from Keystone.Widget.KeystoneTree import (CHAIN_TAG, EDITED_TAG, FILE_TAG,
                                          KeystoneTree)
from Keystone.Utility.KeystoneUtils import SetOpenLinkedFileCallback


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
            self.lastItem = None
            if (self.editor != None):
                self.editor.grid_forget()
                self.editor = None
            return
            #key = tags[1]
            #keyChain = Keychain(self.viewFrame.Collection, key)
            #self.editor = EditKeychain(self.editFrame, keyChain)
        self.editor.grid(row=0, column=0, sticky='nsew')

    def Reset(self):
        if (self.editor != None):
            self.editor.grid_forget()
        self.EditedItems = None
        self.Model = None
        self.viewFrame.Reset()

    def Load(self, path = None, defaults: bool = False):
        self.Reset()

        if (path == None):
            self.viewFrame.New(defaults)
        else:
            self.viewFrame.Load(path)

        self.Model = self.viewFrame.Collection

        children = self.viewFrame.Tree.GetAllChildren() 
        if (len(children) > 1):
            self.Pane.insert(0, self.viewFrame)
        else:
            self.Pane.forget(self.viewFrame)

        self.viewFrame.Tree.selection_set(children[0])
        self.viewFrame.Tree.focus(children[0])

    def New(self, defaults: bool = False):
        self.Load(defaults = defaults)
        self.EditedItems = {NEW_FILE : EditBindFile(self.editFrame, self.viewFrame.Collection.File)}
        self.SetDirty()

    def Open(self, fileName = None):
        if (fileName == None):
            options = {}
            if (self.Model != None):
                filePath = self.Model.FilePath
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

        if (self.SaveCallback != None):
            self.SaveCallback(self)

    def _openLinkedFileCallback(self, path, bind, sourceFile):
        match = [(idx, item[0], item[1], item[2]) for idx, item in enumerate(self.viewFrame._tree) if (item[2][0] == FILE_TAG) and os.path.realpath(item[2][1]) == os.path.realpath(path)]
        sourcePath = sourceFile.FilePath
        sourceMatch = [(idx, item[0], item[1], item[2]) for idx, item in enumerate(self.viewFrame._tree) if (item[2][0] == FILE_TAG) and os.path.realpath(item[2][1]) == os.path.realpath(sourcePath)]
        if (len(match) > 0):
            matchLevel = match[0][1]
            if (matchLevel == 0):
                print("self load")
            else:
                headerIndex = match[0][0] - 1
                headerLevel = 2
                while (headerLevel != 1):
                    chainHeader = self.viewFrame._tree[headerIndex]
                    headerLevel = chainHeader[0]
                    headerIndex = headerIndex - 1
                headerKey = chainHeader[1].split(" ")[-1]
                bindKey = bind.GetKeyWithChord(defaultNames=True)
                if (bindKey == headerKey):
                    print("No change")
                else:
                    sourceLevel = sourceMatch[0][1]
                    if (sourceLevel == 0):
                        print("remapped chain")
                    else:
                        print("Redirect in chain")
        else:
            #new file
            if (len(sourceMatch) > 0):
                sourceLevel = sourceMatch[0][1]
                if (sourceLevel == 0):
                    print("new chain")
                else:
                    print("extended chain")
            else:
                print("#new orphan")



    def __init__(self, parent, saveCallback = None):

        KeystoneEditFrame.__init__(self, parent)

        self.lastItem = None
        self.editor = None
        self.selectedItem = None
        self.EditedItems = None
        self.Model = None
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
    
if (__name__ == "__main__"):
    win = tk.Tk()
    editor = EditBindFileCollection(win)
    #editor.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')
    editor.New(defaults=True)
    editor.pack(fill=tk.BOTH, expand=1)

    tk.mainloop()
