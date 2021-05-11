import time #built-in libraries-  written inside pyton interpreter in C langauge- import sys sys.builtin_module_names
import os #standard libraries- written in both C in python, reside in python libraries. import sys sys.prefix
import pandas #third party libraries- written by third party- to install pip3 install pandas
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def addStartContent(index,contents,txnName,textCheck,value,newFilename):
    contents.pop(index)
    contents.insert(index, "web_reg_find(\"Text=%s\", \"SaveCount=TextCount_%s\", LAST); \n lr_start_transaction(\"%s\");\n " %(textCheck[value],value,txnName[value]))
    
    f = open(newFilename, "w")
    contents = "".join(contents)
    f.write(contents)
    
    index=index+2
    return index

def addEndContent(index2,contents,txnName,textCheck,value,fileName):

    contents.insert(index2+1, "\n if(atoi(lr_eval_string(\"{TextCount_%s}\")) > = 0){ \n lr_end_transaction(\"%s\",LR_PASS);\n} \n else { \n lr_end_transaction(\"%s\",LR_FAIL);\n}\n lr_think_time(2);" %(value,txnName[value],txnName[value]))
    contents.pop(index2)
        
    f = open(fileName, "w")
    contents = "".join(contents)
    f.write(contents)
    
    index2=index2+2
    return index2


def openFileforStartTxn(index,fileName,txnName,textCheck,newFilename):
    f = open(fileName, "r")
    contents = f.readlines()
    value=index

    for items in contents:
        if ((len(contents)-1 >= index) and (contents[index].__contains__("lr_start"))): 
            index=addStartContent(index,contents,txnName,textCheck,value,newFilename)
            value=value+1
            #print(index)          
            continue
        elif index==len(contents)-1:
            break
        else:
            index=index+1
    f.close()

def openFileforEndTxn(index2,fileName,txnName,textCheck):
    f = open(fileName, "r")
    f.seek(0)
    contents = f.readlines()
    value=index2
    

    for items in contents:
        if ((len(contents)-1 >= index2) and (contents[index2].__contains__("lr_end"))): 
            index2=addEndContent(index2,contents,txnName,textCheck,value,fileName)
            value=value+1
            #print(index2, len(contents))          
            continue
        elif index2==len(contents)+1:
            break
        else:
            index2=index2+1
    f.close()

def datasheet(sheetPath):
    if sheetPath.endswith(".csv"):
        content= pandas.read_csv(sheetPath)
        name=list(content.TxnName)
        textcheck=list(content.TextCheck)
        return (name,textcheck)
    else:
        return "File path doesn't exist", sheetPath, sheetPath

def mainFunc(oldfilePath,newfilePath,excelPath):
    global newFilename
    fileName = oldfilePath.filename
   # filedata= oldfilePath.read()
    newFilename = newfilePath
    sheetpath = excelPath.filename
    #print(sheetpath)
    #file2 = open("Action.c","w+") 
    #file2.write(filedata)
    #print(file2)

    if(fileName.endswith(".c") and newfilePath.endswith(".c") and sheetpath.endswith(".csv")):
        oldfilePath.save(fileName)
        excelPath.save(sheetpath)
        lists= list(datasheet(sheetpath))
        #print(lists)
        txnName = list(lists[0])
        textCheck = list(lists[1])
        #print(txnName[0])
        #print(textCheck)
        openFileforStartTxn(0,fileName,txnName,textCheck,newFilename)
        openFileforEndTxn(0,newFilename,txnName,textCheck)
        # f = open(newFilename,'r')
        # data = f.read()
        # f.close()
        return "Done", newFilename, "Done"
    else:
        return "File path doesn't exists", newFilename, sheetpath

def download():
    f = open("{}".format(newFilename),'r')
    data2 = f.read()
    f.close()
    return newFilename,data2

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

        filename = newFilename  # In same directory as script

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
            f"attachment; filename= {newFilename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
        
        return "sent",newFilename
    
    except smtplib.SMTPAuthenticationError as e:
        return "Error",e
    
    except TypeError as er:
        return "Error",er
    
    except KeyError as err:
        return "Error",err