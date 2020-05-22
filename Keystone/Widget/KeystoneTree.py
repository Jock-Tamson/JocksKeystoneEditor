import tkinter as tk
from tkinter import ttk

from Keystone.Widget.KeystoneFormats import (FONT_SIZE, SMALL_FONT_SIZE,
                                             TEXT_FONT)

FILE_TAG = 'file'
EDITED_TAG = 'edited'
CHAIN_TAG = 'chain_header'


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

    def GetAllTaggedChildren(self, tag):

        return [child for child in self.GetAllChildren() if tag in self.item(child)["tags"]]

    def __init__(self, parent, *args, **kwargs):
        ttk.Treeview.__init__(self, parent, *args, **kwargs)
        ttk.Style().configure('keystone.Treeview', font=(TEXT_FONT, SMALL_FONT_SIZE))
        ttk.Style().configure('keystone.Treeview.Heading', font=(TEXT_FONT, FONT_SIZE, 'bold'))
        self.configure(style='keystone.Treeview')
        self.editIcon = tk.PhotoImage(file="Resources\\edit.png")
        self.tag_configure(EDITED_TAG, image=self.editIcon, font=(TEXT_FONT, SMALL_FONT_SIZE, 'bold', 'italic'))
