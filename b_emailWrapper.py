# -*- coding: cp1252 -*-
# ===============================
# author: Paulo Trigo Silva (PTS)
# since: DEC.2012
# version: v03
# ===============================
#
#_______________________________________________________________________________
# Info about IMAP4
# IMAP4 = INTERNET MESSAGE ACCESS PROTOCOL - VERSION 4rev1
# cf., specification at:
# http://tools.ietf.org/html/rfc2060.html
#
# Each command returns a tuple: (type, [data, ...])
# where type is usually 'OK' or 'NO',
# and data is either the text from the command response,
# or mandated results from the command.
#
# Each data is either a string, or a tuple.
# If a tuple, then the first part is the header of the response,
# and the second part contains the data (ie: ‘literal’ value).
#_______________________________________________________________________________



#_______________________________________________________________________________
# the used modules
import imaplib
import getpass
import email
import os
import codecs
import locale
import datetime
#_______________________________________________________________________________



#_______________________________________________________________________________
# Configuration Constants
_EMAIL_USER="amd.isel@gmail.com"
#_EMAIL_USER="paulo.trigo@gmail.com"
_PASSWORD=""
_GMAIL_SERVER="imap.gmail.com"
#_______________________________________________________________________________
# charset encoding
_UTF8 = "utf-8"
_UTF16 = "utf-16"
_WINDOWS = "iso-8859-1"
_FILE_ENCODING = _WINDOWS #_UTF16 #_UTF8
#_______________________________________________________________________________
#_______________________________________________________________________________
# dataset folder name and file extension
_DATASET_FOLDER_NAME = "_dataset_emailClass"
_FILE_EXTENSION=".txt"
#_______________________________________________________________________________
#_______________________________________________________________________________
# the mail access (uses IMAP protocol)
class MailAccess( object ):
   EMAIL_ID = "EMAIL_ID"
   FROM = "FROM"
   SUBJECT = "SUBJECT"
   BODY = "BODY"

   def __init__( self ):
      self.connection = None

      
   def connect( self, emailUser=_EMAIL_USER, password=_PASSWORD, host=_GMAIL_SERVER ):
      print
      print "host: " + host
      print "user: " + emailUser
      result = True
      self.connection = imaplib.IMAP4_SSL( host )
      if password == "": password = getpass.getpass( "pwd?: " )
      try: self.connection.login( emailUser, password )
      except Exception:
         result = False
         print ">> invalid credentials!"
      return result


   def get_allMailboxes( self ):
      ( result, data ) = self.connection.list( pattern="*" )
      if result.lower() <> "ok": return None
      return data

      
   def select_MAILBOX( self, mailboxName ):
      return self.connection.select( mailbox=mailboxName, readonly=True )


   def create_MAILBOX( self, mailboxName ):
      self.connection.create( mailboxName )


   def delete_MAILBOX( self, mailboxName ):
      self.connection.delete( mailboxName )

      
   def copy_emailToMAILBOX( self, email_ID, mailboxName ):
      self.connection.copy( email_ID, mailboxName )


   # get a list of email_IDs that satisfy the "f_searchMethod" and "*searchArguments"
   # "f_searchMethod" can be:
   # - MailAccess.search_ALL
   # - MailAccess.search_SUBJECT
   # - MailAccess.search_DATE_SINCE
   # or other functions that one implements
   # "*searchArguments" are the arguments for each "f_searchMethod"
   def get_email_ID_list( self, mailboxName, f_searchMethod, *searchArguments ):
      ( result, data ) = self.select_MAILBOX( mailboxName )
      ( result, data ) = f_searchMethod( self, *searchArguments )
      email_ID_list = data[ 0 ].split()
      return email_ID_list
   

   def search_ALL( self ):
      searchStatement = "(ALL)"
      return self.connection.search( None, searchStatement )

   
   def search_SUBJECT( self, str_keywords ):
      searchStatement = "(ALL SUBJECT \"%s\")" % str_keywords
      return self.connection.search( None, searchStatement )


   def search_DATE_SINCE( self, str_DD_MM_YYYY ):
      searchStatement = "(SINCE \"%s\")" % str_DD_MM_YYYY
      return self.connection.search( None, searchStatement )


   def fetch( self, email_ID ):
      fetchStatement = "(RFC822)"
      return self.connection.fetch( email_ID, fetchStatement )


   def fetch_list( self, email_ID_list ):
      for email_ID in email_ID_list:
         self.get_emailFromID( email_ID )


   def get_emailFromID( self, email_ID ):
      #print email_ID
      ( result, data ) = self.fetch( email_ID )
      email_raw = data[ 0 ][ 1 ]
      message = MailMessage( email_raw )
      # the email items that we want to get
      #____________________________________
      #
      # "from_addr" is a tuple as follows:
      # (user-name, email-address)
      from_addr = message.get_from()
      #print from_addr

      # "subject" is a (unicode) string
      subject = message.get_subject()
      #print subject

      # "body" is a list
      # (each element is a unicode string)
      body = message.get_body()
      #for e in body: print e
      #____________________________________
      result = { self.EMAIL_ID: email_ID, \
                 self.FROM:     from_addr, \
                 self.SUBJECT:  subject, \
                 self.BODY:     body }
      return result


   def download( self, mailbox, emailComponentAndSuffix_list, f_searchMethod, *searchArguments ):
      ( result, data ) = self.select_MAILBOX( mailbox )
      #print 'result: %s | #messages: %s = %d' % ( result, mailbox, int( data[ 0 ] ) )
      ( result, data ) = f_searchMethod( self, *searchArguments )
      #print ( result, data )
      email_ID_list = data[ 0 ].split()
      for email_ID in email_ID_list:
         email = self.get_emailFromID( email_ID )
         fileName = create_fileNameFullPath( mailbox, email_ID )
         pprint( email, emailComponentAndSuffix_list, fileName=fileName )
      

   def disconnect( self ):
      if self.connection: self.connection.logout()


   #________
   @property
   def connection( self ): return self.__connection
   
   @connection.setter
   def connection( self, value ):
      connectionType = imaplib.IMAP4 # imaplib.IMAP4_SSL
      assert isinstance( value, imaplib.IMAP4_SSL ) or not value, \
             "PTS | MailAccess::connection: IMAP4 expected!"
      self.__connection = value
   
   @connection.deleter
   def connection( self ): self.__connection = None


