# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import functools
import os
import pathlib
import requests

from flask import redirect, render_template, request, session, url_for, flash, send_file
from pip._vendor import cachecontrol
import google.auth.transport.requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow

from app import app
from app import database as db
from app import secret

# env variable to bipass https
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
UPLOAD_FOLDER = "./app/uploads"

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
TEACHERS = [
    "cliu20@stuy.edu",
    "ekrechmer20@stuy.edu",
    "eknapp20@stuy.edu",
    "llee20@stuy.edu",
]


def login_required(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            flash("Not Google Authenticated")
            return redirect(url_for("index"))
        else:
            return function(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET", "POST"])
def index():
    # this should redirect to /teacher and /student for logged in users
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
    if session["email"] in TEACHERS:
        if not db.Teacher.get_teacher_id(session["email"]):
            db.Teacher.create_teacher(
                session["google_id"], session["name"], session["email"]
            )
            return redirect(url_for("setup_teacher"))
        return redirect(url_for("teacher"))
    else:
        if not db.Student.get_student_id(session["email"]):
            db.Student.create_student(
                session["google_id"], session["name"], session["email"]
            )
        return redirect(url_for("student"))


@app.route("/logout", methods=["GET", "POST"])
def logout():

    if "token" in session:
        requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": session["token"]},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

    session.clear()

    flash("Logged Out")
    return redirect(url_for("index"))


@app.route("/setup_teacher", methods=["GET", "POST"])
@login_required
def setup_teacher():
    if not db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("setup_student"))

    teachers = db.Teacher.get_teacher_list()
    return render_template(
        "setup_teacher.html",
        name=session["name"],
        email=session["email"],
        teacher_list=teachers,
    )


# this is the page that a teacher who has already set up their account will land on
@app.route("/teacher", methods=["GET", "POST"])
@login_required
def teacher():
    if not db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("setup_student"))

    teachers = db.Teacher.get_teacher_list()

    return render_template(
        "teacher_landing.html", name=session["name"], teacher_list=teachers
    )


@app.route("/edit_teacherprofile", methods=["GET", "POST"])
@login_required
def edit_teacherprofile():
    teachers = db.Teacher.get_teacher_list()
    
    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    print(schedule_info)
    schedule = []
    for period in schedule_info:
        if not period:
            pass
        else:
            schedule.append(period.split(":"))
    teachers = db.Teacher.get_teacher_list()

    # for now, name and email are temporary
    return render_template("edit_teacherprofile.html", teacher_list=teachers, schedule=schedule, name=session["name"], email=session["email"])


@app.route("/update_teacherprofile", methods=["GET", "POST"])
@login_required  # QUESTION- do you need to be logged in to see the teacher profile
def update_teacherprofile():
    prefix = request.form.get("prefixes")
    name = request.form.get("name")
    pronouns = request.form.get("Pronouns")
    email = request.form.get("Email")
    filename = request.form.get("filename")
    # TODO: CREATE A DB METHOD that takes into account
    # all of the following info to push to the database
    # TODO: CREATE A DB METHOD that gets all of this 
    # information from where it resides in the db

    # for now, i will use the info we have already

    classes = []
    for i in range(10):
        data = []
        data.append(request.form.get("class" + str(i + 1)))
        data.append(request.form.get("status" + str(i + 1)))
        classes.append(data)

    teacher_id = session["google_id"]
    for i, group in enumerate(classes):
        db.Teacher.add_schedule_period(teacher_id, i + 1, group[1])

    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    print(schedule_info)
    schedule = []
    for period in schedule_info:
        if not period:
            pass
        else:
            schedule.append(period.split(":"))
    teachers = db.Teacher.get_teacher_list()

    # the name and email thing WILL BE CHANGED LATER WHEN THE DB FUNCTIONS ARE UPDATED
    return render_template("view_teacherprofile.html", teacher_list=teachers, schedule=schedule, name=session["name"], email=session["email"])

@app.route("/view_teacherprofile", methods=["GET", "POST"])
@login_required 
def view_teacherprofile():
    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    print(schedule_info)
    schedule = []
    for period in schedule_info:
        if not period:
            pass
        else:
            schedule.append(period.split(":"))
    teachers = db.Teacher.get_teacher_list()

    # the name and email thing WILL BE CHANGED LATER WHEN THE DB FUNCTIONS ARE UPDATED
    return render_template("view_teacherprofile.html", teacher_list=teachers, schedule=schedule, name=session["name"], email=session["email"])


# hello- when you log in, that should just always take you to setup student
# there isn't really any setup, so I've renamed to just student so that it's
# equivalent to the teacher route -Eliza
# yes that sounds good -Chris
@app.route("/student", methods=["GET", "POST"])
@login_required
def student():
    if db.Teacher.verify_teacher(session["google_id"]):
        # if it somehow gets here, just return the normal teacher
        # thing so we don't need to pass in form data
        return redirect(url_for("teacher"))

    if request.method == "POST":
        print(request.form.getlist("starred"))

    teachers = db.Teacher.get_teacher_list()

    # teachers = ["daisy sharf", "dw", "topher myklolyk"]

    return render_template("student.html", teacher_list=teachers)


@app.route("/upload_file_test", methods=["GET", "POST"])
@login_required
def file_upload_test():
    if not db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("index"))

    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(url_for("index"))

        files = request.files.getlist("file")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        for file in files:

            if file.filename == "":
                flash("No selected file")
                return redirect(url_for("index"))

            db.Files.add_teacher_file(session["google_id"], file)

        return redirect(url_for("index"))

    return render_template("upload_files.html")


@app.route("/view_files_test", methods=["GET", "POST"])
@login_required
def file_view_test():
    if not db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("index"))

    files = db.Files.get_teacher_files(session["google_id"])
    print(files)

    return render_template("view_files.html", files=files)


@app.route("/file/<path:filename>", methods=["GET", "POST"])
@login_required
def download_file(filename):

    if not os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        flash("Invalid File")
        return redirect(url_for("index"))

    return send_file(f"./uploads/{filename}")
