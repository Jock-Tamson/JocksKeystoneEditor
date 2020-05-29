import os as os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection
from Keystone.Utility.KeystoneUtils import GetDirPathFromRoot, GetFileName
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneTree import CHAIN_TAG, EDITED_TAG, FILE_TAG, KeystoneTree


class BindFileCollectionView(KeystoneFrame):

    def _fillTree(self, path, collection):
        self.File.set(path)
        if (path == NEW_FILE):
            fileName = NEW_FILE
            directory = ""
            tags = (FILE_TAG, fileName, EDITED_TAG,)
        else:
            fileName = GetFileName(path)
            directory = os.path.dirname(path)
            tags = (FILE_TAG, path, )
        item = self.Tree.insert('', 'end', text=fileName, tags=tags)
        for keyBind, boundFiles in collection.KeyChains.items():
            parent = self.Tree.insert(item, 'end', text='Chain for ' + keyBind, tags=(CHAIN_TAG, keyBind))
            for boundFile in boundFiles:
                filePath = os.path.abspath(boundFile.FilePath)
                fileName = GetDirPathFromRoot(directory, filePath)
                self.Tree.insert(parent, 'end', text=fileName, tags=(FILE_TAG, filePath, ))

    def Reset(self):
        self.Tree.delete(*self.Tree.get_children()) 
        self.Collection = None

    def Load(self, path: str):
        path = os.path.abspath(path)
        self.Reset()
        if (os.path.exists(path)):
            self.Collection = BindFileCollection(path)
            self._fillTree(path, self.Collection)

    def New(self, defaults:bool = False):
        self.Reset()
        self.Collection = BindFileCollection()
        self.Collection.New(defaults)
        self._fillTree(NEW_FILE, self.Collection)

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
    
if (__name__ == "__main__"):
    win = tk.Tk()
    viewFrame = BindFileCollectionView(win)
    viewFrame.pack(fill=tk.BOTH, expand=True)
    #viewFrame.New()
    viewFrame.Load('.\\TestReferences\\Jock Tamson\\keybinds.txt')

    tk.mainloop()
