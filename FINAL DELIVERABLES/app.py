from flask import Flask, render_template, request, redirect, url_for, session, flash
import ibm_db
import re
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import requests
from random import * 
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from flask_mail import Mail, Message
import os
from flask_mail import Mail, Message
app = Flask(__name__)


mail = Mail(app) # instantiate the mail class
# configuration of mail
app.config['MAIL_SERVER']='smtp.sendgrid.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = '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'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
otp = randint(000000,999999)

# sg = sendgrid.SendGridAPIClient(api_key='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')
# from_email = Email("abishek12082001@gmail.com")  # Change to your verified sender
# to_email = To("'SELECT * FROM email'")  # Change to your recipient
# subject = "Sending with SendGrid is Fun"
# content = Content("text/plain", "and easy to do anywhere, even with Python")
# mail = Mail(from_email, to_email, subject, content)

# # Get a JSON-ready representation of the Mail object
# mail_json = mail.get()

# # Send an HTTP POST request to /mail/send
# response = sg.client.mail.send.post(request_body=mail_json)
# print(response.status_code)
# print(response.headers)


# from clarifai_setup import (
#     DOG_IMAGE_URL,
#     GENERAL_MODEL_ID,
#     NON_EXISTING_IMAGE_URL,
#     RED_TRUCK_IMAGE_FILE_PATH,
#     both_channels,
#     metadata,
#     raise_on_failure,
#     post_model_outputs_and_maybe_allow_retries,
# )

# def test_predict_image_url():
#     stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

#     req = service_pb2.PostModelOutputsRequest(
#         model_id=GENERAL_MODEL_ID,
#         inputs=[
#             resources_pb2.Input(
#                 data=resources_pb2.Data(image=resources_pb2.Image(url=DOG_IMAGE_URL))
#             )
#         ],
#     )

#     response = post_model_outputs_and_maybe_allow_retries(stub, req, metadata=metadata())
#     print(response)
#     raise_on_failure(response)

#     assert len(response.outputs[0].data.concepts) > 0


app.secret_key = 'a'

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30367;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=bjg03480;PWD=Nw0nFgeEM0S3MdSN;",'','')

picsfolder = os.path.join('static','pics')
app.config['UPLOAD_FOLDER']=picsfolder

@app.route('/')

@app.route('/homepage')
def homepage():
    icon = os.path.join(app.config['UPLOAD_FOLDER'],'icon.gif')
    return render_template('homepage.html',user_image=icon)
    
@app.route('/about')
def about():
    icon = os.path.join(app.config['UPLOAD_FOLDER'],'icon.gif')
    return render_template('about.html',user_image=icon)



@app.route('/login', methods =['GET', 'POST'])
def login():
    msg=''
    if request.method=='POST' and 'username' in request.form and 'passwords' in request.form:
        username = request.form['username']
        passwords = request.form['passwords']
        stmt = ibm_db.prepare(conn,'SELECT * FROM appuser WHERE username = ? AND passwords = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,passwords)
        ibm_db.execute(stmt)
        account=ibm_db.fetch_assoc(stmt)
        if account:
            session['loggedin'] = True
            session['username'] = account['USERNAME']
            msg='Login successful'
            return redirect(url_for('userprofile'))
        else:
            msg='Incorrect username/password'
    return render_template('login.html',msg=msg)


@app.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id',None)
        session.pop('username',None)
        session.pop('passwords',None)
    return redirect(url_for('homepage'))


@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        passwords = request.form['passwords']
        cpassword = request.form['cpassword']
        stmt = ibm_db.prepare(conn,'SELECT * FROM appuser WHERE username = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not passwords or not email:
            msg = 'Please fill out the form !'
        else:
            prep_stmt = ibm_db.prepare(conn,"INSERT INTO appuser(username, fullname, email, passwords, cpassword) VALUES(?, ?, ?, ?, ?)")
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, fullname)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, passwords)
            ibm_db.bind_param(prep_stmt, 5, cpassword)
            ibm_db.execute(prep_stmt)
            msg = 'You have successfully registered !'
            return render_template('email.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('registration.html', msg = msg)

@app.route('/userprofile', methods =['GET', 'POST'])
def userprofile():
    if 'username' in session:
        username = session['username']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM appuser WHERE username = ?')
        ibm_db.bind_param(stmt, 1, username)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)       
        return render_template('userprofile.html',username = acc[1], fullname = acc[2], email = acc[3],)
    return render_template('userprofile.html')

