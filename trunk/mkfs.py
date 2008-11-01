# A script to convert an entire directory to a C array, in the "romfs" format
import os, sys
import re
import struct

_crtline = '  '
_numdata = 0
_bytecnt = 0
# Line output function
def _add_data( data, outfile, moredata = True ):
  global _crtline, _numdata, _bytecnt
  _bytecnt = _bytecnt + 1
  if moredata:
    _crtline = _crtline + "0x%02X, " % data
  else:
    _crtline = _crtline + "0x%02X" % data    
  _numdata = _numdata + 1
  if _numdata == 16 or not moredata:
    outfile.write( _crtline + '\n' )
    _crtline = '  '
    _numdata = 0

# dirname - the directory where the web page is located. It is assumed that
#           the directory contains all the files required by the web page, and
#           nothing more
# outname - the name of the C output
# Returns True for OK, False for error
def mkfs( dirname, outname ):
  # Try to list the directory
  try:
    flist = os.listdir( dirname )
  except:
    print "Unable to list directory %s" % dirname
    return False

  # Then try to create the output files
  outfname = outname + ".h"
  try:
    outfile = file( outfname, "wb" )
  except:
    print "Unable to create output file"
    return False
  
  global _crtline, _numdata, _bytecnt
  _crtline = '  '
  _numdata = 0
  _bytecnt = 0
  # Generate headers
  outfile.write( "// Generated by mkfs.py\n// DO NOT MODIFY\n\n" )
  outfile.write( "#ifndef __%s_H__\n#define __%s_H__\n\n" % ( outname.upper(), outname.upper() ) )
  
  outfile.write( "const unsigned char %s_fs[] = \n{\n" % ( outname.lower() ) )
  
  # Process all files
  for fname in flist:
    # Get actual file name
    realname = os.path.join( dirname, fname )
    
    # Ensure it actually is a file
    if not os.path.isfile( realname ):
      print "Skipping %s ... (not a regular file)" % fname
      continue
      
    # Try to open and read the file
    try:
      crtfile = file( realname, "rb" )
      filedata = crtfile.read()
    except:
      outfile.close()
      os.remove( outfname )
      print "Unable to read %s" % fname    
      return False
        
    # Write name, size, id, numpars
    for c in fname:
      _add_data( ord( c ), outfile )
    _add_data( 0, outfile ) # ASCIIZ
    size_l = len( filedata ) & 0xFF
    size_h = ( len( filedata ) >> 8 ) & 0xFF
    _add_data( size_l, outfile )
    _add_data( size_h, outfile )
    # Then write the rest of the file
    for c in filedata:
      _add_data( ord( c ), outfile )
    
    # Report
    print "Encoded file %s (%d bytes)" % ( fname, len( filedata ) )
    
  # All done, write the final "0" (terminator)
  _add_data( 0, outfile, False )
  outfile.write( "};\n\n#endif\n" );
  outfile.close()
  print "Done, total size is %d bytes" % _bytecnt
  return True

if __name__ == "__main__":
  if len( sys.argv ) != 3:
    print "Usage: mkfs <dirname> <outname>"
    sys.exit( -2 )
    
  mkfs( sys.argv[ 1 ], sys.argv[ 2 ] )