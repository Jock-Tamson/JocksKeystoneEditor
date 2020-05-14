from tkinter import ttk
import tkinter as tk

from KeystoneFormats import KeystoneFrame, KeystoneButton, KeystoneLabel, KeystoneRadio, TEXT_FONT, KeystonePromptFrame
from KeystoneEditFrame import KeystoneEditFrame

class ConfirmationFrame(KeystonePromptFrame):

    def __init__(self, parent, message, command):

        KeystonePromptFrame.__init__(self, parent, message, ["Ok", "Cancel"], [['green', 'black'], ['red', 'black']], [command, None], [True, False])


class FrameListViewItem(KeystoneFrame):

    INSERT_MESSAGE = "Insert Here?"
    DELETE_MESSAGE = "Delete This Item?"

    INSERT_TEXT = 'Insert'
    INSERT_COLOR = 'black'
    INSERT_TEXT_COLOR = 'yellow'
    INSERT_STYLE = tk.FLAT

    MOVE_TEXT = 'Move'
    MOVE_COLOR = 'black'
    MOVE_TEXT_COLOR = 'green'
    MOVE_STYLE = tk.FLAT

    DELETE_TEXT = 'X'
    DELETE_COLOR = 'black'
    DELETE_TEXT_COLOR = 'red'
    DELETE_STYLE = tk.FLAT

    def OnMove(self, *args):
        if (self.Parent.MovingObject ==  self):
            self.Parent.ExitMoveMode()
        else:
            self.Parent.EnterMoveMode(self)

    def OnInsertAbove(self, *args):
        self.TopInsert.grid_forget()
        confirm = ConfirmationFrame(self, self.INSERT_MESSAGE, self.OnInsertAboveCallback)
        confirm.grid(column=0, row=0, columnspan=3, sticky='nsew')

    def OnInsertBelow(self, *args):
        self.BottomInsert.grid_forget()
        confirm = ConfirmationFrame(self, self.INSERT_MESSAGE, self.OnInsertBelowCallback)
        confirm.grid(column=0, row=2, columnspan=3, sticky='nsew')

    def OnInsertAboveCallback(self, result):
        self.TopInsert.grid(column=0, row=0, columnspan=3, sticky='nsew')
        if (result):
            self.Parent.MoveOrCreate(self)

    def OnInsertBelowCallback(self, result):
        self.BottomInsert.grid(column=0, row=2, columnspan=3, sticky='nsew')
        if (result):
            self.Parent.MoveOrCreate(triggeringObject = self, below = True)

    def OnDelete(self, *args):
        self.Parent.EnterDeleteMode()
        self.Item.grid_forget()
        confirm = ConfirmationFrame(self, self.DELETE_MESSAGE, self.OnDeleteCallback)
        confirm.grid(column=1, row=1, columnspan=3, sticky='nsew')

    def OnDeleteCallback(self, result):
        if (result):
            self.Parent.Remove(self)
        else:
            self.Item.grid(column=1, row=1, sticky='nsew')
        self.Parent.ExitDeleteMode()

    def SetIsLast(self, isLast: bool):
        self.IsLast.set(isLast)
        if self.Parent.ShowControls.get():
            if isLast:
                self.BottomInsert.grid(column=0, row=2, columnspan=3, sticky='nsew')
            else:
                self.BottomInsert.grid_forget()

    def OnShowControls(self, *args):
        show = self.ShowControls.get()
        if (show):
            self.TopInsert.grid(column=0, row=0, columnspan=3, sticky='nsew')
            if (not self.Parent.ShowControls.get()):
                self.BottomInsert.grid(column=0, row=2, columnspan=3, sticky='nsew')
            self.Delete.grid(column=0, row=1, sticky='nsew')
            self.Move.grid(column=2, row=1, sticky='nsew')
            self.SetIsLast(self.IsLast.get())
        else:
            self.TopInsert.grid_forget()
            self.BottomInsert.grid_forget()
            self.Delete.grid_forget()
            self.Move.grid_forget()

    def __init__(self, parent, constructor, args):
        KeystoneFrame.__init__(self, parent)
        
        self.Parent = parent

        #layout grid      
        self.columnconfigure(0, weight=0)      
        self.columnconfigure(1, weight=1)      
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        #init show controls vars
        self.ShowControls = tk.BooleanVar()
        self.ShowControls.set(False)
        self.ShowControls.trace("w", self.OnShowControls)
        self.IsLast = tk.BooleanVar()
        self.IsLast.set(False)

        #add controls
        self.TopInsert = tk.Button(self, text=self.INSERT_TEXT, background=self.INSERT_COLOR, foreground=self.INSERT_TEXT_COLOR, font=(TEXT_FONT, 7, "bold"), relief=self.INSERT_STYLE, height=1, pady=0, command=self.OnInsertAbove)
        self.BottomInsert = tk.Button(self, text=self.INSERT_TEXT, background=self.INSERT_COLOR, foreground=self.INSERT_TEXT_COLOR, font=(TEXT_FONT, 7, "bold"), relief=self.INSERT_STYLE, height=1, pady=0, command=self.OnInsertBelow)
        self.Delete = tk.Button(self, text=self.DELETE_TEXT, background=self.DELETE_COLOR, foreground=self.DELETE_TEXT_COLOR, font=(TEXT_FONT, 7, "bold"), relief=self.DELETE_STYLE, width=1, wraplength=1, command=self.OnDelete)
        self.Move = tk.Button(self, text=self.MOVE_TEXT, background=self.MOVE_COLOR, foreground=self.MOVE_TEXT_COLOR, font=(TEXT_FONT, 10, "bold"), relief=self.MOVE_STYLE, command=self.OnMove)
        if (args == None):
            self.Item = constructor(self)
        else:
            self.Item = constructor(self, args)
        self.Item.grid(column=1, row=1, sticky='nsew')

        #bind mouse controls
        self.MouseOver = False
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

        #bind Dirty if available
        if isinstance(self.Item, KeystoneEditFrame):
            self.Item.OnSetDirty.append(parent.SetDirty)

        self.OnShowControls()

    def _on_enter(self, event):
        self.MouseOver = True
        show = self.Parent.ShowControlsOnMouseOver.get() or self.Parent.ShowControls.get()
        if (self.ShowControls.get() != show):
            self.ShowControls.set(show)

    def _on_leave(self, event):
        self.MouseOver = False
        show = self.Parent.ShowControls.get()
        if (self.ShowControls.get() != show):
            self.ShowControls.set(show)
        

