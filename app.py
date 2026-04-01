from flask import Flask, render_template, Response, request, redirect

# Importing functions that generate the diffrent information
from services.account import fetch_account_status
from services.membership import fetch_membership
from services.jobs import fetch_jobs, summarize_jobs_by_partition
from services.storage import fetch_storage

import json

from services.projects import (
    list_projects,
    get_project,
    add_member,
    remove_member
)

# Partition-related infromation (demo)
from services.partitions import fetch_partitions

app = Flask(__name__)

# A function that generates multiple system reports for a user taking their BlazerID ans an input, and the system returns: 
# Account state history, current account state, project memberships, storage usage, job summary by partition 
@app.route("/", methods=["GET", "POST"])
def dashboard():
    # Initialize all variables
    user_id = None
    current = None #  # Latest account state entry
    history = []  # Full account state history
    membership = None
    jobs = None
    storage = None
    partition_summary = None # Job summary grouped by partition for a user
    
    # Default number of jobs to show unless user changes it
    job_limit = 2
    
    # Read GET parameters (date filter) 
    start_date = request.args.get("start") 
    end_date = request.args.get("end")
    
    if request.method == "POST":
        user_id = request.form.get("user_id").strip()

        # first determine if the user exist by checking acount state history
        history = fetch_account_status(user_id)
        
         # If user is not exists (do not have cheaha account), fetch_account_status() returns an empty list/ or history is empty.
         #just return the dashborad with erro log
        if not history: 
            return render_template(
                "dashboard.html",
                user_id=user_id,
                user_not_found=True, # Template uses this to hide all sections
                current=None,
                history=[],
                membership=None,
                storage=None,
                jobs=None,
                partition_summary={},
                job_limit=None
            )

        # If user exists, the firts entry on the history list is current state.
        current = history[0]
        
        # job limit, user selected a different job limit
        if request.form.get("job_limit"):
            job_limit = int(request.form.get("job_limit"))
            
        # call all funtion and  generate all remaining reports
        membership = fetch_membership(user_id)
        #Pass date filters to fetch_jobs
        jobs = fetch_jobs(user_id, limit=job_limit,start=start_date, end=end_date)
        partition_summary = summarize_jobs_by_partition(jobs)
        storage = fetch_storage(user_id)
    
    
     #  GET and user_id already exists in session or page 
    elif request.method == "GET" and request.args.get("user_id"):
        user_id = request.args.get("user_id") 
        history = fetch_account_status(user_id) 
        current = history[0] if history else None 
        membership = fetch_membership(user_id) 
        storage = fetch_storage(user_id)
          
        # Fetch jobs with date filter 
        jobs = fetch_jobs(user_id, limit=job_limit, start=start_date, end=end_date) 
        partition_summary = summarize_jobs_by_partition(jobs)
         
         
    # generate the dashboard with all collected data
    return render_template(
        "dashboard.html",
        user_id=user_id,
        current=current,
        history=history,
        membership=membership,
        storage=storage,
        jobs=jobs,
        partition_summary=partition_summary,
        job_limit=job_limit,
        start_date = start_date,
        end_date = end_date
    )


# Flask decorator that maps the /projects URL to this function
@app.route("/projects")
def projects():
    return render_template("projects.html", projects=list_projects())

#Download project infromation as json file
@app.route("/projects.json")
def download_projects_json():
    projects = list_projects() 

    json_data = json.dumps(projects, indent=4)

    return Response(
        json_data,
        mimetype="application/json",
        headers={
            "Content-Disposition": "attachment; filename=projects.json"
        }
    )
    
# Here the name is extracted from the directory name e.g datascience from /data/project/datascience
@app.route("/projects/<name>", methods=["GET", "POST"])
def project_detail(name):
    project = get_project(name)
    groupname = project["groupname"]
    message = None

    if request.method == "POST":
        action = request.form.get("action")
        user = request.form.get("user")
        
        # this will get a tub with either:
        # (True, "User alice added successfully.") or (False, "User alice does not exist.")
       # from add_member(groupname, user). that is wy ok, message variable used here
        if action == "add":
            ok, message = add_member(groupname, user)
        elif action == "remove":
            ok, message = remove_member(groupname, user)
            
        # reload page but keep the message displayed
        return render_template(
            "partials/project_members.html",
            name = name,
            project = project,
            message = message
            )

    return render_template("partials/project_members.html", name=name, project=project)


# available partitions and their resource information
@app.route("/partitions")
def partitions():
    data = fetch_partitions()
    return render_template("partitions.html", partitions=data)

# Start the flask development server in prot 5000
# use `app.run(debug=True)` instead of app.run(debug=True, port=5000) if you launch as sandboxapp
if __name__ == "__main__":
    app.run(debug=True, port=5000)
