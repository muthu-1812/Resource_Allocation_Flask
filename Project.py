import pandas as pd
from flask_restful import Resource, Api, reqparse
from db_connect import Project
from main import db


class project_endpoint(Resource):
    def get(self):
        # data = pd.read_csv('users.csv')  # read local CSV
        # data = data.to_dict()  # convert dataframe to dict

        data=Project.query.all()
        return {'data': data}, 200  # return data and 200 OK

    def post(self):
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('projectId', required=True)  # add args
        parser.add_argument('projectName', required=True)
        # parser.add_argument('c', required=True)
        args = parser.parse_args()  # parse arguments to dictionary

        entry = Project(project_name=args['projectName'])
        db.session.add(entry)
        db.session.commit()

        # # read our CSV
        # data = pd.read_csv('users.csv')
        #
        # if args['projectId'] in list(data['projectId']):
        #     return {
        #                'message': f"'{args['userId']}' already exists."
        #            }, 409
        # else:
        #     # create new dataframe containing new values
        #     new_data = pd.DataFrame({
        #         'userId': [args['userId']],
        #         'name': [args['name']],
        #         'city': [args['city']],
        #         'locations': [[]]
        #     })
        #     # add the newly provided values
        #     data = data.append(new_data, ignore_index=True)
        #     data.to_csv('users.csv', index=False)  # save back to CSV
        #     return {'data': data.to_dict()}, 200  # return data with 200 OK
