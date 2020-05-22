import threading
import tkinter as tk
from tkinter import messagebox, ttk

from Keystone.Widget.KeystoneFormats import KeystoneFrame


class KeystoneEditFrame(KeystoneFrame):

    def DoWork(self, target, args = None):
        self.Lock.acquire()
        try:
            if (args == None):
                worker = threading.Thread(target=target, daemon=True)
            else:
                worker = threading.Thread(target=target, args=args, daemon=True)
            worker.start()
            worker.join()
        finally:
            self.Lock.release()

    def SetDirty(self, *args):
        if self.Loading:
            return
        self.Dirty.set(True)
        for function in self.OnSetDirty:
            function(self, *args)

    def SetClean(self, *args):
        if self.Loading:
            return
        self.Dirty.set(False)
        for function in self.OnSetClean:
            function(self, *args)


    def __init__(self, parent):
        KeystoneFrame.__init__(self, parent)

        #List of functions to run on SetDirty
        self.OnSetDirty = []

        #List of functions to run on SetClean
        self.OnSetClean = []

        #Loading flag, set to prevent flag changes while loading form
        self.Loading = False

        #init Dirty flag
        self.Dirty = tk.BooleanVar()
        self.Dirty.set(False)

        #init thread lock
        self.Lock = threading.Lock()

if (__name__ == "__main__"):

    def OnDirty():
        target.SetDirty()

    def OnClean():
        target.SetClean()

    def OnSetClean():
        messagebox.showinfo("Clean")

    def OnSetDirty():
        messagebox.showinfo("Dirty")

    win = tk.Tk()
    target = KeystoneEditFrame(win)
    dirty = tk.Button(target, text="Dirty", command=OnDirty)
    dirty.pack()
    clean = tk.Button(target, text="Clean", command=OnClean)
    clean.pack()

    target.OnSetDirty.append(OnSetDirty)
    target.OnSetClean.append(OnSetClean)

    target.pack(anchor='n', fill='both', expand=True, side='left')

    tk.mainloop()
