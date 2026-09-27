# py -3.13 collectors\kubernetes_collector.py

from kubernetes import client, config
from datetime import datetime, timezone
from pathlib import Path
import json


# Load Kubernetes configuration
config.load_kube_config()

# Create raw data output directory
output_dir = Path("data/raw/kubernetes")
output_dir.mkdir(parents=True, exist_ok=True)

# Create a unique timestamp for this collection run
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

# Output file for this collection run
output_file = output_dir / f"kubernetes_{timestamp}.json"


# Connect to Kubernetes API
v1 = client.CoreV1Api()


# Get all Pods across all namespaces
pods = v1.list_pod_for_all_namespaces()


# Collection timestamp
ingested_at = datetime.now(timezone.utc).isoformat()


# Store collected data
pod_records = []


for pod in pods.items:

    pod_record = {
        "pod_name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "status": pod.status.phase,
        "node": pod.spec.node_name,
        "ip": pod.status.pod_ip,
        "ingested_at": ingested_at,
        "containers": []
    }

    # Collect container-level operational state
    if pod.status.container_statuses:

        for container in pod.status.container_statuses:

            container_record = {
                "name": container.name,
                "ready": container.ready,
                "restart_count": container.restart_count,
                "current_state": None,
                "previous_state": None
            }

            if container.state:
                container_record["current_state"] = str(container.state)

            if container.last_state:
                container_record["previous_state"] = str(container.last_state)

            pod_record["containers"].append(container_record)

    pod_records.append(pod_record)


# Create the final raw collection document
collection = {
    "collection_time": ingested_at,
    "source": "kubernetes",
    "pod_count": len(pod_records),
    "pods": pod_records
}


# Write the collection to a new JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, default=str)


print(f"Collected {len(pod_records)} Pods")
print(f"Raw data written to: {output_file}")
