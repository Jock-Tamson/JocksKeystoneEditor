import os as os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile, NewBindFile, ReadBindsFromFile
from Keystone.Model.BindFileCollection import NEW_FILE
from Keystone.Reference.DefaultKeyBindings import (DEFAULT_BIND,
                                                   DEFAULT_LOAD_BIND)
from Keystone.Reference.KeyNames import CHORD_KEYS, KEY_NAMES
from Keystone.Utility.KeystoneUtils import (GetFileName,
                                            TriggerOpenLinkedFileCallback)
from Keystone.View.EditBind import BindEditor, EditBindWindow
from Keystone.Widget.FrameListView import FrameListView, FrameListViewItem
from Keystone.Widget.ScrollingFrame import ScrollingFrame
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import (BACKGROUND, FOREGROUND, KeystoneButton,
                             KeystoneFrame, KeystoneLabel)


class BindListItem(KeystoneEditFrame):

    def EditorCallback(self, result, bind, *args):
        self.Button.Color(BACKGROUND, FOREGROUND)
        self.Editor = None
        if (result):
            if (bind.GetKeyWithChord(defaultNames=True) != self.Bind.GetKeyWithChord(defaultNames=True)):
                self.BindFileEditor.NewBindCallback(True, bind, moving = self.master)
            else:
                self.Bind = bind
                self.SetDirty()
                self.Label.configure(text=self.Bind)
        
            
    def OnEdit(self, *args):
        if self.Editor == None:
            self.Button.Color(FOREGROUND, BACKGROUND)
            self.Editor = EditBindWindow(self, self.EditorCallback, self.Bind, lockKey=True)
        else:
            self.Editor.OnCancel()

    def ShowEditButton(self, show = False):
        if (show and (not self._showingEdit)):
            self.Button.grid(row=0, column=0, sticky="nsew")
            self._showingEdit = True
        elif ((not show) and self._showingEdit):
            self.Button.grid_forget()
            self._showingEdit = False

    def __init__(self, parent, bind: Bind):
        KeystoneEditFrame.__init__(self, parent) 

        self.BindFileEditor = parent
        while (self.BindFileEditor.__class__.__name__ != "EditBindFile"):
            self.BindFileEditor = self.BindFileEditor.master
            if (self.BindFileEditor == None):
                break
        self.Editor = None
        self.Bind = bind

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self._showingEdit = True
        self.Button = KeystoneButton(self, text="...",  width=6, command=self.OnEdit)
        self.Button.grid(row=0, column=0, sticky="nsew")  
        self.Label = KeystoneLabel(self, text=bind)
        self.Label.grid(row=0,column=1, sticky="nsew") 

