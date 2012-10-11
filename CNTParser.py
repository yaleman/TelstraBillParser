import re, os
from tools import *


class CNTParser():
        def __init__( self, directory ):
                """ startup stuff """
		# relies on re, os
                self.directory = directory
                self.siteid = ""
                self.sitename = ""
                self.accounts = []
                
                self.linefinder = re.compile( "(?P<accname>[A-Z0-09\s]*),(?P<accnum>[0-9]*),([0-9A-Z]*),(?P<filedate>[0-9A-Z]*),(?P<filename>[A-Z0-9\.]*),(?P<billsystem>[A-Z0-9]*),\$[\s]*(?P<totinc>[0-9A-Z\.\-]*)[\s]*,\$[\s]*(?P<gst>[0-9A-Z\.\-]*)[\s]*,\$[\s]*(?P<adjustments>[0-9A-Z\.\-]*)[\s]*")
                self.filename = False
                for filename in os.listdir( directory ):
                        if filename.startswith( "CN" ) and filename.endswith( "CSV" ):
                                self.filename = filename
                                break
                if self.filename != False:
                        self.processfile()
                
        def crdr( self, item ):
                """ if it's got a CR amount, make it a negative """
                if item.endswith( "CR" ):
                        item = "-%s" % item[:-2]
                return item
        def processfile( self ):
                fh = open( self.directory+"\\"+self.filename, "U" )
                filecontents = fh.read().replace( "\r", "" )
                for line in filecontents.split( "\n" ):
                        #print "'%s'" % line
                        if line.startswith( "Site ID:" ):
                                self.siteid = line.replace( "Site ID: ", "" ).strip()
                        elif line.startswith( "Site Name:"):
                                self.sitename = line.replace( "Site Name: ", "" ).strip()
                        elif ".DAT" in line:
                                #print line 
                                res = self.linefinder.search( line )
                                if res:
                                        accname,accnum,otherid,filedate,filename,billsystem,incgst,gst,adjust = res.groups()
                                        otherid = otherid #to shut eclipse up
                                        incgst = self.crdr( incgst )
                                        gst = self.crdr( gst )
                                        adjust = self.crdr( adjust )
                                        self.accounts.append( { 'account_name':accname, 'account_number':accnum, 'filedate':filedate, 'filename':filename,'billsystem':billsystem,'total_incgst':incgst,'total_gst':gst,'total_adjustments':adjust} )
                #print "Site ID: %s" % self.siteid
                #print "Site Name: %s" % self.sitename
                #print "\n".join( [ str( account ) for account in self.accounts ]  )


