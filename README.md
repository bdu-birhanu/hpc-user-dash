# HPC Customer Service Management Dashboard

A web-based customer service management application developed for the UAB Research Computing HPC environment (Cheaha).

 ![screenshot of the Cheaha dashboard](/image/user-info.png)

This App includes the following role-based  (for RC team, PI and members) features:

- **User Account Information**:
  - View user account status, group memberships, job submission information per user, and quota usage.
- **Project Allocations**:
  - View project directory names and group names, and project quota usage.
  - Manage membership (list, add, remove users).
  - Search functionality by project name and the ability to generate and download data as a JSON file.
- **Partition Details**:
  - View available nodes per partition along with detailed node states (TBD).

## Installation & Usage

```
#  Clone the repository
git clone https://github.com/bdu-birhanu/hpc-user-dash.git
cd hpc-user-dash

# Set up the environment
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py

# To access the dashboard open your browser and go to:
# http://127.0.0.1:5000
# It is recommended to run this application from the HPC desktop environment terminal
```
