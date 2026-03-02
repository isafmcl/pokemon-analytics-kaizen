from __future__ import annotations

from logging import Logger
from typing import List
import pandas as pd
from core.exceptions import ValidationError
from . import metrics_calculator


class BattleMetricsService:
    """Serviço que calcula métricas de batalha por Pokemon."""
    def __init__(self, *, logger: Logger) -> None:
        self._logger = logger

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
        """Calcula métricas de batalha para cada Pokemon."""

        self._validate_required_columns(
            pokemon_df,
            required_columns=[pokemon_id_column, legendary_column],
            frame_name="pokemon_df",
        )

        pokemon = pokemon_df.copy(deep=True)

        combats = self._normalize_combat_identifier_columns(
            combats_df,
            first_column=combat_first_column,
            second_column=combat_second_column,
            winner_column=combat_winner_column,
        )

        self._validate_required_columns(
            combats,
            required_columns=[
                combat_first_column,
                combat_second_column,
                combat_winner_column,
            ],
            frame_name="combats_df",
        )

        if combats.empty:
            self._logger.info(
                "DataFrame de combates está vazio; métricas serão zeradas",
            )

        pokemon[pokemon_id_column] = pd.to_numeric(
            pokemon[pokemon_id_column], errors="coerce"
        ).astype("Int64")
        combats[combat_first_column] = pd.to_numeric(
            combats[combat_first_column], errors="coerce"
        ).astype("Int64")
        combats[combat_second_column] = pd.to_numeric(
            combats[combat_second_column], errors="coerce"
        ).astype("Int64")
        combats[combat_winner_column] = pd.to_numeric(
            combats[combat_winner_column], errors="coerce"
        ).astype("Int64")

        battles = metrics_calculator.compute_total_battles(
            combats=combats,
            first_column=combat_first_column,
            second_column=combat_second_column,
        )

        wins = metrics_calculator.compute_total_wins(
            combats=combats,
            winner_column=combat_winner_column,
        )

        metrics = metrics_calculator.combine_battles_and_wins(
            pokemon_ids=pokemon[pokemon_id_column],
            battles=battles,
            wins=wins,
        )

        metrics["win_rate"] = metrics_calculator.compute_win_rate(
            total_battles=metrics["total_battles"],
            total_wins=metrics["total_wins"],
        )

        metrics["weighted_score"] = metrics_calculator.compute_weighted_score(
            win_rate=metrics["win_rate"],
            total_battles=metrics["total_battles"],
        )

        result = pokemon.merge(
            metrics,
            how="left",
            left_on=pokemon_id_column,
            right_index=True,
        )

        result[["total_battles", "total_wins"]] = result[[
            "total_battles",
            "total_wins",
        ]].fillna(0).astype("int64")
        result[["win_rate", "weighted_score"]] = result[[
            "win_rate",
            "weighted_score",
        ]].fillna(0.0).astype("float64")

        return result

    def _validate_required_columns(
        self,
        frame: pd.DataFrame,
        *,
        required_columns: List[str],
        frame_name: str,
    ) -> None:
        """Valida se um DataFrame contém todas as colunas obrigatórias."""

        if frame.empty:
            raise ValidationError(f"DataFrame '{frame_name}' está vazio")

        missing = [col for col in required_columns if col not in frame.columns]
        if missing:
            raise ValidationError(
                f"DataFrame '{frame_name}' não contém as colunas obrigatórias: {missing}"
            )

    def _normalize_combat_identifier_columns(
        self,
        combats_df: pd.DataFrame,
        *,
        first_column: str,
        second_column: str,
        winner_column: str,
    ) -> pd.DataFrame:
        """Normaliza nomes de colunas identificadoras de combate vindas do payload da API."""

        if combats_df.empty:
            return combats_df.copy(deep=True)

        normalized = combats_df.copy(deep=True)
        rename_map: dict[str, str] = {}

        def _map_column(target: str, candidates: list[str]) -> None:
            if target in normalized.columns:
                return
            for candidate in candidates:
                if candidate in normalized.columns:
                    self._logger.info(
                        "Renomeando coluna de combates '%s' para '%s' para consistência",
                        candidate,
                        target,
                    )
                    rename_map[candidate] = target
                    break

        _map_column(
            first_column,
            [
                "first_pokemon",
                "First_pokemon",
                "pokemon_1",
                "pokemon1",
            ],
        )
        _map_column(
            second_column,
            [
                "second_pokemon",
                "Second_pokemon",
                "pokemon_2",
                "pokemon2",
            ],
        )
        _map_column(
            winner_column,
            [
                "winner",
                "Winner",
                "winner_pokemon",
            ],
        )

        if rename_map:
            normalized = normalized.rename(columns=rename_map)

        return normalized
