from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from backend.configs import flask_config

app = Flask(__name__)
app.config.from_object(flask_config)
db = SQLAlchemy(app)

from backend.views import main

app.register_blueprint(main)
