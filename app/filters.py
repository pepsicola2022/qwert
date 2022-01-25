import jinja2
from flask import Blueprint
from datetime import datetime

filters = Blueprint('filters', __name__)

@jinja2.contextfilter
@filters.app_template_filter()
def costFormat(context, value):
    return '{0:.2f}'.format(value)

@jinja2.contextfilter
@filters.app_template_filter()
def dateFormat(context, value):
    return datetime.utcfromtimestamp(value).strftime('%d.%m.%Y')