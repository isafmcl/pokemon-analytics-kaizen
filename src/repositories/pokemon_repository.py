from __future__ import annotations
from logging import Logger
from typing import List, Sequence
from sqlalchemy.orm import Session
from database.models import Pokemon
from .base_repository import BaseRepository


class PokemonRepository(BaseRepository[Pokemon]):
    def __init__(self, *, session: Session, logger: Logger) -> None:

        super().__init__(model_class=Pokemon, session=session, logger=logger)

    def get_existing_pokemon_ids(self, pokemon_ids: Sequence[int]) -> List[int]:
        return self.get_existing_ids(pokemon_ids)
