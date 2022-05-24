# Here are where all of the routes will go
from app import app
from flask import render_template, redirect, request, url_for, session
from app import secret
import os
import requests
import pathlib
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests

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
      return render_template('index.html', message = "failed")
    else:
      return function()
  return wrapper

@app.route("/", methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
  authorization_url, state = flow.authorization_url()
  session["state"] = state
  return redirect(authorization_url)

@app.route("/callback", methods=['GET', 'POST'])
def callback():
  return redirect("/")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
  session.clear()
  return redirect("/")

@app.route("/protected_area", methods=['GET', 'POST'])
@login_is_required
def protected_area():
  return render_template('protected.html')
