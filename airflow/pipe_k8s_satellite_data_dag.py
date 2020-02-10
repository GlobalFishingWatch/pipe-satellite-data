from datetime import datetime, timedelta
import os

from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator

from airflow_ext.gfw.models import DagFactory


PIPELINE = "pipe_k8s_satellite_data"


class K8sSatelliteDataDagFactory(DagFactory):

    def __init__(self, pipeline=PIPELINE, **kwargs):
        super(K8sSatelliteDataDagFactory, self).__init__(pipeline=pipeline, **kwargs)

    def source_date(self):
        if self.schedule_interval == '@daily':
            return '{{ ds }}','{{ ds_nodash }}'
        else:
            raise ValueError('Unsupported schedule interval {}'.format(self.schedule_interval))

    def build(self, dag_id):
        config = self.config
        source_date = self.source_date()
        config['date'] = source_date[0]
        config['date_nodash'] = source_date[1]
        print(('config = %s' % (config)))

        satellite_data_image = "{docker_image}".format(**config)
        print(('satellite_data_image = %s' % satellite_data_image))

        satellite_data_args = ['{user}', '{pass}',
                               '{date}',
                               'gs://{pipeline_bucket}/{satellite_directory}',
                               '{project_id}:{pipeline_dataset}.{tle_table}',
                               '{project_id}:{pipeline_dataset}.{sat_locations_table}',
                               '{norad_ids}']
        for i in range(len(satellite_data_args)):
            satellite_data_args[i]=satellite_data_args[i].format(**config)

        satellite_data_args.insert(0,'satellite_data_daily')
        print(('satellite_data_args = %s' % satellite_data_args))
        entrypoint="./scripts/run.sh"

        satellite_data_args.insert(0,entrypoint)

        with DAG(dag_id, schedule_interval=self.schedule_interval, default_args=self.default_args) as dag:

            satellite_data = KubernetesPodOperator(
                namespace=os.getenv('K8_NAMESPACE'),
                image=satellite_data_image,
                cmds=satellite_data_args,
                name="satellite-data",
                task_id="satellite-data-task",
                get_logs=True,
                in_cluster=True if os.getenv('KUBERNETES_SERVICE_HOST') else False,
                dag=dag)

            return dag

k8s_satellite_data_daily_dag = K8sSatelliteDataDagFactory().build('k8s_satellite_data_daily_dag')
