from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ..utils.constants import STAT_LABELS, CORRELATION_COLORS


def render_correlation_bar_chart(corr_df: pd.DataFrame) -> None:
    if corr_df.empty or "win_rate" not in corr_df.columns:
        st.info("Dados insuficientes para exibir correlações.")
        return
    
    win_corr = corr_df["win_rate"].dropna()
    if win_corr.empty:
        st.info("Sem dados de correlação disponíveis.")
        return
    
    plot_data_sorted = win_corr.abs().sort_values(ascending=True)
    plot_labels = [STAT_LABELS.get(idx, idx) for idx in plot_data_sorted.index]
    plot_values = [win_corr[idx] for idx in plot_data_sorted.index]
    plot_values_abs = plot_data_sorted.values
    plot_values_abs_display = [max(val, 0.02) for val in plot_values_abs]
    
    colors = []
    for val in plot_values_abs:
        if val >= 0.7:
            colors.append(CORRELATION_COLORS["high"])
        elif val >= 0.5:
            colors.append(CORRELATION_COLORS["medium"])
        elif val >= 0.3:
            colors.append(CORRELATION_COLORS["low"])
        else:
            colors.append(CORRELATION_COLORS["minimal"])
    
    fig = go.Figure(data=[
        go.Bar(
            y=plot_labels,
            x=plot_values_abs_display,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='white', width=2),
            ),
            hovertemplate="<b>%{y}</b><br>Correlação: <b>%{customdata:.2f}</b><extra></extra>",
            customdata=plot_values,
        )
    ])
    
    annotations = []
    for i, (label, val) in enumerate(zip(plot_labels, plot_values)):
        annotations.append(
            dict(
                x=max(plot_values_abs[i], 0.02) + 0.02,
                y=label,
                text=f"<b>{val:.2f}</b>",
                showarrow=False,
                xanchor='left',
                yanchor='middle',
                font=dict(size=12, color='#1a202c', family='Arial'),
            )
        )
    
    fig.update_layout(
        height=340,
        xaxis_title="Correlação com Win Rate",
        yaxis_title="",
        xaxis=dict(range=[0, 1.4], gridwidth=1, gridcolor='#e2e8f0'),
        plot_bgcolor="rgba(248, 250, 251, 0.5)",
        paper_bgcolor="white",
        margin=dict(l=150, r=80, t=40, b=60),
        showlegend=False,
        font=dict(size=12, family="Arial"),
        annotations=annotations,
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    _render_correlation_insights(win_corr)


def _render_correlation_insights(win_corr: pd.Series) -> None:
    sorted_by_abs = win_corr.abs().sort_values(ascending=False)
    max_idx = sorted_by_abs.index[0]
    second_idx = sorted_by_abs.index[1] if len(sorted_by_abs) > 1 else max_idx
    min_idx = win_corr.abs().idxmin()
    
    max_label = STAT_LABELS.get(max_idx, max_idx)
    second_label = STAT_LABELS.get(second_idx, second_idx)
    min_label = STAT_LABELS.get(min_idx, min_idx)
    max_val = win_corr[max_idx]
    second_val = win_corr[second_idx]
    min_val = win_corr[min_idx]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <div style="font-size: 0.8rem; opacity: 0.9;">Mais Influente</div>
            <div style="font-size: 1.3rem; font-weight: 900; margin: 0.5rem 0;">{max_label}</div>
            <div style="font-size: 1.8rem; font-weight: 900;">{max_val:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <div style="font-size: 0.8rem; opacity: 0.9;">Segundo Lugar</div>
            <div style="font-size: 1.3rem; font-weight: 900; margin: 0.5rem 0;">{second_label}</div>
            <div style="font-size: 1.8rem; font-weight: 900;">{second_val:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
            padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <div style="font-size: 0.8rem; opacity: 0.9;">Menor Impacto</div>
            <div style="font-size: 1.3rem; font-weight: 900; margin: 0.5rem 0;">{min_label}</div>
            <div style="font-size: 1.8rem; font-weight: 900;">{min_val:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
