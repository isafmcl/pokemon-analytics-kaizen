from __future__ import annotations
from typing import Optional
import pandas as pd
import streamlit as st

from analytics.analytics_service import AnalyticsService
from app.ui.utils.constants import STAT_LABELS
from app.ui.utils.data_preparation import (
    calculate_best_pokemon_by_type,
    calculate_win_rate_pct,
    get_pokemon_top_n_by_type,
    build_types_long_format,
    normalize_numeric_column,
)
from app.ui.utils.etl_validation import ETLValidator
from app.ui.renderers import (
    render_dataframe_section,
    render_top_attribute_insight,
    render_validation_results,
    render_top_pokemon_chart,
    render_win_rate_line_chart,
    render_pokemon_cards,
    render_correlation_bar_chart,
    render_win_rate_radar,
)


class ETLValidationSection:
    """ validação do ETL."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def render(
        self,
        pokemon_df: pd.DataFrame,
        combats_df: pd.DataFrame,
        metrics_df: pd.DataFrame,
    ) -> None:
        st.subheader("Validacao do ETL")
        st.caption("Checagens basicas de consistencia dos dados")

        if pokemon_df.empty or combats_df.empty:
            st.warning("Nao foi possivel validar: dados vazios no banco.")
            return

        validator = ETLValidator()
        results = validator.validar_tudo(pokemon_df, combats_df, metrics_df)
        
        results_dicts = [
            {
                "checagem": r.checagem,
                "resultado": r.resultado,
                "status": r.status,
            }
            for r in results
        ]
        render_validation_results(results_dicts)


class InfluentAttributesSection:
    def render(self, corr_metrics_df: Optional[pd.DataFrame]) -> None:
        st.subheader("Quais atributos mais influenciam a vitória em um combate?")

        if corr_metrics_df is None or "win_rate" not in corr_metrics_df.columns:
            st.info("Dados insuficientes para medir influência dos atributos.")
            return

        win_corr = corr_metrics_df["win_rate"].dropna()
        if win_corr.empty:
            st.info("Não há variação suficiente para calcular correlação.")
            return

        render_top_attribute_insight(win_corr, STAT_LABELS)

        table = (
            win_corr.abs()
            .sort_values(ascending=False)
            .reindex(win_corr.abs().index)
            .rename(index=STAT_LABELS)
            .to_frame("Correlacao com Vitorias")
            .round(2)
        )
        st.dataframe(table, use_container_width=True)


class WinRateTypeSection:
    def render(self, metrics_df: pd.DataFrame) -> None:
        plot_df = calculate_best_pokemon_by_type(metrics_df)
        if plot_df.empty:
            st.warning("Nenhuma informação de tipo disponível para cálculo.")
            return

        render_win_rate_line_chart(plot_df)


class TopPokemonTypeSection:

    def render(self, metrics_df: pd.DataFrame) -> None:
        st.markdown("**Top 5 Pokémon do tipo (win rate)**")
        st.markdown("*Selecione um tipo para ver os melhores Pokémons*")

        if "win_rate" not in metrics_df.columns:
            st.info("Dados insuficientes para exibir o ranking.")
            return

        long_df = build_types_long_format(metrics_df)
        
        if long_df.empty:
            st.info("Não há tipos disponíveis para análise.")
            return

        types = sorted(long_df["type"].dropna().unique())
        selected_type = st.selectbox("Tipo", options=types)

        top5 = get_pokemon_top_n_by_type(metrics_df, selected_type, top_n=5)

        if top5.empty:
            st.info("Nenhum Pokemon com batalhas suficientes para este tipo.")
            return

        render_top_pokemon_chart(top5)


class DiagnosticSection:

    def render(self, metrics_df: pd.DataFrame) -> None:
        st.subheader("Diagnostico: por que as taxas estao baixas?")
        st.caption("Mostra o top por tipo com vitorias/batalhas e a taxa real calculada")

        if "total_battles" not in metrics_df.columns or "total_wins" not in metrics_df.columns:
            st.info("Dados insuficientes para diagnostico.")
            return

        long_df = build_types_long_format(metrics_df)
        if long_df.empty:
            st.info("Nao ha tipos disponiveis para diagnostico.")
            return

        long_df = long_df[long_df["total_battles"] > 0]
        long_df["total_battles"] = normalize_numeric_column(long_df["total_battles"])
        long_df["total_wins"] = normalize_numeric_column(long_df["total_wins"])
        
        long_df["win_rate_pct"] = calculate_win_rate_pct(
            long_df["total_wins"],
            long_df["total_battles"],
        )

        types = sorted(long_df["type"].dropna().unique())
        selected_type = st.selectbox("Tipo para diagnostico", options=types, key="diag_type")

        type_df = long_df[long_df["type"] == selected_type].copy()
        top10 = type_df.sort_values(
            by=["win_rate_pct", "total_battles"],
            ascending=[False, False],
        ).head(10)

        if top10.empty:
            st.info("Nao ha pokemons com batalhas suficientes para esse tipo.")
            return

        st.dataframe(
            top10[["name", "type", "total_wins", "total_battles", "win_rate_pct"]],
            use_container_width=True,
        )

        best = top10.iloc[0]
        st.info(
            "Top do tipo = "
            f"{best['name']} com {best['total_wins']}/{best['total_battles']} "
            f"= {best['win_rate_pct']:.2f}%"
        )


class BestTeamSection:
    """Seção de melhor time estratégico."""
    
    def render(
        self,
        metrics_df: pd.DataFrame,
        analytics_service: AnalyticsService,
    ) -> None:
        """Renderiza melhor time sugerido."""
        st.subheader("Melhor Time Estratégico")
        st.caption("Composição ideal baseada em score ponderado")
        
        time_df = analytics_service.sugerir_time(metrics_df, team_size=6)
        cols = ["pokemon_id", "name", "type_1", "type_2", "weighted_score"]
        
        if "total_wins" in time_df.columns:
            cols.append("total_wins")

        time_view = time_df[cols].copy()
        time_view = time_view.fillna("")
        render_pokemon_cards(time_view)


class CorrelationSection:
    def render(self, corr_metrics_df: Optional[pd.DataFrame], metrics_df: Optional[pd.DataFrame] = None) -> None:
        st.markdown("### Análise de Correlações")
        st.markdown("*Como cada atributo impacta a vitória?*")
        
        st.info(
            "**Impacto na Vitória** (Gráfico): Mostra o \"fator decisivo\". Qual atributo realmente separa quem ganha de quem perde.\n\n"
            "**Média Geral** (Radar): Mostra o padrão do jogo. Como é o Pokémon \"comum\"."
        )

        if corr_metrics_df is None or corr_metrics_df.empty:
            st.info("Dados insuficientes para exibir correlações.")
            return

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Correlação com Win Rate")
            st.caption("Impacto de cada atributo nas vitórias")
            render_correlation_bar_chart(corr_metrics_df)
        
        with col2:
            st.subheader("Perfil de Atributos")
            st.caption("Valores médios dos atributos")
            if metrics_df is not None:
                render_win_rate_radar(metrics_df)
