#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Paper Manager..."
/opt/anaconda3/envs/paper-manager/bin/streamlit run app.py
