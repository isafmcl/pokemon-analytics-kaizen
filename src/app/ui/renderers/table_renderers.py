"""Renderização de tabelas e dados estruturados."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_validation_results(validation_results: list[dict]) -> None:
    """Renderiza resultados de validação do ETL em tabela."""
    if not validation_results:
        st.info("Nenhuma validação disponível.")
        return
    
    df = pd.DataFrame(validation_results)
    st.dataframe(df, use_container_width=True)


def render_win_rate_table(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("Dados insuficientes para exibir a tabela.")
        return

    display_df = data.copy()
    display_df = display_df.sort_values(by="win_rate_pct", ascending=False)
    
    cols_to_show = []
    if "type" in display_df.columns:
        cols_to_show.append("type")
    if "name" in display_df.columns:
        cols_to_show.append("name")
    
    cols_to_show.extend([col for col in ["total_wins", "total_battles", "win_rate_pct"] 
                        if col in display_df.columns])
    
    display_df = display_df[cols_to_show]

    rename_map = {
        "type": "Tipo",
        "name": "Pokémon",
        "total_wins": "Vitórias",
        "total_battles": "Batalhas",
        "win_rate_pct": "Win Rate (%)",
    }
    display_df = display_df.rename(columns=rename_map)
    
    if "Win Rate (%)" in display_df.columns:
        display_df["Win Rate (%)"] = display_df["Win Rate (%)"].apply(lambda x: f"{x:.2f}%")
  
    st.dataframe(
        display_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


def render_dataframe_section(
    df: pd.DataFrame,
    title: str = "",
    caption: str = "",
    empty_message: str = "Dados insuficientes.",
) -> None:
    if title:
        st.subheading(title)
    
    if caption:
        st.caption(caption)
    
    if df.empty:
        st.info(empty_message)
        return
    
    st.dataframe(df, use_container_width=True)
