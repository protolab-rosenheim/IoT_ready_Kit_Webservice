# IoT Ready Kit Webservice #



## Setup Postgres Docker Container ##
    docker volume create postgres_data
    docker run -d --name postgres --restart always -e 'POSTGRES_PASSWORD=postgres!1' -p 5432:5432 -v postgres_data:/var/lib/postgresql/data arm32v7/postgres postgres

### Setup user and database ###
```
CREATE USER iotreadykit WITH
	LOGIN
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	INHERIT
	NOREPLICATION
	CONNECTION LIMIT -1
	PASSWORD 'xxxxxx';

CREATE DATABASE iotreadykit
    WITH
    OWNER = iotreadykit
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;

```
After starting flask for the first time, the tables are created. After that you can
```
INSERT INTO public.partstatus(
	part_status)
	VALUES ('onboard');

INSERT INTO public.partstatus(
	part_status)
	VALUES ('not onboard');

INSERT INTO public.partstatus(
	part_status)
	VALUES ('not accepting');
```

## Setup Flask Docker Container ##

    docker volume create flask_data
    docker run -d --name flask --restart always -p 5000:5000 -v flask_data:/data iotreadykit_flask

Mount configuration files: 

    docker run -d -p 5000:5000 --mount type=bind,source="$(pwd)"/irk_conf,target=/usr/src/app/conf iotreadykit_flask