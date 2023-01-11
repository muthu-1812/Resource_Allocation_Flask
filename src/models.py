import datetime
from dataclasses import dataclass

from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


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
    def get_project_id(self):
        return self.project_id

    def get_project_details_by_id(_id):
        project_query = ProjectModel.query.filter_by(project_id=_id).first()
        task_output = TaskModel.get_tasks_names_for_project(_id)
        result = jsonify(project_query).get_json()
        result['tasks'] = task_output

        return result

    @staticmethod
    def get_all_projects():
        query = ProjectModel.query.all()
        return jsonify(query)

    def get_project_by_id(_id):
        query = ProjectModel.query.filter_by(project_id=_id).first()

        return jsonify(query)

    @staticmethod
    def add_project(post_input):
        entry = ProjectModel(project_name=post_input['projectName'], project_priority=post_input['projectPriority'])
        db.session.add(entry)
        db.session.commit()
        return str(entry.project_id)


@dataclass
class DeveloperModel(db.Model):
    developer_id: int
    developer_name: str

    __tablename__ = 'developer'
    developer_id = db.Column(db.Integer, primary_key=True)
    developer_name = db.Column(db.String, nullable=False)

    @staticmethod
    def get_all_developers():
        query = DeveloperModel.query.all()
        return jsonify(query)

    @staticmethod
    def add_developer(post_input):
        entry = DeveloperModel(developer_name=post_input['developer_name'])
        db.session.add(entry)
        db.session.commit()
        return str(entry.developer_id)

    @staticmethod
    def update_developer(post_input, developer_id):
        record = DeveloperModel.query.filter_by(developer_id=developer_id).first()
        if post_input['developer_name']:
            record.developer_name = post_input["developer_name"]

        db.session.commit()
        return record.developer_id

    def developer_details_by_id(_id):
        developer_query = DeveloperModel.query.filter_by(developer_id=_id).first()
        skill_output = DeveloperSkillModel.get_skills_for_developer(_id)
        result = jsonify(developer_query).get_json()
        result['skills'] = skill_output

        return result

    @property
    def get_developer_id(self):
        return self.developer_id


@dataclass()
class DeveloperSkillModel(db.Model):
    skill_id: int
    skill_name: str
    developer_id: int

    __tablename__ = 'developer_skill'
    skill_id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String, nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey("developer.developer_id"))

    @staticmethod
    def get_skills_for_developer(developer_id):
        db_records = DeveloperSkillModel.query.filter_by(developer_id=developer_id).all()
        developer_skills = [record.skill_name for record in db_records]
        return developer_skills

    @staticmethod
    def add_skills_for_developer(post_input, developer_id):
        for skill in post_input['developer_skills']:
            skill_entry = DeveloperSkillModel(skill_name=skill, developer_id=developer_id)
            db.session.add(skill_entry)
        db.session.commit()

    @staticmethod
    def update_skills_for_developer(post_input, developer_id):
        db_records = DeveloperSkillModel.query.filter_by(developer_id=developer_id).all()

        updated_skills = post_input['developer_skills']

        existing_skill_names = [record.skill_name for record in db_records]

        delete_skills = list(set(existing_skill_names) - set(updated_skills))

        add_skill = list(set(updated_skills) - set(existing_skill_names))

        for skill in delete_skills:
            DeveloperSkillModel.query.filter_by(skill_name=skill, developer_id=developer_id).delete()

        for skill in add_skill:
            skill_entry = DeveloperSkillModel(skill_name=skill, developer_id=developer_id)
            db.session.add(skill_entry)

        db.session.commit()

        return "Success"

    @property
    def get_skill_id(self):
        return self.skill_id

    @property
    def get_developer_id(self):
        return self.developer_id

    @staticmethod
    def find_developers_with_matching_skills(post_input):
        required_skills = post_input["task_skills"]

        records = db.session.query(DeveloperSkillModel.developer_id,
                                   db.func.count(DeveloperSkillModel.developer_id).label("skill_count")) \
            .filter(DeveloperSkillModel.skill_name.in_(required_skills)) \
            .group_by(DeveloperSkillModel.developer_id) \
            .order_by("skill_count") \
            .all()

        developers_with_required_skills = []

        for record in records:
            # app.logger.info(str(record['skill_count']) + " " + str(record['developer_id']))
            developers_with_required_skills.append(record['developer_id'])

        return developers_with_required_skills


