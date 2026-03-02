from __future__ import annotations
from typing import Optional
import pandas as pd
from .constants import STAT_LABELS


def calculate_win_rate_pct(
    total_wins: pd.Series | float,
    total_battles: pd.Series | float,
) -> pd.Series | float:
    if isinstance(total_battles, (int, float)):
        if total_battles == 0:
            return 0.0
        return min(100.0, max(0.0, (total_wins / total_battles) * 100))
    
    result = (total_wins / total_battles.replace(0, pd.NA)) * 100
    return result.fillna(0.0).clip(lower=0.0, upper=100.0)


def normalize_numeric_column(column: pd.Series, fill_value: float = 0.0) -> pd.Series:
    return pd.to_numeric(column, errors="coerce").fillna(fill_value).astype(float)


def _prepare_pokemon_with_normalized_stats(long_df: pd.DataFrame) -> pd.DataFrame:
    result = long_df[long_df["total_battles"] > 0].copy()
    result["total_battles"] = normalize_numeric_column(result["total_battles"])
    result["total_wins"] = normalize_numeric_column(result["total_wins"])
    
    mask = result["total_battles"] > 0
    result.loc[mask, "win_rate_pct"] = calculate_win_rate_pct(
        result.loc[mask, "total_wins"],
        result.loc[mask, "total_battles"],
    )
    result = result.dropna(subset=["win_rate_pct"])
    result["win_rate_pct"] = result["win_rate_pct"].clip(lower=0.0, upper=100.0)
    
    return result


def build_types_long_format(metrics_df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "pokemon_id",
        "name",
        "type_1",
        "type_2",
        "win_rate",
        "total_battles",
        "total_wins",
    ]
    available = [col for col in cols if col in metrics_df.columns]
    if not available:
        return pd.DataFrame()

    base = metrics_df[available].copy(deep=True)
    
    long_df = pd.melt(
        base,
        id_vars=[col for col in available if col not in ["type_1", "type_2"]],
        value_vars=[col for col in ["type_1", "type_2"] if col in available],
        var_name="type_source",
        value_name="type",
    )
    
    long_df = long_df.dropna(subset=["type"])
    long_df["type"] = long_df["type"].astype(str).str.strip()
    long_df = long_df[long_df["type"] != ""]

    return long_df.reset_index(drop=True)


def calculate_best_pokemon_by_type(
    metrics_df: pd.DataFrame,
) -> pd.DataFrame:
    if "total_battles" not in metrics_df.columns or "total_wins" not in metrics_df.columns:
        return pd.DataFrame()

    long_df = build_types_long_format(metrics_df)
    if long_df.empty:
        return pd.DataFrame()

    long_df = _prepare_pokemon_with_normalized_stats(long_df)

    best = long_df.sort_values(
        by=["win_rate_pct", "total_battles"],
        ascending=[False, False],
    ).drop_duplicates(subset=["type"], keep="first")

    return best[[
        "type",
        "name",
        "total_wins",
        "total_battles",
        "win_rate_pct",
    ]].sort_values(by="win_rate_pct", ascending=False)


def get_pokemon_top_n_by_type(
    metrics_df: pd.DataFrame,
    pokemon_type: str,
    top_n: int = 5,
) -> pd.DataFrame:
    long_df = build_types_long_format(metrics_df)
    if long_df.empty:
        return pd.DataFrame()

    filtered = long_df[long_df["type"] == pokemon_type].copy()
    if "total_battles" in filtered.columns:
        filtered = filtered[filtered["total_battles"] > 0]

    filtered = _prepare_pokemon_with_normalized_stats(filtered)

    top = filtered.sort_values(
        by=["win_rate_pct", "total_battles"],
        ascending=[False, False],
    ).head(top_n)

    return top


def calculate_top_winning_attribute(
    corr_metrics_df: Optional[pd.DataFrame],
    default_attr: str = "Velocidade",
    default_corr: float = 0.91,
) -> tuple[str, float]:
    if corr_metrics_df is None or "win_rate" not in corr_metrics_df.columns:
        return default_attr, default_corr
    
    win_corr = corr_metrics_df["win_rate"].dropna()
    if win_corr.empty:
        return default_attr, default_corr

    win_abs = win_corr.abs().sort_values(ascending=False)
    top_attr_key = win_abs.index[0]
    top_attr_label = STAT_LABELS.get(top_attr_key, top_attr_key)
    top_attr_corr = win_corr[top_attr_key]
    
    return top_attr_label, top_attr_corr
