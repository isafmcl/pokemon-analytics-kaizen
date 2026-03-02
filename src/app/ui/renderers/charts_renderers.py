from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_win_rate_line_chart(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("Dados insuficientes para exibir o gráfico.")
        return
    
    if "win_rate_pct" not in data.columns or "type" not in data.columns:
        st.warning("Dados incompletos: faltam colunas 'win_rate_pct' ou 'type'.")
        return
    
    plot_df = data.copy().sort_values("win_rate_pct", ascending=True).reset_index(drop=True)
    
    fig = go.Figure()
    
    min_val = plot_df["win_rate_pct"].min()
    max_val = plot_df["win_rate_pct"].max()
    x_numeric = list(range(len(plot_df)))
    
    fig.add_trace(go.Scatter(
        x=x_numeric,
        y=plot_df["win_rate_pct"],
        mode='lines+markers',
        name='Win Rate',
        line=dict(color='#1e40af', width=8, shape='linear', dash='solid'),
        fill='tozeroy',
        fillcolor='rgba(30, 64, 175, 0.25)',
        marker=dict(
            size=16,
            color='#1e40af',
            line=dict(color='white', width=3),
            symbol='circle',
        ),
        connectgaps=True,
        hovertemplate="<b>%{customdata}</b><br>Taxa: <b>%{y:.1f}%</b><extra></extra>",
        customdata=plot_df["type"],
    ))
    
    annotations = []
    for idx, row in plot_df.iterrows():
        annotations.append(
            dict(
                x=idx,
                y=row["win_rate_pct"],
                text=f"<b>{row['win_rate_pct']:.1f}%</b>",
                showarrow=False,
                font=dict(size=11, color='#1a202c', family='Arial'),
                xanchor='center',
                yanchor='bottom',
            )
        )
    
    y_min = max(min_val - 5, 0)
    y_max = min(max_val + 15, 105)
    
    fig.update_layout(
        height=420,
        xaxis_title="Tipo de Pokémon",
        yaxis_title="Win Rate (%)",
        xaxis=dict(
            tickvals=x_numeric,
            ticktext=plot_df["type"].tolist(),
            tickangle=-45,
            showgrid=True,
            gridwidth=1,
            gridcolor='#cbd5e1',
            showline=True,
            linewidth=2,
            linecolor='#475569',
        ),
        yaxis=dict(
            range=[y_min, y_max],
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#475569',
            gridwidth=2,
            gridcolor='#e2e8f0',
            showline=True,
            linewidth=2,
            linecolor='#475569',
        ),
        font=dict(size=12, family="Arial", color='#1e293b'),
        plot_bgcolor="rgba(248, 250, 252, 0.8)",
        paper_bgcolor="#f8fafc",
        margin=dict(l=70, r=60, t=100, b=100),
        showlegend=False,
        hovermode='x unified',
        annotations=annotations,
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_win_rate_radar(metrics_df: pd.DataFrame) -> None:
    if metrics_df.empty:
        st.info("Dados insuficientes para radar chart.")
        return
    
    attrs_base = {
        "Ataque": metrics_df["attack"].mean() if "attack" in metrics_df.columns else 0,
        "Defesa": metrics_df["defense"].mean() if "defense" in metrics_df.columns else 0,
        "HP": metrics_df["hp"].mean() if "hp" in metrics_df.columns else 0,
        "Velocidade": metrics_df["speed"].mean() if "speed" in metrics_df.columns else 0,
        "Esp. Ataque": metrics_df["sp_attack"].mean() if "sp_attack" in metrics_df.columns else 0,
    }
    
    max_val = max(attrs_base.values()) if attrs_base.values() else 1
    attrs_norm = {k: (v / max_val * 100) if max_val > 0 else 0 for k, v in attrs_base.items()}
    
    fig = go.Figure(data=go.Scatterpolar(
        r=list(attrs_norm.values()),
        theta=list(attrs_norm.keys()),
        fill='toself',
        name='Atributos',
        line_color='#2563eb',
        fillcolor='rgba(37, 99, 235, 0.3)',
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
            ),
            bgcolor="rgba(240, 244, 248, 0.3)",
        ),
        height=400,
        font=dict(size=12),
        margin=dict(l=50, r=50, t=50, b=50),
        plot_bgcolor="white",
    )
    
    st.plotly_chart(fig, use_container_width=True)
