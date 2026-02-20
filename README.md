# RUN

```sh
docker compose -f docker-compose.dev.yml --env-file .env.dev up --build
```

# STOP

```sh
docker compose -f docker-compose.dev.yml --env-file .env.dev down
```

> add `-v` to delete DB
