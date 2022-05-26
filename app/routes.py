from app import app
from app import secret
from app import database as db
# Here are where all of the routes will go
import os
import pathlib

import requests
from flask import Flask, render_template, redirect, request, url_for, session
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests


# env variable to bipass https
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = secret.setup()
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
  client_secrets_file=client_secrets_file,
  scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
  redirect_uri="http://127.0.0.1:5000/callback"
)

def login_is_required(function):
  def wrapper(*args, **kwargs):
    if "google_id" not in session:
      return render_template('index.html', message = "not google authenticated- failed")
    else:
      return function()
  return wrapper

@app.route("/", methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
  authorization_url, state = flow.authorization_url(hd="stuy.edu")
  print(state)
  session["state"] = state
  return redirect(authorization_url)

@app.route("/callback", methods=['GET', 'POST'])
def callback():
  flow.fetch_token(authorization_response=request.url)
  if not session["state"] == request.args["state"]:
    render_template("index.html", message="state is wrong- failed")

  credentials = flow.credentials
  request_session = requests.session()
  cached_session = cachecontrol.CacheControl(request_session)
  token_request = google.auth.transport.requests.Request(session=cached_session)

  id_info = id_token.verify_oauth2_token(
    id_token=credentials._id_token,
    request=token_request,
    audience=GOOGLE_CLIENT_ID
  )

  session["google_id"] = id_info.get("sub")
  session["name"] = id_info.get("name")
  print(session["name"])
  return redirect("/protected_area")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
  session.clear()
  print("cleared")
  return redirect("/")

@app.route("/protected_area", methods=['GET', 'POST'])
@login_is_required
def protected_area():
  return render_template('protected.html', name=session["name"], email=session["google_id"])
