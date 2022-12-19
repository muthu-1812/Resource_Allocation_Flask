
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Project import project_endpoint
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String, unique=True, nullable=False)


with app.app_context():
    db.create_all()


api.add_resource(project_endpoint, '/project')  # add endpoints
# api.add_resource(Locations, '/locations')

if __name__ == '__main__':
    app.run()  # run our Flask app
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
