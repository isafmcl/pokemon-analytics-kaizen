"""Cálculos puros de métricas de batalha.

Este módulo contém funções utilitárias para calcular métricas de batalha
a partir de DataFrames. Nenhuma responsabilidade de orquestração ou logging.

"""
from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd


def compute_total_battles(
    *,
    combats: pd.DataFrame,
    first_column: str,
    second_column: str,
) -> pd.Series:
    """Computa o total de batalhas por Pokemon a partir do DataFrame de combates."""

    first_counts = combats[first_column].value_counts(dropna=True)
    second_counts = combats[second_column].value_counts(dropna=True)
    combined = first_counts.add(second_counts, fill_value=0).astype("int64")
    return combined


def compute_total_wins(
    *,
    combats: pd.DataFrame,
    winner_column: str,
) -> pd.Series:
    """Computa o total de vitórias por Pokemon a partir do DataFrame de combates."""

    wins = combats[winner_column].value_counts(dropna=True).astype("int64")
    return wins


def combine_battles_and_wins(
    *,
    pokemon_ids: pd.Series,
    battles: pd.Series,
    wins: pd.Series,
) -> pd.DataFrame:
    """Combina total de batalhas e vitórias em um DataFrame de métricas."""

    index = pd.Index(pokemon_ids.dropna().unique(), name="pokemon_id")
    metrics = pd.DataFrame(index=index)

    metrics["total_battles"] = battles.reindex(index=index).fillna(0).astype(
        "int64"
    )
    metrics["total_wins"] = wins.reindex(index=index).fillna(0).astype("int64")

    return metrics


def compute_win_rate(
    *,
    total_battles: pd.Series,
    total_wins: pd.Series,
) -> pd.Series:
    """Computa a taxa de vitória como ``total_wins / total_battles``."""

    battles = total_battles.astype("float64")
    wins = total_wins.astype("float64")

    with np.errstate(divide="ignore", invalid="ignore"):
        win_rate = wins / battles

    win_rate = win_rate.fillna(0.0)
    win_rate = win_rate.clip(lower=0.0, upper=1.0)
    return win_rate


def compute_weighted_score(
    *,
    win_rate: pd.Series,
    total_battles: pd.Series,
) -> pd.Series:
    """Computa um score ponderado baseado em taxa de vitória e experiência."""

    battles_float = total_battles.astype("float64")
    weight = 1.0 + np.log1p(battles_float)
    score = win_rate.astype("float64") * weight
    return score
