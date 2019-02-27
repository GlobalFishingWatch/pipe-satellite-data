#!/usr/bin/env bash

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"

display_usage() {
  echo "Available Commands"
  echo "  satellite_data_daily   Run satellite_data daily queries."
}


if [[ $# -le 0 ]]
then
  display_usage
  exit 1
fi


case $1 in

  satellite_data_daily)
    ${THIS_SCRIPT_DIR}/satellite_data_daily.sh "${@:2}"
    ;;

  *)
    display_usage
    exit 0
    ;;
esac
