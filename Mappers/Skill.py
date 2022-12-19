class Skill:

    def __init__(self, skill_object):
        self.skill_id = skill_object["skill_id"]

        self.skill_name = skill_object["skill_name"]

    def change_name(self, new_name):
        self.skill_name = new_name


if __name__ == '__main__':
    a = {
        "skill_name": "Skill_Name",
        "skill_id": "1234"
    }
    python = Skill(a)

    # print the names of the two variables
    print(python.skill_name)
    print(python.skill_id)
