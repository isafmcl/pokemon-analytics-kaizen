from __future__ import annotations
from typing import Callable, TypeVar
import pandas as pd
from config.logger import get_logger
from database.session import create_session
from repositories.pokemon_repository import PokemonRepository
from database.models import Combat

T = TypeVar("T")


def _load_from_db_generic(
    query_func: Callable,
    mapper_func: Callable,
    logger_name: str = "app.streamlit.db",
) -> pd.DataFrame:
    session = create_session()
    logger = get_logger(logger_name)

    try:
        rows = query_func(session)

        if not rows:
            return pd.DataFrame()

        records = mapper_func(rows)
        return pd.DataFrame(records)
    finally:
        session.close()


def load_pokemon_from_db() -> pd.DataFrame:
    def query_func(session):
        repo = PokemonRepository(session=session, logger=get_logger("app.streamlit.db"))
        return session.query(repo.model_class).all()

    def mapper_func(rows):
        return [
            {
                "pokemon_id": row.pokemon_id,
                "name": row.name,
                "type_1": row.type_1,
                "type_2": row.type_2,
                "generation": row.generation,
                "legendary": row.legendary,
                "hp": row.hp,
                "attack": row.attack,
                "defense": row.defense,
                "sp_attack": row.sp_attack,
                "sp_defense": row.sp_defense,
                "speed": row.speed,
            }
            for row in rows
        ]

    return _load_from_db_generic(query_func, mapper_func)


def load_combats_from_db() -> pd.DataFrame:
    def query_func(session):
        return session.query(Combat).all()

    def mapper_func(rows):
        get_logger("app.streamlit.db").info(
            f"Loaded {len(rows)} combats from database"
        ) if rows else get_logger("app.streamlit.db").info("No combats found in database")
        return [
            {
                "first_pokemon_id": row.first_pokemon_id,
                "second_pokemon_id": row.second_pokemon_id,
                "winner_id": row.winner_id,
            }
            for row in rows
        ]

    return _load_from_db_generic(query_func, mapper_func)
