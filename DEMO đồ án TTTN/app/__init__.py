from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')
db = SQLAlchemy(app)

from app import views, controllers
