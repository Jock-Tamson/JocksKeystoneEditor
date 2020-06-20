import os as os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Keystone.Model.BindFile import BindFile
from Keystone.Model.BindFileCollection import BindFileCollection, NEW_FILE
from Keystone.Model.Keychain import BOUND_FILES, PATH, REPR
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import LOAD_COMMAND, SAVE_COMMAND
from Keystone.Reference.ImportExportWalkthrough import IMPORT_EXPORT_WALKTHROUGH
from Keystone.Reference.CollectionsAndKeyChainsWalkthrough import COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH, COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH_END_PAGES
from Keystone.Utility.KeystoneUtils import (ComparableFilePath, GetFileName, GetResourcePath,
                                            SetOpenLinkedFileCallback)
from Keystone.View.EditBindFileCollection import EditBindFileCollection
from Keystone.View.BindFileCollectionView import EDITOR
from Keystone.View.EditMacro import EditMacroWindow
from Keystone.Widget.FrameNotebook import FrameNotebook
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame
from Keystone.Widget.KeystoneTree import SELECTED_TAG
from Keystone.Windows.KeystoneAbout import ShowHelpAbout
from Keystone.Windows.KeystoneWalkthroughPages import ShowWalkthrough
from Keystone.Windows.SelectKeybindImportWindow import ShowSelectKeybindImportWindow

