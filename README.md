## Table of contents

- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
- [Edit `.env`](#edit-env)

## General info

Project designed for easy taxi order management. Users can order taxis without calling operators. All interactions between users and operators are conducted through Helpcrunch for detailed orders if needed. The bot features a custom admin panel for managing admins and changing the lexicon. Hosted on Railway.app.

## Technologies

aiogram, loguru, pydantic, alembic, sqlalchemy, postgres, redis, helpcruch api, docker, docker-compose.

## Setup

To run this project, install it locally using pip or any other package managers such as pipenv, poetry etc.:

### Install and run using `poetry`

```bash
$ git clone https://github.com/surgeonofdeaths/taxi-bot.git
$ cd taxi-bot
$ poetry shell # If the shell with installed libraries is required
$ poetry install
$ poetry run python bot/main.py
```

### Run with `docker-compose`

```sh
docker-compose up -d --build # run in background
docker-compose down -v # stop from running in background
```

## Edit `.env`

Rename `env.dist` to `.env` and update it with your preferred variables.
