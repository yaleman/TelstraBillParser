import re,os
from tools import *
from Tkinter import *
import tkMessageBox
import tkFileDialog
import tkFont
from CNTParser import CNTParser
from billfile import BillFile

class Controller( Frame ):
        def __init__(self, parent ):
                """ starter code for the Controller class, which does all the pretties
                """
                Frame.__init__( self, parent, width=80, height=50 )
                self._parent = parent
                self.ACC_FORMAT = "{0:<15}{1:<12}{2:<35}{3:>12}{4:>12}{5:>12}"
                self.parsedir = ""
                #self.parsedir = "./telstra/"
                #self.cntfile = CNTParser( self.parsedir )
                self.cntfile = False
                #for account in self.cntfile.accounts:
                #       print account
                        #bill = BillFile( account['filename'] )
                        #bill.writefiles()
                self.createWidgets()
                self.bills = []

                self.dir_opt = options = {}
                #options['initialdir'] = 'D:\\'
                options['mustexist'] = False
                options['parent'] = self
                options['title'] = 'Please select the data directory...'

        def openFolder( self ):
                """ dialogue box and file opener for the data files """
                newfolder = tkFileDialog.askdirectory(**self.dir_opt)
                if os.path.exists( newfolder ):
                        self.parsedir = newfolder
                        self.cntfile = CNTParser( self.parsedir )
                        self.updatelist()
        
        def createWidgets( self ):
                """ this does the heavy lifting of creating the user interface
                """
                self.font = tkFont.Font( family="Courier", size=12 )
                Label( text= self.ACC_FORMAT.format( "Filename", "Account #", "Account Name", "Total Inc.", "Gst Amount","Adjustments" ), font=self.font).pack()
                self.filebox = Listbox( width=100, font=self.font )
                #FRIENDS_FORMAT = "{0:<20}{1:<50}{2:<12}{3:<10}"
                #return FRIENDS_FORMAT.format( self.name, self.address, self.phone, sbirth )
                self.updatelist()
                self.filebox.pack( )
                Button( text='Open Datafiles', command=self.openFolder ).pack()
                Button( text='Process File', command=self.processfile ).pack()
                Button( text='Dump Readable File', command=self.dumpreadable ).pack()
                Button( text='Update List', command=self.updatelist ).pack()
                
        
        def updatelist( self ):
                """ refreshes the screen on command
                """
                self.filebox.delete( 0, END )
                #self.filebox.insert( END, self.ACC_FORMAT.format( "Filename", "Account #", "Account Name", "Total Inc.", "Gst Amount","Adjustments" ))
                if self.cntfile:
                        for account in self.cntfile.accounts:
                                stracc = self.ACC_FORMAT.format( account['filename'], account['account_number'], account['account_name'], account['total_incgst'], account['total_gst'], account['total_adjustments'] )
                                self.filebox.insert( END, stracc )
                                #self.filebox.insert( END, "%s %s" % ( account['account_number'], account['account_name'] ) )
        def getselection( self ):
                """ returns what's selected """
                selection = self.filebox.curselection()
                if selection == ():
                        tkMessageBox.showerror("Whoops!", "No line selected")
                else:
                        fileselection = self.filebox.get( selection )
                        return fileselection
        def getfilenamefromselection( self ):
                """ returns the filename of whatever's selected in the interface """
                tmp = self.getselection()
                return tmp.split( " " )[0].strip()
        
        def dumpreadable( self ):
                """ this dumps a raw semi-readable file for users to peruse if need be."""
                filename = self.getfilenamefromselection( )
                fh = open( self.parsedir+"/"+filename, "U" )
                newfile = "\r\n".join( [ line[60:] for line in fh.read().split( "\n" ) ] )
                fh.close()
                newfilename = filename.replace( ".", "-readable." )
                newfilename = newfilename.replace( 'DAT', 'txt' )
                fh = open( self.parsedir+'/'+newfilename,'w' )
                fh.write( newfile )
                fh.close
                self.filebox.insert( END, "Dumped readable file {0}".format( newfilename ) ) 
        
        def processfile( self ):
                """ this does the processing out to the final csv """
                filename = self.getfilenamefromselection()
        
                self.filebox.insert( END, "Processing file: %s" % filename )
                billfile = BillFile( self.parsedir + "/" + filename )
                billfile.writefiles()
                self.bills.append( billfile )
                self.filebox.insert( END, "Completed processing file %s" % filename )
                        

