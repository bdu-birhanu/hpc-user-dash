def fetch_jobs(username, limit=5):
    all_jobs = [
        {"id": "1001", "partition": "compute", "state": "COMPLETED", "runtime": "01:22:00", "submit": "2026-02-01"},
        {"id": "1000", "partition": "gpu", "state": "FAILED", "runtime": "00:05:00", "submit": "2026-01-30"},
        {"id": "999", "partition": "compute", "state": "RUNNING", "runtime": "00:10:00", "submit": "2026-01-29"},
        {"id": "998", "partition": "compute", "state": "COMPLETED", "runtime": "03:00:00", "submit": "2026-01-28"},
        {"id": "997", "partition": "gpu", "state": "COMPLETED", "runtime": "00:45:00", "submit": "2026-01-27"},
        {"id": "996", "partition": "compute", "state": "FAILED", "runtime": "00:02:00", "submit": "2026-01-26"},
    ]

    return all_jobs[:limit]

def summarize_jobs_by_partition(jobs):
    summary = {}

    for job in jobs:
        part = job["partition"]

        if part not in summary:
            summary[part] = {
                "running": 0,
                "pending": 0,
                "total": 0
            }

        summary[part]["total"] += 1

        if job["state"] == "RUNNING":
            summary[part]["running"] += 1
        elif job["state"] == "PENDING":
            summary[part]["pending"] += 1

    return summary
