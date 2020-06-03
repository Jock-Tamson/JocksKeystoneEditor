import os as os
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Model.BindFileCollection import NEW_FILE, BindFileCollection, GetKeyChains, KEY_CHAINS, ROOT
from Keystone.Model.Keychain import Keychain, BOUND_FILES, NONE, KEY, CHORD, PATH, REPR
from Keystone.Utility.KeystoneUtils import ComparableFilePath, FormatKeyWithChord, GetDirPathFromRoot, GetFileName, FormatKeyWithChord
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneTree import CHAIN_TAG, EDITED_TAG, FILE_TAG, SELECTED_TAG, KeystoneTree
from Keystone.Model.Bind import UNBOUND
from Keystone.Model.BindFile import BindFile

        
TAG_SEPERATOR = "::"
EDITOR = "editor"

class BindFileCollectionView(KeystoneFrame):

    def _buildExpectedTree(self):
        result = []
        
        tags = [FILE_TAG, self.BuildFileTag(-1, -1)]

        if (self.Directory == NEW_FILE):
            fileName = NEW_FILE
            directory = ""
            tags.append(EDITED_TAG)
        else:
            filePath = os.path.abspath(self.Dictionary[PATH])
            fileName = GetFileName(filePath)
            directory = self.Directory
            if (((self.Dictionary[EDITOR] != None) and (self.Dictionary[EDITOR].Dirty.get())) or (not os.path.exists(filePath))) :
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
                if (((boundFile[EDITOR] != None) and (boundFile[EDITOR].Dirty.get())) or (not os.path.exists(filePath))):
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

    def SetEdited(self, item, value):
        if value:
            self.Tree.AddTag(item, EDITED_TAG)
        else:
            self.Tree.RemoveTag(item, EDITED_TAG)
        fileTag = self.Tree.GetTags(item)[1]
        self.CommitRepr(fileTag)

    def GetEditor(self, fileTag):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            return self.Dictionary[EDITOR]
        else:
            return self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][EDITOR]

    def SetEditor(self, fileTag, editor):
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            self.Dictionary[EDITOR] = editor
        else:
            self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][EDITOR] = editor

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

    def CommitRepr(self, fileTag):
        editor = self.GetEditor(fileTag)
        bindFile = editor.Get()
        if (editor == None):
            return
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            oldRepr = self.Dictionary[ROOT]
            self.Dictionary[ROOT] = bindFile.__repr__()
        else:
            oldRepr = self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][REPR]
            self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][REPR] = bindFile.__repr__()
        
        #check for change in links
        oldBindFile = BindFile(repr=oldRepr)
        if (str(bindFile.GetLoadedFilePaths()) != str(oldBindFile.GetLoadedFilePaths())):
            self._updateTree(chainIndex)

    def _updateTree(self, chainIndex):
        
        orphans = []
        orphanage = None
        collection = self.GetCollection(True)
        collection.KeyChains = GetKeyChains(collection.File, collection.FilePath, collection.GetBoundFiles())
        newDictionary = self.GetDictionary(collection)
        match = [p for p in self.Dictionary[KEY_CHAINS] if (p[KEY] == UNBOUND)]
        if (len(match) > 0):
            orphanage = match[0]
            for orphan in orphanage[BOUND_FILES]:
                orphans.append(orphan)
            self.Dictionary[KEY_CHAINS].remove(orphanage) #to remove or replace at end

        addedChains = []
        removedChains = []
        modifiedChains = []

        if ((newDictionary[KEY_CHAINS] == NONE) and (self.Dictionary[KEY_CHAINS] == NONE)):
            #no key chains, no change
            return
        elif (newDictionary[KEY_CHAINS] == NONE):
            #all chains removed
            for removedChain in self.Dictionary[KEY_CHAINS]:
                removedChains.append(removedChain)
                for oldFile in removedChain[BOUND_FILES]:
                    orphans.append(oldFile)
        elif (self.Dictionary[KEY_CHAINS] == NONE):
            #chains added
            for addedChain in newDictionary[KEY_CHAINS]:
                addedChains.append(newDictionary[KEY_CHAINS])
        else:
      
            #were chains removed
            for oldChain in self.Dictionary[KEY_CHAINS]:
                match = [p for p in newDictionary[KEY_CHAINS] if ((p[KEY] == oldChain[KEY]) and (p[CHORD] == oldChain[CHORD]))]
                if (len(match) == 0):
                    removedChains.append(oldChain)
                    for oldFile in oldChain[BOUND_FILES]:
                        orphans.append(oldFile)

            #were chains added or modified?
            for newChain in newDictionary[KEY_CHAINS]:
                match = [p for p in self.Dictionary[KEY_CHAINS] if ((p[KEY] == newChain[KEY]) and (p[CHORD] == newChain[CHORD]))]
                if (len(match) == 0):
                    addedChains.append(newChain)
                    continue
                oldChain = match[0]
                addedFiles = []
                removedFiles = []
                for newFile in newChain[BOUND_FILES]:
                    oldFile = [p for p in oldChain[BOUND_FILES] if (ComparableFilePath(p[PATH]) == ComparableFilePath(newFile[PATH]))]
                    if (len(oldFile) == 0):
                        addedFiles.append(newFile)

                for oldFile in oldChain[BOUND_FILES]:
                    newFile = [p for p in newChain[BOUND_FILES] if (ComparableFilePath(p[PATH]) == ComparableFilePath(oldFile[PATH]))]
                    if (len(newFile) == 0):
                        removedFiles.append(oldFile)
                        orphans.append(oldFile)

                if ((len(addedFiles) == 0) and (len(removedFiles) == 0)):
                    continue
                
                modifiedChains.append([oldChain, addedFiles, removedFiles])

            if ((len(addedChains) == 0) and (len(removedChains) == 0) and (len(modifiedChains) == 0)):
                #no change
                if (len(orphans) > 0):
                    #need to put this back
                    self.Dictionary[KEY_CHAINS].append(orphanage)   
                return
            
        adoptedOrphans = []
        def adoptionProcess(newFile):
            result = newFile
            adoptees = [p for p in orphans if (ComparableFilePath(p[PATH]) == ComparableFilePath(newFile[PATH]))]
            custodyBattles = [p for p in adoptedOrphans if (ComparableFilePath(p[PATH]) == ComparableFilePath(newFile[PATH]))]
            if (len(adoptees) > 0):
                result = adoptees[0]
                adoptedOrphans.append(adoptees[0])
                for orphan in adoptees:
                    orphans.remove(orphan)
            elif (len(custodyBattles) > 0):
                result = custodyBattles[0]
            return result
            
            

        if (len(addedChains) > 0):
            for addedChain in addedChains:
            #append new chain at end
                addedChain[EDITOR] = None
                addedChain[SELECTED_TAG] = False
                for newFile in  addedChain[BOUND_FILES]:
                    newFile = adoptionProcess(newFile)
                self.Dictionary[KEY_CHAINS].append(addedChain)

        if (len(removedChains) > 0):
            for removedChain in removedChains:
                self.Dictionary[KEY_CHAINS].remove(removedChain)

        if (len(modifiedChains) > 0):
            
            for modifiedChain, addedFiles, removedFiles in modifiedChains:
                #add and remove files in modified chain
                for oldFile in removedFiles:
                    modifiedChain[BOUND_FILES].remove(oldFile)

                for newFile in addedFiles:
                    newFile = adoptionProcess(newFile)
                    modifiedChain[BOUND_FILES].append(newFile)

        if (len(orphans) != 0):
            orphanage = {KEY : UNBOUND , CHORD : "", BOUND_FILES : orphans }
            self.Dictionary[KEY_CHAINS].append(orphanage)   

        self.RefreshTree()            

    def Get(self, fileTag)->BindFile:
        chainIndex, fileIndex = self.ParseFileTag(fileTag)
        if (chainIndex < 0):
            filePath = self.Dictionary[PATH]
            _repr = self.Dictionary[ROOT]
        else:
            filePath = self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][PATH]
            _repr = self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][REPR]
        return BindFile(repr=_repr, filePath = filePath )

    def GetCollection(self, includeUnbound = False):
        if (self.Dictionary == None):
            return None
        keyChains = []
        if (self.Dictionary[KEY_CHAINS] != NONE):
            if includeUnbound:
                chains = self.Dictionary[KEY_CHAINS]
            else:
                chains = [p for p in self.Dictionary[KEY_CHAINS] if p[KEY] != UNBOUND]
            for keyChain in chains:
                boundFiles = [BindFile(repr = p[REPR], filePath = p[PATH]) for p in keyChain[BOUND_FILES]]
                newChain = Keychain(key = keyChain[KEY], chord = keyChain[CHORD], boundFiles = boundFiles)
                keyChains.append(newChain)
        root = BindFile(filePath=self.Dictionary[PATH], repr=self.Dictionary[ROOT])
        collection = BindFileCollection(filePath = root.FilePath, bindFile=root, keyChains = keyChains)
        return collection

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
            self.Tree.selection_set(selectedItem)
            self.Tree.focus(selectedItem)

    def Reset(self):
        self.Tree.Reset()
        self.Dictionary = None
        self.Directory = ""
        self.Tree.heading("#0", text="Keybind Collection", anchor='w')

    def GetDictionary(self, bindFileCollection):

        result = bindFileCollection.GetDictionary()

        #add editor entry to dictiionary
        result[EDITOR] = None
        result[SELECTED_TAG] = False
        keyChains = result[KEY_CHAINS]
        if (keyChains != NONE):
            for keyChain in keyChains:
                boundFiles = keyChain[BOUND_FILES]
                if (boundFiles == NONE):
                    continue
                for boundFile in boundFiles:
                    boundFile[EDITOR] = None
                    boundFile[SELECTED_TAG] = False

        return result

    def Load(self, bindFileCollection):
        self.Reset()
        if (bindFileCollection != None):

            self.Dictionary = self.GetDictionary(bindFileCollection)

            if (bindFileCollection.FilePath == None):
                self.Directory = NEW_FILE
            else:
                self.Directory = os.path.dirname(bindFileCollection.FilePath)
            
            self.Tree.heading("#0", text=self.Directory, anchor='w')

            self.RefreshTree()

    def OnSelectItem(self, *args):
        self.Dictionary[SELECTED_TAG] = False
        chains = self.Dictionary[KEY_CHAINS]
        if (chains != NONE):
            for chain in chains:
                if (chain[BOUND_FILES] == None):
                    continue
                for entry in chain[BOUND_FILES]:
                    entry[SELECTED_TAG] = False
        if (self.Tree.HasTag(self.Tree.SelectedItem, FILE_TAG)):
            tags = self.Tree.GetTags(self.Tree.SelectedItem)
            fieldTag = tags[1]
            chainIndex, fileIndex = self.ParseFileTag(fieldTag)
            if (chainIndex < 0):
                self.Dictionary[SELECTED_TAG] = True
            else:
                self.Dictionary[KEY_CHAINS][chainIndex][BOUND_FILES][fileIndex][SELECTED_TAG] = True

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

        self.Tree.OnSelect.append(self.OnSelectItem)
