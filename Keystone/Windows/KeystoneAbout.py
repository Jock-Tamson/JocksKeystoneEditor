import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystoneLabel, TEXT_FONT, LARGE_FONT_SIZE

AboutWindow = None

class KeystoneAbout(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):

        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.maxsize(324, 180)
        self.attributes("-toolwindow", 1)

        icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            self.iconbitmap(icon)

        self.title("About")

        frame = KeystoneFrame(self)

        #setup grid
        self.columnconfigure(0, weight=1, minsize = 324)
        self.rowconfigure(0, weight=1, minsize = 180)
        frame.columnconfigure(0, minsize=108)
        frame.columnconfigure(1, minsize=216)
        frame.rowconfigure(0, minsize=60)
        frame.rowconfigure(1, minsize=120)

        frame.grid(row=0, column=0, sticky='nsew')

        #logo
        imgPath = GetResourcePath('.\\Resources\\Keystone.png')
        if (imgPath != None):
            img = Image.open(imgPath)
            img = img.resize((54,54))
            self.Logo = ImageTk.PhotoImage(img)
            logoLabel = KeystoneLabel(frame, image=self.Logo)
            logoLabel.grid(row=0, column=0, padx=3, pady=3)

        #name
        nameLabel = KeystoneLabel(frame, text='Keystone', font=(TEXT_FONT, LARGE_FONT_SIZE))
        nameLabel.grid(row=0, column=1, sticky='nw')
        subtextLabel = KeystoneLabel(frame, text='City of Heroes Keybind Editor')
        subtextLabel.grid(row=0, column=1, sticky='sw')

        #version
        versionPath = GetResourcePath('VERSION.txt')
        if (versionPath != None):
            file = open(versionPath, "r")
            try:
                version = file.read()
            finally:
                file.close()
            version = version.split("\n")
            versionLabel = KeystoneLabel(frame, text=version[0], font=(TEXT_FONT, LARGE_FONT_SIZE))
            versionLabel.grid(row=1, column=0, columnspan=2)
            dateLabel = KeystoneLabel(frame, text=version[1])
            dateLabel.grid(row=1, column=0, columnspan=2, sticky='s', pady=3)

def _onCloseAboutWindow(*args):
    global AboutWindow
    AboutWindow.destroy()
    AboutWindow = None

def ShowHelpAbout(parent, image=None):

    global AboutWindow
    if (AboutWindow == None):
        AboutWindow = KeystoneAbout(parent)
        AboutWindow.protocol("WM_DELETE_WINDOW", _onCloseAboutWindow)