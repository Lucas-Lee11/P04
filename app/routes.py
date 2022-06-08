# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

import csv
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
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 #10MB
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

# whitelisted tseachers here for now
TEACHERS = [
    "cliu20@stuy.edu",
    # "ekrechmer20@stuy.edu",
    "llee20@stuy.edu",
    # "ajuang20@stuy.edu",
    "eknapp20@stuy.edu"
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


def teacher_required(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            flash("Not Google Authenticated")
            return redirect(url_for("index"))

        if not db.Teacher.verify_teacher(session["google_id"]):
            flash("Not a Teacher Account")
            return redirect(url_for("student"))

        else:
            return function(*args, **kwargs)

    return wrapper


@app.route("/", methods=["GET", "POST"])
def index():
    if "google_id" in session:
        if db.Teacher.verify_teacher(session["google_id"]):
            return redirect(url_for("teacher"))
        else:
            return redirect(url_for("student"))

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

    try:
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID,
        )
    except Exception as e:
        flash("Login Error")
        return redirect(url_for("index"))

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
            return redirect(url_for("edit_teacherprofile"))
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


# this is the page that a teacher who has already set up their account will land on
@app.route("/teacher", methods=["GET", "POST"])
@teacher_required
def teacher():
    return render_template(
        "teacher_landing.html", name=session["name"], is_teacher=True
    )


@app.route("/teacher/edit", methods=["GET"])
@teacher_required
def edit_teacherprofile():
    info = db.Teacher.get_teacher_info(session["google_id"])
    info = tuple("" if data is None else data for data in info)
    name, email, pronouns, title = info

    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    schedule = []
    for period in schedule_info:
        if not period:
            pass
        else:
            schedule.append(period.split(":"))
    print(schedule)

    files = db.Files.get_teacher_files(session["google_id"])

    # for now, name and email are temporary
    return render_template(
        "edit_teacherprofile.html",
        schedule=schedule,
        name=session["name"],
        email=session["email"],
        pronouns=pronouns,
        title=title,
        files=files,
        is_teacher=True,
    )


@app.route("/teacher/edit", methods=["POST"])
@login_required
def update_teacherprofile():

    prefix = request.form.get("prefixes")
    name = request.form.get("name")
    pronouns = request.form.get("pronouns")
    email = request.form.get("email")

    db.Teacher.add_teacher_name(session["google_id"], name)
    db.Teacher.add_teacher_title(session["google_id"], prefix)
    db.Teacher.add_teacher_email(session["google_id"], email)
    db.Teacher.add_teacher_pronouns(session["google_id"], pronouns)

    existing_files = [filename for file_id, filename in db.Files.get_teacher_files(session["google_id"])]
    if "file" in request.files:
        files = request.files.getlist("file")
        for file in files:
            if file.filename != "":
                if file.filename in existing_files:
                    flash(f"File {file.filename} already exists, please delete it first")
                else:
                    db.Files.add_teacher_file(session["google_id"], file)

    for file_id in request.form.getlist("delete_file"):
        db.Files.remove_teacher_file(session["google_id"], file_id)

    classes = []
    for i in range(10):
        data = []
        data.append(request.form.get("class" + str(i + 1)))
        data.append(request.form.get("status" + str(i + 1)))
        classes.append(data)

    schedule_upload = request.files["schedule_upload"].read().decode("utf-8")
    if schedule_upload:
        classes = []
        schedule_data = schedule_upload.splitlines()
        reader = csv.reader(schedule_data[1:])
        for row in reader:
            if not row[1]:
                row[1] = "Never free (teaching)" if row[0] else "Free for walk-ins"
            classes.append(row)

    print(classes)

    teacher_id = session["google_id"]
    for i, group in enumerate(classes):
        db.Teacher.add_schedule_period(teacher_id, i + 1, group[0] + ":" + group[1])

    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    print(schedule_info)
    schedule = []
    for period in schedule_info:
        if not period:
            pass
        else:
            schedule.append(period.split(":"))

    return redirect(url_for("view_teacherprofile"))


@app.route("/teacher/view", methods=["GET", "POST"])
@login_required
def view_teacherprofile():
    name, email, pronouns, title = db.Teacher.get_teacher_info(session["google_id"])

    schedule = []
    for i in range(10):
        schedule.append(["", ""])
    schedule_info = db.Teacher.get_schedule_periods(session["google_id"])
    if None not in schedule_info:
        schedule = []
        for period in schedule_info:
            if not period:
                pass
            else:
                schedule.append(period.split(":"))

    files = db.Files.get_teacher_files(session["google_id"])

    is_teacher = db.Teacher.verify_teacher(session["google_id"])

    # the name and email thing WILL BE CHANGED LATER WHEN THE DB FUNCTIONS ARE UPDATED
    return render_template(
        "view_teacherprofile.html",
        schedule=schedule,
        name=name,
        email=email,
        prefix=title,
        pronouns=pronouns,
        files=files,
        is_teacher=is_teacher,
    )


@app.route("/student", methods=["GET", "POST"])
@login_required
def student():
    if db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("teacher"))

    ####### FOR TESTING PURPOSES #######
    db.Teacher.create_db()
    db.Teacher.create_teacher("sharaf_id", "Daisy Sharaf", "dsharaf@stuy.edu")
    db.Teacher.create_teacher("stern_id", "Joseph Stern", "jstern@stuy.edu")
    db.Teacher.create_teacher("dw_id", "Jonalf Dyrland-Weaver", "dw@stuy.edu")
    db.Teacher.create_teacher("chew_id", "Glen Chew", "gchew@stuy.edu")
    ####################################

    if request.method == "POST":
        starred_id = request.form.getlist("starred_id")
        for teacher_id in starred_id:
            if not db.StarredTeachers.starred_relationship_exists(
                session["google_id"], teacher_id
            ):
                db.StarredTeachers.star_teacher(session["google_id"], teacher_id)

        removed_id = request.form.get("remove_star")
        db.StarredTeachers.unstar_teacher(session["google_id"], removed_id)

    teachers = db.Teacher.get_teacher_list()
    starred_teachers_hex = db.StarredTeachers.get_student_stars(session["google_id"])

    # Fetches the relevant teacher information of a student's starred teachers
    starred_teachers = []
    for teacher_hex in starred_teachers_hex:
        teacher_id = db.Teacher.hex_to_teacher_id(teacher_hex)
        starred_teachers.append((teacher_hex,db.Teacher.get_teacher_name(teacher_id)))

    return render_template(
        "student.html", teachers=teachers, starred_teachers=starred_teachers, starred_teachers_hex = starred_teachers_hex
    )


