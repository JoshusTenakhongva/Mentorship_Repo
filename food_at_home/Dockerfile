FROM apache/airflow:2.3.0
COPY /docker_init/requirements.txt /requirements.txt 
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirements.txt

FROM postgres:13
COPY /docker_init/docker_postgres_init.sql /docker-entrypoint-initdb.d/