from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy

from models import db
from views import project_bp, developer_bp


def create_app():
    app = Flask(__name__)
    home = Blueprint('home', __name__)

    @home.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    app.register_blueprint(home)
    app.register_blueprint(project_bp)
    app.register_blueprint(developer_bp)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

    SQLAlchemy(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    create_app().run(debug=True)  # run our Flask app
