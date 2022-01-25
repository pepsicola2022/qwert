#!/usr/bin/python3
from app import app, db
from app.models import Category, Record, User
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from random import randrange
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import time

migrate = Migrate(app, db)
manager = Manager(app)

@manager.command
def init():
    "Insert Init Data"
    email = input("Enter email: ")
    name = input("Enter name: ")
    password = generate_password_hash(input("Enter password: "), method='sha256')

    db.create_all()
    db.session.commit()

    db.session.add(User(email=email,
                        password=password,
                        name=name))
    db.session.commit()

    categories = ["Транспорт", "Аптека", "Дом", "Одежда", "Супермаркет", "Такси", "Прочее"]

    for name in categories:
        db.session.add(Category(name=name))
        db.session.commit()

    date = (datetime.today() - timedelta(days = 60)).replace(hour = 0, minute = 0, second = 0, microsecond = 0)

    for index in range(60):
        db.session.add(Record(user_id=1, income=(500.0 + randrange(100000) / 100.0), costs=(500.0 + randrange(100000) / 100.0),
                              date=int(time.mktime(date.timetuple())),
                              reason="Record %s" % (index + 1), category_id=(randrange(len(categories)) + 1)))

        db.session.commit()

        date += timedelta(days=1)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
	manager.run()