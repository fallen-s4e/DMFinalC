# -*- coding: utf-8 -*-
# The above encoding declaration is required and the file must be saved as UTF-8

import codecs
import os

# note the 'u' prefix
p = u"абвгдежзийкл"

# next line is commented because it did not work in Windows with my console chaset
#print p

with codecs.open( "test.txt", "wb", "utf-16" ) as f:   # or utf-8
    f.write( os.linesep )
    #f.write( p + u"\n" )
    f.write( p )
    f.write( os.linesep )
    #f.write( "\n" )
    f.write( u"AAA" )
    f.write( os.linesep )
    #f.write( "\n" )
    f.write( u"BBB" )
    f.write( os.linesep )
    #f.write( '' )
    #f.flush()

with codecs.open( "test.txt", "a", "utf-16" ) as f:   # or utf-8
    #f.write( os.linesep )
    #f.write( p + u"\n" )
    f.write( u'' )
    f.write( u'X' )
