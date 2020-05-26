import os as os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Keystone.Model.BindFile import BindFile
from Keystone.Model.BindFileCollection import BindFileCollection, NEW_FILE
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import LOAD_COMMAND, SAVE_COMMAND
from Keystone.Utility.KeystoneUtils import (GetFileName, GetResourcePath,
                                            SetOpenLinkedFileCallback)
from Keystone.View.EditBindFile import EditBindFile
from Keystone.Widget.FrameNotebook import FrameNotebook
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame
from Keystone.Windows.KeystoneAbout import ShowHelpAbout
from Keystone.Windows.KeystoneWalkthroughPages import ShowIntroWalkthrough


class BindFileEditorWindow(tk.Tk):

    def NewTab(self, mode, path = None, bindFile = None):
        with self.TabLock:
            self.config(cursor="wait")
            self.update()
            try:
                if ((mode == "open") and (path != None) and (self.Notebook.Items != None)):
                    #check we don't already have it open
                    thisPath = os.path.realpath(os.path.abspath(path))
                    for item in self.Notebook.Items:
                        if (item.Model == None):
                            continue
                        openPath = item.Model.FilePath
                        if (openPath == None):
                            continue
                        openPath = os.path.realpath(os.path.abspath(openPath))
                        
                        if ( thisPath == openPath ):
                            return
                self.Notebook.NewFrame("")
                editor = self.Notebook.SelectedFrame()
                if (mode == "open"):
                    editor.Open(fileName = path)
                elif (mode == "new"):
                    editor.New(defaults=False)
                    if (bindFile != None):
                        editor.Load(bindFile)
                        editor.SetDirty()
                elif (mode == "default"):
                    editor.New(defaults=True)
                self.SetTabName()
            finally:
                self.config(cursor="")
            self._showNotebook()

    def SetTabName(self, editor = None):
        if (editor == None):
            editor = self.Notebook.SelectedFrame()
            if (editor == None):
                return
        else:
            tab = self.Notebook.GetTabNameFromItem(editor)
            self.Notebook.select(tab)
        if (editor.Model == None):
            self.Notebook.RemoveSelectedFrame()
        else:
            filePath = editor.Model.FilePath
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
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save()

    def OnFileSaveAs(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save(promptForPath=True)

    def CancelFromSavePrompt(self)->bool:
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
        filePath = filedialog.asksaveasfilename(**options)
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
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        if (editor.Model.FilePath == None):
            return
        filePath = os.path.abspath(editor.Model.FilePath)
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
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        if ((editor.Model.FilePath == None) and self.CancelFromSavePrompt()):
            return
        if (editor.Model.FilePath == None):
            return
        editor.AddUploadBind()
        

    def OnClosing(self):
        if (self.Notebook.Dirty == True):
            response = messagebox.askyesnocancel("Edited Files", "Save all changes before closing?")
            if (response):
                if (self.Notebook.Items != None):        
                    for editor in self.Notebook.Items:
                        editor.Save()
            elif(response == None):
                return
        self.destroy()

    def _onSelectCallback(self, binds, *args):   

        editor = self.Notebook.SelectedFrame()
        bindFilePath = editor.Model.FilePath
        options = {}
        options['initialfile'] = "keybinds.kst"
        options['title'] = "Select File Destination"
        options['filetypes'] = (("Keybind Export Files", "*.kst"), ("All Files", "*.*"))
        options['defaultextension'] = "kst"
        filePath = filedialog.asksaveasfilename(**options)
        if (filePath == ''):
            return False

        bindFile = BindFile(binds, filePath = bindFilePath)
        bindFileCollection = BindFileCollection()
        bindFileCollection.Load(bindFilePath, bindFile = bindFile)
        bindFileCollection.Serialize(filePath) 

        return True
        

    def OnImportBinds(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        
        options = {}
        
        options['title'] = "Open Keybind Export File"
        options['filetypes'] = (("Keybind Export Files", "*.kst"), ("All Files", "*.*"))
        options['defaultextension'] = "kst"
        options['multiple'] = False
        fileName = filedialog.askopenfilename(**options)
        if (fileName == ''):
            return

        importCollection = BindFileCollection()
        importCollection.Deserialize(fileName)
        boundFiles = importCollection.GetBoundFiles()
        if ((editor.Model.FilePath == None) and (len(boundFiles) > 0)):
            options = {}
            options['title'] = "Select Target Directory for Linked Files"
            dirName = filedialog.askdirectory(**options)
            if (dirName == ''):
                return
            pointPath = os.path.join(dirName, "keybinds.txt")
        else:
            pointPath = editor.Model.FilePath

        importCollection.RepointFilePaths(pointPath)

        for bindFile in importCollection.GetBoundFiles():
            self.NewTab("new", bindFile = bindFile)

        self.Notebook.SelectTabForItem(editor)
        for bind in importCollection.File.Binds:
            editor.NewBindCallback(True, bind)

    def OnExportBinds(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        if (self.CancelFromSavePrompt()):
            return
        editor.OnSelectCallback = self._onSelectCallback
        editor.SetSelectMode(not editor.SelectMode)

    def AddCommand(self, menu: tk.Menu, frame, label, command):
        menu.add_command(label=label, command=command)
        KeystoneButton(frame, text=label, command=command).pack(anchor='nw', side=tk.LEFT)

    def _openLinkedFileCallback(self, path):
        editor = self.Notebook.SelectedFrame()
        self.NewTab("open", path)
        if (editor != None):
            self.Notebook.SelectTabForItem(editor)

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
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Close", command=self.OnFileClose)
        menu.add_cascade(label="File", menu=fileMenu)

        cohMenu = tk.Menu(menu, tearoff = 0)
        cohMenu.add_command(label="Download File", command=self.OnDownloadFile)
        cohMenu.add_command(label="Upload File", command=self.OnUploadFile)
        cohMenu.add_command(label="Add Upload Bind", command=self.OnAddUploadBind)
        menu.add_cascade(label="Game Commands", menu=cohMenu)

        importExportMenu = tk.Menu(menu, tearoff = 0)
        importExportMenu.add_command(label="Import Binds", command=self.OnImportBinds)
        importExportMenu.add_command(label="Export Binds", command=self.OnExportBinds)
        menu.add_cascade(label="Import\\Export", menu=importExportMenu)

        helpMenu = tk.Menu(menu, tearoff = 0)
        helpMenu.add_command(label='Getting Started', command=lambda parent=win: ShowIntroWalkthrough(parent))
        self.AddCommand(menu=helpMenu, frame=speedBar, label="About", command = lambda parent=win: ShowHelpAbout(parent))
        menu.add_cascade(label='Help', menu=helpMenu)

        SetOpenLinkedFileCallback(self._openLinkedFileCallback)

        self.FirstFrame = KeystoneFrame(win)
        self.FirstFrame.columnconfigure(0, weight=1, minsize = 800)
        self.FirstFrame.rowconfigure(0, weight=1, minsize = 400)
        walkthroughButton = KeystoneButton(self.FirstFrame, text='Intro Walkthrough', command = lambda parent=win: ShowIntroWalkthrough(parent))
        walkthroughButton.Color('lightskyblue', 'black')
        walkthroughButton.configure(relief = tk.RAISED)
        walkthroughButton.grid()
        self.FirstFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.Notebook = FrameNotebook(win, EditBindFile, [None, False, False, self.OnSaveCallback])
        self.ShowingNotebook = False

        win.config(menu=menu, width=800, height=400)

        win.protocol("WM_DELETE_WINDOW", self.OnClosing)

        self.TabLock = threading.Lock()
