from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Record
from .forms import FilterForm
from . import db
import numpy as np
from sklearn.linear_model import LinearRegression
import datetime
import calendar
import time

charts = Blueprint('charts', __name__)

@charts.route('/charts', methods=['GET', 'POST'])
@login_required
def index():
    filter_form = FilterForm()

    r = db.aliased(Record)

    steps = 10

    # Main Graph
    labels = []

    records = db.session.query(r.costs, r.date).filter(r.user_id == current_user.id)

    if filter_form.filter_submit.data:
        if filter_form.filter_from.data:
            records = records.filter(r.date >= to_unix_time(filter_form.filter_from.data))
        if filter_form.filter_to.data:
            records = records.filter(r.date <= to_unix_time(filter_form.filter_to.data))

    records = records.order_by(r.date).all()

    if len(records) > 1:
        error = False

        if len(records) <= steps:
            ds = 1
        else:
            ds = len(records) / steps

        current_ds = -ds

        for index, record in enumerate(records):
            if (index >= (current_ds + ds)) or index == len(records) - 1:
                current_ds += ds
                labels.append(datetime.datetime.utcfromtimestamp(record.date).strftime('%d.%m'))
            else:
                labels.append('')
    else:
        error = True

    # Linear regression
    second_in_day = 60 * 60 * 24

    date_start = datetime.datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    date_end = to_unix_time(add_months(date_start, 1))

    date_start = to_unix_time(date_start)

    records_regression = db.session.query(r.costs, r.date).filter(r.user_id == current_user.id).filter(r.date >= date_start).\
        filter(r.date <= date_end).order_by(r.date).all()

    day_in_month = int((date_end - date_start) / second_in_day)

    y = [record.costs for record in records_regression]
    x = [(record.date - date_start) / second_in_day for record in records_regression]
    np_x = np.array(x).reshape((-1, 1))
    np_y = np.array(y)
    model = LinearRegression().fit(np_x, np_y)
    x_new = np.arange(31).reshape((-1, 1))
    y_new = model.predict(x_new)

    labels_regression = []

    ds = day_in_month / steps

    current_ds = -ds

    for index in range(day_in_month):
        if (index >= (current_ds + ds)) or index == day_in_month - 1:
            current_ds += ds
            labels_regression.append(datetime.datetime.fromtimestamp(date_start).strftime('%d.%m'))
        else:
            labels_regression.append('')

        date_start += second_in_day

    return render_template('charts.html', title='Charts', name=current_user.name, error=error,
                           labels="','".join(labels), labels_regression="','".join(labels_regression),
                           filter_form=filter_form, records=records, point_regression=",".join([str(y) for y in y]),
                           line_regression=",".join([str(y_new) for y_new in y_new]))

def to_unix_time(date):
    return int(time.mktime(date.timetuple()))

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)