class EditBindFile(KeystoneEditFrame):

    def ShowSaveButtons(self, *args):
        if (self.Model == None):
            return
        self.SaveButton.grid(row=0, column=1, sticky='nse')
        if (self.Model.FilePath != None):
            self.CancelButton.grid(row=0, column=2, sticky='nse')

    def HideSaveButtons(self, *args):
        self.SaveButton.grid_forget()
        self.CancelButton.grid_forget()

    def Load(self, bindFile):
        self.Loading = True
        try:
            if (bindFile.Binds != None):

                binds = []
                if (self.List.get()):
                    binds = [Bind(repr=bind.__repr__()) for bind in bindFile.Binds]
                else:
                    #check for and load each permutation of known keys and chords
                    chords = ['']
                    for chord, altname, desc in CHORD_KEYS:
                        dummy = altname
                        dummy = desc
                        chords.append(chord)
                    for key, altname, desc in KEY_NAMES:
                        dummy = altname
                        dummy = desc
                        for chord in chords:
                            keyBinds = bindFile.GetBindForKey(key, chord)
                            if (len(keyBinds) > 0):
                                binds.append(Bind(repr=keyBinds[0].__repr__()))
                    #load anything in the file we didn't match at the end
                    for bind in bindFile.Binds:
                        loaded = [b for b in binds if (bind.GetKeyWithChord(defaultNames=True) == b.GetKeyWithChord(defaultNames = True))]
                        if (len(loaded) == 0):
                            binds.append(Bind(repr=bind.__repr__()))

                self.view.Load(BindListItem, binds, Bind(repr=DEFAULT_BIND))

            self.Model = bindFile

        finally:
            self.Loading = False
        self.SetClean(self)
        if (bindFile.FilePath == None):
            self.PathLabel.configure(text="")
        else:
            self.PathLabel.configure(text=bindFile.FilePath)
        self.OnLinkedFilesFound()
        
    def _buildKeyWithChord(self, key, chord):        
        if (chord == ""):
            result = str.upper(key)
        else:
            result = "%s+%s" % (str.upper(chord), str.upper(key))
        return result

    def NewBindCallback(self, result, bind, moving = None):

        self.Editor = None
        if (result):
            insertIndex = None
            replaceItem = None
            newKey = bind.Key
            newChord = bind.Chord
            if (self.view.Items == None):
                self.view.Items = []

            #find place in list
            itemsInList = [ (idx, self._buildKeyWithChord(item.Item.Bind.Key, item.Item.Bind.Chord)) for idx, item in enumerate(self.view.Items) ]
            newKeyWithChord = self._buildKeyWithChord(newKey, newChord)
            chords = ['']
            for chord, altname, desc in CHORD_KEYS:
                dummy = altname
                dummy = desc
                chords.append(chord)
            for key, altname, desc in KEY_NAMES:
                dummy = altname
                dummy = desc
                for chord in chords:
                    keyWithChord = self._buildKeyWithChord(key, chord)
                    match = [(idx, listedKeyWithChord) for idx, listedKeyWithChord in itemsInList if listedKeyWithChord == keyWithChord]
                    if (len(match) > 0):
                        #this key is in binds
                        index = match[0][0]
                        #we are overwriting it
                        matchKeyWithChord = match[0][1]
                        if (matchKeyWithChord == newKeyWithChord ):
                            replaceItem = self.view.Items[index]
                            insertIndex = index
                            break
                    if (keyWithChord == newKeyWithChord):
                        #this is our spot
                        insertIndex = index + 1
                        break
                if (insertIndex != None):
                    break

            if (replaceItem != None):
                response = messagebox.askokcancel("Existing Bind", "Overwrite the existing bind for " + newKeyWithChord)
                if (response):
                    self.view.Remove(replaceItem)
                else:
                    if (moving == None):
                        title = 'New Bind'
                        self.Editor = EditBindWindow(self, self.NewBindCallback, bind, title=title)
                    else:  
                        title = moving.Item.Bind.GetKeyWithChord()          
                        moving.Item.Button.Color(FOREGROUND, BACKGROUND)
                        moving.Item.Editor = EditBindWindow(moving.Item, moving.Item.EditorCallback, bind, title=title)
                    return

            if (moving != None):
                #remapping rather than inserting new
                movingIndex = self.view.GetIndex(moving)
                if (movingIndex >= 0):
                    self.view.Remove(moving)
                    if (movingIndex < insertIndex):
                        insertIndex = insertIndex - 1

            self.view.Insert(insertIndex, FrameListViewItem(self.view, BindListItem, bind))

    def OnNewBind(self, *args):
        if (self.Editor == None):
            self.Editor = EditBindWindow(self, self.NewBindCallback)

    def Get(self) -> BindFile:       
        if (self.view.Items == None):
            return []
        self.Model.Binds = [item.Item.Bind for item in self.view.Items if item.Item.Bind.Commands != None]
        return self.Model

    def OnSave(self, *args):
        if ((self.Model.FilePath == None) or (self.Model.FilePath == '')):
            filePath = self.PromptForFilePath()
            if (filePath == ''):
                return        
        self.DoWork(target=self._write)
        self.SetClean(self)
        if (self.OnSaveCallback != None):
            self.OnSaveCallback(self)
    
    def OnCancel(self, *args):
        self.Load(self.Model)

    def _read(self, fileName):
        self.Model = ReadBindsFromFile(fileName)

    def _write(self):
        self.Get()
        self.Model.WriteBindsToFile(self.Model.FilePath)

    def OnLinkedFilesFound(self, *args):
        for bind in self.Model.GetLoadFileBinds():
            for command in bind.GetLoadFileCommands():
                targetPath = command.GetTargetFile()
                TriggerOpenLinkedFileCallback(targetPath)
        

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
            self.DoWork(target=self._read, args=(fileName,))
            self.Load(self.Model)

    def New(self, defaults: bool = False):
        file = NewBindFile(defaults)
        self.Load(file)
        self.SetDirty(self)

    def PromptForFilePath(self)->str:
        if (self.Model == None):
            return ''
        options = {}
        options['initialfile'] = "keybinds.txt"
        options['title'] = "Save Keybind File As"
        options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
        options['defaultextension'] = "txt"
        filePath = filedialog.asksaveasfilename(**options)
        if (filePath != ''):
            self.Model.FilePath = filePath
            self.PathLabel.configure(text=self.Model.FilePath)

        return filePath

    def Save(self, promptForPath: bool = False):
        if (self.Model == None):
            return
        if (promptForPath):
            filePath = self.PromptForFilePath()
            if (filePath == ''):
                return
        self.OnSave()

    def OnOkSelect(self, *args):
        close = True
        if (self.OnSelectCallback != None):
            selected = [b.Bind for b in self.view.GetSelected()]
            if (len(selected) > 0):
                close = self.OnSelectCallback(selected)
        if (close):
            self.SetSelectMode(False)

    def OnCancelSelect(self, *args):
        self.SetSelectMode(False)

    def AddUploadBind(self, *args):
        if (self.Model.FilePath == None):
            return
        path = os.path.abspath(self.Model.FilePath)
        bind = None
        dirty = False
        #find current biind
        loadBinds = [item.Item.Bind for item in self.view.Items if item.Item.Bind.IsLoadFileBind()]
        for loadBind in loadBinds:
            loadCommands = loadBind.GetLoadFileCommands()
            for command in loadCommands:
                boundPath = command.GetTargetFile()
                if (boundPath == path):
                    bind = loadBind
                    break
            if (bind != None):
                break
        
        if (bind == None):
            bind = Bind(repr=DEFAULT_LOAD_BIND % path)
            dirty = True

        if (self.Editor == None):
            self.Editor = EditBindWindow(self, self.NewBindCallback, bind=bind, dirty = dirty)

    def SetSelectMode(self, set = False):    
        if (set != self.SelectMode):  
            self.SelectMode = set 
            self.view.SelectMode.set(set)
            if (self.view.Items != None):
                for item in [item.Item for item in self.view.Items]:
                    item.ShowEditButton(not set)
            if (set):
                self.NewBindButton.grid_forget()
                self.OkSelectButton.grid(row=0, column=1, sticky='nse')
                self.CancelSelectButton.grid(row=0, column=2, sticky='nse')
            else:
                self.NewBindButton.grid(row=0, column=3, sticky='nse')
                self.OkSelectButton.grid_forget()
                self.CancelSelectButton.grid_forget()

    def __init__(self, parent, bindFile: BindFile = None, list = False, showUploadBindButton = False, onSaveCallback = None, onSelectCallback = None):
        KeystoneEditFrame.__init__(self, parent) 

        self.OnSetDirty.append(self.ShowSaveButtons)
        self.OnSetClean.append(self.HideSaveButtons)

        self.Model = None

        self.SaveButton = None

        self.CancelButton = None

        self.SelectMode = False
        self.OnSelectCallback = onSelectCallback

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.Model = bindFile

        self.PathLabel = KeystoneLabel(self)
        self.PathLabel.grid(row=0, column=0, sticky='nsew')

        self.SaveButton = KeystoneButton(self, text="Save", command=self.OnSave)
        self.SaveButton.Color("green", "black")

        self.CancelButton = KeystoneButton(self, text="Cancel", command=self.OnCancel)
        self.CancelButton.Color("red", "black")

        self.NewBindButton = KeystoneButton(self, text="New Bind", command=self.OnNewBind)
        self.NewBindButton.Color("yellow", "black")
        self.NewBindButton.grid(row=0, column=3, sticky='nse')

        self.OkSelectButton = KeystoneButton(self, text="Select", command=self.OnOkSelect)
        self.OkSelectButton.Color("green", "black")

        self.CancelSelectButton = KeystoneButton(self, text="Cancel", command=self.OnCancelSelect)
        self.CancelSelectButton.Color("red", "black")

        if (showUploadBindButton):
            self.UploadBindButton = KeystoneButton(self, text="Add Upload Bind", command=self.AddUploadBind)
            self.UploadBindButton.Color("orange", "black")
            self.UploadBindButton.grid(row=0, column=4, sticky='nse')

        scrollingFrame = ScrollingFrame(self)
        scrollingFrame.grid(row=1, column=0, columnspan=5, sticky='nsew')

        self.view = FrameListView(scrollingFrame.scrollwindow, showControlsOnMouseOver=(list))
        self.view.pack(fill=tk.BOTH, expand=1)
        self.view.OnSetDirty.append(self.SetDirty)

        self.List = tk.BooleanVar()
        self.List.set(list)

        self.Editor = None

        self.OnSaveCallback = onSaveCallback

        if (bindFile != None):
            self.Load(bindFile)
        
if (__name__ == "__main__"):
    win = tk.Tk()
    file = ReadBindsFromFile("../TestReferences/keybinds.txt")
    binds = EditBindFile(win, file, showUploadBindButton=True)

    win.columnconfigure(0, weight=1)
    win.rowconfigure(0, weight=1)
    binds.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

    tk.mainloop()
