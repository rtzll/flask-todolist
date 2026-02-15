# pyright: reportImportCycles=false

from flask import Blueprint

auth = Blueprint("auth", __name__)

from . import views
