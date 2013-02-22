# -*- coding: cp1252 -*-
# ===============================
# author: Paulo Trigo Silva (PTS)
# since: DEC.2012
# version: v03
# ===============================
#
#_______________________________________________________________________________
# This represents an "interface" to deal with the "dataset"
#_______________________________________________________________________________



#_______________________________________________________________________________
import b_emailWrapper as mailWrapper
import os
#_______________________________________________________________________________



#_______________________________________________________________________________
#_______________________________________________________________________________
# Configuration Constants
_EMAIL_USER="amd.isel@gmail.com"
_PASSWORD=""
_GMAIL_SERVER="imap.gmail.com"
#_______________________________________________________________________________
#_______________________________________________________________________________
_DEFAULT_FILE_NAME_SUFFIX = None
_EMAIL_ID_SUFFIX  = _DEFAULT_FILE_NAME_SUFFIX
_FROM_SUFFIX      = "FROM"
_SUBJECT_SUFFIX   = _DEFAULT_FILE_NAME_SUFFIX
_BODY_SUFFIX      = _DEFAULT_FILE_NAME_SUFFIX
#_______________________________________________________________________________
#_______________________________________________________________________________
# a representation of the Dataset that provides a way to:
# - establish a connection to the dataset (i.e., connect to email server)
# - populate the dataset (i.e., download emails from mailboxes in email server)
# - get a representation of dataset (i.e., each class value and its individuals)
class Dataset( object ):
   def __init__( self ):
      self.email = None

      
   def connect( self, emailUser=_EMAIL_USER, password=_PASSWORD, host=_GMAIL_SERVER ):
      self.email = mailWrapper.MailAccess()
      return self.email.connect( emailUser, password, host )


   # populate the dataset with the emails downloaded
   # from the mailboxes defined in the "mailbox_list"
   def populateFrom( self, mailbox_list, searchMethod, *searchArgument ):
      emailComponent_list = [ ( mailWrapper.MailAccess.EMAIL_ID, _EMAIL_ID_SUFFIX ), \
                              ( mailWrapper.MailAccess.FROM    , _FROM_SUFFIX ), \
                              ( mailWrapper.MailAccess.SUBJECT , _SUBJECT_SUFFIX ), \
                              ( mailWrapper.MailAccess.BODY    , _BODY_SUFFIX ) ]
      # in gmail the "mailbox" is aka as "label"
      for mailbox in mailbox_list:
         print mailbox
         self.email.download( mailbox, emailComponent_list, searchMethod, *searchArgument )


   # get a representation of the dataset already in the local repository
   # (i.e., the emails that were already downloaded and classified in folders)
   # dataset is here represented as a hash table:
   # - key is a class name, i.e., the name of a folder within _DATASET_DIR_NAME
   # - value is a list with the name of each file () (with path) within that folder
   # The format is:
   # { className : [ fileName-1, fileName-2, ... ]
   def getRepresentation( self ):
      dataset = {}
      dataset_path = ( ".", mailWrapper._DATASET_FOLDER_NAME )
      dataset_path = os.path.join( *dataset_path )
      if not os.path.exists( dataset_path ): return dataset
      if not os.path.isdir( dataset_path ): return dataset
      classValue_list = os.listdir( dataset_path )
      # eliminate invisible folders (i.e., those that start with ".")
      classValue_list = [ c for c in classValue_list if c[0]<>'.' ]
      for classValue in classValue_list:
         classValue_path = ( dataset_path, classValue )
         classValue_path = os.path.join( *classValue_path )
         if not os.path.isdir( classValue_path ): continue
         instance_list = os.listdir( classValue_path )
         instance_list = [ os.path.join( classValue_path, c ) \
                           for c in instance_list if c[0]<>'.' ]
         dataset[ classValue ] = instance_list
      return dataset


   # create a mailbox (aka label, folder) in the email server)
   def createClassInMailServer( self, classValue_list ):
      self.__manipulateClassInMailServer( classValue_list, \
                                          mailWrapper.MailAccess.create_MAILBOX )


   # delete a mailbox (aka label, folder) in the email server)
   def deleteClassInMailServer( self, classValue_list ):
      self.__manipulateClassInMailServer( classValue_list, \
                                          mailWrapper.MailAccess.delete_MAILBOX )


   # private auxuliary method
   def __manipulateClassInMailServer( self, classValue_list, f_manipulation ):
      for classValue in classValue_list: f_manipulation( self.email, classValue )


   def disconnect( self ):
      if self.email: self.email.disconnect()


   #________
   @property
   def email( self ): return self.__email
   
   @email.setter
   def email( self, value ):
      assert isinstance( value, mailWrapper.MailAccess ) or not value, \
             "PTS | Dataset::email: mailWrapper.MailAccess expected!"
      self.__email = value
   
   @email.deleter
   def email( self ): self.__email = None



#_______________________________________________________________________________
#_______________________________________________________________________________
# some test cases
def test_populate():
   dataset = Dataset()
   if not dataset.connect(): return
   #mailbox_list = [ "INBOX", "[Gmail]/Drafts" ]
   mailbox_list = [ "INBOX" ]
   #dateSince = "12-Dec-2012"
   dateSince = mailWrapper.get_today()
   dataset.populateFrom( mailbox_list, \
                         mailWrapper.MailAccess.search_DATE_SINCE, dateSince )
   #dataset.populateFrom( mailbox_list, mailWrapper.MailAccess.search_ALL )
   # terminate interaction with (IMAP) mail server
   dataset.disconnect


def test_getRepresentation():
   dataset = Dataset()
   # get a representation of the dataset already in the local repository
   # (does not need to connect to the mail server)
   datasetRepresentation = dataset.getRepresentation()
   print datasetRepresentation


def test_createClassInMailServer():
   dataset = Dataset()
   if not dataset.connect(): return
   classValue_list = [ "H", "M", "L" ]
   dataset.createClassInMailServer( classValue_list )
   # terminate interaction with (IMAP) mail server
   dataset.disconnect
   print "created mailboxes in the email server: ",
   print classValue_list
   

def test_deleteClassInMailServer():
   dataset = Dataset()
   if not dataset.connect(): return
   classValue_list = [ "H", "M", "L" ]
   dataset.deleteClassInMailServer( classValue_list )
   # terminate interaction with (IMAP) mail server
   dataset.disconnect
   print "deleted mailboxes in the email server: ",
   print classValue_list


#_______________________________________________________________________________
#_______________________________________________________________________________
if __name__ == '__main__':
   print mailWrapper.email.__version__
   print
   test_populate()
   print
   test_getRepresentation()
   print
   test_createClassInMailServer()
   print
   test_deleteClassInMailServer()
   print 123

