import subprocess

def fetch_jobs(user_id, limit=None, start=None, end=None):
    jobs = []

    cmd = [
        "sacct",
        "-u", user_id,
        "--format=JobID,Partition,State,Elapsed,Submit,Node,NodeList,ReqMem,ReqCPUS,ExitCode",
        "--noheader"
    ]
    
    if start:
        cmd.extend(["--starttime", start])
    if end:
        cmd.extend(["--endtime", end])
    

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        lines = output.split("\n")

        for line in lines:
            parts = line.split()
            if len(parts) < 10:
                continue

            jobid = parts[0]

            # Skip step jobs like 37319389.ex+, 37319389.bat+
            if "." in jobid:
                continue

            job = {
                "jobid": jobid,
                "partition": parts[1],
                "state": parts[2],
                "elapsed": parts[3],
                "submit": parts[4],
                "node": parts[5],
                "nodelist": parts[6],
                "memory": parts[7],
                "cpus": parts[8],
                "exitcode": parts[9]
            }

            jobs.append(job)

        # pply job limit if requested
        if limit:
            jobs = jobs[:limit]

    except Exception as e:
        print("Error fetching jobs:", e)

    return jobs
    
def summarize_jobs_by_partition(jobs):
    summary = {}

    for job in jobs:
        part = job.get("partition", "unknown")

        if part not in summary:
            summary[part] = {
                "total": 0,
                "running": 0,
                "pending": 0,
                "failed": 0,
                "completed": 0
            }

        summary[part]["total"] += 1

        state = job.get("state", "").upper()

        if state.startswith("RUN"):
            summary[part]["running"] += 1
        elif state.startswith("PEND"):
            summary[part]["pending"] += 1
        elif state.startswith("FAIL"):
            summary[part]["failed"] += 1
        elif state.startswith("COMP"):
            summary[part]["completed"] += 1

    return summary

