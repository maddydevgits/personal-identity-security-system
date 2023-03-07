from flask import Flask,render_template,redirect,request,session
from web3 import Web3,HTTPProvider
from werkzeug.utils import secure_filename
import json
import os
import hashlib

def hash_file(filename):
   """"This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()


def connect_with_register_blockchain(acc):
    blockchain='http://127.0.0.1:7545' # step - 1: pass blockchain server details

    web3=Web3(HTTPProvider(blockchain)) # step - 2: Connecting through HTTP Provider of Web3

    if acc==0: # step - 3: loading the account details
        acc=web3.eth.accounts[0] # primary account, if no account is mentioned
    web3.eth.defaultAccount=acc # account is needed because we have to make money transactions

    artifact_path="../build/contracts/register.json" # step - 4: loading the register artifact
    with open(artifact_path) as f:
        contract_json=json.load(f) # string into json object
        contract_abi=contract_json['abi'] # application binary interface
        contract_address=contract_json['networks']['5777']['address']
    
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # step - 5: connect with contract

    return (contract,web3)

def connect_with_file_blockchain(acc):
    blockchain='http://127.0.0.1:7545' # step - 1: pass blockchain server details

    web3=Web3(HTTPProvider(blockchain)) # step - 2: Connecting through HTTP Provider of Web3

    if acc==0: # step - 3: loading the account details
        acc=web3.eth.accounts[0] # primary account, if no account is mentioned
    web3.eth.defaultAccount=acc # account is needed because we have to make money transactions

    artifact_path="../build/contracts/fileProtect.json" # step - 4: loading the register artifact
    with open(artifact_path) as f:
        contract_json=json.load(f) # string into json object
        contract_abi=contract_json['abi'] # application binary interface
        contract_address=contract_json['networks']['5777']['address']
    
    contract=web3.eth.contract(address=contract_address,abi=contract_abi) # step - 5: connect with contract

    return (contract,web3)
# launch web app
app=Flask(__name__)
app.secret_key='sacetc1'
app.config["UPLOAD_FOLDER"] = "static/uploads/"

@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/registerUser',methods=['post']) # route to create account in platform
def registerUser(): 
    username=request.form['username'] # step-1: collect details from HTML Form
    name=request.form['name']
    password=request.form['password']
    email=request.form['email']
    mobile=request.form['mobile']
    print(username,name,password,email,mobile)

    try:
        contract,web3=connect_with_register_blockchain(0) # step - 2: connecting with blockchain
        tx_hash=contract.functions.registerUser(username,name,int(password),email,mobile).transact() # step - 3: making contract call
        web3.eth.waitForTransactionReceipt(tx_hash) # step - 4: wait until block is added to chain
        return render_template('index.html',res='Registered Successfully')
    except:
        return render_template('index.html',err='You have already registered')

@app.route('/loginUser',methods=['post'])
def loginUser():
    username=request.form['username1']
    password=request.form['password1']
    print(username,password)

    try:
        contract,web3=connect_with_register_blockchain(0)
        state=contract.functions.loginUser(username,int(password)).call()
        if state==True:
            session['username']=username
            return redirect('/dashboard')
        else:
            return render_template('index.html',err1='Invalid Credentials')
    except:
        return render_template('index.html',err1='First register Account')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/uploadFile',methods=['post','get'])
def uploadImage():
    doc=request.files['chooseFile']
    if session['username'] not in os.listdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    doc1=secure_filename(doc.filename)
    doc.save(os.path.join(app.config['UPLOAD_FOLDER'], session['username']+'/'+doc1))
    hashid=hash_file(os.path.join(app.config['UPLOAD_FOLDER'], session['username']+'/'+doc1))
    print(hashid)
    try:
        contract,web3=connect_with_file_blockchain(0)
        tx_hash=contract.functions.addFile(session['username'],os.path.join(app.config['UPLOAD_FOLDER'], session['username']+'/'+doc1),hashid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return (render_template('dashboard.html',res='file uploaded'))
    except:
        return (render_template('dashboard.html',err='file already uploaded'))

@app.route('/myFiles')
def myFiles():
    try:
        k=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
        print(k)
        data=[]
        for i in k:
            dummy=[]
            dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username'])+'/'+i)
            data.append(dummy)
        print(data)
    except:
        data=[]
    return render_template('myFiles.html',dashboard_data=data,len=len(data))

@app.route('/shareFile')
def shareImage():
    data=[]
    data1=[]
    contract,web3=connect_with_register_blockchain(0)
    _usernames,_names,_passwords,_emails,_mobiles=contract.functions.viewUsers().call()
    for i in range(len(_usernames)):
        dummy=[]
        if(_usernames[i]!=session['username']):
            dummy.append(_usernames[i])
            data.append(dummy)
    try:
        k=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
        print(k)
    except:
        k=[]
    for i in k:
        dummy=[]
        dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username'])+'/'+i)
        data1.append(dummy)
    return render_template('sharefile.html',dashboard_data=data,dashboard_data1=data1,len=len(data),len1=len(data1))

@app.route('/toShareBuddy',methods=['post'])
def toShareBuddy():
    flag=0
    userId=request.form['userId']
    docId=request.form['docID']
    #print(userId,docId)
    hashid=hash_file(docId)
    #print(hashid)
    contract,web3=connect_with_file_blockchain(0)
    _users,_names,_files,_tokens=contract.functions.viewFiles().call()
    #print(_users)
    print(_files)
    print(_tokens)
    try:
        for i in range(len(_files)):
            if(hashid==_files[i]):
                print('file found')
                if userId in _tokens[i]:
                    print('Occured')
                    flag=1
                    break
        if(flag==0):
            tx_hash=contract.functions.addToken(hashid,userId).transact()
            web3.eth.waitForTransactionReceipt(tx_hash)
    except:
        pass

    data=[]
    data1=[]
    contract,web3=connect_with_register_blockchain(0)
    _usernames,_names,_passwords,_emails,_mobiles=contract.functions.viewUsers().call()
    for i in range(len(_users)):
        dummy=[]
        if(_users[i]!=session['username']):
            dummy.append(_users[i])
            data.append(dummy)

    k=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    #print(k)
    for i in k:
        dummy=[]
        dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username'])+'/'+i)
        data1.append(dummy)
    if(flag==1):
        return(render_template('sharefile.html',err='Already Shared',dashboard_data=data,dashboard_data1=data1,len=len(data),len1=len(data1)))
    else:
        return(render_template('sharefile.html',res='Shared to Buddy',dashboard_data=data,dashboard_data1=data1,len=len(data),len1=len(data1)))

@app.route('/logout')
def logout():
    session['username']=None
    return redirect('/')

@app.route('/sharedFiles')
def sharedFiles():
    data=[]
    contract,web3=connect_with_file_blockchain(0)
    _users,_names,_files,_tokens=contract.functions.viewFiles().call()
    for i in range(len(_names)):
        if session['username'] in _tokens[i][1:]:
            dummy=[]
            dummy.append(_tokens[i][0])
            dummy.append(_names[i])
            data.append(dummy)
    return render_template('sharedfiles.html',dashboard_data=data,len=len(data))

@app.route('/mysharedfiles')
def mysharedfiles():
    contract,web3=connect_with_file_blockchain(0)
    _users,_names,_files,_tokens=contract.functions.viewFiles().call()
    data=[]
    print(_tokens)
    for i in range(len(_names)):
        if(_users[i]==session['username']):
            for j in _tokens[i]:
                if j!=session['username'] and j!='0x0000000000000000000000000000000000000000':
                    dummy=[]
                    dummy.append(_names[i])
                    dummy.append(j)
                    data.append(dummy)

    return render_template('mysharedfiles.html',dashboard_data=data,len=len(data))

@app.route('/cancel/static/uploads/<id1>/<id2>/<id3>')
def cancelImage(id1,id2,id3):
    print(id1,id2,id3)
    hashid=hash_file(os.path.join(app.config['UPLOAD_FOLDER']+id1+'/'+id2))
    contract,web3=connect_with_file_blockchain(0)
    tx_hash=contract.functions.removeToken(hashid,id3).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    return redirect('/mysharedfiles')


if __name__=="__main__":
    app.run(port=5001,host='0.0.0.0',debug=True)