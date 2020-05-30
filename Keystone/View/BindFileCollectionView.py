import os as os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection
from Keystone.Utility.KeystoneUtils import GetDirPathFromRoot, GetFileName
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneTree import CHAIN_TAG, EDITED_TAG, FILE_TAG, KeystoneTree
from Keystone.Model.BindFile import BindFile


class BindFileCollectionView(KeystoneFrame):

    def _buildExpectedTree(self, path, collection):
        result = []
        if (path == NEW_FILE):
            fileName = NEW_FILE
            directory = ""
            tags = (FILE_TAG, fileName, EDITED_TAG,)
        else:
            fileName = GetFileName(path)
            directory = os.path.dirname(path)
            tags = (FILE_TAG, path, )
        result.append((0, fileName, tags))

        if (collection.KeyChains == None):
            return result
        for keyChain in collection.KeyChains:
            keyBind = keyChain.GetKeyWithChord()
            boundFiles = keyChain.BoundFiles
            result.append((1, 'Loaded Files for ' + keyBind, (CHAIN_TAG, keyBind)))
            for boundFile in boundFiles:
                filePath = os.path.abspath(boundFile.FilePath)
                fileName = GetDirPathFromRoot(directory, filePath)
                result.append((2, fileName, (FILE_TAG, filePath, )))

        return result


    def _fillTree(self, path, collection):
        self.File.set(path)
        expected = self._buildExpectedTree(path, collection)
        parent = ['', ]
        for level, text, tags in expected:
            item = self.Tree.insert(parent[level], 'end', text=text, tags=tags)
            if (len(parent) < (level + 2)):
                parent.append(item)
            else:
                parent[level + 1] = item
        self._tree = expected
        self.Tree.OpenCloseAll()

    def Reset(self):
        self.Tree.Reset()
        self.Model = None
        self.Collection = None

    def _doLoad(self, model):
        if (model != None):
            bindFile = BindFile(repr=self.Model.File.__repr__(), filePath=self.Model.File.FilePath)
            boundFilesSource = [BindFile(repr = b.__repr__(), filePath = b.FilePath) for b in self.Model.GetBoundFiles()]
            self.Collection = BindFileCollection()
            self.Collection.Load(self.Model.FilePath, bindFile = bindFile, boundFilesSource = boundFilesSource)
            path = self.Model.FilePath
            if (path == None):
                path = NEW_FILE
            self._fillTree(path, self.Collection)
        else:
            self.Collection = None

    def Load(self, path: str, ):
        self.Reset()
        path = os.path.abspath(path)
        if (os.path.exists(path)):
            self.Model = BindFileCollection()
            self.Model.Load(path)
        else:
            self.Model = None
        self._doLoad(self.Model)

    def New(self, defaults:bool = False):
        self.Reset()
        self.Model = BindFileCollection()
        self.Model.New(defaults)
        self._doLoad(self.Model)

    def __init__(self, parent, showScroll = False, showBrowse = False):

        KeystoneFrame.__init__(self, parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        # creating a scrollbars      
        self.yscrlbr = ttk.Scrollbar(self)
        if showScroll:
            self.yscrlbr.grid(column = 1, row = 1, sticky = 'ns')   

        #create tree
        self.Tree = KeystoneTree(self, selectmode=tk.BROWSE, yscrollcommand=self.yscrlbr.set)
        self.Tree.grid(row=1, column=0, sticky='nsew')

        self.Tree['columns'] = ('bound_files')
        self.Tree.heading("#0", text="Keybind Collection", anchor='w')
        self.Tree.column("#0", stretch=True, width=300)
        self.Tree.column("#1", stretch=False, width = 0)

        # accociating scrollbar comands to tree scroling
        self.yscrlbr.config(command = self.Tree.yview)

        self.yscrlbr.lift(self.Tree)  

        #create file browse frame
        browseFrame = KeystoneFrame(self) 
        browseFrame.grid(row=0, column=0, columnspan=2, sticky='nsew')
        browseFrame.columnconfigure(0, weight=1)
        browseFrame.columnconfigure(1, weight=0)
        self.File = tk.StringVar()
        directoryEdit = KeystoneLabel(browseFrame, textvariable=self.File)
        if showBrowse:
            directoryEdit.grid(column=0, row=0, sticky='nsew')

        self.Collection = None
        self._tree = [(None,None,None)]
    
if (__name__ == "__main__"):
    win = tk.Tk()
    viewFrame = BindFileCollectionView(win)
    viewFrame.pack(fill=tk.BOTH, expand=True)
    #viewFrame.New()
    viewFrame.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')

    tk.mainloop()
