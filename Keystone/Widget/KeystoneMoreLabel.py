import tkinter as tk
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystoneLabel, KeystoneButton

class KeystoneMoreLabel(KeystoneFrame):

    MORE = "...more..."
    LESS = "...less..."


    def ToggleText(self):

        text = self.ButtonText.get()
        if (text == self.MORE):
            self.LongLabel.grid(row = 0, column = 0, sticky='nsew')
            self.ShortLabel.grid_forget()
            self.ButtonText.set(self.LESS)
        else:
            self.ShortLabel.grid(row = 0, column = 0, sticky='nsew')
            self.LongLabel.grid_forget()
            self.ButtonText.set(self.MORE)

    def __init__(self, parent, text, *args, **kwargs):

        KeystoneFrame.__init__(self, parent, *args, **kwargs)

        #setup grid
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1)

        parts = text.split("\n", 1)
        self.ShortText = parts[0]
        if (len(parts) > 1):
            self.LongText = "\n".join(parts)
        else:
            self.LongText = None

        self.ShortLabel = KeystoneLabel(self, text = self.ShortText)
        self.ShortLabel.grid(row = 0, column = 0, sticky='nsew')
        self.LongLabel = None
        self.Button = None
        self.ButtonText = None
        if (self.LongText != None):
            self.LongLabel = KeystoneLabel(self, text = self.LongText)
            self.ButtonText = tk.StringVar(value=self.MORE)
            self.Button = KeystoneButton(self, textvariable=self.ButtonText, command = self.ToggleText)
            self.Button.grid(row=1, column=0, sticky='sw')

        
