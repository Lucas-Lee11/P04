import os
import pathlib

def setup():
    path = os.path.join(pathlib.Path(__file__).parent, "keys/key_oauth2.txt")
    with open("app/keys/key_oauth2.txt") as f:
        GOOGLE_CLIENT_ID = f.readline().strip()
        return GOOGLE_CLIENT_ID
