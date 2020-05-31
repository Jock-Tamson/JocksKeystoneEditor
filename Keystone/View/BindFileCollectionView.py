import os as os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection, KEY_CHAINS, ROOT
from Keystone.Model.Keychain import Keychain, BOUND_FILES, NONE, KEY, CHORD, PATH, REPR
from Keystone.Utility.KeystoneUtils import FormatKeyWithChord, GetDirPathFromRoot, GetFileName
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneTree import CHAIN_TAG, EDITED_TAG, FILE_TAG, SELECTED_TAG, KeystoneTree
from Keystone.Model.BindFile import BindFile

        
TAG_SEPERATOR = "::"
EDITOR = "editor"

class BindFileCollectionView(KeystoneFrame):

    def _buildExpectedTree(self):
        result = []
        if (self.Directory == NEW_FILE):
            fileName = NEW_FILE
            directory = ""
        else:
            fileName = GetFileName(self.Dictionary[PATH])
            directory = self.Directory
        
        tags = [FILE_TAG, self.BuildFileTag(-1, -1)]
        if ((self.Dictionary[EDITOR] != None) and (self.Dictionary[EDITOR].Dirty.get())):
            tags.append(EDITED_TAG)
        if (self.Dictionary[SELECTED_TAG]):
            tags.append(SELECTED_TAG)

        result.append((0, fileName, tags))

        if (self.Dictionary[KEY_CHAINS] == NONE):
            return result
        for chainIndex, keyChain in enumerate(self.Dictionary[KEY_CHAINS]):
            keyBind = FormatKeyWithChord(keyChain[KEY], keyChain[CHORD])
            boundFiles = keyChain[BOUND_FILES]
            if (boundFiles == NONE):
                continue
            result.append((1, 'Loaded Files for ' + keyBind, [CHAIN_TAG, keyBind]))
            for fileIndex, boundFile in enumerate(boundFiles):
                filePath = os.path.abspath(boundFile[PATH])
                fileName = GetDirPathFromRoot(directory, filePath)
                tags = [FILE_TAG, self.BuildFileTag(chainIndex, fileIndex)]
                if ((boundFile[EDITOR] != None) and (boundFile[EDITOR].Dirty.get())):
                    tags.append(EDITED_TAG)
                if (boundFile[SELECTED_TAG]):
                    tags.append(SELECTED_TAG)
                result.append((2, fileName, tags, ))

        return result


    def BuildFileTag(self, chainIndex, fileIndex):
        tag = "%d%s%d" % (chainIndex, TAG_SEPERATOR, fileIndex)
        return tag

    def ParseFileTag(self, tag)->(int,int):
        parts = tag.split(TAG_SEPERATOR)
        return (int(parts[0]), int(parts[1]))

    def SetEdited(self, fileTag, value):
        item = self.GetItem(fileTag)
        if value:
            self.Tree.AddTag(item, EDITED_TAG)
        else:
            self.Tree.RemoveTag(item, EDITED_TAG)

    def GetEditor(self, fileTag):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            return self.Dictionary[EDITOR]
        else:
            return self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][EDITOR]

    def GetEditedItem(self, editor):
        
        chainIndex = None
        fileIndex = None
        if self.Dictionary[EDITOR] == editor:
            chainIndex = -1
            fileIndex = -1
        elif self.Dictionary[KEY_CHAINS] != NONE:
            for c, keyChain in enumerate(self.Dictionary[KEY_CHAINS]):
                boundFiles = keyChain[BOUND_FILES]
                if (boundFiles == NONE):
                    continue
                for f, boundFile in enumerate(boundFiles):
                    if (boundFile[EDITOR] == editor):
                        chainIndex = c
                        fileIndex = f
                        break
                if (chainIndex != None):
                    break
        
        if (chainIndex == None):
            return None

        return self.GetItem(self.BuildFileTag(chainIndex, fileIndex))


    def GetItem(self, fileTag):
        child = [item for item in self.Tree.GetAllTaggedChildren(FILE_TAG) if self.Tree.HasTag(item, fileTag)]
        if (len(child) == 0):
            return None
        else:
            return child[0]

    def CommitRepr(self, fileTag, repr):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            self.Dictionary[ROOT] = repr
        else:
            self.Dictionary[KEY_CHAINS][chainIndex][fileIndex][REPR] = repr

    def Get(self, fileTag)->BindFile:
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            filePath = self.Dictionary[PATH]
            _repr = self.Dictionary[ROOT]
        else:
            filePath = self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][PATH]
            _repr = self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][REPR]
        return BindFile(repr=_repr, filePath = filePath )

    def RefreshTree(self):
        self.Tree.Reset()
        expected = self._buildExpectedTree()
        parent = ['', ]
        selectedItem = None
        for level, text, tags in expected:
            item = self.Tree.insert(parent[level], 'end', text=text, tags=tags)
            if SELECTED_TAG in tags:
                selectedItem = item
            if (len(parent) < (level + 2)):
                parent.append(item)
            else:
                parent[level + 1] = item
        self.Tree.OpenCloseAll()
        if (selectedItem != None):
            self.Tree.focus(selectedItem)

    def Reset(self):
        self.Tree.Reset()
        self.Dictionary = None
        self.Directory = ""
        self.Tree.heading("#0", text="Keybind Collection", anchor='w')

    def Load(self, bindFileCollection):
        self.Reset()
        if (bindFileCollection != None):

            self.Dictionary = bindFileCollection.GetDictionary()

            #add editor entry to dictiionary
            self.Dictionary[EDITOR] = None
            self.Dictionary[SELECTED_TAG] = False
            keyChains = self.Dictionary[KEY_CHAINS]
            if (keyChains != NONE):
                for keyChain in keyChains:
                    boundFiles = keyChain[BOUND_FILES]
                    if (boundFiles == NONE):
                        continue
                    for boundFile in boundFiles:
                        boundFile[EDITOR] = None
                        boundFile[SELECTED_TAG] = False

            if (bindFileCollection.FilePath == None):
                self.Directory = NEW_FILE
            else:
                self.Directory = os.path.dirname(bindFileCollection.FilePath)
            
            self.Tree.heading("#0", text=self.Directory, anchor='w')

            self.RefreshTree()

    def __init__(self, parent, showScroll = False):

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
        self.Directory = ""
