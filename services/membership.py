
import subprocess

def fetch_membership(username):
    
    # output from `groups BlazerID` command: "BlazerID : BlazerID lab2 lab3, etc"
    output = subprocess.check_output(["groups", username]).decode().strip()
    
    
    # Split `group blazerID` at ":" and take the right side
    parts = output.split(":")
    if len(parts) < 2:
        return []

    # will return ["BlazerID", "lab2", "lab3"]
    groups = parts[1].strip().split()
    return groups


