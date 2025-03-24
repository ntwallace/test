# powerx-api

## Running the dev environment

Run the `dev-up` make command. This will start all the docker containers in `docker-compose.yml`.

```bash
make dev-up
```

## Seeding the local database

Once the dev environment is up and running, run the `seed-db` make command. This will seed the local database using the `scripts/seed.py` script.

```bash
make seed-db
```

## Accessing the Swagger UI

Once the dev environment is up and running, you can access the Swagger UI at `http://localhost:8000/docs`.

## Authenticating using the Swagger UI

1. Click the "Authorize" button in the top right corner of the Swagger UI.
2. Enter the following info:
    - username: `admin@powerx.co`
    - password: `powerxisneat`
3. Continue to use the Swagger UI as needed.

## Shutting down the dev environment

Run the `dev-down` make command. This will stop all the docker containers in `docker-compose.yml`.

```bash
make dev-down
```

## Creating a new migration

Run the alembic command to create a new migration in the docker environment.

```bash
docker compose -f docker-compose.yml run app alembic revision --autogenerate -m "migration message" 
```

> *Note*: In order to edit the migration files, you need to change the ownership of the files to your user. By default the files created by the docker container have a `user:group` of `root:root`. This should be updated to your user and group.

## Reverting a migration

If you need to revert a migration (and don't want to go through the hassle of destroying your local database), you can run the following command:

```bash
docker compose -f docker-compose.yml run app alembic downgrade -1
```

This will revert the last migration using alembic's [relative migration identifier](https://alembic.sqlalchemy.org/en/latest/tutorial.html#relative-migration-identifiers) feature.

If you need to revert to a specific revision, you can run the following commands:

```bash
docker compose -f docker-compose.yml run app alembic history
```

```bash
docker compose -f docker-compose.yml run app alembic downgrade <revision>
```

This will get the revision history, then copy a revision hash and use it in the downgrade command.

## Running pytest unit tests

Run the unit test suite docker image to run the unit tests.

```bash
make run-pytest
```

## Running mypy static type checking

Run mypy static type checking.

```bash
make run-mypy
```
