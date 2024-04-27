
#Flask
from flask import  Flask,redirect, render_template, session, url_for
# Authentication
import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

# Load the .env file
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

#Initialize Flask
app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

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

@app.route('/repurpose')
def repurpose():
    if "user_info" not in session:
        return redirect(url_for("login"))
    else:
        name = (session.get("user_info")['name'])
        print("Hello World")
    return render_template('repurpose.html', **locals())

@app.route('/sell')
def sell():
    if "user_info" not in session:
        return redirect(url_for("login"))
    else:
        name = (session.get("user_info")['name']) 
        print("Hello World")
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