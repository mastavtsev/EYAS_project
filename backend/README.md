# Fundus

Fundus analysis microservices

## Services

- usersvc: responsible for handling users (auth, etc.)
- reportsvc: for conveying and supervising reports
- avsvc: for performing vessels analysis
- odsvc: for performing optic disk analysis
- macsvc: for performing macula analysis

## FAQ

- How to boot it up locally?

```shell
docker-compose up .
```

Make sure you apply migrations after the first launch

- How to apply migrations?

```shell
cd db && poetry install && poetry run alembic upgrade head
```

- How to regenerate clients?

```shell
cd report && poetry install && poetry run generate-client
```

- Why name services like that?

Cause of strange poetry behaviour with names containing special symbols
