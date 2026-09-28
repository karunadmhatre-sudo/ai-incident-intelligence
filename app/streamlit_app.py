# py -3.13 -m streamlit run app\streamlit_app.py

import streamlit as st
import pandas as pd
import json
from pathlib import Path


st.set_page_config(
    page_title="Operations Intelligence",
    layout="wide"
)


st.title("Operations Intelligence")


tab_kubernetes, tab_git = st.tabs(
    ["Kubernetes", "Git Changes"]
)


# ============================================================
# Kubernetes
# ============================================================

with tab_kubernetes:

    st.header("Kubernetes Operations")

    # Location of raw Kubernetes JSON files
    data_dir = Path("data/raw/kubernetes")

    files = sorted(
        data_dir.glob("kubernetes_*.json")
    )

    if not files:

        st.warning("No Kubernetes JSON files found.")

    else:

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
        df["collection_time"] = pd.to_datetime(
            df["collection_time"]
        )


        st.subheader("Kubernetes Pod Snapshots")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# Git Changes
# ============================================================

with tab_git:

    st.header("Git Changes")

    # Location of raw Git JSON files
    git_data_dir = Path("data/raw/git")

    git_files = sorted(
        git_data_dir.glob("git_*.json"),
        reverse=True
    )


    if not git_files:

        st.warning("No Git JSON files found.")

    else:

        # Read all Git JSON files
        git_records = []

        for file in git_files:

            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for commit in data["commits"]:

                git_records.append({
                    "commit_time": commit["commit_time"],
                    "commit_sha": commit["commit_sha"],
                    "author": commit["author"],
                    "message": commit["message"],
                    "changed_files": ", ".join(
                        commit["changed_files"]
                    ),
                    "repository": data["repository"],
                    "branch": data["branch"]
                })


        # Convert to DataFrame
        git_df = pd.DataFrame(git_records)


        # Convert commit time to datetime
        git_df["commit_time"] = pd.to_datetime(
            git_df["commit_time"]
        )


        # Show newest commits first
        git_df = git_df.sort_values(
            "commit_time",
            ascending=False
        )


        st.subheader("Git Commit History")

        st.dataframe(
            git_df,
            use_container_width=True,
            hide_index=True
        )

