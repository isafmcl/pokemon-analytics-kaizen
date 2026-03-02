"""Módulo de renderização UI - re-exporta todas as funções."""

from .cards_renderers import (
    render_metric_cards,
    render_overview_cards,
    render_pokemon_cards,
    render_pokemon_team_cards,
    render_top_pokemon_chart,
)

from .charts_renderers import (
    render_win_rate_line_chart,
    render_win_rate_radar,
)

from .correlation_renderers import (
    render_correlation_bar_chart,
)

from .table_renderers import (
    render_validation_results,
    render_win_rate_table,
    render_dataframe_section,
)

from .insight_renderers import (
    render_top_attribute_insight,
)

__all__ = [
    "render_metric_cards",
    "render_overview_cards",
    "render_pokemon_cards",
    "render_pokemon_team_cards",
    "render_top_pokemon_chart",
    "render_win_rate_line_chart",
    "render_correlation_bar_chart",
    "render_win_rate_radar",
    "render_validation_results",
    "render_win_rate_table",
    "render_dataframe_section",
    "render_top_attribute_insight",
]
