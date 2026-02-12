import os
import time
import json
import logging
import argparse

from shutil import rmtree
from itertools import tee
from dateutil.parser import parse as dateutil_parse
from urllib.parse import urlparse

from google.cloud import storage
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, SourceFormat
from google.cloud.bigquery import SchemaField

from pipe_satellite_data.utils.locations import fetch_TLE
from pipe_satellite_data.utils.locations import satellite_locations


def split_gcs_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip("/")
    return bucket, prefix


class SatLocations:
    def __init__(
        self,
        space_track_user,
        space_track_password,
        destination_bucket,
        destination_sat_locations,
        schema_directory,
        bq_project: str,
        gcs_project: str,
    ):
        self.st_auth = dict(user=space_track_user, password=space_track_password)
        self.destination_bucket = destination_bucket
        self.destination_sat_locations = destination_sat_locations
        self.schema_directory = schema_directory
        self.bq_project = bq_project
        self.gcs_project = gcs_project

    def process(self, date_ts, norad_ids):
        # dt = datetimeFromTimestamp(date_ts)
        dt = dateutil_parse(date_ts)
        self.str_date = dt.strftime("%Y%m%d")

        # get TLEs for norad_ids for the date
        tles = fetch_TLE(self.st_auth, norad_ids, dt)
        tles, tles_4_sats = tee(tles)

        # store in GCP
        self.store(
            records=tles,
            filename="%s/%s_%s.json" % ("download", "tles", self.str_date),
        )

        sat_locations = satellite_locations(tles_4_sats, dt)

        self.store(
            records=sat_locations,
            filename="%s/%s_%s.json" % ("download", "satellite_locations", self.str_date),
            destination_table=self.destination_sat_locations,
            schema="%s/%s" % (self.schema_directory, "sat_location.schema.json"),
        )

    def store(self, records, filename, destination_table=None, schema=None):

        logging.info("Writing to local file %s", filename)

        with open(filename, "w") as outfile:
            for message in records:
                json.dump(message, outfile)
                outfile.write("\n")

        logging.info("Uploading to GCS...")

        bucket_name, prefix = split_gcs_uri(self.destination_bucket)
        blob_name = f"{prefix}/{os.path.basename(filename)}"

        storage_client = storage.Client(project=self.gcs_project)
        bucket = storage_client.get_bucket(bucket_name)

        blob = bucket.blob(blob_name)
        blob.upload_from_filename(filename)

        gcsp_path_file = f"gs://{bucket_name}/{blob_name}"
        logging.info("Uploaded to %s", gcsp_path_file)

        if destination_table and schema:
            logging.info("Loading into BQ table %s", destination_table)

            with open(schema) as f:
                schema_json = json.load(f)

            bq_schema = [SchemaField.from_api_repr(field) for field in schema_json]

            table_id = f"{destination_table}_{self.str_date}"

            bq_client = bigquery.Client(project=self.bq_project)

            job_config = LoadJobConfig(
                source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                schema=bq_schema,
            )

            load_job = bq_client.load_table_from_uri(
                gcsp_path_file,
                table_id,
                job_config=job_config,
            )

            logging.info("Starting BigQuery load job %s", load_job.job_id)
            load_job.result()
            logging.info("BigQuery load finished")


def main(args):
    parser = argparse.ArgumentParser(
        description="Downloads Satellite data using the REST API uploads to GCS and BQ."
    )
    parser.add_argument(
        "-u", "--auth_user", help="The Username to access the Space Track API", required=True
    )
    parser.add_argument(
        "-p", "--auth_pass", help="The Password to access the Space Track API", required=True
    )
    parser.add_argument(
        "-d", "--date", help="Day to be downloaded format YYYY-MM-DD", required=True
    )
    parser.add_argument(
        "-gcsp",
        "--gcs_path",
        help=(
            'GCS path to store downloaded files. eg: "gs://scratch-matias/satellite-data" '
            'you will end up with "gs://scratch-matias/satellite-data/download/YEAR"'
        ),
        required=True,
    )
    parser.add_argument(
        "-bqsl",
        "--bq_sat_locations",
        help="Big Query Table project.dataset.table to store Satellite Locations",
        required=True,
    )
    parser.add_argument(
        "-nrids",
        "--norad_ids",
        nargs="+",
        help="List of norad_ids or satellite names",
        required=True,
    )
    parser.add_argument(
        "-sd",
        "--schema_dir",
        help="Complete path to the directory where are the schemas",
        default="/opt/project/assets",
    )
    parser.add_argument(
        "-bqproj",
        "--bq_project",
        help="GCP project to use when executing queries.",
    )

    parser.add_argument(
        "-gcsproj",
        "--gcs_project",
        help="GCP project in which to write the GCS files.",
    )

    args_parsed = parser.parse_args(args)

    auth_user = args_parsed.auth_user
    auth_pass = args_parsed.auth_pass
    date = args_parsed.date
    gcs_path = args_parsed.gcs_path
    bq_sat_locations = args_parsed.bq_sat_locations
    norad_ids = args_parsed.norad_ids
    schema_dir = args_parsed.schema_dir
    bq_project = args_parsed.bq_project
    gcs_project = args_parsed.gcs_project

    start_time = time.time()

    logging.info(("norad_ids=%s" % (norad_ids)))

    if not os.path.exists("download"):
        os.makedirs("download")

    sat_location = SatLocations(
        auth_user, auth_pass, gcs_path, bq_sat_locations, schema_dir, bq_project, gcs_project)

    sat_location.process(date, norad_ids)

    rmtree("download")

    logging.info(("Execution time {0} minutes".format((time.time() - start_time) / 60)))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
