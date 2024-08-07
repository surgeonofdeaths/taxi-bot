# Taxi Bot

![python](https://img.shields.io/badge/python-3.11-blue?style=flat-square)
![aiogram](https://img.shields.io/badge/aiogram-^3.4.1%20-orange?style=flat-square)
![pydantic](https://img.shields.io/badge/pydantic-^2.3.0%20-orange?style=flat-square)
![loguru](https://img.shields.io/badge/loguru-^0.7.2%20-orange?style=flat-square)
![alembic](https://img.shields.io/badge/alembic-^1.13.1%20-orange?style=flat-square)
![sqlalchemy](https://img.shields.io/badge/sqlalchemy-^2.0.29%20-orange?style=flat-square)
![redis](https://img.shields.io/badge/redis-^5.0.4%20-orange?style=flat-square)

## Table of contents

- [General info](#general-info)
- [Technologies](#technologies)
- [Setup](#setup)
- [Edit .env](#edit-env)

## General info

Project designed for easy taxi order management. Users can order taxis without calling operators. All interactions between users and operators are conducted through Helpcrunch for detailed orders if needed. The bot features a custom admin panel for managing admins and changing the lexicon. Hosted on Railway.app.

## Technologies

aiogram, loguru, pydantic, alembic, sqlalchemy, postgres, redis, helpcruch api, docker, docker-compose.

## Setup

To run this project, install it locally using poetry or docker-compose:

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

## Edit .env

Rename `env.dist` to `.env` and update it with your preferred variables.
