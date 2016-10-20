#!/usr/bin/python
 
import urllib2
import cookielib
from getpass import getpass
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import logging

''' 
username = raw_input("Enter Username: ")
passwd = getpass()
message = raw_input("Enter Message: ")
number = raw_input("Enter Mobile number:")
'''

class sms:
#    username = "9840873901"
#    passwd = "boffin"
#    message = "hello"
#    number = "9884067041"
#    message = "+".join(message.split(' '))

    def __init__(self, username, passwd):
        self.logger = logging.getLogger("iMonitor.message.sms")
        self.username = username
        self.passwd = passwd


    def sendMany(self, numbers, message):
        for number in numbers.split(","):
            self.send(number, message)


    def send(self, number, message):
        self.logger.info("Sending sms to %s", number)
        message = "+".join(message.split(' '))
        #Logging into the SMS Site
        url = 'http://site24.way2sms.com/Login1.action?'
        data = 'username='+self.username+'&password='+self.passwd+'&Submit=Sign+in'
 
        #For Cookies:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
 
        # Adding Header detail:
        opener.addheaders = [('User-Agent',
               'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36')]
 
        try:
            usock = opener.open(url, data)
        except IOError:
            self.logger.error("Error while logging (username: %s) for sending sms", username)
            print "Error while logging in."
            return False
 
        session_id = str(cj).split('~')[1].split(' ')[0]
        send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
        send_sms_data = 'ssaction=ss&Token='+session_id+'&mobile='+number+'&message='+message+'&msgLen=136'
        opener.addheaders = [('Referer', 'http://site25.way2sms.com/sendSMS?Token='+session_id)]
 
        try:
            sms_sent_page = opener.open(send_sms_url,send_sms_data)
        except IOError:
            self.logger.error("Error while sending sms to %s", number)
            print "Error while sending message"
            return False

        return True


class email:
    def __init__ (self, mailServer, fromAddr, username, password):
        self.logger = logging.getLogger("iMonitor.message.sms")
        self.mailServer = mailServer
        self.fromAddr = fromAddr
        self.username = username
        self.password = password


    def sendMany(self, mailIds, message):
        self.send(mailIds, message)
#        for mailId in mailIds.split(","):
#            self.send(mailId, message)


    def send(self, mailIds, message):
        self.logger.info("Sending email to %s", mailIds)
#        toaddr = ['ukesh.vasudevan@infinite.com']
        toaddr = mailIds.split(",")
        ccaddr = []

        message_subject = "iMonitor Alert"

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = message_subject
        msg['From'] = self.fromAddr
        msg['To'] = ', '.join(toaddr)
        msg['Cc'] = ', '.join(ccaddr)

        # Create the body of the message (a plain-text and an HTML version).

        dt = datetime.datetime.now().strftime("%B %d, %Y  %I:%M%p")

        htmlheader = """\
           <html>
           <head></head>
           <body>
           <h3>iMonitor Alarm raised - %s </h3>
           """ % dt
 
        htmlfoter = """\
          </table><br>
          <B>iMonitor</B> - <a href="http://52.77.45.117/iMonitor_UI/admin/dashboard.php"> http://52.77.45.117/iMonitor_UI/admin/dashboard.php </a>
          <br><br>
          <table width= "100%" BORDER=0  bgcolor="#e0ebeb"> <tr> <td>*** This is an automatically generated email *** </td> </tr> </table>
          </body>
          </html> """

        html = htmlheader + message + htmlfoter

        #print html
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

        try:
            MailServer = smtplib.SMTP(self.mailServer)
            MailServer.starttls()
            MailServer.login(self.username, self.password)
            MailServer.sendmail(self.fromAddr, toaddr + ccaddr, msg.as_string())
            MailServer.quit()
        except Exception as err:
            self.logger.error("Can't Send: %s", str(err))
            print "Can't send email: " + str(err)


if __name__ == "__main__":
    msg = sms()
    msg.send("9843033525", "to check")

