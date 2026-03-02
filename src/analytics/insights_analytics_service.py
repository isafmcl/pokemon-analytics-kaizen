from __future__ import annotations
from logging import Logger
from typing import Dict, List, Sequence
import pandas as pd
from .base_analytics_service import BaseAnalyticsService
from core.exceptions import ValidationError


class InsightsAnalyticsService(BaseAnalyticsService):
    """Serviço para operações de analytics mais avançadas."""

    def __init__(self, *, logger: Logger) -> None:
        self._logger = logger

    def correlacao_atributos(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        metric_columns: Sequence[str] = ("win_rate", "weighted_score"),
        stat_columns: Sequence[str] = (
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        ),
    ) -> pd.DataFrame:
        """Calcula correlações entre atributos e métricas."""

        all_columns = list(metric_columns) + list(stat_columns)
        self.ensure_columns(pokemon_metrics_df, all_columns, "pokemon_metrics_df")

        numeric_df = pokemon_metrics_df[list(all_columns)].apply(
            pd.to_numeric, errors="coerce"
        )

        corr_matrix = numeric_df.corr(method="pearson")
        corr_sub = corr_matrix.loc[list(stat_columns), list(metric_columns)]
        return corr_sub

    def win_rate_por_tipo(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        type_1_column: str = "type_1",
        type_2_column: str = "type_2",
        win_rate_column: str = "win_rate",
    ) -> pd.DataFrame:
        """Calcula win rate por tipo usando vitórias e batalhas.

        Fórmula: ( vitórias do tipo) / ( batalhas do tipo).
        """
        self.ensure_columns(
            pokemon_metrics_df,
            [
                type_1_column,
                type_2_column,
                "total_battles",
                "total_wins",
            ],
            "pokemon_metrics_df",
        )

        records: List[Dict[str, float | str]] = []

        for _, row in pokemon_metrics_df.iterrows():
            battles = float(row.get("total_battles", 0) or 0)
            wins = float(row.get("total_wins", 0) or 0)
            if battles <= 0:
                continue
            for col in (type_1_column, type_2_column):
                raw_type = row.get(col)
                if raw_type is None:
                    continue
                type_value = str(raw_type).strip()
                if not type_value:
                    continue
                records.append(
                    {
                        "type": type_value,
                        "total_battles": battles,
                        "total_wins": wins,
                    }
                )

        if not records:
            raise ValidationError(
                "Não há informações de tipo disponíveis para análise de win rate",
            )

        temp_df = pd.DataFrame.from_records(records)
        grouped = temp_df.groupby("type").agg(
            total_battles=("total_battles", "sum"),
            total_wins=("total_wins", "sum"),
        )

        grouped["mean_win_rate"] = grouped["total_wins"] / grouped["total_battles"]
        grouped["mean_win_rate"] = grouped["mean_win_rate"].fillna(0.0).clip(
            lower=0.0,
            upper=1.0,
        )
        grouped["sample_size"] = grouped["total_battles"].astype("int64")

        return grouped.sort_values(by="mean_win_rate", ascending=False).reset_index()

    def sugerir_time(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        team_size: int = 6,
        score_column: str = "weighted_score",
        diversity_by_type: bool = True,
        type_1_column: str = "type_1",
    ) -> pd.DataFrame:
        """Sugere um time de Pokemons com base em score e diversidade."""

        if team_size <= 0:
            raise ValidationError("team_size deve ser positivo")

        self.ensure_columns(pokemon_metrics_df, [score_column], "pokemon_metrics_df")

        candidates = pokemon_metrics_df.sort_values(
            by=score_column,
            ascending=False,
        ).reset_index(drop=True)

        if not diversity_by_type or type_1_column not in candidates.columns:
            return candidates.head(team_size)

        chosen_indices: List[int] = []
        used_types: set[str] = set()

        for idx, row in candidates.iterrows():
            if len(chosen_indices) >= team_size:
                break

            type_value_raw = row.get(type_1_column)
            type_value = str(type_value_raw).strip() if type_value_raw is not None else ""

            if type_value and type_value in used_types:
                continue

            chosen_indices.append(idx)
            if type_value:
                used_types.add(type_value)

        if len(chosen_indices) < team_size:
            remaining = [
                idx
                for idx in range(len(candidates))
                if idx not in chosen_indices
            ]
            for idx in remaining:
                if len(chosen_indices) >= team_size:
                    break
                chosen_indices.append(idx)

        chosen_df = candidates.loc[chosen_indices]
        return chosen_df.reset_index(drop=True)