@app.route('/updateprofile', methods =['GET', 'POST'])
def updateprofile():
    msg = ''
    if request.method == 'POST':
            username=request.form["username"]
            height = request.form['height']
            weight = request.form['weight']
            gender = request.form['gender']
            blood = request.form['blood']
            prep_stmt = ibm_db.prepare(conn,"INSERT INTO userdetail(username, height, weight, gender, blood) VALUES(?, ?, ?, ?, ?)")
            ibm_db.bind_param(prep_stmt, 1, username)
            ibm_db.bind_param(prep_stmt, 2, height)
            ibm_db.bind_param(prep_stmt, 3, weight)
            ibm_db.bind_param(prep_stmt, 4, gender)
            ibm_db.bind_param(prep_stmt, 5, blood)
            ibm_db.execute(prep_stmt)
            return redirect(url_for('detail'))
    return render_template('updateprofile.html')


@app.route('/detail', methods =['GET', 'POST'])
def detail():
    if 'username' in session:
        username = session['username']
        stmt = ibm_db.prepare(conn, 'SELECT * FROM  userdetail WHERE username = ?')
        ibm_db.bind_param(stmt, 1,username)    
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_tuple(stmt)       
        return render_template('detail.html',username = acc[0], height = acc[1], weight = acc[2], gender = acc[3], blood = acc[4])
    return render_template('detail.html')



@app.route('/window', methods=['POST', 'GET'])
def window():

  # Calorie Ninja
    url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

    headers = {
        "X-RapidAPI-Key": "8112050c4emsh723a2f0f2077ec0p1be092jsn91abf0528072",
        "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com"
    }

    if request.method == 'POST':
        foodname = request.form['foodname']

        querystring = {"query": foodname}
        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        return response.text

    return render_template('window.html')


@app.route('/window', methods=['POST', 'GET'])
def clarifai():
    if request.files.get('image'):
        image = request.files['image'].stream.read()
        stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

        CLARIFAI_API_KEY = "a4d1d4d3de3a4b6da5777636c754921e"
        APPLICATION_ID = "my-first-application"


        metadata = (("authorization", f"Key {CLARIFAI_API_KEY}"),)

        with open(image, "rb") as f:
            file_bytes = f.read()

        request = service_pb2.PostModelOutputsRequest(
            model_id='1d5fd481e0cf4826aa72ec3ff049e044',
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ])
        response = stub.PostModelOutputs(request, metadata=metadata)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " +
                            str(response.status.code))

        for concept in response.outputs[0].data.concepts:
            print('%12s: %.2f' % (concept.name, concept.value))

    return render_template('window.html')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email1 = request.form['email1'] 
        sql = "SELECT * FROM email WHERE email1 = ? "
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,email1)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_tuple(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        else:
           insert_sql = "INSERT INTO email(email1) VALUES(?)"
           stmt = ibm_db.prepare(conn,insert_sql)
           ibm_db.bind_param(stmt, 1, email1)
           ibm_db.execute(stmt)
           msg = Message('NUTRITION ASSISTANT',sender ='abishek12082001@gmail.com',recipients = [email1])
           msg.body = 'Hello user,THIS IS YOUR ONE TIME PASSWORD'
           msg.body = str(otp)
           mail.send(msg)
           return render_template('verify.html')
    return render_template('email.html')  


@app.route('/validate',methods=['GET', 'POST'])   
def validate():  
 user_otp = request.form['otp']  
 if otp == int(user_otp):  
     return render_template('login.html')  
 return render_template('verify.html')   


@app.route('/services')
def services():
    icon = os.path.join(app.config['UPLOAD_FOLDER'],'icon.gif')
    return render_template('services.html',user_image=icon)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=8080)
