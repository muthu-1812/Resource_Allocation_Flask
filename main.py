import datetime
import json
from dataclasses import dataclass

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from sqlalchemy import func
from sqlalchemy.orm import load_only

app = Flask(__name__)
api = Api(app)

# create the extension
db = SQLAlchemy()
# create the app
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
# initialize the app with the extension
db.init_app(app)


@dataclass
class ProjectModel(db.Model):
    project_id: int
    project_name: str
    project_priority: int

    __tablename__ = 'project'
    project_id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String, unique=True, nullable=False)
    project_priority = db.Column(db.Integer, nullable=True)

    @property
    def serialize(self):
        return {
            'project_id': self.project_id,
            'project_name': self.project_name,
            'project_priority': self.project_priority
        }

    @property
    def get_project_id(self):
        return self.project_id


class DeveloperSkillModel(db.Model):
    __tablename__ = 'developer_skill'
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey("developer.developer_id"))

    @property
    def serialize(self):
        return {
            'skill_id': self.skill_id,
            'skill_name': self.skill_name,
            'developer_id': self.developer_id

        }

    @property
    def get_skill_id(self):
        return self.skill_id

    @property
    def get_developer_id(self):
        return self.developer_id


class DeveloperModel(db.Model):
    __tablename__ = 'developer'
    developer_id = db.Column(db.Integer, primary_key=True)
    developer_name = db.Column(db.String, nullable=False)

    @property
    def serialize(self):
        return {
            'developer_id': self.developer_id,
            'developer_name': self.developer_name,
        }

    @property
    def get_developer_id(self):
        return self.developer_id


class TaskModel(db.Model):
    __tablename__ = 'task'
    task_id = db.Column(db.Integer, primary_key=True)
    associated_project = db.Column(db.Integer, db.ForeignKey("project.project_id"))
    task_name = db.Column(db.String, unique=True, nullable=False)
    task_priority = db.Column(db.String, nullable=False)

    # todo below 2 should is redundant
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    @property
    def serialize(self):
        return {
            'task_id': self.task_id,
            'assoctated_project': self.associated_project,
            'task_priority': self.task_priority,
            'task_name': self.task_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }

    @property
    def get_task_id(self):
        return self.task_id


