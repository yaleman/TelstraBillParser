#!/usr/bin/python

#import sys
import re,os
from Tkinter import *
import tkMessageBox
import tkFileDialog
import tkFont
from tools import *

from controller import Controller



class TBillApp():
        """ this is the core of the application """
        def __init__(self, master=None):
                master.title("TBill")
                self.controller = Controller(master)

def main():
        root = Tk()
        app = TBillApp(root)
        root.mainloop()
        
if  __name__ == '__main__':
       # main()
	from billfile import BillFile
	billfile = BillFile( "RCP66516.DAT" )
	billfile.writefiles()

	