#_______________________________________________________________________________
#_______________________________________________________________________________
# the mail message (uses IMAP protocol)
class MailMessage( object ):
   __TEXT_PLAIN = "text/plain"
   __FROM = "From"
   __SUBJECT = "Subject"

   def __init__( self, email_str ):
      # see the "message" @property decorator (bellow)
      # (to better understand this assigment)
      self.message = email_str


   def get_from( self ):
      from_message = self.message.get( self.__FROM, None )
      if not from_message: return None
      from_addr = email.utils.parseaddr( from_message )
      # leave off the name and only return the address
      return from_addr[ 1 ]

      
   def get_subject( self ):
      subject_message = self.message.get( self.__SUBJECT, None )
      if not subject_message: return None
      decoded_header = email.Header.decode_header( subject_message )
      subject = []
      for decoded_string, charset in decoded_header:
         if charset: decoded_string = to_unicode( decoded_string, charset )
         subject.append( decoded_string )
      subject = ''.join( subject )
      return subject


   # cf., http://docs.python.org/2.7/library/email.message.html:
   # "Message objects can also optionally contain two instance attributes,
   #  which can be used when generating the plain text of a MIME message."
   #
   # PTS: the above statement causes a problem in the recursion termination:
   # PTS: - if a multipart message is duplicated the recusrion doesn't terminate
   # PTS: - and gmail makes such duplication of "multipart message"
   # PTS: to overome the termination problem recursion must:
   # PTS  - discard duplicates (DD)
   # PTS: (which complicates the solution)
   def get_body( self ):
      return self.__get_body_DD( self.message, None )


   # DD means: Discard Duplicates (i.e., multipart messages wihtin each other)
   # duplicates are only discarded between adjacent recursion levels
   # i.e., a multipart message that originates a descendning recursion level
   # can not occur in its descending level (otherwise, recursion wouldn't terminate)
   def __get_body_DD( self, email_message, possibleDuplicate ):
      # discard the duplicated message (contained within a multipart recursion)
      if email_message == possibleDuplicate: return None
      # the case of a non-multipart message
      if not email_message.is_multipart():
         body = email_message.get_payload( decode=True )
         body_unicode = self.__get_body_unicode( email_message, body )
         if body_unicode: return [ body_unicode ]
      # the case of a multipart message
      result = []
      for part in email_message.walk():
         # the recursion step
         # (passes the multipart message, "email_message", that originates recursion)
         body_unicode = self.__get_body_DD( part, email_message )
         if body_unicode: result += body_unicode
      return result


   def __get_body_unicode( self, part, body ):
      content_type = part.get_content_type()
      if content_type <> self.__TEXT_PLAIN: return None
      content_charset = part.get_content_charset()
      body_unicode = to_unicode( body, content_charset )
      return body_unicode


   #________
   @property
   def message( self ): return self.__message
   
   @message.setter
   def message( self, value ):
      assert isinstance( value, str ), "PTS | MailMessage::message: str expected!"
      self.__message = email.message_from_string( value )
   
   @message.deleter
   def message( self ): self.__message = None



#_______________________________________________________________________________
#_______________________________________________________________________________
# utility functions

