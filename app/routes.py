# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w


import functools
import os
import pathlib

import google.auth.transport.requests
import requests
from flask import redirect, render_template, request, session, url_for, flash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from werkzeug.utils import secure_filename

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

# whitelisted teachers here for now
TEACHERS = ["cliu20@stuy.edu", "eknapp20@stuy.edu"]


def login_required(function):
    @functools.wraps(function)
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

    # hi yall so this is my idea of the basic flow for new accounts and stuff
    # like that--that's what i started with the setup_teacher and setup_student
    # stuff
    #
    # so basically when someone makes a new account it should check to see if
    # they're a student or a teacher and then send them to new account setup
    # which for teachers allows you to configure your profile and for students
    # allows you to star teachers
    #
    # all of this should be changable later with the edit_teacher and
    # edit_student pages but i think new users should be immediately prompted
    # to set up their accounts
    #
    # so for both students and teachers there should be a setup page and an
    # edit page, and then there should be a general teacher_lookup page that's
    # accessible by both students and teachers (but only students can star...?)
    #
    # btw there's no logout button yet on the setup pages--maybe a navbar and
    # a base template could be the next step (either by me or someone else) so
    # every page has the basic page tools like log out
    #
    # -- chris

    # check if email is whitelisted as a teacher, otherwise create student
    if session["email"] in TEACHERS:
        if not db.Teacher.get_teacher_id(session["email"]):
            db.Teacher.create_teacher(
                session["google_id"], session["name"], session["email"]
            )
            return redirect(url_for("setup_teacher"))
    else:
        if not db.Student.get_student_id(session["email"]):
            db.Student.create_student(
                session["google_id"], session["name"], session["email"]
            )
            return redirect(url_for("setup_student"))

    # this should go to either the student or teacher protected page
    return redirect(url_for("protected_area"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": session["token"]},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    session.clear()
    return redirect(url_for("index"))


@app.route("/protected_area", methods=["GET", "POST"])
@login_required
def protected_area():
    return render_template(
        "protected.html", name=session["name"], email=session["google_id"]
    )


@app.route("/setup_teacher", methods=["GET", "POST"])
@login_required
def setup_teacher():
    if not db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("setup_student"))
    return render_template(
        "setup_teacher.html", name=session["name"], email=session["email"]
    )


@app.route("/edit_teacherprofile", methods=["GET", "POST"])
def edit_teacher_profile():
    return render_template("edit_teacherprofile.html")


@app.route("/view_teacherprofile", methods=["GET", "POST"])
def view_teacher_profile():
    prefix = request.form.get("prefixes")
    name = request.form.get("name")
    pronouns = request.form.get("Pronouns")
    email = request.form.get("Email")
    filename = request.form.get("filename")



    return render_template("view_teacherprofile.html")


@app.route("/setup_student", methods=["GET", "POST"])
@login_required
def setup_student():
    if db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("setup_teacher"))

    teachers = db.Teacher.get_teacher_list()

    return render_template("setup_student.html", teacher_list=teachers)


@app.route("/upload_file_test", methods=["GET", "POST"])
def file_test():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(url_for("index"))

        file = request.files["file"]
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        if file.filename == "":
            flash("No selected file")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        upload_folder = "./app/uploads"
        path = os.path.join(upload_folder, filename)

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        file.save(path)

        db.Files.add_teacher_file("3", filename)
        fs = db.Files.get_teacher_files("3")
        print(fs)

        return redirect(url_for("index"))

    return render_template("upload_files.html")
