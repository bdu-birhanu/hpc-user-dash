projects = {
    "projA": {
        "pi": "dr_smith",
        "members": ["alice", "bob", "charlie"]
    },
    "projB": {
        "pi": "dr_jones",
        "members": ["david", "emma"]
    }
}

def list_projects():
    return projects

def get_project(name):
    return projects.get(name)

def add_member(project, user):
    if user not in projects[project]["members"]:
        projects[project]["members"].append(user)

def remove_member(project, user):
    if user in projects[project]["members"]:
        projects[project]["members"].remove(user)
