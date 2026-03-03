def fetch_account_status(username):
    # Mock account history
    return [
        {
            "id": "101",
            "account": username,
            "state": "ACTIVE",
            "timestamp": "2026-02-01 10:22:00",
            "extra1": "Login OK",
            "node": "node01"
        },
        {
            "id": "100",
            "account": username,
            "state": "PENDING",
            "timestamp": "2026-01-15 09:10:00",
            "extra1": "Awaiting approval",
            "node": "node02"
        }
    ]
