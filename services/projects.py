import os
import pwd
import grp
import subprocess

#===================this is fro cache
import time
_project_cache = {
    "data": None,
    "timestamp": 0
}
catch_time = 300   # 5 minutes
#===================



BASE = "/data/project"

# convert uid to group name  if not fallback to "gid:<id>" if missing
def get_username(uid):
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return f"uid:{uid}"

#convert gid to groupname (fallback to "uid:<id>" if missing)
def get_groupname(gid):
    try:
        return grp.getgrgid(gid).gr_name
    except KeyError:
        return f"gid:{gid}"

# function reads each directory under `/data/project` and returns dirname,pi,unix group, members.
def list_projects():

    now= time.time()
    # Return cached data if still valid
    if _project_cache["data"] and now - _project_cache["timestamp"] < catch_time:
        return _project_cache["data"]
    
    project_dict = {}

    for entry in os.scandir(BASE):
        if entry.is_dir():
            stat = entry.stat()

            pi = get_username(stat.st_uid) 
            groupname = get_groupname(stat.st_gid)
            members = get_group_members(groupname) if not groupname.startswith("gid:") else []

            project_dict[entry.name] = {
                "pi": pi,
                "groupname": groupname,
                "members": members
            }

    # Sort alphabetically by project directory name
    project_dict_alpha = dict(sorted(project_dict.items()))

    # Store in cache
    _project_cache["data"] = project_dict_alpha
    _project_cache["timestamp"] = now

    return project_dict_alpha

# Return a single project's metadata by directoryname.
# here "name" is the name from project directory e.g datasciencetem from `/data/project/datascienceteam`
def get_project(name):
    projects = list_projects()
    return projects.get(name)

# returns a list of usernames in that groupname.
def get_group_members(groupname):
    try:
        output = subprocess.check_output(["getent", "group", groupname]).decode().strip()
        parts = output.split(":")
        if len(parts) >= 4:
            return parts[3].split(",") if parts[3] else []
    except:
        pass
    return []

# add new memebers, it checks if the user already have a cheaha account
def add_member(groupname, user):
    try:
        subprocess.check_output([
            "/cm/shared/rabbitmq_agents/venv/bin/python",
            "/cm/shared/rabbitmq_agents/group_manager.py",
            "-g", groupname,
            user
        ], stderr=subprocess.STDOUT)
        return True, f"User {user} added successfully."
    except subprocess.CalledProcessError as e:
        return False, f"User {user} does not exist."

# remove members from the
def remove_member(groupname, user):
    try:
        subprocess.check_output([
            "/cm/shared/rabbitmq_agents/venv/bin/python",
            "/cm/shared/rabbitmq_agents/group_manager.py",
            "-d",
            "-g", groupname,
            user
        ], stderr=subprocess.STDOUT)
        return True, f"User {user} removed successfully."
    except subprocess.CalledProcessError as e:
        return False, f"Failed to remove user {user}."
