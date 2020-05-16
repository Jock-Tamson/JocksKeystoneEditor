from tkinter import ttk
import tkinter as tk
from tkinter.colorchooser import askcolor
from ColorDictionary import STANDARD_COLOR_DICTIONARY
from KeystoneUtils import ReverseColorLookup

class ColorPicker(ttk.Frame):

    def choosecolor(self):
        choice = askcolor()[1]
        if (choice != None):
            self.ColorEntryText.set(choice)    

    def lookupcolor(self, *args):
        color = self.ColorEntryText.get() 
        if (color.startswith('#')):
            color = str.upper(color)
            color = ReverseColorLookup(color)
        self._colorEntryText.set(color)  

    def setcolor(self, *args):
        color = self._colorEntryText.get()
        self.ColorEntryText.set(color)

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        self.ColorEntryText = None
        self.Combo = None

        container = ttk.Frame(self)
        container.pack()

        self._colorEntryText = tk.StringVar(self)
        self._colorEntryText.trace("w", self.setcolor)
        self.ColorEntryText = tk.StringVar(self)
        self.ColorEntryText.trace("w", self.lookupcolor)
        self.Combo = ttk.Combobox(container, textvariable=self._colorEntryText,values=" ".join(STANDARD_COLOR_DICTIONARY.keys()))
        self.Combo.grid(row=0, column=0)

        btn = ttk.Button(container, text="Color", command=self.choosecolor, width=5)
        btn.grid(row=0, column=1)

if (__name__ == "__main__"):
    win = tk.Tk()
    picker = ColorPicker(win)
    s = ttk.Style()
    s.configure('My.TFrame', background='red')
    picker.configure(style="My.TFrame")
    picker.pack(anchor='n', fill='both', expand=True, side='left')

    tk.mainloop()