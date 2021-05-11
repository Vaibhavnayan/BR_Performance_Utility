import os

def addStartContent(index,contents,newFilename,i):
    
    contents.insert(index, "web_reg_find(\"Text=textcheck%s\", \"SaveCount=TextCount%s\", LAST); \n lr_start_transaction(\"Transaction%s\");\n" %(i,i,i))
    f = open(newFilename, "w")
    contents = "".join(contents)
    f.write(contents)
    
    index=index+2
    return index

def addEndContent(index2,contents,fileName,i):
   
    contents.insert(index2+1, "\n if(atoi(lr_eval_string(\"{TextCount%s}\")) > = 0){ \n lr_end_transaction(\"Transaction%s\",LR_PASS);\n} \n else { \n lr_end_transaction(\"Transaction%s\",LR_FAIL);\n}\n" %(i,i,i))
    f = open(fileName, "w")
    contents = "".join(contents)
    f.write(contents)
    
    index2=index2+2
    return index2


def openFileforStartTxn(index,fileName,newFilename,i):
    f = open(fileName, "r")
    contents = f.readlines()
    

    for items in contents:
        if ((len(contents)-1 >= index) and (contents[index].__contains__("web_"))): 
            index=addStartContent(index,contents,newFilename,i)
            i=i+1         
            continue
        elif index==len(contents)-1:
            break
        else:
            index=index+1
    f.close()

def openFileforEndTxn(index2,fileName,i):
    f = open(fileName, "r")
    f.seek(0)
    contents = f.readlines()
    

    for items in contents:
        if ((len(contents)-1 >= index2) and (contents[index2].__contains__("LAST")) and not(contents[index2].__contains__("web_reg_find"))): 
            index2=addEndContent(index2,contents,fileName,i)
            i=i+1          
            continue
        elif index2==len(contents)+1:
            break
        else:
            index2=index2+1
    f.close()

def mainFunc(oldfilePath,newfilePath):
    fileName = oldfilePath
    newFilename = newfilePath
    i=1
    if(os.path.exists(fileName) and fileName.endswith(".c") and newfilePath.endswith(".c")):
        openFileforStartTxn(0,fileName,newFilename,i)
        openFileforEndTxn(0,newFilename,i)
        return "Done"
    else:
        return "File doesn't exists"