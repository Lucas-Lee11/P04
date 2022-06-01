# Team Loophole -- Lucas Lee, Andrew Juang, Eliza Knapp, Ella Krechmer, Christopher Liu
# Softdev
# P04 -- Final Project
# 2022-06-15w

from os import urandom
from flask import Flask

app = Flask(__name__)

from app import routes

# Secret key 32 bytes (lowkey this is useless dwai)
app.secret_key = urandom(32)

app.debug = True

# if __name__ == "__main__":
app.run()

