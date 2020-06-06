import tkinter as tk
from tkinter import ttk

from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.Widget.KeystoneFormats import KeystoneButton, KeystoneFrame
from Keystone.Widget.KeystoneWizardPage import (KeystoneWizardPage,
                                                KeystoneWizardPageTest)


class KeystoneWizard(tk.Toplevel):

    def __init__(self, parent, title = None, icon = None, onBack = None, onNext = None, onClose = None, *args, **kwargs):

        #initialize
        tk.Toplevel.__init__(self, parent, *args, **kwargs)

        if (title == None):
            title = type(parent).__name__ + " Wizard"
        self.title(title)

        if (icon == None):
            icon = GetResourcePath('.\\Resources\\keystone.ico')
        if (icon != None):
            self.iconbitmap(icon)

        self.Frame = KeystoneFrame(self)

        self.Pages = None
        self.CurrentPage = None

        self.PageIndex = tk.IntVar(value = 0)
        self.PageIndex.trace("w", self.ShowPage)

        #callbacks
        self.OnBackCallback = onBack
        self.OnNexCallback = onNext
        self.OnCloseCallback = onClose

        #setup grid
        self.rowconfigure(0, weight=1, minsize=200)
        self.columnconfigure(0, weight = 1, minsize=400)
        self.Frame.columnconfigure(0, weight=0, minsize=50)
        self.Frame.columnconfigure(1, weight=1)
        self.Frame.columnconfigure(2, weight=0, minsize=50)
        self.Frame.columnconfigure(3, weight=1)
        self.Frame.columnconfigure(4, weight=0, minsize=50)
        self.Frame.rowconfigure(0, weight=1)
        self.Frame.rowconfigure(1, weight=0)

        #setup controls
        self.Frame.grid(row=0, column=0, sticky='nsew')

        self.Back = KeystoneButton(self.Frame, text="Back", command=self.OnBack)
        self.Back.Color('green', 'black')
        self.ShowBack = tk.BooleanVar(value = False)
        self.ShowBack.trace("w", self.OnShowBack)

        self.Next = KeystoneButton(self.Frame, text="Next", command=self.OnNext)
        self.Next.Color('green', 'black')
        self.ShowNext= tk.BooleanVar(value = False)
        self.ShowNext.trace("w", self.OnShowNext)

        self.Close = KeystoneButton(self.Frame, text="Close", command=self.OnClose)
        self.Close.Color('red', 'black')
        self.ShowClose = tk.BooleanVar(value = False)
        self.ShowClose.trace("w", self.OnShowClose)

    def LoadPages(self, pages: [KeystoneWizardPage]):
        if (self.CurrentPage != None):
            self.CurrentPage.grid_forget()
            self.CurrentPage = None
        self.Pages = pages
        for eachPage in pages:
            eachPage.Wizard = self
        self.PageIndex.set(0)

    def PageCount(self)->int:
        if (self.Pages == None):
            return 0
        return len(self.Pages)

    def OnShowBack(self, *args):
        if (self.PageIndex.get() == 0):
            show = False
        else:
            show = self.ShowBack.get()
        if (show):
            self.Back.grid(column = 0, row = 1, sticky='nsew')
        else:
            self.Back.grid_forget()

    def OnShowNext(self, *args):
        if (self.PageIndex.get() == (self.PageCount() - 1)):
            show = False
        else:
            show = self.ShowNext.get()
        if (show):
            self.Next.grid(column = 4, row = 1, sticky='nsew')
        else:
            self.Next.grid_forget()

    def OnShowClose(self, *args):
        show = self.ShowClose.get()
        if (show):
            self.Close.grid(column = 2, row = 1, sticky='nsew')
        else:
            self.Close.grid_forget()

    def ShowPage(self, *args):

        if (self.PageCount() == 0):
            return

        #get index
        index = self.PageIndex.get()
        if (index >= self.PageCount()):
            index = self.PageCount() -1
            self.PageIndex.set(index)
            return #as set will callback due to trace            
        elif(index < 0):
            index = 0
            self.PageIndex.set(index)
            return #as set will callback due to trace

        #drop current page
        if (self.CurrentPage != None):
            self.CurrentPage.grid_forget()

        #show page and buttons
        page = self.Pages[index]
        page.grid(row=0, column=0, columnspan=5, sticky='nsew')
        self.CurrentPage = page
        self.ShowBack.set(page.AllowBack.get())
        self.ShowNext.set(page.AllowNext.get())
        self.ShowClose.set(page.AllowClose.get())

    def _onButton(self, callback, pageCallback, allowVar, showVar, indexChange):
        if (pageCallback != None):
            pageCallback(self, self.CurrentPage)
        allow = allowVar.get()
        showVar.set(allow)
        index = self.PageIndex.get() + indexChange 
        if (index > self.PageCount()):
            index = self.PageCount() -1
        elif(index < 0):
            index = 0
        if (index != self.PageIndex.get()):
            self.PageIndex.set(index)
            if (callback != None):
                callback(self)

    def OnBack(self, *args):
        page = self.CurrentPage
        self._onButton(self.OnBackCallback, page.OnBack, page.AllowBack, self.ShowBack, -1)

    def OnNext(self, *args):
        page = self.CurrentPage
        self._onButton(self.OnNexCallback, page.OnNext, page.AllowClose, self.ShowClose, 1)

    def OnClose(self, *args):
        page = self.CurrentPage
        if (page.OnClose != None):
            page.OnClose(self)
        if (page.AllowClose.get()):
            self.destroy()
        if (self.OnCloseCallback != None):
            self.OnCloseCallback(self)
        
        
if (__name__ == "__main__"):

    win = tk.Tk()

    wizard = KeystoneWizard(win, title='Keystone Wizard Test')

    page1 = KeystoneWizardPageTest(wizard, '1', allowBack = True)

    page2 = KeystoneWizardPageTest(wizard, '2', allowBack = True)

    page3 = KeystoneWizardPageTest(wizard, '3', allowBack = True, allowClose = True)

    pages = [page1, page2, page3]

    wizard.LoadPages(pages)

    tk.mainloop()