class BindFileEditorWindow(tk.Tk):

    def _isOpenFile(self, path):
        if (self.Notebook.Items == None):
            return None
        thisPath = ComparableFilePath(path)
        for item in self.Notebook.Items:
            openPath = item.FilePath
            if (openPath == None):
                continue
            openPath = ComparableFilePath(openPath)
            
            if ( thisPath == openPath ):
                return item
        
        return None

    def NewTab(self, mode, path = None, bindFile = None):
        with self.TabLock:
            setDirty = False
            self.config(cursor="wait")
            self.update()
            try:
                if ((mode == "open") and (path != None) and (self.Notebook.Items != None)):
                    if (self._isOpenFile(path) != None):
                        return
                self.Notebook.NewFrame("")
                editor = self.Notebook.SelectedFrame()
                if (mode == "open"):
                    editor.Open(fileName = path)
                    if (editor.FilePath == None):
                        self.Notebook.RemoveSelectedFrame()
                        return
                elif (mode == "new"):
                    editor.New(defaults=False)
                    if (bindFile != None):
                        editor.Load(bindFile)
                        setDirty = True
                elif (mode == "default"):
                    editor.New(defaults=True)
                self.SetTabName()
                if setDirty:
                    editor.SetDirty()
            finally:
                self.config(cursor="")
            self._showNotebook()
        print("Unlock")

    def SetTabName(self, editor = None):
        if (editor == None):
            editor = self.Notebook.SelectedFrame()
            if (editor == None):
                return
        else:
            tab = self.Notebook.GetTabNameFromItem(editor)
            self.Notebook.select(tab)

        filePath = editor.FilePath
        if (filePath == None):
            fileName = NEW_FILE
        else:
            fileName = GetFileName(filePath)
        self.Notebook.tab(self.Notebook.select(), text=fileName)

    def OnFileOpen(self):
        self.NewTab("open")

    def OnFileNew(self):
        self.NewTab("new")

    def OnFileNewDefaults(self):
        self.NewTab("default")

    def OnSaveCallback(self, editor, *args):
        self.SetTabName(editor = editor)

    def OnFileSave(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save()

    def OnFileSaveAs(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save(True)

    def CancelFromSavePrompt(self)->bool:
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return False
        if (editor.Dirty.get()):
            response = messagebox.askyesnocancel("Edited File", "Save changes before proceeding?")
            if (response):
                self.OnFileSaveAs()
                if (editor.Dirty.get()):
                #didn't save, abort
                    return True
            elif(response == None):
                return  True
        return False

    def OnFileClose(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        self.Notebook.RemoveSelectedFrame()

    def OnDownloadFile(self):     
        options = {}
        options['initialfile'] = "keybinds.txt"
        options['title'] = "Select File Destination"
        options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
        options['defaultextension'] = "txt"
        self.update()
        filePath = filedialog.asksaveasfilename(**options)
        self.update()
        if (filePath == ''):
            return
        command = SlashCommand(name=SAVE_COMMAND, text="\"%s\"" % os.path.abspath(filePath))
        self.clipboard_clear()
        self.clipboard_append("/" + str(command))
        response = messagebox.askokcancel("Download from City of Heroes",  
            "The command:\n\n" +
            "/%s\n\n" % str(command) +
            "has been copied to  the clipboard.\n\n" +
            "Paste and execute this command in the game to save the current keybinds to the selected location\n\n" +
            "Click OK to open the saved file.")
        if (response):
            self.NewTab("open", filePath)

    def OnUploadFile(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame().editor
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        if (editor.FilePath == None):
            return
        filePath = os.path.abspath(editor.FilePath)
        command = SlashCommand(name=LOAD_COMMAND, text="\"%s\"" % os.path.abspath(filePath))
        self.clipboard_clear()
        self.clipboard_append("/" + str(command))
        messagebox.showinfo("Upload to City of Heroes",  
            "The command:\n\n" +
            "/%s\n\n" % str(command) +
            "has been copied to  the clipboard.\n\n" +
            "Paste and execute this command in the game to load the current keybinds from the selected location\n" +
            "You can add this command as a bind using the Add Upload Bind menu item.")

    def OnAddUploadBind(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame().editor
        if (editor == None):
            return
        if ((editor.FilePath == None) and self.CancelFromSavePrompt()):
            return
        if (editor.FilePath == None):
            return
        editor.AddUploadBind()
        

    def OnClosing(self):
        if (self.Notebook.Dirty == True):
            response = messagebox.askyesnocancel("Edited Files", "Save all changes before closing?")
            if (response):
                self.OnSaveAll()
            elif(response == None):
                return
        self.destroy()
        
    def OnSaveAll(self):
        if (self.Notebook.Dirty == True):
            if (self.Notebook.Items != None):        
                for editor in self.Notebook.Items:
                    if editor.Dirty.get():
                        editor.Save()

    def OnCloseAll(self):
        while ((self.Notebook.Items != None) and (len(self.Notebook.Items) > 0)):
            self.CancelFromSavePrompt()
            self.Notebook.RemoveSelectedFrame()

    def _getBoundFilesSource(self):
        return [e.Get() for e in self.Notebook.Items if e.FilePath != None]

    def _onSelectCallback(self, binds, *args):   

        editor = self.Notebook.SelectedFrame().editor
        bindFilePath = editor.FilePath
        options = {}
        options['initialfile'] = "keybinds.kst"
        options['title'] = "Select File Destination"
        options['filetypes'] = (("Keybind Export Files", "*.kst"), ("All Files", "*.*"))
        options['defaultextension'] = "kst"
        self.update()
        filePath = filedialog.asksaveasfilename(**options)
        self.update()
        if (filePath == ''):
            return False

        bindFile = BindFile(binds, filePath = bindFilePath)
        boundFilesSource = self._getBoundFilesSource()
        bindFileCollection = BindFileCollection()
        bindFileCollection.Load(bindFilePath, bindFile = bindFile, boundFilesSource = boundFilesSource)
        bindFileCollection.Serialize(filePath) 

        return True
        

    def OnImportBinds(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        bindFileEditor = self.Notebook.SelectedFrame().editor
        if (bindFileEditor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        
        options = {}
        
        options['title'] = "Open Keybind Export File"
        options['filetypes'] = (("Keybind Export Files", "*.kst"), ("All Files", "*.*"))
        options['defaultextension'] = "kst"
        options['multiple'] = False
        self.update()
        fileName = filedialog.askopenfilename(**options)
        self.update()
        if (fileName == ''):
            return

        collectionEditor.ImportBinds(fileName)
        self.SetTabName(collectionEditor)

    def OnExportBinds(self):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        editor = self.Notebook.SelectedFrame().editor
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        editor.OnSelectCallback = self._onSelectCallback
        editor.SetSelectMode(not editor.SelectMode)

    def OnCreateMacro(self):
        EditMacroWindow(self)

    def OnPredefinedBindsCallback(self, importWindow, filePath):
        collectionEditor = self.Notebook.SelectedFrame()
        if (collectionEditor == None):
            return
        bindFileEditor = self.Notebook.SelectedFrame().editor
        if (bindFileEditor == None):
            return
        if (self.CancelFromSavePrompt()):
            return

        collectionEditor.ImportBinds(filePath)
        self.SetTabName(collectionEditor)

    def AddCommand(self, menu: tk.Menu, frame, label, command):
        menu.add_command(label=label, command=command)
        KeystoneButton(frame, text=label, command=command).pack(anchor='nw', side=tk.LEFT)

    def _openLinkedFileCallback(self, path):  
        if not self.SuppressCallback:      
            self.NewTab("open", path)

    def _showNotebook(self):
        if (not self.ShowingNotebook):
            self.Notebook.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
            self.FirstFrame.pack_forget()
            self.ShowingNotebook = True

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        win = self
        win.title("Keystone")
        icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            win.iconbitmap(icon)

        speedBar = KeystoneFrame(win)
        speedBar.config(height=45)
        speedBar.pack(anchor='n', fill=tk.X, expand=False, side=tk.TOP)

        menu = tk.Menu(win)

        fileMenu = tk.Menu(menu, tearoff=0)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Open", command=self.OnFileOpen)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="New (Empty)", command=self.OnFileNew)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="New (Defaults)", command=self.OnFileNewDefaults)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Save", command=self.OnFileSave)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Save As...", command=self.OnFileSaveAs)
        fileMenu.add_command(label="Save All", command=self.OnSaveAll)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Close", command=self.OnFileClose)
        fileMenu.add_command(label="Close All", command=self.OnCloseAll)
        menu.add_cascade(label="File", menu=fileMenu)

        cohMenu = tk.Menu(menu, tearoff = 0)
        cohMenu.add_command(label="Download File", command=self.OnDownloadFile)
        cohMenu.add_command(label="Upload File", command=self.OnUploadFile)
        cohMenu.add_command(label="Create Macro", command=self.OnCreateMacro)
        menu.add_cascade(label="Game Commands", menu=cohMenu)

        importExportMenu = tk.Menu(menu, tearoff = 0)
        importExportMenu.add_command(label="Import Binds", command=self.OnImportBinds)
        importExportMenu.add_command(label="Export Binds", command=self.OnExportBinds)
        importExportMenu.add_command(label="Add Upload Bind", command=self.OnAddUploadBind)
        importExportMenu.add_command(label="Predefined Binds...", 
            command=lambda parent = win, callback = self.OnPredefinedBindsCallback : ShowSelectKeybindImportWindow(parent, importCallback = callback))
        menu.add_cascade(label="Import\\Export", menu=importExportMenu)

        helpMenu = tk.Menu(menu, tearoff = 0)
        helpMenu.add_command(label='Getting Started', command=lambda parent=win: ShowWalkthrough(parent))
        helpMenu.add_command(label='Import and Export', command=lambda parent=win: ShowWalkthrough(parent, 
            title="Import and Export Walkthrough", walkthrough=IMPORT_EXPORT_WALKTHROUGH))
        helpMenu.add_command(label='Collections and Loaded Files', command=lambda parent=win: ShowWalkthrough(parent, 
            title="Collections and Loaded Files Walkthrough", walkthrough=COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH, endPages=COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH_END_PAGES))
        self.AddCommand(menu=helpMenu, frame=speedBar, label="About", command = lambda parent=win: ShowHelpAbout(parent))
        menu.add_cascade(label='Help', menu=helpMenu)

        SetOpenLinkedFileCallback(self._openLinkedFileCallback)

        self.FirstFrame = KeystoneFrame(win)
        self.FirstFrame.columnconfigure(0, weight=1, minsize = 800)
        self.FirstFrame.rowconfigure(0, weight=1, minsize = 400)
        walkthroughButton = KeystoneButton(self.FirstFrame, text='Intro Walkthrough', command = lambda parent=win: ShowWalkthrough(parent))
        walkthroughButton.Color('lightskyblue', 'black')
        walkthroughButton.configure(relief = tk.RAISED)
        walkthroughButton.grid()
        self.FirstFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.Notebook = FrameNotebook(win, EditBindFileCollection, [self.OnSaveCallback])
        self.ShowingNotebook = False
        self.SuppressCallback = False

        win.config(menu=menu, width=800, height=400)

        win.protocol("WM_DELETE_WINDOW", self.OnClosing)

        self.TabLock = threading.Lock()
