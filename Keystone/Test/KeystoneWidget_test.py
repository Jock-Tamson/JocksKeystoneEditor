import os
import inspect
import tkinter as tk
import unittest
from tkinter import ttk

from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.FrameListView import FrameListView

      
class TestFrame(KeystoneEditFrame):

    def __init__(self, parent, message):
        KeystoneEditFrame.__init__(self, parent)
        self.Text = tk.StringVar()
        self.Text.set(message)
        self.Edit = ttk.Entry(self, textvariable=self.Text)
        self.Text.trace("w", self.SetDirty)
        self.Edit.pack(fill=tk.BOTH, expand=1)

class TestFrameListView(unittest.TestCase):      

    def test_FrameListView(self):
        win = tk.Tk()
        constructor = TestFrame
        args = ("1", "2", "3")
        view = FrameListView(win)
        view.Load(constructor, args, "X")
        view.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')

        #tk.mainloop()
        win.destroy()

    def test_FrameListViewSelectMode(self):
        win = tk.Tk()
        constructor = TestFrame
        args = ("1", "2", "3")
        view = FrameListView(win, selectMode = True)
        view.Load(constructor, args, "X")
        view.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')

        #tk.mainloop()
        result = [p.Text.get() for p in view.GetSelected()]
        print(result)
        win.destroy()

        
