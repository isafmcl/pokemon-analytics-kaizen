from __future__ import annotations
from functools import lru_cache
from typing import Callable
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from config.logger import get_logger
from config.settings import get_settings
from database.base import Base


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    logger = get_logger("database.engine")

    engine = create_engine(settings.database_url, future=True)
    logger.info("Engine do banco de dados inicializado")

    from database import models

    Base.metadata.create_all(engine)
    logger.info("Esquema do banco garantido via create_all")
    return engine


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    engine = get_engine()
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def create_session() -> Session:
    session_factory = get_session_factory()
    return session_factory()
