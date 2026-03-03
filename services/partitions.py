# services/partitions.py

def fetch_partitions():
    return [
        {
            "name": "compute",
            "nodes": 120,
            "cpus": 3840,
            "gpus": 0,
            "running": 320,
            "pending": 45,
            "state": "UP",
            "utilization": "78%"
        },
        {
            "name": "gpu",
            "nodes": 20,
            "cpus": 640,
            "gpus": 80,
            "running": 18,
            "pending": 12,
            "state": "UP",
            "utilization": "65%"
        },
        {
            "name": "bigmem",
            "nodes": 10,
            "cpus": 320,
            "gpus": 0,
            "running": 4,
            "pending": 0,
            "state": "DRAIN",
            "utilization": "40%"
        }
    ]
