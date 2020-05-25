
import tkinter as tk
import webbrowser

from PIL import Image, ImageTk

from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.Reference.IntroWalkthrough import (WALKTHROUGH, WALKTHROUGH_END_PAGES)
from Keystone.Widget.KeystoneFormats import KeystoneFrame, KeystoneLabel
from Keystone.Widget.KeystoneWizard import KeystoneWizard, KeystoneWizardPage


WalkthroughWindow = None
LeadBrickImage = None

class KeystoneWalkthroughPages(KeystoneWizardPage):

    def __init__(self, wizard: KeystoneWizard, text: str, urls = None, *args, **kwargs):

        KeystoneWizardPage.__init__(self, wizard, allowBack = True, allowClose=True, allowNext=True, *args, **kwargs)

        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1, minsize=510)
        self.rowconfigure(0, weight = 1)

        label = KeystoneLabel(self, text = text, wraplength=500, justify=tk.LEFT)
        label.grid(row=0, column=1, sticky='n', padx=5, pady=5 )
        global LeadBrickImage
        if (LeadBrickImage == None):
            imgPath = GetResourcePath('.\\Resources\\LeadBrick1.jpg')
            if (imgPath != None):
                LeadBrickImage = ImageTk.PhotoImage(Image.open(imgPath))
            else:
                LeadBrickImage = 0
        if (LeadBrickImage != 0):
            self.Image = LeadBrickImage
            self.ImagePanel = tk.Label(self, image=self.Image)          
            self.ImagePanel.grid(row=0, column=0, sticky='nsew')

        if (urls != None):
            urlFrame = KeystoneFrame(self)
            for idx, eachURL in enumerate(urls):
                link = KeystoneLabel(urlFrame, text = eachURL)
                link.bind("<Button-1>", lambda e, url = eachURL: self.callback(url))
                link.grid(row = idx, column=0, sticky='nsew')
            urlFrame.grid(row=0, column=1)

    def callback(self, url):
        webbrowser.open_new(url)

def _onCloseWalkthroughWindow(wizard, *args):
    global WalkthroughWindow
    WalkthroughWindow = None

def ShowIntroWalkthrough(parent, image=None):

    global WalkthroughWindow
    global LeadBrickImage
    LeadBrickImage = image
    if (WalkthroughWindow == None):
        WalkthroughWindow = KeystoneWizard(parent, title='Keystone Walkthrough', onClose = _onCloseWalkthroughWindow)
        pages= []
        for eachLine in WALKTHROUGH:
            pages.append(KeystoneWalkthroughPages(WalkthroughWindow, text=eachLine))
        for text, urls in WALKTHROUGH_END_PAGES:
            pages.append(KeystoneWalkthroughPages(WalkthroughWindow, text=text, urls=urls))

        WalkthroughWindow.LoadPages(pages)


if (__name__ == "__main__"):

    win = tk.Tk()

    ShowIntroWalkthrough(win)

    tk.mainloop()
