import tkinter as tk
from tkinter import ttk

from Keystone.Utility.KeystoneUtils import GetResourcePath
from Keystone.Widget.KeystoneFormats import (BACKGROUND, FOREGROUND, FONT_SIZE, SMALL_FONT_SIZE,
                                             TEXT_FONT)

FILE_TAG = 'file'
EDITED_TAG = 'edited'
CHAIN_TAG = 'chain_header'
SELECTED_TAG = 'selected'


class KeystoneTree(ttk.Treeview):

    def GetAllChildren(self, item = None):
        if (item == None):
            ids = [child for child in self.get_children()]
        else:
            ids = [child for child in self.get_children(item)]
        
        for item in ids:
            for subItem in self.GetAllChildren(item):
                if (not (subItem in ids)):
                    ids.append(subItem)

        return ids

    def Reset(self):
        self.delete(*self.get_children())

    def OpenCloseAll(self, close=False):
        children = self.GetAllChildren()
        for eachChild in children:
            self.item(eachChild, open=not False)

    def GetAllTaggedChildren(self, tag):

        return [child for child in self.GetAllChildren() if tag in self.item(child)["tags"]]

    def selectItem(self, *args):

        #detag deselected
        selectedTaged = self.GetAllTaggedChildren(SELECTED_TAG)
        for item in selectedTaged:
            tags = self.item(item)['tags']
            tags.remove(SELECTED_TAG)
            self.item(item, tags=tags)

        #tag selected
        self.SelectedItem = self.focus()
        tags = self.item(self.SelectedItem)['tags']
        tags.append(SELECTED_TAG)
        self.item(self.SelectedItem, tags=tags)

    def fixed_map(self, style, option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
        return [elm for elm in style.map('keystone.Treeview', query_opt=option) if
        elm[:2] != ('!disabled', '!selected')]

    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, **kwargs)
        style=ttk.Style(self)
        style.theme_use("winnative")
        style.map('keystone.Treeview', foreground=self.fixed_map(style, 'foreground'),
        background=self.fixed_map(style, 'background'))
        style.layout("keystone.Treeview", [('keystone.Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders
        style.configure('keystone.Treeview', font=(TEXT_FONT, SMALL_FONT_SIZE), background=BACKGROUND, 
                fieldbackground=BACKGROUND, foreground=FOREGROUND, relief=tk.FLAT)
        style.configure('keystone.Treeview.Heading', font=(TEXT_FONT, FONT_SIZE, 'bold'), background=BACKGROUND, 
                fieldbackground=BACKGROUND, foreground=FOREGROUND, relief=tk.FLAT)
        style.configure('keystone.Treeview', font=(TEXT_FONT, SMALL_FONT_SIZE), background=BACKGROUND, 
                fieldbackground=BACKGROUND, foreground=FOREGROUND)
        self.configure(style='keystone.Treeview')
        editIconPath = GetResourcePath("Resources\\edit.png")
        self.editIcon = tk.PhotoImage(file=editIconPath)
        self.tag_configure(EDITED_TAG, image=self.editIcon, font=(TEXT_FONT, SMALL_FONT_SIZE, 'bold', 'italic'))      
        self.tag_configure(FILE_TAG, font=(TEXT_FONT, SMALL_FONT_SIZE))     
        self.tag_configure(CHAIN_TAG, font=(TEXT_FONT, SMALL_FONT_SIZE, 'bold'))   
        self.tag_configure(SELECTED_TAG, background=FOREGROUND, foreground=BACKGROUND) 
        self.SelectedItem = None
        self.bind('<<TreeviewSelect>>', self.selectItem)
