import e_dataset
import b_emailWrapper as mailWrapper
import credentials


def populate(mailbox_list =["Inbox"], dateSince = "12-Dec-2012" ):
   dataset = e_dataset.Dataset()
   if not dataset.connect(_EMAIL_USER,_PASSWORD,_GMAIL_SERVER): 
       print "Connection was not established. Check connection settings"
       return
   print "connection has been established"
   #mailbox_list = [ "INBOX", "[Gmail]/Drafts" ]
 
   #dateSince = mailWrapper.get_today()
   dateSince = "03-Feb-2012"
   dataset.populateFrom( mailbox_list, mailWrapper.MailAccess.search_DATE_SINCE, dateSince )
   #dataset.populateFrom( mailbox_list, mailWrapper.MailAccess.search_ALL )
   # terminate interaction with (IMAP) mail server
   dataset.disconnect


if __name__ == '__main__':
    populate(["Inbox"], "12-Dec-2012")
    
    
    print "end of line"
