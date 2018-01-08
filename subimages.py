#!/usr/bin/python3

import os
import numpy as np
from math import sqrt
from time import time
from queue import Queue
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageChops
from skimage.feature import match_template  # requires numpy, scipy, and six


MAX_WIDTH = 640
MAX_HEIGHT = 640
RMS_THRESHOLD = 50


class FindSubset:
    def __init__(self, master):
        self.master = master
        self.master.title('Find Subset Images')
        self.master.resizable(True, True)

        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(padx=5, pady=5)
        ttk.Label(self.main_frame, text='Search Directory:').grid(
            row=0, column=0, sticky='w')
        self.path_entry = ttk.Entry(self.main_frame, width=54)
        self.path_entry.insert(0, os.getcwd())
        self.path_entry.grid(row=1, column=0, sticky='w')
        self.browse_button = ttk.Button(self.main_frame, text='Browse...', command=self.browse_callback
                                        )
        self.browse_button.grid(row=1, column=1, sticky='w')

        self.search_button = ttk.Button(self.main_frame, text='Find Subset Images',
                                        )
        self.search_button.grid(row=2, column=0, columnspan=2)

        self.results_table = ttk.Treeview(self.main_frame, column=('subset'))
        self.results_table.heading('#0', text='Original Image')
        self.results_table.column('#0', width=200)
        self.results_table.heading('subset', text='Subset Image')
        self.results_table.column('subset', width=200)

        self.status_frame = ttk.Frame(self.master)
        self.status_frame.pack(fill=BOTH, expand=True)
        self.status_var = StringVar()
        self.status_label = ttk.Label(
            self.status_frame, textvariable=self.status_var)

        self.progress_var = DoubleVar()
        self.progressbar = ttk.Progressbar(self.status_frame)
        self.progressbar.config(mode='determinate',
                                variable=self.progress_var)

    def browse_callback(self):
        path = filedialog.askdirectory(initialdir=self.path_entry.get())
        self.path_entry.delete(0, END)
        self.path_entry.insert(0, path)


def main():
    root = Tk()
    FindSubset(root)
    root.mainloop()


if __name__ == "__main__":
    main()
