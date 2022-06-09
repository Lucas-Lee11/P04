#!/usr/bin/python
import sys
import logging
from os import urandom

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/P04/")
sys.path.insert(0, "/var/www/P04/app/")

from app import app as application
