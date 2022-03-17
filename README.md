# Database initialization

## Prerequisites

Before running the web crawler, we need to start a Docker container with a Postgre SQL database, which we will use as storage for our web crawler.

To start the container, set the directory of your command line tool of choice to the root directory of the project and run the following command:
```
docker run --name postgresql-wier -e POSTGRES_PASSWORD=SecretPassword -e POSTGRES_USER=user -v $PWD/pgdata:/var/lib/postgresql/data -v $PWD/init-scripts:/docker-entrypoint-initdb.d -p 5432:5432 -d postgres:12.2
```

Then, run the `database.sql` script to intialize the crawldb database with all the necceseary tables and relations.

To check container's logs, run `docker logs -f postgresql-wier`.

To log into the database and execute SQL statements, run the following command: `docker exec -it postgresql-wier psql -U user`.

## Running the crawler

In order to run the crawler, simply run the `main.py` file.