from flask import Blueprint

web = Blueprint('web', __name__)

from app.web import auth
from app.web import errors
from app.web import assign
from app.web import accept
from app.web import task
from app.web import test

