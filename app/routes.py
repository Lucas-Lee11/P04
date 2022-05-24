# Here are where all of the routes will go
from app import app
from flask import render_template, redirect, request, url_for, session

@app.route("/", methods=['GET', 'POST'])
def index():
  return render_template('gen_login.html')