class ScheduleModel(db.Model):
    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.task_id"))
    allocated_developer = db.Column(db.Integer, db.ForeignKey("developer.developer_id"))
    task_status = db.Column(db.String, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    @property
    def serialize(self):
        return {
            'schedule_id': self.schedule_id,
            'task_id': self.task_id,
            'allocated_developer': self.allocated_developer,
            'task_status': self.task_status,
            'start_date': self.start_date,
            'end_date': self.end_date,
        }


class TaskSkill(db.Model):
    __tablename__ = 'task_skill'
    serial_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.task_id"))
    skill_name = db.Column(db.String)

    @property
    def serialize(self):
        return {
            'serial_id': self.serial_id,
            'skill_id': self.skill_id,
            'task_id': self.task_id,

        }


with app.app_context():
    db.create_all()


@app.route("/projects", methods=["GET", "POST"])
def Projects():
    if request.method == 'GET':
        projects = ProjectModel.query.all()

        # return jsonify([i.serialize for i in projects])
        return jsonify(projects)
    if request.method == 'POST':
        post_input = request.get_json()
        project_name = post_input['projectName']
        project_priority = post_input['projectPriority']
        entry = ProjectModel(project_name=project_name, project_priority=project_priority)
        db.session.add(entry)
        db.session.commit()
        return entry.serialize


@app.route("/projects/<project_id>", methods=["GET", "POST"])
def Project_Endpoint(project_id):
    if request.method == 'GET':
        fields = ['project_name']
        query = ProjectModel.query.filter(ProjectModel.project_id == project_id).with_entities(ProjectModel.project_id,
                                                                                               ProjectModel.project_name)
        # query = ProjectModel.query.filter(ProjectModel.project_id == project_id)
        # query = ProjectModel.query(project_id).filter(ProjectModel.project_id.in_((1, 2)))
        results = query.all()

        # return jsonify([i.serialize for i in results])

        # return jsonify(json_list=results)

        return str(results[0]["project_id"])


@app.route("/skills", methods=["GET", "POST"])
def Skills():
    if request.method == 'GET':
        skills = DeveloperSkillModel.query.all()

        return jsonify([i.serialize for i in skills])

    if request.method == 'POST':
        post_input = request.get_json()
        skill_name = post_input['skill_name']

        entry = DeveloperSkillModel(skill_name=skill_name)
        db.session.add(entry)
        db.session.commit()
        return entry.serialize


@app.route("/developers", methods=["GET", "POST"])
def Developers():
    if request.method == 'GET':
        resources = DeveloperModel.query.all()

        return jsonify([i.serialize for i in resources])

    if request.method == 'POST':
        post_input = request.get_json()
        developer_name = post_input['developer_name']
        entry = DeveloperModel(developer_name=developer_name)
        db.session.add(entry)
        db.session.commit()
        develper_id = entry.get_developer_id
        developer_skills = post_input['developer_skills']

        for skill in developer_skills:
            skill_entry = DeveloperSkillModel(skill_name=skill, developer_id=develper_id)
            db.session.add(skill_entry)
            db.session.commit()
            skill_id = skill_entry.get_skill_id

            app.logger.info('%s created skill id', skill_id)
        return "Success"

#TODO I have 3 separate db write I should make it acid compliant
@app.route("/tasks", methods=["GET", "POST"])
def Tasks():
    if request.method == 'GET':
        resources = TaskModel.query.all()

        return jsonify([i.serialize for i in resources])

    if request.method == 'POST':
        post_input = request.get_json()
        associated_project = post_input['associated_project']
        task_name = post_input['task_name']
        task_priority = post_input['task_priority']
        task_skills = post_input['task_skills']
        start_date = datetime.datetime.fromisoformat(post_input['start_date'])
        end_date = datetime.datetime.fromisoformat(post_input['end_date'])

        task_entry = TaskModel(task_name=task_name, associated_project=associated_project, task_priority=task_priority,
                               start_date=start_date, end_date=end_date)
        db.session.add(task_entry)
        db.session.commit()
        task_id = task_entry.get_task_id

        for skill in task_skills:
            skill_entry = TaskSkill(task_id=task_id, skill_name=skill)
            db.session.add(skill_entry)

        db.session.commit()

        records = db.session.query(DeveloperSkillModel.developer_id,
                                   db.func.count(DeveloperSkillModel.developer_id).label("skill_count")) \
            .filter(DeveloperSkillModel.skill_name.in_(task_skills)) \
            .group_by(DeveloperSkillModel.developer_id) \
            .order_by("skill_count") \
            .all()
        app.logger.info(str(len(records)))

        developers_with_required_skills = []

        for record in records:
            app.logger.info(str(record['skill_count']) + " " + str(record['developer_id']))
            developers_with_required_skills.append(record['developer_id'])

        if len(records) == 0:
            return "No resources with required skills "

        busy_developer_records = db.session.query(ScheduleModel.allocated_developer) \
            .filter(ScheduleModel.allocated_developer.in_(developers_with_required_skills)
                    , ScheduleModel.start_date <= start_date, ScheduleModel.end_date >= ScheduleModel.end_date).all()

        busy_developers = []
        for record in busy_developer_records:
            busy_developers.append(record['allocated_developer'])

        app.logger.info("Busy developers %s", str(busy_developers))

        viable_developers = [x for x in developers_with_required_skills if x not in busy_developers]
        app.logger.info("no of viable developers %s", str(len(viable_developers)))

        if len(viable_developers) == 0:
            return "Resources with required skills are busy please set another date for task using put request"

        schedule_entry = ScheduleModel(task_id=task_id, allocated_developer=viable_developers[0],
                                       task_status="ASSIGNED",

                                       start_date=start_date, end_date=end_date)
        db.session.add(schedule_entry)
        db.session.commit()

        return "Sucess"


@app.route("/")
def hello():
    return "Hello World"


# api.add_resource(Projects, '/projects')
# app.register_blueprint(project_api)

if __name__ == '__main__':
    app.run(debug=True)  # run our Flask app
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