@app.route("/starred_teachers", methods=["GET", "POST"])
@login_required
def starred_teachers():
    if db.Teacher.verify_teacher(session["google_id"]):
        return redirect(url_for("teacher"))

    # Remove teacher star
    if request.method == "POST":
        removed_hex = request.form.get("remove_star")
        db.StarredTeachers.unstar_teacher(session["google_id"], removed_hex)

    # Get list of starred teachers
    starred_teachers_hex = db.StarredTeachers.get_student_stars(session["google_id"])

    # Fetches the relevant teacher information of a student's starred teachers
    starred_teachers = []
    for teacher_hex in starred_teachers_hex:
        teacher_id = db.Teacher.hex_to_teacher_id(teacher_hex)
        starred_teachers.append((teacher_hex,db.Teacher.get_teacher_name(teacher_id)))

    return render_template("starred_teachers.html", starred_teachers=starred_teachers)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    teacher_searched = request.form.get("teacher")
    print("THE FOLLOWING IS THE TEACHER SEARCHED")
    print(teacher_searched)
    info = []
    # the following assumes there will be one hit exactly
    if db.Teacher.get_teacher_id_name(teacher_searched):
        teacher_ids = db.Teacher.get_teacher_id_name(teacher_searched)

        info = []
        for id in teacher_ids:
            hex_and_info = []
            hex_and_info.append(db.Teacher.teacher_id_to_hex(id[0]))
            hex_and_info.append(db.Teacher.get_teacher_info(id[0]))
            info.append(hex_and_info)

        print(info)
    return render_template("student_searchresults.html", info=info)


@app.route("/schedule/<hex>", methods=["GET", "POST"])
@login_required
def view_teacher(hex):

    teacher_id = db.Teacher.hex_to_teacher_id(hex)
    name, email, pronouns, title = db.Teacher.get_teacher_info(teacher_id)

    schedule = []
    for i in range(10):
        schedule.append(["", ""])
    print("CALL 1")
    print(schedule)
    schedule_info = db.Teacher.get_schedule_periods(teacher_id)
    if None not in schedule_info:
        print(schedule_info)
        schedule = []
        for period in schedule_info:
            if not period:
                pass
            else:
                schedule.append(period.split(":"))
        print(schedule)

    files = db.Files.get_teacher_files(teacher_id)

    is_teacher = db.Teacher.verify_teacher(session["google_id"])

    # the name and email thing WILL BE CHANGED LATER WHEN THE DB FUNCTIONS ARE UPDATED
    return render_template(
        "view_teacherprofile.html",
        schedule=schedule,
        name=name,
        email=email,
        prefix=title,
        pronouns=pronouns,
        files=files,
        is_teacher=is_teacher,
    )

    teachers = db.Teacher.get_teacher_list()

    return render_template(
        "view_teacherprofile.html",
        teacher_list=teachers,
        name=name,
        prefix=prefix,
        email=email,
        pronouns=pronouns,
        schedule=schedule,
    )


@app.route("/file/<file_id>", methods=["GET", "POST"])
@login_required
def download_file(file_id):
    teacher_id, filename = db.Files.get_file_info(file_id)

    if not os.path.exists(os.path.join(UPLOAD_FOLDER, teacher_id, filename)):
        flash("Invalid File")
        return redirect(url_for("index"))

    return send_file(f"./uploads/{teacher_id}/{filename}")
