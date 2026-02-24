# INSTRUCTIONS

## run

```sh
docker compose -f docker-compose.dev.yml --env-file .env.dev up --build
```

> add `-d` to run in background (detached mod)

## stop

```sh
docker compose -f docker-compose.dev.yml --env-file .env.dev down
```

> add `-v` to delete DB

# LINKS

- **fastapi**
  - [OAuth2 with Password, Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
  - [testing](https://fastapi.tiangolo.com/tutorial/testing/#extended-testing-file)
- **habr**
  - [poetry VS pip](https://habr.com/ru/articles/969296/)
- **react**
  - [start react](https://create-react-app.dev/docs/getting-started/)
