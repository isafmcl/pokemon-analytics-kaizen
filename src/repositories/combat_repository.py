from __future__ import annotations
from logging import Logger
from typing import List, Sequence, Tuple
from sqlalchemy.orm import Session
from database.models import Combat
from .base_repository import BaseRepository


class CombatRepository(BaseRepository[Combat]):
    def __init__(self, *, session: Session, logger: Logger) -> None:
        super().__init__(model_class=Combat, session=session, logger=logger)

    def get_existing_combat_keys(
        self,
        combat_keys: Sequence[Tuple[int, int, int]],
    ) -> List[Tuple[int, int, int]]:

        if not combat_keys:
            return []

        first_ids = [k[0] for k in combat_keys]
        second_ids = [k[1] for k in combat_keys]
        winner_ids = [k[2] for k in combat_keys]

        query = self._session.query(
            Combat.first_pokemon_id,
            Combat.second_pokemon_id,
            Combat.winner_id,
        ).filter(
            Combat.first_pokemon_id.in_(first_ids),
            Combat.second_pokemon_id.in_(second_ids),
            Combat.winner_id.in_(winner_ids),
        )

        return [(row[0], row[1], row[2]) for row in query.all()]
