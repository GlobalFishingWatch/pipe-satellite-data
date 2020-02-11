from airflow.models import DAG

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

        satellite_data_args = ['{user}', '{pass}',
                               '{date}',
                               'gs://{pipeline_bucket}/{satellite_directory}',
                               '{project_id}:{pipeline_dataset}.{tle_table}',
                               '{project_id}:{pipeline_dataset}.{sat_locations_table}',
                               '{norad_ids}']
        for i in range(len(satellite_data_args)):
            satellite_data_args[i]=satellite_data_args[i].format(**config)
        satellite_data_args.insert(0,'satellite_data_daily')

        with DAG(dag_id, schedule_interval=self.schedule_interval, default_args=self.default_args) as dag:

            satellite_data = self.build_docker_task({
                'task_id':'satellite_data_task',
                'pool':'k8operators_limit',
                'docker_run':'{docker_run}'.format(**config),
                'image':'{docker_image}'.format(**config),
                'name':'satellite-data',
                'dag':dag,
                'arguments':satellite_data_args
            })

            return dag

k8s_satellite_data_daily_dag = K8sSatelliteDataDagFactory().build('k8s_satellite_data_daily_dag')
