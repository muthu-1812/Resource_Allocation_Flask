import datetime

from flask import Blueprint, request, jsonify

from models import ProjectModel, DeveloperModel, DeveloperSkillModel, TaskModel, TaskSkillModel, ScheduleModel

project_bp = Blueprint('projects', __name__)
developer_bp = Blueprint('developers', __name__)


@project_bp.route("/projects", methods=["GET", "POST"])
def projects():
    if request.method == 'GET':
        return ProjectModel.get_all_projects()

    if request.method == 'POST':
        post_input = request.get_json()
        return ProjectModel.add_project(post_input)


@project_bp.route("/project/<project_id>", methods=["GET", "POST"])
def project(project_id):
    if request.method == 'GET':
        return ProjectModel.get_project_by_id(project_id)


@developer_bp.route("/developers", methods=["GET", "POST"])
def developers():
    if request.method == 'GET':
        return DeveloperModel.get_all_developers()

    if request.method == 'POST':
        post_input = request.get_json()
        developer_id = DeveloperModel.add_developer(post_input)
        DeveloperSkillModel.add_skills_for_developer(post_input, developer_id)

        return str(developer_id)


@developer_bp.route("/developers/<developer_id>", methods=["GET", "POST"])
def developer(developer_id):
    if request.method == 'GET':
        return DeveloperModel.developer_details_by_id(developer_id)


# TODO I have 3 separate db write I should make it acid compliant
@project_bp.route("/tasks", methods=["GET", "POST"])
def Tasks():
    if request.method == 'GET':
        return TaskModel.get_all_tasks()

    if request.method == 'POST':

        post_input = request.get_json()

        task_id = TaskModel.add_task(post_input)

        TaskSkillModel.add_skills_for_task(post_input['task_skills'], task_id)

        developers_with_required_skills = ScheduleModel.find_developers_with_matching_skills(post_input)

        if len(developers_with_required_skills) == 0:
            return "No resources with required skills"

        busy_developers = ScheduleModel.find_busy_developers(post_input, developers_with_required_skills)

        # app.logger.info("Busy developers %s", str(busy_developers))

        viable_developers = [x for x in developers_with_required_skills if x not in busy_developers]
        # app.logger.info("no of viable developers %s", str(len(viable_developers)))

        if len(viable_developers) == 0:
            return "Resources with required skills are busy please set another date for task using put request"

        developer_id=ScheduleModel.create_schedule_for_task(task_id, viable_developers, post_input)

        return "Task assigned to developer id:"+str(developer_id)

