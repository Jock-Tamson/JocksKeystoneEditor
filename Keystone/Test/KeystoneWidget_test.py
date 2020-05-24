import os
import inspect
import tkinter as tk
import unittest
from tkinter import ttk

from Keystone.Widget.KeystoneEditFrame import KeystoneEditFrame
from Keystone.Widget.FrameListView import FrameListView, FrameListViewItem

      
class TestFrame(KeystoneEditFrame):

    def __init__(self, parent, message):
        KeystoneEditFrame.__init__(self, parent)
        self.Text = tk.StringVar()
        self.Text.set(message)
        self.Edit = ttk.Entry(self, textvariable=self.Text)
        self.Text.trace("w", self.SetDirty)
        self.Edit.pack(fill=tk.BOTH, expand=1)

class TestFrameListView(unittest.TestCase):    

    def test_FrameListView(self):
        win = tk.Tk()
        constructor = TestFrame
        args = ("1", "2", "3")
        view = FrameListView(win)
        view.Load(constructor, args, "X")
        view.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')  

        #tk.mainloop()
        win.destroy()

    def test_FrameListViewMoves(self):
        win = tk.Tk()
        constructor = TestFrame
        args = ("1", "2", "3")
        view = FrameListView(win)
        view.Load(constructor, args, "X")
        view.pack(anchor='n', fill=tk.BOTH, expand=True, side='left')
        view.Insert(2, FrameListViewItem(view, TestFrame, "A"))
        view.Insert(3, FrameListViewItem(view, TestFrame, "B"))
        view.Insert(4, FrameListViewItem(view, TestFrame, "C"))
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', 'A', 'B', 'C', '3']
        self.assertEqual(str(actual), str(expected), "Insert of items mid list failed")
        view.MovingObject = view.Items[2]
        view.MoveOrCreate(view.Items[0])
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['A', '1', '2', 'B', 'C', '3']
        self.assertEqual(str(actual), str(expected), "Move of item to start of list failed")
        view.MovingObject = view.Items[0]
        view.MoveOrCreate(view.Items[5])
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', 'B', 'C', 'A', '3']
        self.assertEqual(str(actual), str(expected), "Move of item to before end of list failed")
        view.MovingObject = view.Items[4]
        view.MoveOrCreate(view.Items[5], True)
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', 'B', 'C', '3', 'A']
        self.assertEqual(str(actual), str(expected), "Move of item to end of list failed")
        view.MovingObject = view.Items[-1]
        view.MoveOrCreate(view.Items[4])
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', 'B', 'C', 'A', '3']
        self.assertEqual(str(actual), str(expected), "Move of item to middle of list failed")
        view.MovingObject = None
        view.MoveOrCreate(view.Items[-1], True)
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', 'B', 'C', 'A', '3', 'X']
        self.assertEqual(str(actual), str(expected), "Add of item to end of list failed")
        view.Remove(view.Items[-1])
        view.Remove(view.Items[4])
        view.Remove(view.Items[3])
        view.Remove(view.Items[2])
        actual = [item.Item.Text.get() for item in view.Items]
        expected = ['1', '2', '3']
        self.assertEqual(str(actual), str(expected), "Removing items failed")
        win.destroy()