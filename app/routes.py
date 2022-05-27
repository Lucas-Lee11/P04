# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import os
import pathlib

import google.auth.transport.requests
import requests
from flask import redirect, render_template, request, session, url_for
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

from app import app
from app import database as db
from app import secret

# env variable to bipass https
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = secret.setup()
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
)


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return render_template(
                "index.html", message="not google authenticated- failed"
            )
        else:
            return function()

    return wrapper


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    flow.redirect_uri = url_for("callback", _external=True)
    authorization_url, state = flow.authorization_url(hd="stuy.edu")
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback", methods=["GET", "POST"])
def callback():
    flow.fetch_token(authorization_response=request.url)
    if not session["state"] == request.args["state"]:
        render_template("index.html", message="state is wrong- failed")

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    session["token"] = credentials.token

    # check if email is whitelisted as a teacher, otherwise create student
    if session["email"] == "cliu20@stuy.edu":
        if not db.Teacher.get_teacher_id(session["email"]):
            db.Teacher.create_teacher(
                session["google_id"], session["name"], session["email"]
            )
    else:
        if not db.Student.get_student_id(session["email"]):
            db.Student.create_student(
                session["google_id"], session["name"], session["email"]
            )

    # this should go to either the student or teacher protected page
    return redirect("/protected_area")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": session["token"]},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    session.clear()
    return redirect("/")


@app.route("/protected_area", methods=["GET", "POST"])
@login_required
def protected_area():
    return render_template(
        "protected.html", name=session["name"], email=session["google_id"]
    )
