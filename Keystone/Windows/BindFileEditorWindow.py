import os as os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Keystone.Model.BindFileCollection import NEW_FILE
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.DefaultKeyBindings import LOAD_COMMAND, SAVE_COMMAND
from Keystone.Utility.KeystoneUtils import (GetFileName, GetResourcePath,
                                            SetOpenLinkedFileCallback)
from Keystone.View.EditBindFile import EditBindFile
from Keystone.Widget.FrameNotebook import FrameNotebook
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame
from Keystone.Windows.KeystoneWalkthroughPages import ShowIntroWalkthrough


class BindFileEditorWindow(tk.Tk):

    def NewTab(self, mode, path = None):
        with self.TabLock:
            self._showNotebook()
            self.config(cursor="wait")
            self.update()
            try:
                if ((mode == "open") and (path != None) and (self.Notebook.Items != None)):
                    #check we don't already have it open
                    for item in self.Notebook.Items:
                        if (item.Model == None):
                            continue
                        openPath = item.Model.FilePath
                        if (openPath == None):
                            continue
                        if (os.path.abspath(openPath) == os.path.abspath(path)):
                            return
                self.Notebook.NewFrame("")
                editor = self.Notebook.SelectedFrame()
                if (mode == "open"):
                    editor.Open(fileName = path)
                elif (mode == "new"):
                    editor.New(defaults=False)
                elif (mode == "default"):
                    editor.New(defaults=True)
                self.SetTabName()
            finally:
                self.config(cursor="")

    def SetTabName(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
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

    def OnFileSaveAll(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save()
        self.SetTabName()

    def OnFileSaveAs(self):
        editor = self.Notebook.SelectedFrame()
        if (editor == None):
            return
        editor.Save(promptForPath=True)
        self.SetTabName()

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
                for editor in self.Notebook.children.items():
                    editor.Save()
            elif(response == None):
                return
        self.destroy()

    def AddCommand(self, menu: tk.Menu, frame, label, command):
        menu.add_command(label=label, command=command)
        KeystoneButton(frame, text=label, command=command).pack(anchor='nw', side=tk.LEFT)

    def _openLinkedFileCallback(self, path):
        self.NewTab("open", path)

    def _showNotebook(self):
        if (not self.ShowingNotebook):
            self.Notebook.grid(row=0, column=0, sticky='nsew')
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
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Save", command=self.OnFileSaveAll)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Save As...", command=self.OnFileSaveAs)
        self.AddCommand(menu=fileMenu, frame=speedBar, label="Close", command=self.OnFileClose)
        menu.add_cascade(label="File", menu=fileMenu)

        cohMenu = tk.Menu(menu, tearoff = 0)
        cohMenu.add_command(label="Download File", command=self.OnDownloadFile)
        cohMenu.add_command(label="Upload File", command=self.OnUploadFile)
        cohMenu.add_command(label="Add Upload Bind", command=self.OnAddUploadBind)
        menu.add_cascade(label="Game Commands", menu=cohMenu)

        helpMenu = tk.Menu(menu, tearoff = 0)
        helpMenu.add_command(label='Getting Started', command=lambda parent=win: ShowIntroWalkthrough(parent))
        menu.add_cascade(label='Help', menu=helpMenu)

        SetOpenLinkedFileCallback(self._openLinkedFileCallback)

        self.FirstFrame = KeystoneFrame(win)
        self.FirstFrame.columnconfigure(0, weight=1, minsize=800)
        self.FirstFrame.rowconfigure(0, weight=1, minsize=400)
        walkthroughButton = KeystoneButton(self.FirstFrame, text='Intro Walkthrough', command = lambda parent=win: ShowIntroWalkthrough(parent))
        walkthroughButton.Color('lightskyblue', 'black')
        walkthroughButton.configure(relief = tk.RAISED)
        walkthroughButton.grid()
        self.FirstFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.Notebook = FrameNotebook(self.FirstFrame, EditBindFile, None)
        self.ShowingNotebook = False

        win.config(menu=menu, width=800, height=400)

        win.protocol("WM_DELETE_WINDOW", self.OnClosing)

        self.TabLock = threading.Lock()
