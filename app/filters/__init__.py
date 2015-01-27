# -*- coding: utf-8 -*-

from flask import Blueprint

filters_blueprint = Blueprint('filters_blueprint', __name__)

from . import filters
