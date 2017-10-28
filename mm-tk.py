import Tkinter as Tk
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk

import json
from pprint import pprint
import os

class Model():
    def __init__(self):
        pass

class View():
    def __init__(self, master):
        self.frame = Tk.Frame(master, width=200, height=100)
        self.frame.pack(side=Tk.LEFT, fill=Tk.BOTH)
        self.sidepanel = SidePanel(master)

        self.background = ImageTk.PhotoImage(Image.open("assets/body_outline.jpg"))
        self.canvas = Tk.Canvas(self.frame, width=600, height=722, bg='black')
        self.canvas.pack(side=Tk.TOP, fill=Tk.BOTH)
        self.canvas.create_image(0, 0, image=self.background, anchor=Tk.NW)

class SidePanel():
    def __init__(self, root):
        self.panel = Tk.Frame(root)
        self.panel.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=1)

        self.clearBtn = Tk.Button(self.panel, text='Clear')
        self.clearBtn.pack(side='top', fill=Tk.BOTH)
        self.openBtn = Tk.Button(self.panel, text='Open file ...')
        self.openBtn.pack(side='top', fill=Tk.BOTH)
        self.saveBtn = Tk.Button(self.panel, text='Save')
        self.saveBtn.pack(side='top', fill=Tk.BOTH)

        self.quitBtn = Tk.Button(self.panel,
                                 text="Quit",
                                 fg="red")
        self.quitBtn.pack(side='top', fill=Tk.BOTH)

class Controller():

    VERSION = '0.1.0'

    def __init__(self):
        self.points = list()
        self.fdir  = os.path.expanduser('~')
        self.fname = 'molemap.mma'
        self.need_save = False

        self.root = Tk.Tk()
        self.model = Model()
        self.view = View(self.root)
        self.view.sidepanel.clearBtn.bind('<Button>', self.clear_state)
        self.view.sidepanel.openBtn.bind('<Button>', self.show_file_open)
        self.view.sidepanel.saveBtn.bind('<Button>', self.show_file_save)
        self.view.sidepanel.quitBtn.bind('<Button>', self.confirm_quit)
        self.view.canvas.bind('<Button-1>', self.state_add_spot)
        self.view.canvas.bind('<Button-3>', self.state_del_spot)

    def run(self):
        self.root.title("MoleAid")
        self.root.deiconify()
        self.root.mainloop()

    def load_state(self, fname):
        with open(fname) as fh:
            d = json.load(fh)
            if d['points']:
                self.points = d['points']
                pprint(d)
                self.fdir  = os.path.dirname(fname)
                self.fname = os.path.basename(fname)
                self.canvas_clear()
                self.canvas_draw_all_points(self.points)

    def clear_state(self, event):
        self.points = list()
        self.canvas_clear()
        self.need_save = False

    def save_state(self, fname):
        with open(fname, 'w') as fh:
            json.dump({ 'points': self.points, 'version': self.VERSION }, fh)
            self.fdir  = os.path.dirname(fname)
            self.fname = os.path.basename(fname)

    def show_file_open(self, event):
        fname = tkFileDialog.askopenfilename(initialdir=self.fdir,
                                             title="Select patient folder",
                                             initialfile=self.fname,
                                             filetypes=(("MoleMap files", "*.mma"),
                                                        ("All files", "*.*") ))
        if fname:
            print fname
            self.load_state(fname)
        return "break"

    def show_file_save(self, event):
        fname = tkFileDialog.asksaveasfilename(initialdir=self.fdir,
                                               title="Select patient folder",
                                               initialfile=self.fname,
                                               filetypes=(("MoleMap files", "*.mma"),
                                                          ("All files", "*.*") ))
        if fname:
            self.save_state(fname)
        return "break"

    def confirm_quit(self, event):
        if self.need_save:
            self.show_file_save(event)
            self.root.destroy()

        elif tkMessageBox.askokcancel("Quit?", "Do you really wish to quit?"):
            self.root.destroy()

    def canvas_draw_all_points(self, points):
        for coord in points:
            self.canvas_add_spot(coord)

    def canvas_clear(self):
        self.view.canvas.delete('item')

    def canvas_del_spot(self, idx):
        t = self.view.canvas.find_withtag('text_%d' % idx)
        s = self.view.canvas.find_withtag('spot_%d' % idx)
        self.view.canvas.delete(t)
        self.view.canvas.delete(s)

    def canvas_add_spot(self, coord):
        idx = coord['idx']
        x = coord['x']
        y = coord['y']
        self.view.canvas.create_oval(x - 5, y -5, x + 5, y + 5, outline='red', fill='red', tags=('item', 'spot_%d' % idx))
        self.view.canvas.create_text(x, y - 12, fill='red', text=idx, tags=('item', 'text_%d' % idx))

    def state_add_spot(self, event):
        idx = len(self.points) + 1
        coord = {'idx':idx, 'x':event.x, 'y':event.y}
        self.points.append(coord)
        self.canvas_add_spot(coord)
        self.need_save = True


    def state_del_spot(self, event):
        if len(self.points) > 0:
            self.canvas_del_spot(len(self.points))
            self.points.pop()
            self.need_save = True


if __name__ == '__main__':
    c = Controller()
    c.run()

