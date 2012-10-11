import os, re
from tools import *

class MyService( object ):
        def __init__(self, serviceid ):
                """ this should hold the details of a service """
                self.serviceid = serviceid
                self.header = ""
                self.datalines = []
                self.ignoredlines = []
                self.total = ""
                self.servicetype = ""
                self.planlines = []
                self.errors = []
                self.mobiledata = []
                self.mobile_data_total = 0.0
                self.mobile_data_ynv = "N"
                self.idd = []
                self.idd_total = ""
                self.ndd_total = 0.0
                self.user = ""
        def __eq__( self, otherserviceid ):
                if self.serviceid == otherserviceid:
                        return True
                return False
        def __lt__( self, otherserviceid ):
                if self.serviceid < otherserviceid:
                        return True
                return False
        def ismobiledata( self ):
                """ if there's lines in the mobiledata variable, it means there was usage """
                if len( self.mobiledata ) > 0:
                        return True
                return False
        def isiddusage( self ):
                if len( self.idd ) > 0:
                        return True
                return False
        
        def set_header( self, string ):
                """ sets the header string for the service """
                self.header = string
        def set_servicetype(self, string):
                """ sets the service type for the service, expects a string """
                self.servicetype = string



