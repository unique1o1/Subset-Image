#!/usr/bin/python3

import os
import numpy as np
from math import sqrt
from time import time
from queue import Queue
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageChops
from skimage.feature import match_template

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
        self.path_entry.insert(0, '/home/unique/Documents/images')
        self.path_entry.grid(row=1, column=0, sticky='w')
        self.browse_button = ttk.Button(self.main_frame, text='Browse...', command=self.browse_callback
                                        )
        self.browse_button.grid(row=1, column=1, sticky='w')

        self.search_button = ttk.Button(self.main_frame, text='Find Subset Images', command=self.search_callback
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

    def search_callback(self):
        self.start_time = time()

        try:  # build list of all jpg image files in directory
            self.path = self.path_entry.get()
            images = list(entry for entry in os.listdir(
                self.path) if entry.endswith('.jpg'))
        except:
            messagebox.showerror(title='Invalid Directory',
                                 message='Invalid Search Directory:\n' + self.path)
            return

        if len(images) < 2:
            messagebox.showerror(title='Not Enough Images',
                                 message='Need at least 2 images to analyze.')
            return

        self.queue = Queue()  # queue of image pairs to process
        for i in images:
            for j in images:
                if i != j:
                    self.queue.put((i, j))

        self.results_table.grid_forget()  # clear previous results

        for item in self.results_table.get_children(''):
            self.results_table.delete(item)

        self.status_var.set('Beginning...')
        self.status_label.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.progressbar.config(value=0.0, maximum=self.queue.qsize())
        self.progressbar.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.browse_button.state(['disabled'])
        self.search_button.state(['disabled'])

        self.master.after(10, self.process_queue)

    def process_queue(self):              
        pair = self.queue.get()          
        orig_img = Image.open(os.path.join(self.path, pair[0]))
        temp_img = Image.open(os.path.join(self.path, pair[1]))
        
        # verify that template image is larger than the original            
        if (temp_img.size[0] < orig_img.size[0]) and (temp_img.size[1] < orig_img.size[1]):
            
            # determine if images need to be resized smaller       
            if (orig_img.size[0] > MAX_WIDTH) or (orig_img.size[1] > MAX_HEIGHT):         
                # calculate ratio for resizing
                ratio = min(MAX_WIDTH/float(orig_img.size[0]),
                            MAX_HEIGHT/float(orig_img.size[1]))
                
                # resize images based on ratio   
                orig_img = orig_img.resize((int(ratio*orig_img.size[0]),
                                            int(ratio*orig_img.size[1])),
                                           Image.ANTIALIAS)
                temp_img = temp_img.resize((int(ratio*temp_img.size[0]),
                                            int(ratio*temp_img.size[1])),
                                           Image.ANTIALIAS)
            else:
                ratio = 1 # no resize was required
                       
            orig_arr = np.array(orig_img.convert(mode = 'L'))
            temp_arr = np.array(temp_img.convert(mode = 'L'))
            
            match_arr = match_template(orig_arr, temp_arr)        
            match_loc = np.unravel_index(np.argmax(match_arr), match_arr.shape)
          
            if ratio != 1: # if images were resized, get originals and calculate corresponding match_loc
                match_loc = (int(match_loc[0]/ratio), int(match_loc[1]/ratio))               
                orig_img = Image.open(os.path.join(self.path, pair[0]))
                temp_img = Image.open(os.path.join(self.path, pair[1]))
    
            # get matching subsection from original image (using RGB mode)                          
            orig_sub_arr = np.array(orig_img)[match_loc[0]:match_loc[0] + temp_img.size[0],
                                                 match_loc[1]:match_loc[1] + temp_img.size[1]]
            orig_sub_img = Image.fromarray(orig_sub_arr, mode = 'RGB')           
           
            # calculate the root-mean-square difference between orig_sub_img and sub_img
            h_diff = ImageChops.difference(orig_sub_img, temp_img).histogram()
        
            sum_of_squares = sum(value * ((idx % 256) ** 2) for idx, value in enumerate(h_diff))
            rms = sqrt(sum_of_squares/float(temp_img.size[0]*temp_img.size[1]))
                       
            if RMS_THRESHOLD > rms: # add matches to table
                self.results_table.grid(row = 3,column = 0, columnspan = 2, padx = 5, pady = 5)
                self.results_table.insert('', 'end', str(self.progress_var.get()),text = pair[0])
                self.results_table.set(str(self.progress_var.get()), 'subset', pair[1])
                self.results_table.config(height = len(self.results_table.get_children('')))

        self.progressbar.step()   
        self.status_var.set('Analyzed {} vs {} - {} pairs remaining...'.format(pair[0], pair[1], self.queue.qsize()))            
        
        if not self.queue.empty():
            self.master.after(10, self.process_queue)
        else:
            self.progressbar.pack_forget()
            self.browse_button.state(['!disabled'])
            self.search_button.state(['!disabled'])             
            elapsed_time = time() - self.start_time
            self.status_var.set('Done - Elapsed Time: {0:.2f} seconds'.format(elapsed_time))


def main():
    root = Tk()
    FindSubset(root)
    root.mainloop()


if __name__ == "__main__":
    main()