class FrameListView(KeystoneEditFrame):

    def __init__(self, parent, showControls = False, showControlsOnMouseOver = True):
        KeystoneEditFrame.__init__(self, parent)

        self.MovingObject = None
        self.Items = None
        self.Constructor = None
        self.DefaultArgs = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        #setup show controls vars
        self.ShowControls = tk.BooleanVar()
        self.ShowControls.set(showControls)
        self.ShowControls.trace("w", self.OnShowControls)

        self.ShowControlsOnMouseOver = tk.BooleanVar()
        self.ShowControlsOnMouseOver.set(showControlsOnMouseOver)

    def Load(self, constructor, args, defaultArgs):
        if (self.Items != None):
            for item in self.Items:
                item.grid_forget()
        self.Constructor = constructor
        self.DefaultArgs = defaultArgs
        self.Items = [FrameListViewItem(self, constructor, item) for item in args]
        for idx, item in enumerate(self.Items):
            item.grid(row=idx, column=0, sticky='nsew')
            self.rowconfigure(idx, weight=1)

        if (len(self.Items) > 0):
            self.Items[-1].SetIsLast(True)

        self.SetClean(self)

    def OnShowControls(self, *args):
        show = self.ShowControls.get()
        for item in self.Items:
            item.ShowControls.set(show)


    def EnterMoveMode(self, triggeringItem: FrameListViewItem):
        self.ShowControls.set(True)
        self.MovingObject = triggeringItem
        for item in self.Items:

            if (item != self.MovingObject):
                item.Move.configure(background='black')
                item.Move.configure(foreground='black')
                item.Move['state'] = tk.DISABLED
            else:
                item.Move.configure(background= FrameListViewItem.INSERT_COLOR)
                item.Move.configure(foreground=FrameListViewItem.INSERT_TEXT_COLOR)

            item.TopInsert.configure(background=FrameListViewItem.INSERT_TEXT_COLOR)
            item.TopInsert.configure(foreground=FrameListViewItem.INSERT_COLOR)

            item.BottomInsert.configure(background=FrameListViewItem.INSERT_TEXT_COLOR)
            item.BottomInsert.configure(foreground=FrameListViewItem.INSERT_COLOR)
            
            item.Delete.configure(background='black')
            item.Delete.configure(foreground='black')
            item.Delete['state'] = tk.DISABLED


    def EnterDeleteMode(self):
        for item in self.Items:

            item.Move.configure(background='black')
            item.Move.configure(foreground='black')
            item.Move['state'] = tk.DISABLED
            
            item.TopInsert.configure(background='black')
            item.TopInsert.configure(foreground='black')
            item.TopInsert['state'] = tk.DISABLED

            item.BottomInsert.configure(background='black')
            item.BottomInsert.configure(foreground='black')
            item.BottomInsert['state'] = tk.DISABLED

    def ExitMoveMode(self):
        self.ShowControls.set(False)

        self.MovingObject = None

        for item in self.Items:
            item.Move.configure(background=FrameListViewItem.MOVE_COLOR)
            item.Move.configure(foreground=FrameListViewItem.MOVE_TEXT_COLOR)
            item.Move['state'] = tk.NORMAL
            
            item.Delete.configure(background=FrameListViewItem.DELETE_COLOR)
            item.Delete.configure(foreground=FrameListViewItem.DELETE_TEXT_COLOR)
            item.Delete['state'] = tk.NORMAL

            item.TopInsert.configure(background=FrameListViewItem.INSERT_COLOR)
            item.TopInsert.configure(foreground=FrameListViewItem.INSERT_TEXT_COLOR)

            item.BottomInsert.configure(background=FrameListViewItem.INSERT_COLOR)
            item.BottomInsert.configure(foreground=FrameListViewItem.INSERT_TEXT_COLOR)

            item.SetIsLast(False)

        self.Items[-1].SetIsLast(True)

    def ExitDeleteMode(self):
        
        for item in self.Items:

            item.Move.configure(background=FrameListViewItem.MOVE_COLOR)
            item.Move.configure(foreground=FrameListViewItem.MOVE_TEXT_COLOR)
            item.Move['state'] = tk.NORMAL
            
            item.TopInsert.configure(background=FrameListViewItem.INSERT_COLOR)
            item.TopInsert.configure(foreground=FrameListViewItem.INSERT_TEXT_COLOR)
            item.TopInsert['state'] = tk.NORMAL

            item.BottomInsert.configure(background=FrameListViewItem.INSERT_COLOR)
            item.BottomInsert.configure(foreground=FrameListViewItem.INSERT_TEXT_COLOR)
            item.BottomInsert['state'] = tk.NORMAL

            item.SetIsLast(False)

        if (len(self.Items) == 0):
            self.MoveOrCreate(-1)
        
        self.Items[-1].SetIsLast(True)


    def MoveOrCreate(self, triggeringObject: FrameListViewItem, below: bool = False):

        create = False
        if (self.MovingObject == None):
            self.MovingObject = FrameListViewItem(self, self.Constructor, self.DefaultArgs)
            create = True

        #pass -1 to insert below last item
        if ((triggeringObject == -1) or (below and triggeringObject.IsLast.get())):
            triggeringIndex = -1
        else:
            for idx, item in enumerate(self.Items):
                if (item == triggeringObject):
                    triggeringIndex = idx
                    break

            if (below):
                triggeringIndex = triggeringIndex + 1

        if (not create):
            self.Remove(self.MovingObject)

        self.Insert(triggeringIndex, self.MovingObject)
        
        self.ExitMoveMode()

    def Remove(self, itemToRemove: FrameListViewItem):
        for idx, item in enumerate(self.Items):
            if (item == itemToRemove):
                index = idx
        for idx in range(index, len(self.Items)):
            self.Items[idx].grid_forget()
            self.rowconfigure(idx, weight=0)
        self.Items.remove(itemToRemove)
        for idx in range(index, len(self.Items)):
            self.Items[idx].grid(row=idx, column=0, sticky='nsew')
            self.rowconfigure(idx, weight=1)

        self.SetDirty()
        

    def Insert(self, index: int, itemToInsert: FrameListViewItem):
        if ((index < 0) or (index >= len(self.Items))):
            self.Items.append(itemToInsert)
            idx = len(self.Items) - 1
            self.Items[idx].grid(row=idx, column=0, sticky='nsew')
            self.rowconfigure(idx, weight=1)
        else:
            for idx in range(index, len(self.Items)):
                self.Items[idx].grid_forget()
                self.rowconfigure(idx, weight=0)
            self.Items.insert(index, itemToInsert)
            for idx in range(index, len(self.Items)):
                self.Items[idx].grid(row=idx, column=0, sticky='nsew')
                self.rowconfigure(idx, weight=1)

        self.SetDirty()



        
class TestFrame(KeystoneEditFrame):

    def __init__(self, parent, message):
        KeystoneEditFrame.__init__(self, parent)
        self.Text = tk.StringVar()
        self.Text.set(message)
        self.Edit = ttk.Entry(self, textvariable=self.Text)
        self.Text.trace("w", self.SetDirty)
        self.Edit.pack(fill=tk.BOTH, expand=1)



if (__name__ == "__main__"):
    win = tk.Tk()
    constructor = TestFrame
    args = ("1", "2", "3")
    view = FrameListView(win)
    view.Load(constructor, args, "X")
    view.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')

    tk.mainloop()