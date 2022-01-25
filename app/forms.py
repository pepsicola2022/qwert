from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import DateField, FloatField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired

class FilterForm(FlaskForm):
    filter_from = DateField('Date from')
    filter_to = DateField('Date to')
    filter_category = SelectField('Category', coerce=int)
    filter_submit = SubmitField('Apply')

class RecordForm(FlaskForm):
    income = FloatField('Income', validators=[DataRequired()])
    costs = FloatField('Costs', validators=[DataRequired()])
    date = DateField('Date and time', validators=[DataRequired()])
    reason = StringField('Reason', validators=[DataRequired()])
    category = SelectField('Category', coerce=int)
    submit = SubmitField('Add')