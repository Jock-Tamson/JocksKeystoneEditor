import tkinter as tk
from tkinter import filedialog, ttk

from Keystone.Utility.KeystoneUtils import AverageRGBValues
from Keystone.Widget.KeystoneFormats import FONT_SIZE, TEXT_FONT


class KeystoneTextEntry(tk.Text):

    def __init__(self, parent, height = 1, *args, **kwargs):
        tk.Text.__init__(self, parent, *args, **kwargs)   
        self.bind("<Key>", self._update_size)
        self.bind("<Leave>", self._update_size)
        self.configure(height=height)


    def _update_size(self, event):
      widget_height = float(event.widget.index(tk.END))-1.0
      event.widget.config(height=widget_height)
    
    def SetText(self, text):
        self.delete(1.0, tk.END)
        self.insert(tk.INSERT, text)
        widget_height = float(self.index(tk.END))-1.0
        self.config(height=widget_height)

    def GetText(self) -> str:
        return self.get(1.0, tk.END)[:-1] #need to remove /n added when we get the text

