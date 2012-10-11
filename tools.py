def string_to_file( string, filename ):
        fh = open( filename, "w" )
        fh.write( string )
        fh.close()

def totcount( i ):
        x = "".join( i )
        return len( x )


