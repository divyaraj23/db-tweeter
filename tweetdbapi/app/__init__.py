from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from flask_bootstrap import Bootstrap
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tweets.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "02]zz^`{JO3+P~f<'fC.WQpL,+Q9Ph"
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

db = SQLAlchemy(app)
ma = Marshmallow(app)
jt = JWTManager(app)
Bootstrap(app)

db.create_all()

from app import routes