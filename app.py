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
# MyAnonymousUser = "Nobody"
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
# login_manager.anonymous_user = MyAnonymousUser

class User(UserMixin, db.Document):
    meta = {'collection': 'marketplace'}
    email = db.StringField(max_length=30)
    password = db.StringField()
    userlevel = db.StringField()
    # name = db.StringField()
    # meta = {'strict': False}

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

class RegForm(FlaskForm):
    email = StringField('email',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=20)])
    # name = StringField('name', validators=[InputRequired(),Length(min=3, max=30)])

@app.route('/')
@login_required
def index():
    data = read_categories()
    categories = {}
    for d in data:
        categories[id] = d['name']
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    if current_user.is_authenticated:
        return render_template('index.html',
          pwhash=current_user.password,
          userlevel=current_user.userlevel,
          userid=current_user.id,
          data=read_markedplace_active(),
          # categories=categories,
          # cats=read_categories(),
          categories=read_categories(),
          name=name,
          userlist=read_userlist(),
          loggedIn = "1",
        )
    else:
        return render_template('index.html',
            loggedIn = "0",
            data=read_markedplace_active(),
            categories=categories,
        )

@app.route('/category/<id>', methods=['GET'])
@login_required
def categoryId(id):
    data = read_categories()
    categories = {}
    for d in data:
        categories[id] = d['name']
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    if current_user.is_authenticated:
        return render_template('index.html',
          pwhash=current_user.password,
          userlevel=current_user.userlevel,
          userid=current_user.id,
          # data=read_markedplace_active(),
          data=read_category_active(id),
          # categories=categories,
          # cats=read_categories(),
          categories=read_categories(),
          name=name,
          userlist=read_userlist(),
          loggedIn = "1",
        )
    else:
        return render_template('index.html',
            loggedIn = "0",
            data=read_markedplace_active(),
            categories=categories,
        )


@app.route('/dashboard/profil', methods=['GET'])
@login_required
def dashboardProfil():
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    # print ("Name: " + str(profileExtras) ) # + " test: " + profileExtras)
    # x = dict(profileExtras)
    # print ("X: ", x['name'])
    return render_template('profil.html',
      email=current_user.email,
      password=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      profileExtras=profileExtras,
      name=name,
      categories=read_categories(),
      loggedIn = loggedIn
    )

@app.route('/dashboard/profil/save', methods=['POST'])
@login_required
def dashboardProfilSave():
    name = str(request.form['name'])
    email = request.form['email']
    userid = request.form['userid']
    print ("seller: " + userid)
    apiurl = "http://api:4006/api/v1/marketplace/profil/edit"
    data = {
        'id': userid,
        'name': name,
        'email': email
        }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(apiurl, json=dumps(data), headers=headers)
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    data = read_categories()
    categories = {}
    for d in data:
        categories[id] = d['name']
    return render_template('dashboard.html',
      name=name,
      pwhash=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      # data=read_markedplace(),
      data=read_marketplace_my(),
      # categories=categories,
      categories=read_categories(),
      userlist=read_userlist(),
      loggedIn=loggedIn
      # uploads=read_uploads()
    )

@app.route('/dashboard/offer/<id>')
@login_required
def dashboardOffer(id):
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    data = read_markedplace_myoffer(id)
    return render_template('dashboard_offer.html',
      name=name,
      pwhash=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      data=data,
      id=id,
      uploads=read_uploads(),
      categories=read_categories(),
      loggedIn=loggedIn
    )

@app.route('/dashboard/offer/edit/<id>', methods=['GET'])
@login_required
def dashboardOfferEdit(id):
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    categories = read_categories()
    data = read_markedplace_offer(id)
    print ("data: " + str(data))
    return render_template('editoffer.html',
      name=name,
      pwhash=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      data=data,
      id=id,
      categories=categories,
      userlist=read_userlist(),
      uploads=read_uploads(),
      loggedIn=loggedIn
    )

@app.route('/view/<id>', methods=['GET'])
@login_required
def viewOffer(id):
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    categories = read_categories()
    data = read_markedplace_offer(id)
    print ("data: " + str(data))
    return render_template('offer.html',
      name=name,
      pwhash=current_user.password,
      userlevel=current_user.userlevel,
      userid=current_user.id,
      data=data,
      id=id,
      categories=categories,
      userlist=read_userlist(),
      loggedIn=loggedIn
    )


@app.route('/newitem', methods=['POST'])
def addItemSave():
    # print ("Title: " + request.form['title'])
    title = str(request.form['title'])
    description = request.form['description']
    price = request.form['price']
    image = request.form['image']
    active = request.form['active']
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
        'active': active,
        'image': image
        }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(apiurl, json=dumps(data), headers=headers)
    return redirect(url_for('dashboard'))

@app.route('/newitem', methods=['GET'])
def addItem():
    data = read_categories()
    categories = {}
    for d in data:
        categories[id] = d['name']
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
    # if request.method == 'POST':
    #     print (request.is_json)
    return render_template('newarticle.html',
        seller=current_user.id,
        name=name,
        categorylist=read_categories(),
        categories=read_categories(),
        uploads=read_uploads(),
        loggedIn=loggedIn
        )

@app.route('/dashboard/offer/save/<id>', methods=['POST'])
@login_required
def dashboardOfferSave(id):
    title = str(request.form['title'])
    description = request.form['description']
    price = request.form['price']
    category = request.form['category']
    type= request.form['type']
    active = request.form['active']
    image = request.form['image']
    id = request.form['id']
    seller=request.form['userid']
    print ("seller: " + seller)
    apiurl = "http://api:4006/api/v1/marketplace/offer/edit"
    data = {
        'id': id,
        'title': title,
        'description': description,
        'price': price,
        'category': category,
        'type': type,
        'seller': seller,
        'active': active,
        'image': image
        }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(apiurl, json=dumps(data), headers=headers)
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if current_user.is_authenticated:
        loggedIn = "1"
    profileExtras = getProfileExtras()
    for i in profileExtras:
        name=i['name']
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
    return render_template('upload.html',
        uploads=read_uploads(),
        loggedIn=loggedIn,
        categories=read_categories(),
        name=name
    )
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form method=post enctype=multipart/form-data>
    #   <input type=file name=file>
    #   <input type=submit value=Upload>
    # </form>
    # '''

@app.route('/logout', methods = ['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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
    else:
        loggedIn = True
    form = RegForm()
    if request.method == 'POST':
        if form.validate():
            check_user = User.objects(email=form.email.data).first()
            if check_user:
                if check_password_hash(check_user['password'], form.password.data):
                    login_user(check_user)
                    return redirect(url_for('dashboard'))
    return render_template('login.html', form=form, loggedIn=loggedIn)

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

def read_markedplace():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/" + str(current_user.id)
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_markedplace_active():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/active"
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_category_active(id):
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/categoryactive/" + id
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_markedplace_open():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/open"
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def getProfileExtras():
    data = {}
    import urllib, json
    import urllib.request
    userid = current_user.id
    apiurl = "http://api:4006/api/v1/marketplace/profile/extras/" + str(userid)
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data


def read_categories():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/categories"
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_markedplace_offer(id):
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/" + id
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_marketplace_my():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/my/" + str(current_user.id)
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_markedplace_myoffer(id):
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/myone/" + id
    response = urllib.request.urlopen(apiurl)
    data = json.loads(response.read())
    return data

def read_userlist():
    data = {}
    import urllib, json
    import urllib.request
    apiurl = "http://api:4006/api/v1/marketplace/profile/users"
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

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=4006)
