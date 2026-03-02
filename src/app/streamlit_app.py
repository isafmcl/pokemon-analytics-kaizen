from __future__ import annotations
import sys
from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

CURRENT_FILE = Path(__file__).resolve()
SRC_PATH = CURRENT_FILE.parents[1]
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analytics.analytics_service import AnalyticsService
from app.data_access import load_combats_from_db, load_pokemon_from_db
from app.ui.utils.components import inject_theme
from app.ui.utils.data_preparation import calculate_top_winning_attribute
from app.ui.sections import (
    TopPokemonTypeSection,
    CorrelationSection,
    WinRateTypeSection,
)
from app.ui.renderers import (
    render_overview_cards,
    render_pokemon_team_cards,
)
from config.logger import get_logger
from services.etl.data_transformation.transform_service import TransformService


def _setup_page() -> None:
    st.set_page_config(
        page_title="Análise Estratégica de Combates Pokémon",
        layout="wide",
    )
    inject_theme()


def _load_and_prepare_data(
    logger,
) -> tuple[Optional[pd.DataFrame], pd.DataFrame, pd.DataFrame]:
    pokemon_df = load_pokemon_from_db()
    if pokemon_df.empty:
        st.warning("Nenhum dado encontrado no banco. Execute o ETL primeiro.")
        return None, pokemon_df, pd.DataFrame()

    transform_service = TransformService(logger=logger)
    cleaned_pokemon_df = transform_service.clean_pokemon_dataframe(pokemon_df)

    combats_df = load_combats_from_db()
    if combats_df.empty:
        st.warning("Nenhum combate encontrado no banco. Execute o ETL primeiro.")
        return None, pokemon_df, combats_df

    metrics_df = transform_service.build_pokemon_battle_metrics(
        cleaned_pokemon_df,
        combats_df,
    )
    return metrics_df, pokemon_df, combats_df

def main() -> None:
    """Orquestrador principal da dashboard."""
    _setup_page()
    logger = get_logger("app.streamlit")
    metrics_df, pokemon_df, combats_df = _load_and_prepare_data(logger)
    if metrics_df is None:
        return

    analytics_service = AnalyticsService(logger=logger)
    
    try:
        corr_metrics_df = analytics_service.correlacao_atributos(metrics_df)
    except Exception as exc:
        st.warning(f"Não foi possível calcular correlações: {exc}")
        corr_metrics_df = None

    st.title("Análise Estratégica de Combates Pokémon")
    top_attr, top_attr_corr = calculate_top_winning_attribute(corr_metrics_df)
    
    render_overview_cards(
        total_pokemon=len(pokemon_df),
        total_combats=len(combats_df),
        top_attribute=top_attr,
        top_attribute_corr=top_attr_corr,
    )
    
    st.markdown("---")
    CorrelationSection().render(corr_metrics_df, metrics_df)
    
    # ========== WIN RATE ANÁLISE ==========
    st.markdown("### Taxa de Vitória por Tipo")
    WinRateTypeSection().render(metrics_df)
    
    # ========== RANKING DETALHADO ==========
    st.markdown("---")
    st.markdown("### Ranking Detalhado")
    TopPokemonTypeSection().render(metrics_df)
    
    # ========== MELHOR TIME ESTRATÉGICO ==========
    st.markdown("---")
    st.markdown("### Melhor Time Estratégico")
    time_df = analytics_service.sugerir_time(metrics_df, team_size=6)
    cols_to_show = ["pokemon_id", "name", "type_1", "type_2", "weighted_score"]
    if "total_wins" in time_df.columns:
        cols_to_show.append("total_wins")
    time_view = time_df[cols_to_show].copy()
    time_view = time_view.fillna("")
    render_pokemon_team_cards(time_view)
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #718096; font-size: 0.85rem; margin-top: 2rem;'>"
        "Dashboard de Análise Pokémon | Desenvolvido com Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()