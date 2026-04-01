import subprocess
import os

DB_PATH = "/data/rc/rabbitmq_agents/.agent_db/user_reg.db"
SQLITE3 = "/usr/bin/sqlite3"

def fetch_account_status(username):
    log_file = os.path.expanduser(
        "/data/user/$USER/ondemand/dev/cheaha-demo/logs/"
    )
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    try:
        query = f"SELECT * FROM user_state WHERE username LIKE '{username}';"

        # combine SQLITE3, DB_PATH, and query to match the slurm-acct-state function in .bashrc
        result = subprocess.run(
            [SQLITE3, DB_PATH, query],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, #captures error output
            universal_newlines=True, #display output strings instead of bytes.
            check=True, #raise an error instead of silent sqlite3 failer
        )

        lines = result.stdout.strip().split("\n")
        records = []

        for line in lines:
            #if sqlite outputs empty lines (in case of a user who don not have cheaha account)
            if not line.strip():
                continue
            columns = line.split("|")
            while len(columns) < 6:
                columns.append("")

            records.append({
                "id": columns[0],
                "account": columns[1],
                "state": columns[2].upper(),
                "timestamp": columns[3],
                "updated": columns[4],
                "node": columns[5],
            })

        with open(log_file, "a") as f:
            f.write(f"Fetched account status for {username}: {records}\n")

        return records

    except Exception as e:
        with open(log_file, "a") as f:
            #handles sqlite3 subprocess failures e.g DB table not found
            if isinstance(e, subprocess.CalledProcessError):
                f.write(f"sqlite3 command failed: {e.stderr}\n")
            else:
                #otherwise it handle any error that is not from sqlite3 itself e.g premission error 
                f.write(f"Unexpected error: {e}\n")
        return []

