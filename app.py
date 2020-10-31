from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine, Document
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from bson.json_util import dumps
from flask_cors import CORS
import os
import time
import requests
import json
import logging

UPLOAD_FOLDER = '/app/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'marketplace',
    # 'host': 'mongodb://',
    'host': 'mongodb://mongo/marketplace?retryWrites=true&w=majority'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = MongoEngine(app)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
cors = CORS(app, resources={r"/*": {"origins": "*"}})
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Document):
    meta = {'collection': 'marketplace'}
    email = db.StringField(max_length=30)
    password = db.StringField()
    userlevel = db.StringField()

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

class RegForm(FlaskForm):
    email = StringField('email',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if request.method == 'POST':
        print ("Mail: " + form.email.data)
        if form.validate():
            existing_user = User.objects(email=form.email.data).first()
            if existing_user is None:
                hashpass = generate_password_hash(form.password.data, method='sha256')
                # hey = User(form.email.data,hashpass).save()
                hey = User(email=form.email.data,password=hashpass).save()
                login_user(hey)
                return redirect(url_for('dashboard'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated == True:
        return redirect(url_for('dashboard'))
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = User.objects(email=form.email.data).first()
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

def read_markedplace():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace"
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_uploads():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/uploads/" + str(current_user.id)
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

@app.route('/dashboard')
@login_required
def dashboard():
    data = read_markedplace()
    return render_template('dashboard.html',
      name=current_user.email,
      pwhash=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      data=data,
      uploads=read_uploads()
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_upload(filename):
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/uploads/" + str(current_user.id) + "/" + filename
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = str(current_user.id) + "_" + str(time.time()) + "_" + str(file.filename)
            print ("Filename: " + filename)
            save_upload(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/newitem', methods=['POST'])
def addItemSave():
    # print ("Title: " + request.form['title'])
    title = str(request.form['title'])
    description = request.form['description']
    price = request.form['price']
    category = request.form['category']
    type= request.form['type']
    seller=current_user.id
    # print ("Seller: " + str(current_user.id))
    apiurl = "http://api:4006/api/v1/marketplace"
    data = {
        'title': description,
        'description': description,
        'price': price,
        'category': category,
        'type': type,
        'seller': str(current_user.id),
        'active': '0'
        }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(apiurl, json=dumps(data), headers=headers)
    return redirect(url_for('dashboard'))

@app.route('/newitem', methods=['GET'])
def addItem():
    # if request.method == 'POST':
    #     print (request.is_json)
    return render_template('newarticle.html',
        seller=current_user.id
        )

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=4006)
