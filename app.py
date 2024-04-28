import ai
#Flask
from flask import  Flask,redirect, render_template, session, url_for, request, flash,send_from_directory
from werkzeug.utils import secure_filename
import os
# Authentication
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
#MongoDB
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
client = MongoClient(env.get("MONGO_URI"))
db = client['Marketplace']
marketplace = db['marketplace']
products = db['products']
# Marketplace Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'marketplace_uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

    
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

#Initialize Flask
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Auth0
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Routes
@app.route('/')
def index():
    if "user_info" in session:
        email = (session.get("user_info")['email'])
        name = (session.get("user_info")['name'])
        print(email)
        print(name)
    return render_template('index.html', **locals())

UPLOAD_FOLDER = 'uploads'

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/repurpose', methods=['GET', 'POST'])
def repurpose():
    result = ""
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))  # save file to uploads directory
            with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
                image_data = f.read()
            object = ai.Image_Analysis(image_data)
            result = ai.Suggest_Use(object)
            result = result.replace('\n', '<br>').replace('**', '<strong>').replace('**', '</strong>')
    return render_template('repurpose.html', result=result)


## Marketplace Routes
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/sell', methods=["GET", "POST"])
def sell():
    currproducts = db.products.find()
    if "user_info" not in session:
        return redirect(url_for("login"))
    else:
        name = (session.get("user_info")['name']) 
        email = (session.get("user_info")['email'])
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
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product_description = request.form.get('description')
                productupload = {'description': product_description, 'image': filename, 'email': email, 'name': name}
                products.insert_one(productupload)
                return redirect(url_for('sell'))
    return render_template('sell.html', **locals())

# Authentication Routes
@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    # Fetch user info
    resp = oauth.auth0.get(f"https://{env.get('AUTH0_DOMAIN')}/userinfo")
    user_info = resp.json()
    # Save user info into flask session
    session["user_info"] = user_info
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))