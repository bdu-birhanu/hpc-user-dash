from flask import Flask, render_template, Response, request, session, jsonify, redirect, url_for
import json
import os
# Importing functions that generate the diffrent information
from services.user_info.account import fetch_account_status, update_account_state
from services.user_info.membership import fetch_membership
from services.user_info.jobs import fetch_jobs, summarize_jobs_by_partition
from services.user_info.storage import fetch_storage
#from services.partitions import fetch_partitions
from services.projects import (list_projects, get_project, add_member,remove_member)

# initializes the web application
app = Flask(__name__)
app.secret_key = "flask need this secretkey before we use a session"

# before every route, check the loged in  user and assigne a role
@app.before_request
def auto_auth():
    
    with open("role.json") as f:
        roles = json.load(f)
    
     # any time the browser refreshed we should fetch the username and update session user_id
    cheaha_user = os.getenv("USER")
    session["user_id"] = cheaha_user

    # Update role from role.json 
    if cheaha_user in roles.get("rc-team", []):
        session["role"] = "rc-team"
    else:
        session["role"] = "normal_user"

# A function taking a BlazerID as an input, and  returns: 
# Account state history, current account state, project memberships, storage usage, job summary by partition 
@app.route("/", methods=["GET", "POST"])
def dashboard():
    logged_in_user = session["user_id"]
    role = session.get("role", "normal_user")

    # for facilitation when they submit a search form (POST)
    if role == "rc-team" and request.method == "POST":
            user_id = request.form.get("user_id", "").strip()
            job_limit = int(request.form.get("job_limit", 2))

            # Redirect POST to GET to avoid form resubmission on refresh
            return redirect(url_for("dashboard", user_id=user_id, job_limit=job_limit))
    
    # if GET request (normal page load)
    if role == "rc-team":
        user_id = request.args.get("user_id")
        job_limit = int(request.args.get("job_limit", 2))


    # if other users/researchers
    else:
        user_id = logged_in_user
        job_limit = 2

    # If no user_id (rc-team hasn't searched yet)
    if not user_id:
        return render_template("dashboard.html")

    # Fetch account history to check if user exists
    history = fetch_account_status(user_id)

    # User not found (if a user dont have a cheaha account)
    if not history:
        return render_template(
            "dashboard.html",
            user_id=user_id,
            user_not_found=True,
            history=[],
            current=None,
            membership=None,
            jobs=None,
            partition_summary={},
            job_limit=None,
            storage=None
        )

    # User exists (have a cheaha account) then load all data
    current = history[0]
    membership = fetch_membership(user_id)
    jobs = fetch_jobs(user_id, limit=job_limit)
    partition_summary = summarize_jobs_by_partition(jobs)
    storage = fetch_storage(user_id)
     
    # Render final dashboard then
    return render_template(
        "dashboard.html",
        user_id=user_id,
        current=current,
        history=history,
        membership=membership,
        jobs=jobs,
        partition_summary=partition_summary,
        job_limit=job_limit,
        storage=storage
    )

@app.route("/update_state/<user_id>", methods=["POST"])
def update_state_route(user_id):
   
    #AJAX endpoint called by fetch() from the frontend.
    #Updates the account state without reloading the page.

    data = request.get_json()
    new_state = data.get("state")

    # Run backend update (same as bash acct())
    update_account_state(user_id, new_state)

    # Fetch updated DB row
    updated_record = fetch_account_status(user_id)

    return jsonify({
        "success": True,
        "state": new_state,
        "record": updated_record
    })


# When you visit a /projects url in the browser (e.g http://localhost:5000/projects), excute the function projects
@app.route("/projects")
def projects():
    user = session["user_id"]
    role = session.get("role", "normal_user")

    all_projects = list_projects()
    filtered = {}

    for dirname, p in all_projects.items():

        # rc-team sees everything
        if role == "rc-team":
            filtered[dirname] = p
            continue

        # normal users, show only PI or membership
        if p["pi"] == user or user in p["members"]:
            filtered[dirname] = p

    return render_template(
        "projects.html",
        projects=filtered,
        user=user
    )
    #return render_template("projects.html", projects=list_projects())
    
# The name is extracted from the projec directory name e.g datascience from /data/project/datascience
@app.route("/projects/<name>", methods=["GET", "POST"])
def project_detail(name):
    user = session["user_id"]
    role = session.get("role", "normal_user")
    
    project = get_project(name)
    groupname = project["groupname"]
    message = None

    if request.method == "POST":

        action = request.form.get("action")
        user = request.form.get("user")
        
        # this will get  output with either:
        # (True, "User <BlazerID> added successfully.") or (False, "User <BlazerID> does not exist.")
        # from add_member(groupname, user). that is why ok, message variable used here
        if action == "add":
            ok, message = add_member(groupname, user)
        elif action == "remove":
            ok, message = remove_member(groupname, user)
            
        # reload page but keep the message displayed
        return render_template(
            "partials/project_members.html",
            name = name,
            project = project,
            message = message,
            user=user
            )

    return render_template("partials/project_members.html", name=name, project=project, user=user)

# Download project infromation as json file
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

# partion info
@app.route("/partitions")
def partitions():
    # data = fetch_partitions()
    return render_template("partitions.html")

# Start the flask development server in prot 5000
# use `app.run(debug=True)` instead of app.run(debug=True, port=5000) if you launch as sandboxapp
if __name__ == "__main__":
    app.run(debug=True, port=5000)
