from flask import Flask, render_template, request,jsonify, redirect, Response, make_response,send_file
from flask import json
import TxnNaming
import TxnNaming_with_sheet
import TxnNaming_API
import api_request
import os
import requests
import webbrowser

app=Flask(__name__)
errorExc=""

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/error/<error2Exc>')
def error(error2Exc):
    return render_template('error.html',error2Exc=error2Exc)

@app.route('/success2')
def success2():
    return render_template('success2.html')

@app.route('/<errorExc>')
def error2(errorExc):
    return render_template('error2.html',errorExc=errorExc)

@app.route('/Blazemeter_Template')
def LR_Template():
    return render_template('index.html')

@app.route('/Excel_Sheet')
def Excel_Sheet():
    return render_template('index3.html')

@app.route('/LR_Template_With_Excel')
def LR_Template_With_Excel():
    return render_template('index2.html') 

@app.route('/Perf_Estimator')
def Perf_Estimator():
    return render_template('index4.html') 

@app.route('/New_Scripts')
def New_Scripts():
    return render_template('NewScripts.html')
    
@app.route('/New_Scripts_API')
def New_Scripts_API():
    return render_template('NewScripts_API.html')

@app.route('/Exist_Scripts')
def Exist_Scripts():
    return render_template('ExistingScripts.html') 

@app.route('/Exist_New_Scripts')
def Exist_New_Scripts():
    return render_template('ExistNewScripts.html') 

@app.route('/save-files/', methods=['GET', 'POST'])
def return_files():
    try:
        #name = request.headers["Referer"]
        #print(name)
        if(("Blazemeter_Template" in name) or ("convert" in name)):
            #print("no")
            downloadFile, data2 = api_request.download()
            #print("download file done")
            res = Response(data2,
                            mimetype="text/csv",
                            headers={"Content-disposition":
                                    "attachment; filename={}".format(downloadFile)})
            return res
        if(("LR_Template_With_Excel" in name) or ("conversionDone2" in name)):
            #print("yes"+""+script_ty)
            if (script_ty == "API"):
                downloadFile, data2 = TxnNaming_API.download()
                #print("download file done")
                res = Response(data2,
                                mimetype="text/c",
                                headers={"Content-disposition":
                                        "attachment; filename={}".format(downloadFile)})
                return res
            if (script_ty == "WEB"):
                downloadFile, data2 = TxnNaming_with_sheet.download()
                #print("download file done")
                res = Response(data2,
                                mimetype="text/c",
                                headers={"Content-disposition":
                                        "attachment; filename={}".format(downloadFile)})
                return res

    except Exception as ex:
        return str(ex)  

@app.route('/mail-file', methods = ['POST'])
def mail_files():
    to = request.form['exampleInputEmail1']
    fromEmail = request.form['exampleInputEmail2']
    pwd = request.form['exampleInputPassword1']
    subject = request.form['exampleInputEmail3']
    message = request.form['exampleInputEmail4']
   # print(name)
    if(("Blazemeter_Template" in name) or ("convert" in name)):
        mailFile,fname= api_request.sendMail(to,fromEmail,pwd,subject,message)
        #print("yes")
        if mailFile == "sent":
            return render_template('success.html')
    if(("LR_Template_With_Excel" in name) or ("conversionDone2" in name)):
            #print("yes"+""+script_ty)
            if (script_ty == "API"):
                mailFile,fname= TxnNaming_API.sendMail(to,fromEmail,pwd,subject,message)
                if mailFile == "sent":
                    return render_template('success2.html')
            if (script_ty == "WEB"):
                mailFile,fname= TxnNaming_with_sheet.sendMail(to,fromEmail,pwd,subject,message)
                if mailFile == "sent":
                    return render_template('success2.html')
    else:
         return render_template('error.html',error2Exc=mailFile)
    
@app.route('/convert', methods = ['POST'])
def conversionDone():
    global name
    resultId = request.form['filePath']
    fileNames = request.form['newfilePath']
    req = request.url
    name = req
    #print(name)
    response1 = api_request.mainFunc(resultId,fileNames)
    if (response1 == "Done"):
        return render_template('success.html')  
    else:
        #return render_template('error.html')
        return redirect('/error/{}'.format(response1))

@app.route('/conversionDone2', methods = ['POST'])
def conversionDone2():
    global script_ty
    global name
    script_type = request.form['scripts']
    filePath = request.files['filePath']
    newfilePath = filePath.filename
    excelPath = request.files['excelPath']
    script_ty = script_type
    req = request.url
    name = req
    #print(name + " " + "converted")
    
    try:
        if (script_type == "WEB"):
            response1, fileName, data = TxnNaming_with_sheet.mainFunc(filePath,newfilePath,excelPath)
            #print("The file path is '" + response1 +""+fileName+""+data)
            if response1 == "File path doesn't exists":
                errorExc="Incorrect File Type"
                return redirect('/{}'.format(errorExc))
            elif not(newfilePath.endswith(".c")):
                errorExc="Incorrect File Type"
                return redirect('/{}'.format(errorExc))
            else:
                # return Response(data,
                #                 mimetype="text/c",
                #                 headers={"Content-disposition":
                #                         "attachment; filename={}".format(fileName)})
                #return redirect('/success2')
                return render_template('success2.html')  

    
        elif (script_type == "API"):
            response1, fileName, data = TxnNaming_API.mainFunc(filePath,newfilePath,excelPath)
            #print("The file path is '" + filePath + "'" + newfilePath+ " " + response1 + "" + excelPath +" " + script_type)
            if response1 == "File path doesn't exists":
                errorExc="Incorrect File Type"
                return redirect('/{}'.format(errorExc))
            elif not(newfilePath.endswith(".c")):
                errorExc="Incorrect File Type"
                return redirect('/{}'.format(errorExc))
            else:
                # return Response(data,
                #             mimetype="text/c",
                #             headers={"Content-disposition":
                #                     "attachment; filename={}".format(fileName)})
                return render_template('success2.html')
    except IndexError:
        errorExc = "Sheet index out of range"
        return redirect('/{}'.format(errorExc))
            
@app.route('/excelSheet', methods = ['POST'])
def excelSheet():
    global script_ty
    global name
    script_type = request.form['scripts']
    filePath = request.files['filePath']
    newfilePath = filePath.filename
    excelPath = request.files['excelPath']
    script_ty = script_type
    req = request.url
    name = req



if __name__== "__main__":
    app.run(debug=True)
