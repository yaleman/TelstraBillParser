import os, re
from tools import *

from myservice import MyService

class BillFile():
        def __init__( self, filename ):
                self.filename = filename
                self.fh = open( filename, "U" )
                self.services = []
        
                #anything with a linetype of this type will be ignored
		self.ignoredlines = [ "2S  D", "2S  H", "2S02D", "2D  H", "2S10D" ]
		# linea
                self.lineparser = re.compile( "(?P<linetype>[A-Z]{6})(?P<account_name>[A-Z\s\.\-]{30})(?P<account_number>[0-9]{10})([\s]{8})(?P<filedate>[0-9]{6})(?P<service>[A-Z0-9\s\&]{10})[\s]{1,}(?P<line>.*)")
                self.header_parser = re.search( "HDR:(?P<filetype>[A-Z]{4})[\s]{1,}(?P<account_number>[0-9]{10})[\s]{1,}20(?P<filedate>[0-9]{6})(?P<remains>.*)", self.fh.readline().strip() )
                # parse_2S02V should find the plan's details in the service line
                self.parse_2S02V = re.compile( "[\s]{0,}(?P<plan>[A-Z0-9\$\-\/\s\.]{10,30})[\s]{0,}(?P<plandate>[0-9]{2} [A-Z]{3} TO [0-9]{2} [A-Z]{3})[\s]*(?P<exgst>[A-Z0-9\.\-]{4,})[\s]*([A-Z0-9\.\-]{4,})[\s]*(?P<gst>[A-Z0-9\.\-]{4,})[\s]*(?P<incgst>[A-Z0-9\.\-]{4,})" )
                # parse_plan_find_plan should find the plan within plan name
                self.parse_plan_find_plan = re.compile( "$([0-9]{1,})")
                # parse_service_type finds the service type, ignores the service number and should return the user
                self.parse_service_type = re.compile( "(?P<servicetype>[A-Z\s]*)[0-9]{8,}[\s]*USER: (?P<user>[A-Z0-9\.\s]*)")
                
                # parse 2S21V handles lines with voice calls
                self.parse_2S21V = re.compile( "[\/\(\)\-A-Z0-9\s\/\(\)\-]{46}[\s]*[0-9]*[\s]*[\/\(\)\-A-Z0-9\s\/\(\)\-]{5}[\s]*[\/\(\)\-A-Z0-9\s\/\(\)\-]{50}[\s]*([0-9]{0,} CALLS)[\s]*([0-9\,\.\-A-Z]*)" )

                #self.parse_2DTre = re.compile( "([A-Z0-9\s]{35,40}[\s]*[0-9]{10}[\s]*[0-9]*[\s]*2D  T[\s]*[\/\-\(\)\sA-Z0-9]*)\$([\,0-9\.\-]*)" )
		# something to do with 2S21V calls?
                self.parse_2DTre = re.compile( "[\s]*([A-Z0-9\s\-\(\)\/\&]*)[\s]*\$([\,0-9\.\-]*)" )
                self.errors = []
                self.parse_2S21V = re.compile( "[A-Z0-9\s\\\/\(\)\-]{142}[\s]*([0-9]{0,}[\s]*CALL)[S\s]*([0-9\,\.\-A-Z]*)" ) 
                
                self.services, self.billdetails, self.linetypes = self.dofile( )

        def parse_2DT( self, line ):
        # parse 2DT handles lines with voice calls
                stuff = self.parse_2DTre.search( line ).groups()
                foo = stuff[1].replace( ",", "" )
                if "GST FREE" in stuff[0] or "TOTAL FOR" in stuff[0]:
                        foo = round( float( foo ) * 1.1, 2 )
		elif line.strip().endswith( "$0.00" ) != True : 
			print "parse_2DT '{}'".format( line )
                return foo

        def dofile( self ):
                """ reads in the file and does magic """
                linetypes = []
                data_services = []
		data_services_hashtable = ()
                billdetails = ""
		lines = [ line for line in self.fh.read().split("\n") if line.strip() not in [ "", "EOF" ]]
                for line in lines:
			linestrip = line.strip()
                        res = self.lineparser.search( line )
                        if not res:
                                self.errors.append( "LINE-ERROR: %s" % line )
                        else:
                                #dline = res.groups()
                                linetype = res.group( 'linetype' )
                                serviceid = res.group( 'service' ).strip()
                                line_details = res.group( 'line' )
                                #if linetype not in linetypes:
                                	#linetypes.append( linetype )
                                if serviceid not in data_services_hashtable:
                                        data_services.append( MyService( serviceid ) )
					data_services_hashtable += ( serviceid, )
                                        #print "Adding service: %s" % serviceid
                                serviceindex = data_services.index( serviceid )
                                this_service = data_services[ serviceindex ]
                                       
                                if linetype == "RBMICA":
					if serviceid == "":
						billdetails += "{}\n".format( line_details )
					else:
						ld = line_details.strip()
						line_subtype = ld[:5]
						ld = ld[5:]
						# should ignore some lines
						if line_subtype == "2D10D" or line_subtype == "2S10V":
							this_service.mobiledata.append( ld.strip() )
						elif line_subtype in self.ignoredlines:
							this_service.ignoredlines.append( [ line_subtype, ld.strip() ] )
							continue
						# grabs the line where they tell you the total service charges
						elif line_subtype == "2D  T":
							ynv = self.parse_2DT( ld )
							if ynv != "" and ynv != 0.00 and str( ynv ) != "0.00":
								#print "before", ynv, this_service.mobile_data_ynv
								if this_service.mobile_data_ynv in [ "Y", "N" ]:
									this_service.mobile_data_ynv = ynv
								else:
									this_service.mobile_data_ynv += ynv
								#print "after ", ynv, this_service.mobile_data_ynv
								#print ''
	#                                                elif this_service.ismobiledata():
	 #                                                       this_service.mobile_data_ynv = "Y"
	  #                                              else:
	   #                                                     this_service.mobile_data_ynv = "N"
						# deal with total service charges
						elif line_subtype == "2S  T" and "TOTAL SERVICE CHARGES" in ld:
							this_service.total = ld.replace( "TOTAL SERVICE CHARGES", "" ).replace( "$", "" ).strip()
						# ignore lines which aren't the total service charges
						elif line_subtype == "2S  T":
							this_service.ignoredlines.append( [ line_subtype, ld.strip() ] )
						# national call costs, if they make phone calls
						elif line_subtype == "2S11V": 
							#print "National call"
							try:
								this_service.ndd_total = float( self.parse_2S21V.search( line ).groups()[1].replace( ",", "" ) )
							except:
								print line
						# idd voice charges
						elif line_subtype == "2S21V":
							
							try:
								foo = self.parse_2S21V.search( line ).groups()
								this_service.idd_total = foo[1].replace( ",", "" )
							except:
								print line
						# these lines should show charges and stuff
						elif line_subtype == "2S02V":
							# this is the plan?
							plandetails = self.parse_2S02V.search( ld )
							if plandetails:
								plan_date = plandetails.group( 'plandate' ).strip()
								plan_name = plandetails.group( 'plan' ).strip()
								plan_incgst = plandetails.group( 'incgst' ).strip()
								if plan_incgst.endswith( "CR" ):
									plan_incgst = "-%s" % plan_incgst[:-2]
								plan_exgst = plandetails.group( 'exgst' ).strip()
								if plan_exgst.endswith( "CR" ):
									plan_exgst = "-%s" % plan_exgst[:-2]
								planvalue = self.parse_plan_find_plan.search( plan_name )
								if planvalue:
									plan_guess = int( planvalue.groups()[0] )
								else:
									plan_guess = None
								this_service.planlines.append( { 'date':plan_date, 'name':plan_name, 'incgst':plan_incgst, 'exgst':plan_exgst,'guess':plan_guess})
							else:
								this_service.errors.append( "Unable to parse 2S02V: %s" % ld )
						#elif line_subtype == "2D10D" or line_subtype == "2S10V": # data


						elif line_subtype == "2D21D": # voice calls/international calls
							this_service.idd.append( ld.strip() )
						else:
							this_service.errors.append( "Dataline: %s" % line_details.strip() )
                                elif linetype == "RHMICA":
                                        header = line_details.strip()
                                        #this_service.set_header( header )
                                        pst = self.parse_service_type.search( header ) 
                                        if pst:
                                                this_service.user = pst.group( 'user' ).strip()
                                                this_service.servicetype = pst.group( 'servicetype' ).strip()
                                        else:
                                                this_service.servicetype = header.replace( this_service.serviceid, "" ).strip()
                                                this_service.user = header.replace( this_service.serviceid, "" ).replace( this_service.servicetype, "" ).replace( "USER:", "" ).strip()
 
                return data_services, billdetails, linetypes
        
        def dumperrors( self ):
                """ returns a string dump of the error lines to be dumped to a logfile """
                lines = ""
                for service in self.services:
                        for error in service.errors:
                                lines += "%s,%s\n" % (service.serviceid, error )
                #if lines == "":
                #       return "No Errors"
                self.dumperrors = lines
                return self.dumperrors  

        def dumpignored( self ):
                """ this returns a string dump of the ignored lines, so you can dump it to a logfile """
                lines = ""
                for service in self.services:
                        for linetype, line in service.ignoredlines:
                                lines += "%s: %s %s\n" % ( service.serviceid, linetype, line )
                return lines    


        def printservice( self, this_service ):
                printval = "Service type: {}".format( this_service.servicetype )
                printval += "\nService ID: %s" % this_service.serviceid
                printval += "\nService total cost: %s" % this_service.total
                printval += "\nPlan lines:"
                for plan in this_service.planlines:
                        printval += "\n%s" % str( plan )
                printval += "\n#Data lines: " 
                for dataline in this_service.datalines:
                        printval += "\n%s" % dataline
                printval += "\n#Ignored lines"
                for ignoredline in this_service.ignoredlines:
                        printval += "\n%s" % ignoredline
                printval += "\n#Errors:"
                for error in this_service.errors:
                        printval += "\n%s" % str( error )
                return printval

        def csvit( self ):
                """ outputs the csv file with all the service details on it """
                lines = '"Service","Description","Plan Inc","Plan Ext","NULL","NULL","NULL","User","Cost"\n'
                for service in self.services:
                        lines += self.serviceline( service )
                return lines
        
        def serviceline( self, ts ):
                """ this will be run for each service on the account, should return a csv-formatted line """
                retval = ""
                total_incgst = 0.00
                total_exgst = 0.00
                
                for line in ts.planlines:
                        # there might be multiple plan lines, have to add 'em up
                        if not line['guess']:
                                line['guess'] = " "
                        #retval += ",".join(  [ "\"+ts.serviceid+"\"", "\""+ts.servicetype+"\"", line['incgst'], line['exgst'], line['guess'] ] )+","
                        #retval += ",".join( [ "\""+line['name']+"\"", "\""+line['date']+"\"","\""+ts.user+"\"" ] )+"\n" 
                        total_incgst += float( line['incgst'] )
                        total_exgst += float( line['exgst'] )
                        
                
                data_idd = self.tftoyn( ts.isiddusage() )
                if data_idd == "Y" and ts.idd_total != 0.0:
                        data_idd = ts.idd_total
                        if ts.mobile_data_ynv in [ "N", "Y" ]:
                                ts.mobile_data_ynv = ts.idd_total
                        else:
                        #elif float( ts.mobile_data_ynv ) != 0.0:
                                ts.mobile_data_ynv += str( float( ts.mobile_data_ynv ) + float( ts.idd_total ) )
                
                if ts.ndd_total != 0.0:
                        if ts.mobile_data_ynv in [ "N", "Y" ]:
                                ts.mobile_data_ynv = ts.ndd_total
                        else:
				#print type( ts.mobile_data_ynv ), ts.mobile_data_ynv
				#print type( ts.ndd_total ), ts.ndd_total
                                ts.mobile_data_ynv += float( ts.ndd_total )
                #, data_idd     
                retval += '="%s","CALCULATED TOTAL",%s,%s," "," "," ","%s",%s\n' % ( ts.serviceid, total_incgst, total_exgst, ts.user, ts.mobile_data_ynv )
                return retval
        def tftoyn( self, value ):
                isdata = { 'True':'Y', 'False':'N' }
                return isdata[ str( value ) ]
                        
        def writefiles( self ):
                sourcefile = self.filename.replace( ".DAT", "" )
                string_to_file( "\n".join( self.errors ), sourcefile+"-errors.txt" )
                string_to_file( self.dumperrors(  ), sourcefile+"-dumperrors.txt" )
                string_to_file( self.csvit(  ), sourcefile+".csv" )
                string_to_file( self.dumpignored( ), sourcefile+"-ignored.txt" )


