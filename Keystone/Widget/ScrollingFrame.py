import tkinter as tk
from tkinter import ttk


#From https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
#Bind objects to scrollwindow
class ScrollingFrame(ttk.Frame):

    def __init__(self, parent):

        ttk.Frame.__init__(self, parent)

        scrollBarFrame = ttk.Frame(self)
        scrollBarFrame.pack(fill=tk.BOTH, expand=1)
        scrollBarFrame.columnconfigure(0, weight=1)
        scrollBarFrame.columnconfigure(1, weight=0)
        scrollBarFrame.rowconfigure(0, weight=1)
        scrollBarFrame.rowconfigure(1, weight=0)
        frameStyle = ttk.Style()
        frameStyle.configure('frameStyle.TFrame', background='black', border=0)
        scrollBarFrame.configure(style='frameStyle.TFrame')

        # creating a scrollbars
        self.xscrlbr = ttk.Scrollbar(scrollBarFrame, orient = 'horizontal')
        self.showx = False      
        self.yscrlbr = ttk.Scrollbar(scrollBarFrame)
        self.showy = False      
        # creating a canvas
        self.canv = tk.Canvas(scrollBarFrame)
        self.canv.config(relief = 'flat',
                         width = 800,
                         height = 400, bd = 0, 
                         bg='black',
                         highlightbackground='black',
                         xscrollcommand = self.xscrlbr.set,
                         yscrollcommand = self.yscrlbr.set)
        # placing a canvas into frame
        self.canv.grid(column = 0, row = 0, sticky='nsew', padx=0, pady=0)
        # accociating scrollbar comands to canvas scroling
        self.xscrlbr.config(command = self.canv.xview)
        self.yscrlbr.config(command = self.canv.yview)

        # creating a frame to inserto to canvas
        self.scrollwindow = ttk.Frame(scrollBarFrame)
        self.scrollwindow.configure(style='frameStyle.TFrame')

        self.canv_window = self.canv.create_window(0, 0, window = self.scrollwindow, anchor = 'nw')

        self.yscrlbr.lift(self.scrollwindow)        
        self.xscrlbr.lift(self.scrollwindow)
        self.bind('<Configure>', self._configure_window)  
        self.canv.bind_all("<Configure>", self._configure_window) 
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)

        return

    def _bound_to_mousewheel(self, event):
        self.canv.bind_all("<MouseWheel>", self._on_mousewheel)   

    def _unbound_to_mousewheel(self, event):
        self.canv.unbind_all("<MouseWheel>") 

    def _on_mousewheel(self, event):
        if (self.showy):
            self.canv.yview_scroll(int(-1*(event.delta/120)), "units")  

    def _configure_window(self, event):
        # update the scrollbars to match the size of the inner frame
        required_size = (self.scrollwindow.winfo_reqwidth(), self.scrollwindow.winfo_reqheight())
        actual_size = (self.canv.winfo_width(), self.canv.winfo_height())

        if (required_size[0] > actual_size[0]):
            if (not self.showx):
                self.xscrlbr.grid(column = 0, row = 1, sticky = 'ew', columnspan = 2, padx=0, pady=0)  
                self.showx = True 
        elif (self.showx):
            self.xscrlbr.grid_forget()
            self.showx = False

        if (required_size[1] > actual_size[1]):
            if (not self.showy):
                self.yscrlbr.grid(column = 1, row = 0, sticky = 'ns', padx=0, pady=0)   
                self.showy = True 
        elif (self.showy):
            self.yscrlbr.grid_forget()
            self.showy = False

        if (self.showx or self.showy):
            self.canv.config(scrollregion='0 0 %s %s' % required_size)

            if required_size[0] != actual_size[0]:
                # update the canvas's width to fit the inner frame
                self.canv.config(width = required_size[0])
            if required_size[1] != actual_size[1]:
                # update the canvas's width to fit the inner frame
                self.canv.config(height = required_size[1])
