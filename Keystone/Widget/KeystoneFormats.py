from tkinter import ttk
import tkinter as tk

BACKGROUND = 'black'
FOREGROUND = 'lightskyblue'
FONT_SIZE = 10
SMALL_FONT_SIZE = 9
LARGE_FONT_SIZE = 20
TEXT_FONT = "Montreal-DemiBold"

class KeystoneFrame(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.TFrame', background=BACKGROUND, font=(TEXT_FONT, FONT_SIZE))
        self.configure(style='keystone.TFrame')

class KeystoneLabel(ttk.Label):

    def __init__(self, parent, *args, **kwargs):
        ttk.Label.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.TLabel', background=BACKGROUND, foreground=FOREGROUND, font=(TEXT_FONT, FONT_SIZE))
        self.configure(style='keystone.TLabel')

class KeystoneCombo(ttk.Combobox):

    def __init__(self, parent, *args, **kwargs):
        ttk.Combobox.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystoneCombo.TCombobox', font=(TEXT_FONT, FONT_SIZE))
        self.configure(style='keystoneCombo.TCombobox')

class KeystoneKeyCombo(ttk.Combobox):

    def __init__(self, parent, *args, **kwargs):
        ttk.Combobox.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystoneKeyCombo.TCombobox', width = 100, height = 50, font=(TEXT_FONT, LARGE_FONT_SIZE))
        self.configure(style='keystoneKeyCombo.TCombobox')

class KeystoneButton(tk.Button):

    def __init__(self, parent, *args, **kwargs):
        tk.Button.__init__(self, parent, *args, **kwargs)
        self.configure(background=BACKGROUND, foreground=FOREGROUND, relief=tk.FLAT, font=(TEXT_FONT, SMALL_FONT_SIZE))

    def Color(self, background=BACKGROUND, foreground=FOREGROUND):
        self.configure(background=background, foreground=foreground)

class KeystoneRadio(ttk.Radiobutton):

    def __init__(self, parent, *args, **kwargs):
        ttk.Radiobutton.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.TRadiobutton', background=BACKGROUND, foreground=FOREGROUND, font=(TEXT_FONT, SMALL_FONT_SIZE))
        self.configure(style='keystone.TRadiobutton')

class KeystoneEntry(ttk.Entry):

    def __init__(self, parent, *args, **kwargs):
        ttk.Entry.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.TEntry', font=(TEXT_FONT, FONT_SIZE),  relief=tk.FLAT, border=0)
        self.configure(style='keystone.TEntry')

class KeystonePanedWindow(ttk.PanedWindow):

    def __init__(self, parent, *args, **kwargs):
        ttk.PanedWindow.__init__(self, parent, *args, **kwargs)
        style = ttk.Style(self)
        style.theme_use("winnative")
        style.configure('keystone.TPanedwindow', background=FOREGROUND, sashwidth=1)
        self.configure(style='keystone.TPanedwindow')

class KeystoneCheckbutton(ttk.Checkbutton):

    def __init__(self, parent, *args, **kwargs):
        ttk.Checkbutton.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.TCheckbutton', background=BACKGROUND, foreground=FOREGROUND)
        self.configure(style='keystone.TCheckbutton')

        
class KeystonePromptFrame(KeystoneFrame):

    def OnButton(self, idx, *args):
        self.Result = self.Results[idx]
        self.grid_forget()
        if (self.Commands[idx] != None):
            self.Commands[idx](self.Result)

    def __init__(self, parent, message, buttons, colors = [], commands = [], results = []):

        KeystoneFrame.__init__(self, parent)

        self.Result = None
        self.Parent = parent
        self.Commands = commands
        self.Results = results

        while (len(colors) < len(buttons)):
            colors.append([BACKGROUND, FOREGROUND])
        while (len(self.Commands) < len(buttons)):
            self.Commands.append(None)
        while (len(self.Results) < len(buttons)):
            self.Results.append(None)
   
        self.columnconfigure(0, weight=1)
        label = KeystoneLabel(self, text = message, anchor='n')
        label.grid(row = 0, column=0, sticky="nsew", padx=6)

        for idx, button in enumerate(buttons):
            self.columnconfigure(idx + 1, weight=0)
            button = KeystoneButton(self, text = button, command=lambda i = idx: self.OnButton(idx=i))
            button.Color( colors[idx][0], colors[idx][1])
            button.grid(row = 0, column = idx + 1, sticky='nsew', padx=3, pady=3)
