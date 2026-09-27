# py -3.13 -m streamlit run app\streamlit_app.py
import streamlit as st
import pandas as pd
import json
from pathlib import Path


st.set_page_config(
    page_title="Kubernetes Operations",
    layout="wide"
)

st.title("Kubernetes Operations")


# Location of raw Kubernetes JSON files
data_dir = Path("data/raw/kubernetes")

files = sorted(data_dir.glob("kubernetes_*.json"))


if not files:
    st.warning("No Kubernetes JSON files found.")
    st.stop()


# Read all JSON files
records = []

for file in files:

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    collection_time = data["collection_time"]

    for pod in data["pods"]:

        for container in pod["containers"]:

            records.append({
                "collection_time": collection_time,
                "pod_name": pod["pod_name"],
                "namespace": pod["namespace"],
                "status": pod["status"],
                "node": pod["node"],
                "ip": pod["ip"],
                "container": container["name"],
                "ready": container["ready"],
                "restart_count": container["restart_count"],
                "current_state": container["current_state"],
                "previous_state": container["previous_state"]
            })


# Convert to DataFrame
df = pd.DataFrame(records)


# Convert collection time to datetime
df["collection_time"] = pd.to_datetime(df["collection_time"])


st.subheader("Kubernetes Pod Snapshots")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
