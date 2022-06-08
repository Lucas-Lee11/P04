#!/usr/bin/python
import sys
import logging
from os import urandom

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/P04/")
sys.path.insert(0,"/var/www/P04/app/")

def application(environ, start_response):
    from app import app as _application
    return _application(environ, start_response)

if __name__ == "__main__":
    _application.run()
