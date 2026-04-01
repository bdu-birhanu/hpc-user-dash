# this is a demo to show storagequota, 
# the real quota will be computed when we have access to it
def fetch_storage(username):
    home_used = 42
    home_quota = 100
    scratch_used = 120
    scratch_quota = 500

    return {
        "home_used": f"{home_used} GB",
        "home_quota": f"{home_quota} GB",
        "home_percent": int((home_used / home_quota) * 100),

        "scratch_used": f"{scratch_used} GB",
        "scratch_quota": f"{scratch_quota} GB",
        "scratch_percent": int((scratch_used / scratch_quota) * 100)
    }