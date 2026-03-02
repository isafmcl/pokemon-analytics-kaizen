from __future__ import annotations
from logging import Logger
from typing import Optional, Sequence
import pandas as pd
from .insights_analytics_service import InsightsAnalyticsService
from .ranking_analytics_service import RankingAnalyticsService


class AnalyticsService:
    def __init__(self, *, logger: Logger) -> None:
        self._ranking_service = RankingAnalyticsService()
        self._insights_service = InsightsAnalyticsService(logger=logger)

    def ranking_por_score(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        score_column: str = "weighted_score",
        top_n: Optional[int] = None,
    ) -> pd.DataFrame:
        return self._ranking_service.ranking_por_score(
            pokemon_metrics_df,
            score_column=score_column,
            top_n=top_n,
        )

    def top_win_rate(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        win_rate_column: str = "win_rate",
        min_battles_column: str = "total_battles",
        min_battles: int = 1,
        top_n: int = 10,
    ) -> pd.DataFrame:
        
        return self._ranking_service.top_win_rate(
            pokemon_metrics_df,
            win_rate_column=win_rate_column,
            min_battles_column=min_battles_column,
            min_battles=min_battles,
            top_n=top_n,
        )

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

        return self._insights_service.correlacao_atributos(
            pokemon_metrics_df,
            metric_columns=metric_columns,
            stat_columns=stat_columns,
        )

    def win_rate_por_tipo(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        type_1_column: str = "type_1",
        type_2_column: str = "type_2",
        win_rate_column: str = "win_rate",
    ) -> pd.DataFrame:
    
        return self._insights_service.win_rate_por_tipo(
            pokemon_metrics_df,
            type_1_column=type_1_column,
            type_2_column=type_2_column,
            win_rate_column=win_rate_column,
        )

    def sugerir_time(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        team_size: int = 6,
        score_column: str = "weighted_score",
        diversity_by_type: bool = True,
        type_1_column: str = "type_1",
    ) -> pd.DataFrame:

        return self._insights_service.sugerir_time(
            pokemon_metrics_df,
            team_size=team_size,
            score_column=score_column,
            diversity_by_type=diversity_by_type,
            type_1_column=type_1_column,
        )
