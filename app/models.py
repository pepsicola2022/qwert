from flask_login import UserMixin
from . import db

class Category(UserMixin, db.Model):
	__tablename__ = 'po_categories'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1000))

class Record(UserMixin, db.Model):
	__tablename__ = 'po_records'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	income = db.Column(db.Float)
	costs = db.Column(db.Float)
	date = db.Column(db.Integer)
	reason = db.Column(db.String(100))
	category_id = db.Column(db.Integer)

class User(UserMixin, db.Model):
	__tablename__ = 'po_users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(1000))