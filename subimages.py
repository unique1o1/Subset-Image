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


def main():
    root = Tk()
    FindSubset(root)
    root.mainloop()


if __name__ == "__main__":
    main()
