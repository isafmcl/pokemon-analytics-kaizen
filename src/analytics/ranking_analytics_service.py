from __future__ import annotations
from typing import Optional
import pandas as pd
from .base_analytics_service import BaseAnalyticsService


class RankingAnalyticsService(BaseAnalyticsService):

    def ranking_por_score(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        score_column: str = "weighted_score",
        top_n: Optional[int] = None,
    ) -> pd.DataFrame:

        self.ensure_columns(pokemon_metrics_df, [score_column], "pokemon_metrics_df")
        ranked = pokemon_metrics_df.sort_values(by=score_column, ascending=False)
        if top_n is not None:
            ranked = ranked.head(top_n)
        return ranked.reset_index(drop=True)

    def top_win_rate(
        self,
        pokemon_metrics_df: pd.DataFrame,
        *,
        win_rate_column: str = "win_rate",
        min_battles_column: str = "total_battles",
        min_battles: int = 1,
        top_n: int = 10,
    ) -> pd.DataFrame:
        self.ensure_columns(
            pokemon_metrics_df,
            [win_rate_column, min_battles_column],
            "pokemon_metrics_df",
        )

        eligible = pokemon_metrics_df[
            pokemon_metrics_df[min_battles_column] >= int(min_battles)
        ]
        sorted_df = eligible.sort_values(by=win_rate_column, ascending=False)
        return sorted_df.head(top_n).reset_index(drop=True)
