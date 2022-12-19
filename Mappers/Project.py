class Project:

    def __init__(self, name):
        self.name = name["name"]
        self.p_id = name["p_id"]

    def change_name(self, new_name):
        self.name = new_name


if __name__ == '__main__':
    a = {
        "name": "Project_Name",
        "p_id": "1234"
    }
    python = Project(a)

    # print the names of the two variables
    print(python.name)
    print(python.p_id)
