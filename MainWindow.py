import tkinter as tk
import os as os
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading

from BindFileCollection import NEW_FILE
from EditBindFile import EditBindFile
from KeystoneFormats import KeystoneFrame, KeystoneButton
from FrameNotebook import FrameNotebook
from KeystoneUtils import GetFileName, SetOpenLinkedFileCallback, GetResourcePath
from SlashCommand import SlashCommand
from DefaultKeyBindings import SAVE_COMMAND, LOAD_COMMAND



def NewTab(mode, path = None):
    with tabLock:
        win.config(cursor="wait")
        win.update()
        try:
            if ((mode == "open") and (path != None) and (notebook.Items != None)):
                #check we don't already have it open
                for item in notebook.Items:
                    if (item.Model == None):
                        continue
                    openPath = item.Model.FilePath
                    if (openPath == None):
                        continue
                    if (os.path.abspath(openPath) == os.path.abspath(path)):
                        return
            notebook.NewFrame("")
            editor = notebook.SelectedFrame()
            if (mode == "open"):
                editor.Open(fileName = path)
            elif (mode == "new"):
                editor.New(defaults=False)
            elif (mode == "default"):
                editor.New(defaults=True)
            SetTabName()
        finally:
            win.config(cursor="")

def SetTabName():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    if (editor.Model == None):
        notebook.RemoveSelectedFrame()
    else:
        filePath = editor.Model.FilePath
        if (filePath == None):
            fileName = NEW_FILE
        else:
            fileName = GetFileName(filePath)
        notebook.tab(notebook.select(), text=fileName)

def OnFileOpen():
    NewTab("open")

def OnFileNew():
    NewTab("new")

def OnFileNewDefaults():
    NewTab("default")

def OnFileSaveAll():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    editor.Save()
    SetTabName()

def OnFileSaveAs():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    editor.Save(promptForPath=True)
    SetTabName()

def CancelFromSavePrompt()->bool:
    editor = notebook.SelectedFrame()
    if (editor == None):
        return False
    if (editor.Dirty.get()):
        response = messagebox.askyesnocancel("Edited File", "Save changes before proceeding?")
        if (response):
            OnFileSaveAs()
            if (editor.Dirty.get()):
            #didn't save, abort
                return True
        elif(response == None):
            return  True
    return False

def OnFileClose():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    if (CancelFromSavePrompt()):
        return
    notebook.RemoveSelectedFrame()

def OnDownloadFile():     
    options = {}
    options['initialfile'] = "keybinds.txt"
    options['title'] = "Select File Destination"
    options['filetypes'] = (("Text Files", "*.txt"), ("All Files", "*.*"))
    options['defaultextension'] = "txt"
    filePath = filedialog.asksaveasfilename(**options)
    if (filePath == ''):
        return
    command = SlashCommand(name=SAVE_COMMAND, text="\"%s\"" % os.path.abspath(filePath))
    win.clipboard_clear()
    win.clipboard_append("/" + str(command))
    response = messagebox.askokcancel("Download from City of Heroes",  
        "The command:\n\n" +
        "/%s\n\n" % str(command) +
        "has been copied to  the clipboard.\n\n" +
        "Paste and execute this command in the game to save the current keybinds to the selected location\n\n" +
        "Click OK to open the saved file.")
    if (response):
        NewTab("open", filePath)

def OnUploadFile():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    if (CancelFromSavePrompt()):
        return
    if (editor.Model.FilePath == None):
        return
    filePath = os.path.abspath(editor.Model.FilePath)
    command = SlashCommand(name=LOAD_COMMAND, text="\"%s\"" % os.path.abspath(filePath))
    win.clipboard_clear()
    win.clipboard_append("/" + str(command))
    messagebox.showinfo("Upload to City of Heroes",  
        "The command:\n\n" +
        "/%s\n\n" % str(command) +
        "has been copied to  the clipboard.\n\n" +
        "Paste and execute this command in the game to load the current keybinds from the selected location\n" +
        "You can add this command as a bind using the Add Upload Bind menu item.")

def OnAddUploadBind():
    editor = notebook.SelectedFrame()
    if (editor == None):
        return
    if ((editor.Model.FilePath == None) and CancelFromSavePrompt()):
        return
    if (editor.Model.FilePath == None):
        return
    editor.AddUploadBind()
    

def OnClosing():
    if (notebook.Dirty == True):
        response = messagebox.askyesnocancel("Edited Files", "Save all changes before closing?")
        if (response):
            for editor in notebook.children.items():
                editor.Save()
        elif(response == None):
            return
    win.destroy()

    

def AddCommand(menu: tk.Menu, frame, label, command):
    menu.add_command(label=label, command=command)
    KeystoneButton(speedBar, text=label, command=command).pack(anchor='nw', side=tk.LEFT)

def _openLinkedFileCallback(path):
    NewTab("open", path)


if (__name__ == "__main__"):
    win = tk.Tk()
    win.title("Keystone")
    icon = GetResourcePath('.\\Resources\\keystone.ico')
    if (icon != None):
        win.iconbitmap(icon)

    speedBar = KeystoneFrame(win)
    speedBar.config(height=45)
    speedBar.pack(anchor='n', fill=tk.X, expand=False, side=tk.TOP)

    menu = tk.Menu(win)

    fileMenu = tk.Menu(menu, tearoff=0)
    AddCommand(menu=fileMenu, frame=speedBar, label="Open", command=OnFileOpen)
    AddCommand(menu=fileMenu, frame=speedBar, label="New (Empty)", command=OnFileNew)
    AddCommand(menu=fileMenu, frame=speedBar, label="New (Defaults)", command=OnFileNewDefaults)
    AddCommand(menu=fileMenu, frame=speedBar, label="Save", command=OnFileSaveAll)
    AddCommand(menu=fileMenu, frame=speedBar, label="Save As...", command=OnFileSaveAs)
    AddCommand(menu=fileMenu, frame=speedBar, label="Close", command=OnFileClose)
    menu.add_cascade(label="File", menu=fileMenu)

    cohMenu = tk.Menu(menu, tearoff = 0)
    cohMenu.add_command(label="Download File", command=OnDownloadFile)
    cohMenu.add_command(label="Upload File", command=OnUploadFile)
    cohMenu.add_command(label="Add Upload Bind", command=OnAddUploadBind)
    menu.add_cascade(label="Game Commands", menu=cohMenu)

    SetOpenLinkedFileCallback(_openLinkedFileCallback)

    notebook = FrameNotebook(win, EditBindFile, None)
    notebook.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

    win.config(menu=menu, width=800, height=400)

    win.protocol("WM_DELETE_WINDOW", OnClosing)

    tabLock = threading.Lock()

    tk.mainloop()