# convert string to unicode format
def to_unicode( obj, charset=_UTF16 ):
   if not obj: obj = ""
   if isinstance( obj, basestring ):
      if not isinstance( obj, unicode ):
         # try to transform to unicode using the "encoding"
         # if the above falis try the _UTF16 (defined in the top of this file)
         # if the above falis try the _UTF8 (defined in the top of this file)
         # if the above falis try the _WINDOWS (defined in the top of this file)
         try: obj = unicode( obj, charset )
         except Exception:
            try: obj = unicode( obj, _UTF16 )
            except Exception:
               try: obj = unicode( obj, _UTF8 )
               except Exception:
                  try: obj = unicode( obj, _WINDOWS )
                  except Exception: print ">> PTS >> problem with unicode convertion!"
   return obj


# the "pretty print" function that registers each email into a file
# the name of each file has the format:
# emailID_suffix.txt
# the "suffix" is provided in the "emailComponentAndSuffix_list"
def pprint( email, emailComponentAndSuffix_list, fileName=None ):
   suffix_list = [ s for ( _, s ) in emailComponentAndSuffix_list if s ]
   if fileName: remove_fileNameSet( suffix_list, fileName )
   separator = 70*"="
   if not fileName: pprint_streamOUT( separator )
   for ( emailComponent, suffix ) in emailComponentAndSuffix_list:
      fileNameComplete = get_fileNameComplete( fileName, suffix )
      pprint_hashTable( email, emailComponent, fileNameComplete )
   if not fileName: pprint_streamOUT( separator )

  
def pprint_hashTable( hashTable, emailComponent, fileName=None ):
   value = hashTable.get( emailComponent, None )
   if not value: return
   if not fileName:
      pprint_streamOUT( len( emailComponent )*"_" )
      pprint_streamOUT( emailComponent + ":" )
   # now the info that may also be written in a file
   if isinstance( value, str ):
      pprint_streamOUT( value, fileName )
   if isinstance( value, tuple ) or \
      isinstance( value, list ):
      total_v = ""
      for v in value: total_v = total_v + v
      pprint_streamOUT( total_v, fileName )


def pprint_streamOUT( text, fileName=None ):
   # print to stdout
   if not fileName:
      print text
      return
   fileAlreadyExists = os.path.exists( fileName )
   # write to fileName
##   with open( fileName, 'ab' ) as f:
##      f.write( text.encode( _FILE_ENCODING, "replace" ) )
   with codecs.open( fileName, 'ab',  _UTF16 ) as f:
      # add a newline separator (depends on the operating system)
      if fileAlreadyExists: f.write( os.linesep )
      f.write( text )
   if not fileAlreadyExists:
      print ">> file created: '%s'" % fileName


def remove_fileNameSet( suffix_list, fileName ):
   if not fileName: return
   fileNameComplete = get_fileNameComplete( fileName, None )
   remove_fileName( fileNameComplete )
   for suffix in suffix_list:
      fileNameComplete = get_fileNameComplete( fileName, suffix )
      remove_fileName( fileNameComplete )


def remove_fileName( fileName ):
   try: os.remove( fileName )
   except OSError: print ">> file does not exist yet: '%s'" % fileName


def create_fileNameFullPath( mailbox, fileName ):
   fileName = str( fileName )
   fullPath = ( ".", _DATASET_FOLDER_NAME, mailbox )
   fullPath = os.path.join( *fullPath )
   if not os.path.exists( fullPath ): os.makedirs( fullPath )
   fileNameFullPath = ( fullPath, fileName )
   fileNameFullPath = os.path.join( *fileNameFullPath )
   return fileNameFullPath


def get_fileNameComplete( fileName, suffix ):
   if not fileName: return None
   ending = ""
   if suffix: ending = "_" + suffix
   return fileName + ending + _FILE_EXTENSION


# get the "today string" with the
# correct (IMAP) format: "DD-MMM-YYYY", e.g., "18-Dec-2012"
def get_today():
   # get current locale
   currentLocale = locale.getlocale()
   # "C" is the defualt locale for any program
   # but, just in case, make sure that we are using "C" locale
   locale.setlocale( locale.LC_TIME, "C" )
   today = datetime.date.today()
   # format date according to email protocol (IMAP)
   today = today.strftime( "%d-%b-%Y" )
   
   # restore saved locale
   locale.setlocale( locale.LC_ALL, currentLocale )
   #print today
   return today



#_______________________________________________________________________________
#_______________________________________________________________________________
def main():
   #print email.__version__
   myMail = MailAccess()
   if not myMail.connect(): return
   allMailboxes = myMail.get_allMailboxes()
   print allMailboxes
   print
#_______________________________________________________________________________
#_______________________________________________________________________________
if __name__ == '__main__':
   main()







   
