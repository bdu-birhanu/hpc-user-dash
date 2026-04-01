import subprocess


def clean_int(value):
    # Convert slurm CPU non intiger values e.g '24+' into integers 24.
    return int(value.replace("+", "").strip())


def parse_gpu_field(gpu_field):
    # Extract GPU count by taking the last bvalue from outputs  e.g from  gpu:ampere:2 it takes 2
    if not gpu_field or gpu_field in ("(null)", "N/A"):
        return 0
    parts = gpu_field.split(":")
    try:
        return int(parts[-1])
    except:
        return 0

# Return node-level details for a partition.
def fetch_partition_nodes(partition_name):
    """   
    Outpus
    - node: node name
    - state: node state (idle, alloc, mix, drain,etc)
    - cpus: total CPUs on the node
    - memory: total memory on the node
    - gpus: GPU info
    """
    # Columns:  Node| State | CPUs | Memory | GPUs
    cmd = ["sinfo", "-p", partition_name, "-h", "-o", "%N|%t|%c|%m|%G"]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True) #`universal_newlines` displays output strings instead of bytes.

    nodes = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue

        node, state, cpus, mem, gpus = line.split("|")

        nodes.append({
            "state": state,
            "node": node,
            "cpus": clean_int(cpus),
            "memory": mem,
            "gpus": gpus
        })

    return nodes

#Returns one entry per partition or partition-level details
def fetch_partitions():
    """
    sample output if this command:
      largemem|7|116/0/76/192|(null)|draining
      largemem|2|37/35/0/72|(null)|mixed
     """
    # %P=partition, %D=#nodes, %C=CPUs satets summary (alloc/idle/other/total), %G=GRES or GPU (e.g. GPUs), %T=state of partiton (idel/alloc/drain/)
    # running a command `sinfo -h -o "%P|%D|%C|%G|%T"

    cmd = ["sinfo", "-h", "-o", "%P|%D|%C|%G|%T"]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    partitions = {}

    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue

        name, nodes, cpu_states, gpus, part_state = line.split("|")

        # CPU parsing: alloc/idle/other/total 
        alloc, idle, other, total = [clean_int(x) for x in cpu_states.split("/")]

        gpu_count = parse_gpu_field(gpus)

        
        # partition-level dictionary
        partitions[name] = {
            "name": name,
            "nodes": int(nodes),
            "cpus": total,
            "gpus": gpu_count,
            "state": part_state.upper(),  # UP / DOWN / DRAIN
            "nodes_detail": [] # this will be genrated next
        }

    # generate node level details for each partition
    for part_name in partitions:
        partitions[part_name]["nodes_detail"] = fetch_partition_nodes(part_name)
     # return list of partitions
    return list(partitions.values())
