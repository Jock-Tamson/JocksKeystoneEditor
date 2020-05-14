from tkinter import filedialog, ttk
import tkinter as tk

from KeystoneFormats import TEXT_FONT, FONT_SIZE
from KeystoneUtils import AverageRGBValues

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



