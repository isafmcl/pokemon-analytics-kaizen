"""Renderização de insights de correlação e análises."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from ..utils.constants import STAT_LABELS


def render_top_attribute_insight(
    corr_series: pd.Series,
    labels_map: dict[str, str] = None,
) -> None:
    if corr_series.empty:
        st.info("Dados insuficientes para análise.")
        return
    
    labels = labels_map or {}
    
    win_abs = corr_series.abs().sort_values(ascending=False)
    top_attr = win_abs.index[0]
    top_label = labels.get(top_attr, top_attr)
    
    st.markdown(f"**Mais influente:** {top_label} (correlação {corr_series[top_attr]:.2f}).")


def render_top_correlations(corr_series: pd.Series, top_n: int = 5) -> None:
    """Exibe as principais correlações com win rate."""
    if corr_series.empty:
        st.info("Dados de correlação não disponíveis.")
        return
    
    top_corr = corr_series.abs().nlargest(top_n)
    
    for attr, abs_val in top_corr.items():
        actual_val = corr_series[attr]
        label = STAT_LABELS.get(attr, attr)
        direction = "Positiva ↑" if actual_val > 0 else "Negativa ↓"
        
        st.write(f"**{label}**: {actual_val:.3f} ({direction})")


def render_correlation_summary(corr_df: pd.DataFrame) -> None:
    """Resumo de correlações para win rate."""
    if corr_df.empty or "win_rate" not in corr_df.columns:
        st.info("Dados insuficientes para análise de correlações.")
        return
    
    win_corr = corr_df["win_rate"].dropna()
    if win_corr.empty:
        st.info("Sem correlações de win rate disponíveis.")
        return
    
    top_3_abs = win_corr.abs().nlargest(3)
    
    st.write("**Principais influenciadores de vitória:**")
    for i, (attr, _) in enumerate(top_3_abs.items(), 1):
        actual = win_corr[attr]
        label = STAT_LABELS.get(attr, attr)
        emoji = "📈" if actual > 0 else "📉"
        st.write(f"{i}. {emoji} **{label}**: {actual:.3f}")
