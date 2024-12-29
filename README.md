


```sh
curl -Lfo ./docker/compose.yaml 'https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml'

mkdir -p ./airflow/{config,dags,logs}

docker compose -f ./docker/compose.yaml up
```

Add plugins. Then restart webserver and sheduler Airflow components:

```sh
docker restart docker-airflow-webserver-1 docker-airflow-scheduler-1
```
