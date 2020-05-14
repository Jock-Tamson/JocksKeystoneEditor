from tkinter import ttk
import tkinter as tk
from tkinter.colorchooser import askcolor
from ColorDictionary import STANDARD_COLOR_DICTIONARY
from KeystoneUtils import ReverseColorLookup

class ColorPicker(ttk.Frame):

    def choosecolor(self):
        choice = askcolor()[1]
        if (choice != None):
            color = str.upper(choice)
            color = ReverseColorLookup(color)
            self.ColorEntryText.set(color)       

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)

        self.ColorEntryText = None
        self.Combo = None

        container = ttk.Frame(self)
        container.pack()

        self.ColorEntryText = tk.StringVar(self)
        self.Combo = ttk.Combobox(container, textvariable=self.ColorEntryText,values=" ".join(STANDARD_COLOR_DICTIONARY.keys()))
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