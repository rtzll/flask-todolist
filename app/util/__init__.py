# -*- coding: utf-8 -*-

from flask import Blueprint

util = Blueprint('util', __name__)

from . import filters
