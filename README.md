


```sh
curl -Lfo ./docker/compose.yaml 'https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml'

mkdir -p ./airflow/{config,dags,logs,plugins}

docker compose -f ./docker/compose.yaml up airflow-init

```
