from flask import Flask, render_template, request, redirect

# User-related services
from services.account import fetch_account_status
from services.membership import fetch_membership
from services.jobs import fetch_jobs, summarize_jobs_by_partition
from services.storage import fetch_storage

# Project-related services
from services.projects import (
    list_projects,
    get_project,
    add_member,
    remove_member
)

# Partition-related services
from services.partitions import fetch_partitions

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def dashboard():
    user_id = None
    current = None
    history = []
    membership = None
    jobs = None
    storage = None
    partition_summary = None

    # Default job limit
    job_limit = 2

    if request.method == "POST":
        user_id = request.form.get("user_id").strip()

        # Read job limit from dropdown (if provided)
        if request.form.get("job_limit"):
            job_limit = int(request.form.get("job_limit"))

        # Account state
        history = fetch_account_status(user_id)
        current = history[0] if history else None

        # Membership
        membership = fetch_membership(user_id)

        # Storage
        storage = fetch_storage(user_id)

        # Jobs (dynamic limit)
        jobs = fetch_jobs(user_id, limit=job_limit)

        # Partition summary
        partition_summary = summarize_jobs_by_partition(jobs)

    return render_template(
        "dashboard.html",
        user_id=user_id,
        current=current,
        history=history,
        membership=membership,
        storage=storage,
        jobs=jobs,
        partition_summary=partition_summary,
        job_limit=job_limit
    )

@app.route("/projects")
def projects():
    return render_template("projects.html", projects=list_projects())


@app.route("/projects/<name>", methods=["GET", "POST"])
def project_detail(name):
    project = get_project(name)

    if request.method == "POST":
        action = request.form.get("action")
        user = request.form.get("user")

        if action == "add":
            add_member(name, user)
        elif action == "remove":
            remove_member(name, user)

        return redirect(f"/projects/{name}")

    return render_template("partials/project_members.html", name=name, project=project)


@app.route("/partitions")
def partitions():
    data = fetch_partitions()
    return render_template("partitions.html", partitions=data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
