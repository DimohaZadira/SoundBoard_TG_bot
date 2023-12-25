from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Database:
    host: str
    user: str
    password: str
    name: str


@dataclass
class Config:
    tg_bot: TgBot
    db: Database


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env.str("BOT_TOKEN")),
        db=Database(
            host=env.str("DB_HOST"),
            name=env.str("DB_NAME"),
            user=env.str("DB_USER"),
            password=env.str("DB_PASS"),
        ),
    )
