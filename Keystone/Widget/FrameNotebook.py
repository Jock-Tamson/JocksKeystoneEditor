from tkinter import ttk
import tkinter as tk

from Keystone.Utility.KeystoneUtils import ReverseDictionaryLookup
from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame

class FrameNotebook(ttk.Notebook):

    def __init__(self, parent, constructor, defaultArgs, *args, **kwargs):
        ttk.Notebook.__init__(self, parent,*args, **kwargs)

        #container for frames loaded into  Notebook
        self.Items = None

        #frame construction method for frame
        self.Constructor = constructor

        #arguments to use in creating a new frame
        self.DefaultArgs = defaultArgs

        self.Dirty = None

    def GetTabNameFromItem(self, item):
        name = str(self) + "." + ReverseDictionaryLookup(self.children, item)
        return name

    def SelectTabForItem(self, item):
        tab = self.GetTabNameFromItem(item)
        self.select(tab)

    def GetTabTextFromItem(self, item):
        tab = self.GetTabNameFromItem(item)
        text = self.tab(tab)['text']
        return text

    def SetTabTextForItem(self, item, text):
        tab = self.GetTabNameFromItem(item)
        self.tab(tab, text=text)

    def _add_or_remove_asterisk(self, item, add):
        text = self.GetTabTextFromItem(item)
        has_asterisk = (( len(text) > 0 ) and (text[-1] == "*"))
        if (add and (not has_asterisk)):
            text = text + "*"
        elif ((not add) and has_asterisk):
            text = text[:-1]
        self.SetTabTextForItem(item, text)                 

    def DirtyFrame(self, *args):
        self._add_or_remove_asterisk(args[0], True)
        self.Dirty = True

    def _areDirtyFrames(self):
        if (self.Items == None):
            return False
        elif (len([p for p in self.Items if p.Dirty.get()]) == 0):
            return False
        else:
            return True

    def CleanFrame(self, *args):
        self._add_or_remove_asterisk(args[0], False)
        if (not self._areDirtyFrames()):
            self.Dirty = False

    def AddFrame(self, args, label):
        if args == None:
            item = self.Constructor(self)
        else:
            item = self.Constructor(self, *args)
        if self.Items == None:
            self.Items = [item]
        else:
            self.Items.append(item)
        self.add(item, text=label)
        #use OnSetDirty, Clean if available
        try:
            item.OnSetDirty.append(self.DirtyFrame)
            item.OnSetClean.append(self.CleanFrame)
        except:
            pass
        tab = self.tabs()[-1]
        self.select(tab)

    def NewFrame(self, label):
        self.AddFrame(self.DefaultArgs, label)

    def RemoveSelectedFrame(self):
        if self.Items == None:
            return
        item = self.SelectedFrame()
        self.Items.remove(item)
        if len(self.Items) == 0:
            self.Items = None
        if (not self._areDirtyFrames()):
            self.Dirty = False
        self.forget(self.select())

    def SelectedFrame(self): 
        if self.Items == None:
            return None
        name = self.select().split('.')[-1]
        return self.children[name]


class TestFrame(ttk.Frame):

    def __init__(self, parent, message):
        ttk.Frame.__init__(self, parent)
        self.Text = tk.StringVar()
        self.Text.set(message)
        self.Edit = ttk.Entry(self, textvariable=self.Text)
        self.Edit.pack(fill=tk.BOTH, expand=1)



if (__name__ == "__main__"):

    def OnNew():
        notebook.NewFrame("New")

    def OnClose():
        notebook.RemoveSelectedFrame()

    win = tk.Tk()
    constructor = TestFrame
    args = ("1")
    notebook = FrameNotebook(win, constructor, ("X"))
    notebook.AddFrame(args, "First")
    notebook.NewFrame("New")
    new = ttk.Button(win, text="New", command=OnNew)
    delete = ttk.Button(win, text="Close", command=OnClose)
    notebook.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')
    new.pack(anchor='s', fill=tk.BOTH, expand=True, side='left')
    delete.pack(anchor='s', fill=tk.BOTH, expand=True, side='left')

    tk.mainloop()

