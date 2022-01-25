from flask import make_response, Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import Category, Record
from .forms import FilterForm, RecordForm
from sqlalchemy import desc
from . import db
import xlsxwriter
import tempfile
import datetime
import time
import os

main = Blueprint('main', __name__)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    categories = Category.query.all()

    record_form = RecordForm()

    record_form.category.choices = [(c.id, c.name) for c in categories]

    filter_form = FilterForm()

    filter_form.filter_category.choices = [(0, "")] + [(c.id, c.name) for c in categories]

    if record_form.submit.data and record_form.validate():

        db.session.add(Record(user_id=current_user.id, income=record_form.income.data, costs=record_form.costs.data,
                              date=to_unix_time(record_form.date.data),
                              reason=record_form.reason.data, category_id=record_form.category.data))
        db.session.commit()

        return redirect(url_for('main.profile'))

    r = db.aliased(Record)
    c = db.aliased(Category)

    records = db.session.query(r.income, r.costs, r.date, r.reason, c.name).\
        filter(r.user_id==current_user.id)

    if filter_form.filter_submit.data:
        if filter_form.filter_category.data:
            records = records.filter(r.category_id==filter_form.filter_category.data)
        if filter_form.filter_from.data:
            records = records.filter(r.date >= to_unix_time(filter_form.filter_from.data))
        if filter_form.filter_to.data:
            records = records.filter(r.date <= to_unix_time(filter_form.filter_to.data))

    records = records.join(c, c.id == r.category_id).order_by(desc(r.id)).limit(10).all()

    return render_template('profile.html', title='Records', name=current_user.name, record_form=record_form,
                           filter_form=filter_form, records=records)

@main.route('/download')
@login_required
def download():
    temp_name = next(tempfile._get_candidate_names())

    temp_dir = tempfile.mkdtemp()

    temp_name = os.path.join(temp_dir, temp_name)

    workbook = xlsxwriter.Workbook(temp_name)
    worksheet = workbook.add_worksheet()

    bold = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Income', bold)
    worksheet.write('B1', 'Costs', bold)
    worksheet.write('C1', 'Date and time', bold)
    worksheet.write('D1', 'Reason', bold)
    worksheet.write('E1', 'Category', bold)

    r = db.aliased(Record)
    c = db.aliased(Category)

    records = db.session.query(r.income, r.costs, r.date, r.reason, c.name).\
        filter(r.user_id==current_user.id).join(c, c.id == r.category_id).order_by(r.id).all()

    index = 1

    for record in records:
        index += 1

        worksheet.write('A%d' % index, record.income)
        worksheet.write('B%d' % index, record.costs)
        worksheet.write('C%d' % index, datetime.datetime.utcfromtimestamp(record.date).strftime('%d.%m.%Y'))
        worksheet.write('D%d' % index, record.reason)
        worksheet.write('E%d' % index, record.name)

    workbook.close()

    with open(temp_name, mode='rb') as file:
        data = file.read()

    response = make_response(data)

    os.remove(temp_name)
    os.rmdir(temp_dir)

    response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response.headers.set('Content-Disposition', 'attachment; filename=Report.xlsx')
    return response

def to_unix_time(date):
    return int(time.mktime(date.timetuple()))