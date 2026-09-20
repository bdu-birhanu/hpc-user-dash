import subprocess
import os

DB_PATH = "/data/rc/rabbitmq_agents/.agent_db/user_reg.db"
SQLITE3 = "/usr/bin/sqlite3"

def fetch_account_status(user_id):
    query = f"SELECT * FROM user_state WHERE username LIKE '{user_id}';"
    print([SQLITE3, DB_PATH, query])
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
        #if sqlite outputs empty lines (in case of a user who do not have cheaha account)
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
    records.reverse() # to reodreder the account state from oldest->older->newest to newest->older-oldest...
    return records


def update_account_state(user_id, new_state):
 
    # Update the account state by calling account_manager.py,
    # exactly like my bashrc acct() function does.
 
    subprocess.run(
        [
            "/cm/shared/rabbitmq_agents/venv/bin/python",
            "/cm/shared/rabbitmq_agents/account_manager.py",
            user_id,
            new_state
        ],
        check=True,
        stdout=subprocess.PIPE,   
        stderr=subprocess.PIPE    
    )