#!/usr/bin/env bash

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"
ASSETS=${THIS_SCRIPT_DIR}/../assets
LIB=${THIS_SCRIPT_DIR}/../pipe_satellite_data
source ${THIS_SCRIPT_DIR}/pipeline.sh

PROCESS=$(basename $0 .sh)
ARGS=( USER \
  PASS \
  DATE \
  GCSP_DIRECTORY \
  TLE_TABLE \
  SAT_LOCATIONS_TABLE \
  NORAD_IDS )

echo -e "\nRunning:\n${PROCESS}.sh $@ \n"

display_usage() {
  echo -e "\nUsage:\n${PROCESS}.sh ${ARGS[*]}\n"
  echo -e "USER: Username credential for Space Track API.\n"
  echo -e "PASS: Password credential for Space Track API.\n"
  echo -e "DATE: The date expressed with the following format YYYY-MM-DD. To be used for request.\n"
  echo -e "GCSP_DIRECTORY: The GCSP directory where the json responses will be saved (Format expected gs://<BUCKET>/<OBJECT>).\n"
  echo -e "TLE_TABLE: Table id where place the tle data results (Format expected PROJECT:DATASET.TABLE).\n"
  echo -e "SAT_LOCATIONS_TABLE: Table id where place the satellite data results (Format expected PROJECT:DATASET.TABLE).\n"
  echo -e "NORAD_IDS: List of NORAD ids for satellites to retrieve location for.\n"
}

if [[ $# -ne ${#ARGS[@]} ]]
then
    display_usage
    exit 1
fi

arg_values=("$@")
params=()
for index in ${!ARGS[*]}; do
  echo "${ARGS[$index]}=${arg_values[$index]}"
  declare "${ARGS[$index]}"="${arg_values[$index]}"
done


options="-u $USER -p $PASS -d $DATE -gcsp $GCSP_DIRECTORY -bqt $TLE_TABLE -bqsl $SAT_LOCATIONS_TABLE -nrids $NORAD_IDS -sd $ASSETS"
echo "python ${LIB}/process/sat_locations.py $options"
python ${LIB}/process/sat_locations.py $options
result=$?
if [ $result -eq 0 ]
then
  echo "Finished downloading Satellite data for $DATE, you can find it here $GCS_PATH."
else
  echo "Error downloading Satellite data."
  display_usage
  exit $result
fi

