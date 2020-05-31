import os as os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection, KEY_CHAINS, ROOT
from Keystone.Model.Keychain import Keychain, BOUND_FILES, NONE, KEY, CHORD, PATH, REPR
from Keystone.Utility.KeystoneUtils import FormatKeyWithChord, GetDirPathFromRoot, GetFileName
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneTree import CHAIN_TAG, EDITED_TAG, FILE_TAG, KeystoneTree
from Keystone.Model.BindFile import BindFile

        
TAG_SEPERATOR = "::"

class BindFileCollectionView(KeystoneFrame):

    def _buildExpectedTree(self):
        result = []
        if (self.Directory == NEW_FILE):
            fileName = NEW_FILE
            directory = ""
        else:
            fileName = GetFileName(self.Dictionary[PATH])
            directory = self.Directory
        
        if (self.Dictionary[EDITED_TAG] >= 0):
            tags = (FILE_TAG, self.BuildFileTag(-1, -1), EDITED_TAG)
        else:
            tags = (FILE_TAG, self.BuildFileTag(-1, -1),)

        result.append((0, fileName, tags))

        if (self.Dictionary[KEY_CHAINS] == NONE):
            return result
        for chainIndex, keyChain in enumerate(self.Dictionary[KEY_CHAINS]):
            keyBind = FormatKeyWithChord(keyChain[KEY], keyChain[CHORD])
            boundFiles = keyChain[BOUND_FILES]
            if (boundFiles == NONE):
                continue
            result.append((1, 'Loaded Files for ' + keyBind, (CHAIN_TAG, keyBind)))
            for fileIndex, boundFile in enumerate(boundFiles):
                filePath = os.path.abspath(boundFile[PATH])
                fileName = GetDirPathFromRoot(directory, filePath)
                if (boundFile[EDITED_TAG] >= 0):
                    tags = (FILE_TAG, self.BuildFileTag(chainIndex, fileIndex), EDITED_TAG)
                else:
                    tags = (FILE_TAG, self.BuildFileTag(chainIndex, fileIndex), )
                result.append((2, fileName, tags, ))

        return result


    def BuildFileTag(self, chainIndex, fileIndex):
        tag = "%d%s%d" % (chainIndex, TAG_SEPERATOR, fileIndex)
        return tag

    def ParseFileTag(self, tag)->(int,int):
        parts = tag.split(TAG_SEPERATOR)
        return (int(parts[0]), int(parts[1]))

    def SetEdited(self, fileTag, value):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            self.Dictionary[EDITED_TAG] = value
        else:
            self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][EDITED_TAG] = value
        item = self.GetItem(fileTag)
        tags = self.Tree.item(item)['tags']
        if ((value >= 0) and (tags[-1] != EDITED_TAG)):
            tags.append(EDITED_TAG)
        elif ((value == -1) and (tags[-1] == EDITED_TAG)):
            tags.remove(EDITED_TAG)
        
        self.Tree.item(item, tags=tags)

    def GetEditorIndex(self, fileTag):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            return self.Dictionary[EDITED_TAG]
        else:
            return self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][EDITED_TAG]

    def GetEditedItem(self, editorIndex):
        
        chainIndex = None
        fileIndex = None
        if self.Dictionary[EDITED_TAG] == editorIndex:
            chainIndex = -1
            fileIndex = -1
        elif self.Dictionary[KEY_CHAINS] != NONE:
            for c, keyChain in enumerate(self.Dictionary[KEY_CHAINS]):
                boundFiles = keyChain[BOUND_FILES]
                if (boundFiles == NONE):
                    continue
                for f, boundFile in enumerate(boundFiles):
                    if (boundFile[EDITED_TAG] == editorIndex):
                        chainIndex = c
                        fileIndex = f
                        break
                if (chainIndex != None):
                    break
        
        if (chainIndex == None):
            return None
        return self.GetItem(self.BuildFileTag(chainIndex, fileIndex))


    def GetItem(self, fileTag):
        child = [item for item in self.Tree.GetAllTaggedChildren(FILE_TAG) if self.Tree.item(item)['tags'][1] == fileTag]
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
        expected = self._buildExpectedTree()
        parent = ['', ]
        for level, text, tags in expected:
            item = self.Tree.insert(parent[level], 'end', text=text, tags=tags)
            if (len(parent) < (level + 2)):
                parent.append(item)
            else:
                parent[level + 1] = item
        self.Tree.OpenCloseAll()

    def Reset(self):
        self.Tree.Reset()
        self.Dictionary = None
        self.Directory = ""
        self.Tree.heading("#0", text="Keybind Collection", anchor='w')

    def Load(self, bindFileCollection):
        self.Reset()
        if (bindFileCollection != None):

            self.Dictionary = bindFileCollection.GetDictionary()

            #add edited tags to dictionary, index of editor, -1 is none
            self.Dictionary[EDITED_TAG] = -1
            keyChains = self.Dictionary[KEY_CHAINS]
            if (keyChains != NONE):
                for keyChain in keyChains:
                    boundFiles = keyChain[BOUND_FILES]
                    if (boundFiles == NONE):
                        continue
                    for boundFile in boundFiles:
                        boundFile[EDITED_TAG] = -1

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
