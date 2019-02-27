#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"

# satellite_data daily
python $AIRFLOW_HOME/utils/set_default_variables.py \
    --force docker_image=$1 \
    pipe_k8s_satellite_data \
    dag_install_path="${THIS_SCRIPT_DIR}" \
    docker_run="{{ var.value.DOCKER_RUN }}" \
    project_id="{{ var.value.PROJECT_ID }}" \
    temp_bucket="{{ var.value.TEMP_BUCKET }}"  \
    pipeline_bucket="{{ var.value.PIPELINE_BUCKET }}" \
    pipeline_dataset="{{ var.value.PIPELINE_DATASET }}" \
    user="matias@globalfishingwatch.org" \
    pass="wSvi6xiCK3NyAas" \
    satellite_directory="satellite-data" \
    tle_table="spacetrack_raw_tle" \
    sat_locations_table="satellite_positions_one_second_resolution" \
    norad_ids="MUST be a list separated by spaces (ex. )25114 40019)"

echo "Installation Complete"