@dataclass()
class TaskModel(db.Model):
    task_id: int
    associated_project: int
    task_name: str
    task_priority: int
    start_date: datetime.datetime
    end_date: datetime.datetime

    __tablename__ = 'task'
    task_id = db.Column(db.Integer, primary_key=True)
    associated_project = db.Column(db.Integer, db.ForeignKey("project.project_id"))
    task_name = db.Column(db.String, unique=True, nullable=False)
    task_priority = db.Column(db.String, nullable=False)
    skills = db.relationship("TaskSkillModel", lazy=True, backref='task')

    # todo below 2 should remove is redundant
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def get_all_tasks():
        query = TaskModel.query.all()
        return jsonify(query)

    @staticmethod
    def add_task(post_input,start_date,end_date):

        task_entry = TaskModel(task_name=post_input['task_name'], associated_project=post_input['associated_project'],
                               task_priority=post_input['task_priority'],
                               start_date=start_date, end_date=end_date)

        db.session.add(task_entry)
        db.session.commit()

        return task_entry.task_id

    @property
    def get_task_id(self):
        return self.task_id

    @staticmethod
    def get_tasks_names_for_project(_id):
        db_records = TaskModel.query.filter_by(associated_project=_id).all()
        tasks = [record.task_name for record in db_records]
        return tasks

    @staticmethod
    def get_task_details_for_project(_id):
        task_records = TaskModel.query.filter_by(associated_project=_id).all()

        # task_records = TaskModel.query \
        #     .filter_by(associated_project=_id) \
        #     .join(TaskSkillModel, TaskModel.task_id == TaskSkillModel.task_id) \
        #     .add_columns(db.func.group_concat(TaskSkillModel.task_id).label("skills")) \
        #     .group_by(TaskModel.task_id).all()

        # return str(task_records[0].skills)

        return jsonify(task_records)
#

@dataclass()
class TaskSkillModel(db.Model):
    serial_id: int
    task_id: int
    skill_name: str

    __tablename__ = 'task_skill'
    serial_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.task_id"))
    skill_name = db.Column(db.String)

    @staticmethod
    def add_skills_for_task(task_skills, task_id):
        for skill in task_skills:
            skill_entry = TaskSkillModel(skill_name=skill, task_id=task_id)
            db.session.add(skill_entry)
        db.session.commit()


@dataclass()
class ScheduleModel(db.Model):
    schedule_id: int
    task_id: int
    allocated_developer: int
    task_status: str
    start_date: datetime.datetime
    end_date = datetime.datetime

    __tablename__ = 'schedule'
    schedule_id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("task.task_id"))
    allocated_developer = db.Column(db.Integer, db.ForeignKey("developer.developer_id"))
    task_status = db.Column(db.String, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)

    @staticmethod
    def find_busy_developers(post_input, developers_with_required_skills):
        start_date = datetime.datetime.fromisoformat(post_input['start_date'])
        end_date = datetime.datetime.fromisoformat(post_input['end_date'])
        busy_developer_records = db.session.query(ScheduleModel.allocated_developer) \
            .filter(ScheduleModel.allocated_developer.in_(developers_with_required_skills)
                    , ScheduleModel.start_date <= start_date, ScheduleModel.end_date >= end_date).all()

        busy_developers = []
        for record in busy_developer_records:
            busy_developers.append(record['allocated_developer'])

        return busy_developers

    @staticmethod
    def create_schedule_for_task(task_id, viable_developers, post_input):
        start_date = datetime.datetime.fromisoformat(post_input['start_date'])
        end_date = datetime.datetime.fromisoformat(post_input['end_date'])
        schedule_entry = ScheduleModel(task_id=task_id, allocated_developer=viable_developers[0],
                                       task_status="ASSIGNED",

                                       start_date=start_date, end_date=end_date)
        db.session.add(schedule_entry)
        db.session.commit()

        return schedule_entry.allocated_developer

    @staticmethod
    def get_all_schedules():
        query = ScheduleModel.query.all()
        return jsonify(query)

