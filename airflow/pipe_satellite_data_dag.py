from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from pipe_tools.airflow.models import DagFactory


PIPELINE = "pipe_satellite_data"


class SatelliteDataDagFactory(DagFactory):

    def __init__(self, pipeline=PIPELINE, **kwargs):
        super(SatelliteDataDagFactory, self).__init__(pipeline=pipeline, **kwargs)

    def source_date(self):
        if self.schedule_interval == '@daily':
            return '{{ ds }}','{{ ds_nodash }}'
        else:
            raise ValueError('Unsupported schedule interval {}'.format(self.schedule_interval))

    def build(self, dag_id):
        config = self.config
        source_date = self.source_date()
        config['source_dataset'] = '{pipeline_dataset}'.format(**config)
        config['date'] = source_date[0]
        config['date_nodash'] = source_date[1]

        with DAG(dag_id, schedule_interval=self.schedule_interval, default_args=self.default_args) as dag:
            # source_sensors = self.source_table_sensors(dag)

            satellite_data_tasks = BashOperator(
                task_id='satellite_data_task',
                pool='bigquery',
                bash_command='{docker_run} {docker_image} satellite_data_daily '
                             '{user} {pass} '
                             '{date} '
                             'gs://{pipeline_bucket}/{satellite_directory} '
                             '{project_id}:{pipeline_dataset}.{tle_table} '
                             '{project_id}:{pipeline_dataset}.{sat_locations_table} '
                             '{norad_ids}'.format(**config)
            )

            # for sensor in source_sensors:
            #     dag >> sensor >> satellite_data_tasks

            dag >> satellite_data_tasks
            return dag


satellite_data_daily_dag = SatelliteDataDagFactory().build('satellite_data_daily_dag')
