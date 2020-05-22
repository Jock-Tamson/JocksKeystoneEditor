import tkinter as tk

from Keystone.Widget.KeystoneFormats import KeystoneFrame


class KeystoneWizardPage(KeystoneFrame):

    def __init__(self, wizard, allowBack = False, allowNext = False, allowClose = False, onBack = None, onNext = None, onClose = None, *args, **kwargs):

        KeystoneFrame.__init__(self, wizard.Frame, *args, **kwargs)
        self.Wizard = wizard
        self.OnBack = onBack
        self.OnNext = onNext
        self.OnClose = onClose
        self.AllowBack = tk.BooleanVar(value = allowBack)
        self.AllowBack.trace("w", self._setAllowBack)
        self.AllowNext = tk.BooleanVar(value = allowNext)
        self.AllowNext.trace("w", self._setAllowNext)
        self.AllowClose = tk.BooleanVar(value = allowClose)
        self.AllowClose.trace("w", self._setAllowClose)

    def _setAllowBack(self, *args):
        value = self.AllowBack.get()
        if (self.Wizard.CurrentPage == self):
            self.Wizard.ShowBack.set(value)

    def _setAllowNext(self, *args):
        value = self.AllowNext.get()
        if (self.Wizard.CurrentPage == self):
            self.Wizard.ShowNext.set(value)

    def _setAllowClose(self, *args):
        value = self.AllowClose.get()
        if (self.Wizard.CurrentPage == self):
            self.Wizard.ShowClose.set(value)



class KeystoneWizardPageTest(KeystoneWizardPage):

    def __init__(self, parent, text, *args, **kwargs):

        KeystoneWizardPage.__init__(self, parent, *args, **kwargs)

        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 0)

        label1 = tk.Label(self, text=text)
        label1.grid(row=0, column=0, columnspan = 2,  sticky='nsew')
        label2 = tk.Label(self, text='Allow Change')
        label2.grid(row=1, column=0,  sticky='nsew')
        
        self.Checked = tk.BooleanVar(value = False)
        self.Checked.trace("w", self.OnCheck)
        checkbox = tk.Checkbutton(self, variable=self.Checked)
        checkbox.grid(row=1, column=1, sticky='sw')

    def OnCheck(self, *args):
        value = self.Checked.get()
        self.AllowNext.set(value)
