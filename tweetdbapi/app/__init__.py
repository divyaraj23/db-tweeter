from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kfopqaazqonabh:e2dbbd44ad7c785d56146028dee9e6b2cf640321b6488f929ba8380d0447af46@ec2-50-19-32-96.compute-1.amazonaws.com:5432/d9r9ag8p9ffcir'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "02]zz^`{JO3+P~f<'fC.WQpL,+Q9Ph"
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

db = SQLAlchemy(app)
ma = Marshmallow(app)
jt = JWTManager(app)


db.create_all()

from app import routes