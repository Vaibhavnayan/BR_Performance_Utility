import subprocess
import json,os
import requests
from zipfile import ZipFile
import pandas as pd
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import getpass


def getResultLog(resultId,fileNames):
    #27792787
    lists=[]
    command = "curl 'https://a.blazemeter.com/api/v4/masters/{}'        --user 962ba9f2b9045301001bf263:d4e5d0a1029ddb0e222c2ac6cff053002c3fd281a7a054074dc8f282ae448e381afa4df1".format(resultId)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    #print(type(out))
    result=json.loads(out)
    message= result['error']
    if(message != None):
        message = result['error']['message']
        return "Master ID not found"
    sessionsIds= result['result']['sessionsId']


    for sessionID in sessionsIds:
        command2 = "curl 'https://a.blazemeter.com/api/v4/sessions/{}/reports/logs'        --user 962ba9f2b9045301001bf263:d4e5d0a1029ddb0e222c2ac6cff053002c3fd281a7a054074dc8f282ae448e381afa4df1".format(sessionID)
        p2 = subprocess.Popen(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out2, err = p2.communicate()
        result2=json.loads(out2)
        artifact_url= result2['result']['data'][0]['dataUrl']
        #print(result2['result']['data'][0]['dataUrl'])
        url = artifact_url
        r = requests.get(url, allow_redirects=True)
        #print(r)
        open('artifact_{}.zip'.format(sessionID), 'wb').write(r.content)
        lists.append("artifact_{}.zip".format(sessionID))
        
#02_vsm_shareholder_prod_p_MeetingID1.dat.csv
    if(os.path.exists("{}".format(fileNames))):
        os.remove("{}".format(fileNames))
    
    for listing in lists:
        with ZipFile(listing) as myzip:
            try:
                data = myzip.read('{}'.format(fileNames)).decode('utf-8')
                with open("{}".format(fileNames),'a+') as newfile:
                    newfile.write(data)
            except KeyError:
                return "File not found"

    #f = open("{}".format(fileNames),'r')
    #data2 = f.read()
    #f.close()
    return "Done"

def mainFunc(resultId,fileNames):
    global fname
    fname = fileNames
    return getResultLog(resultId,fileNames)


def download():
    f = open("{}".format(fname),'r')
    data2 = f.read()
    f.close()
    return fname,data2
    
def sendMail(to,fromEmail,pwd,sub,message):
    subject = sub
    body = message
    sender_email = fromEmail
    receiver_email = to
    password = pwd
    # Create a multipart message and set headers
    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email  # Recommended for mass emails

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        filename = fname  # In same directory as script

        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
        
        return "sent",filename
    
    except smtplib.SMTPAuthenticationError as e:
        return "Error",e
    
    except TypeError as er:
        return "Error",er
    
    except KeyError as err:
        return "Error",err
