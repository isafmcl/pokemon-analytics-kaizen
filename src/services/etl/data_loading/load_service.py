"""Data loading service responsible for persisting data idempotently.

This service maps pandas DataFrames into ORM entities and delegates
persistence to repositories. It guarantees idempotent bulk loads by
checking existing records before inserting new ones.

No extraction, transformation, or analytics logic should be added
here; the sole responsibility is coordinating writes to the database.

"""
from __future__ import annotations

from logging import Logger

import pandas as pd
from sqlalchemy.orm import Session

from repositories.combat_repository import CombatRepository
from repositories.pokemon_repository import PokemonRepository
from .combat_load_service import CombatLoadService
from .pokemon_load_service import PokemonLoadService


class LoadService:
    """Facade providing idempotent bulk load operations."""

    def __init__(
        self,
        *,
        session: Session,
        pokemon_repository: PokemonRepository,
        combat_repository: CombatRepository,
        logger: Logger,
    ) -> None:
        """Initialize a new LoadService instance.

        Args:
            session: Active SQLAlchemy session shared with repositories.
            pokemon_repository: Repository used for Pokemon entities.
            combat_repository: Repository used for Combat entities.
            logger: Logger used for diagnostic messages.
        """

        self._session = session
        self._pokemon_loader = PokemonLoadService(
            repository=pokemon_repository,
            logger=logger,
        )
        self._combat_loader = CombatLoadService(
            repository=combat_repository,
            pokemon_repository=pokemon_repository,
            logger=logger,
        )

    def load_pokemon(
        self,
        pokemon_df: pd.DataFrame,
        *,
        id_column: str = "pokemon_id",
        name_column: str = "name",
        type_1_column: str = "type_1",
        type_2_column: str = "type_2",
        generation_column: str = "generation",
        legendary_column: str = "legendary",
        hp_column: str = "hp",
        attack_column: str = "attack",
        defense_column: str = "defense",
        sp_attack_column: str = "sp_attack",
        sp_defense_column: str = "sp_defense",
        speed_column: str = "speed",
    ) -> int:
        """Delegate Pokemon load to PokemonLoadService."""

        return self._pokemon_loader.load_pokemon(
            pokemon_df,
            id_column=id_column,
            name_column=name_column,
            type_1_column=type_1_column,
            type_2_column=type_2_column,
            generation_column=generation_column,
            legendary_column=legendary_column,
            hp_column=hp_column,
            attack_column=attack_column,
            defense_column=defense_column,
            sp_attack_column=sp_attack_column,
            sp_defense_column=sp_defense_column,
            speed_column=speed_column,
        )

    def load_combats(
        self,
        combats_df: pd.DataFrame,
        *,
        first_pokemon_column: str = "first_pokemon_id",
        second_pokemon_column: str = "second_pokemon_id",
        winner_column: str = "winner_id",
    ) -> int:
        """Delegate combats load to CombatLoadService."""

        return self._combat_loader.load_combats(
            combats_df,
            first_pokemon_column=first_pokemon_column,
            second_pokemon_column=second_pokemon_column,
            winner_column=winner_column,
        )
