from __future__ import annotations
from logging import Logger
import pandas as pd
from .battle_metrics_service import BattleMetricsService
from ..data_cleaning.pokemon_cleaning_service import PokemonCleaningService


class TransformService:
    def __init__(self, *, logger: Logger) -> None:
        self._cleaning_service = PokemonCleaningService(logger=logger)
        self._battle_metrics_service = BattleMetricsService(logger=logger)

    def clean_pokemon_dataframe(
        self,
        pokemon_df: pd.DataFrame,
        *,
        legendary_column: str = "legendary",
    ) -> pd.DataFrame:
        """Delegate to PokemonCleaningService for dataframe cleaning."""

        return self._cleaning_service.clean_pokemon_dataframe(
            pokemon_df,
            legendary_column=legendary_column,
        )

    def build_pokemon_battle_metrics(
        self,
        pokemon_df: pd.DataFrame,
        combats_df: pd.DataFrame,
        *,
        pokemon_id_column: str = "pokemon_id",
        legendary_column: str = "legendary",
        combat_first_column: str = "first_pokemon_id",
        combat_second_column: str = "second_pokemon_id",
        combat_winner_column: str = "winner_id",
    ) -> pd.DataFrame:
        return self._battle_metrics_service.build_pokemon_battle_metrics(
            pokemon_df=pokemon_df,
            combats_df=combats_df,
            pokemon_id_column=pokemon_id_column,
            legendary_column=legendary_column,
            combat_first_column=combat_first_column,
            combat_second_column=combat_second_column,
            combat_winner_column=combat_winner_column,
        )
