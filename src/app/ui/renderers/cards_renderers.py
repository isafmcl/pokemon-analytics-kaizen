from __future__ import annotations
import pandas as pd
import streamlit as st


def render_metric_cards(
    total_pokemon: int,
    total_combats: int,
    total_victories: int,
) -> None:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Pokémon", f"{total_pokemon}")
    with col2:
        st.metric("Total de Combates", f"{total_combats}")
    with col3:
        st.metric("Total de Vitórias", f"{total_victories}")


def render_overview_cards(
    total_pokemon: int,
    total_combats: int,
    top_attribute: str = "Velocidade",
    top_attribute_corr: float = 0.91,
) -> None:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pokémons</div>
            <div class="metric-value">{total_pokemon}</div>
            <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.5rem;">Disponíveis</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card orange">
            <div class="metric-label">Combates</div>
            <div class="metric-value">{total_combats}</div>
            <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.5rem;">Realizados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card green">
            <div class="metric-label">Atributo Vencedor</div>
            <div class="metric-value">{top_attribute}</div>
            <div style="font-size: 0.8rem; opacity: 0.9; margin-top: 0.5rem;">Correlação: {top_attribute_corr:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_pokemon_cards(team_df: pd.DataFrame) -> None:
    if team_df.empty:
        st.info("Dados insuficientes para sugerir um time.")
        return

    cols = st.columns(len(team_df))
    
    for col, (_, row) in zip(cols, team_df.iterrows()):
        tipos = " / ".join(filter(None, [row.get("type_1"), row.get("type_2")]))
        wins = int(row.get("total_wins", 0))
        
        with col:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:8px; text-align:center;">
                <h3>{row.get('name', '?')}</h3>
                <p style="color:gray; font-size:12px; margin-bottom:5px;">{tipos}</p>
                <b>🏆 {wins} Vitórias</b>
            </div>
            """, unsafe_allow_html=True)


def render_pokemon_team_cards(team_df: pd.DataFrame) -> None:
    if team_df.empty:
        st.info("Dados insuficientes para sugerir um time.")
        return
    team_df_sorted = team_df.sort_values("total_wins", ascending=False).reset_index(drop=True)
    
    num_pokemons = min(len(team_df_sorted), 6)
    cols = st.columns(num_pokemons)
    
    for col_idx, (_, pokemon) in enumerate(team_df_sorted.head(6).iterrows()):
        with cols[col_idx]:
            name = pokemon.get("name", "?")
            tipo1 = pokemon.get("type_1", "")
            tipo2 = pokemon.get("type_2", "")
            tipos = f"{tipo1}"
            if tipo2:
                tipos += f"/{tipo2}"
            
            wins = int(pokemon.get("total_wins", 0))
            battles = int(pokemon.get("total_battles", 0))
            score = pokemon.get("weighted_score", 0)
            
            st.markdown(f"""
            <div class="team-card">
                <div class="pokemon-avatar">{name[0] if name else "?"}</div>
                <div class="pokemon-name">{name}</div>
                <div class="pokemon-type">{tipos}</div>
                <div class="pokemon-stats">
                    🏆 {wins} Vitórias
                </div>
                {f'<div style="font-size: 0.75rem; color: #718096; margin-top: 0.5rem;">Score: {score:.1f}</div>' if score > 0 else ''}
            </div>
            """, unsafe_allow_html=True)


def render_top_pokemon_chart(data: pd.DataFrame) -> None:
    if data.empty:
        st.warning("Dados insuficientes para exibir o ranking.")
        return
    
    plot_df = data.sort_values("win_rate_pct", ascending=False).reset_index(drop=True).head(5)
    
    cols = st.columns(5)
    
    for idx, (col, (_, row)) in enumerate(zip(cols, plot_df.iterrows())):
        with col:
            winrate = row.get('win_rate_pct', 0)
            name = row.get('name', '?')
            
            if winrate >= 95:
                color = '#10b981'
            elif winrate >= 90:
                color = '#3b82f6'
            elif winrate >= 85:
                color = '#f59e0b'
            else:
                color = '#ef4444'
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color} 0%, {color}cc 100%);
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                color: white;
                font-weight: 700;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            ">
                <div style="font-size: 0.8rem; opacity: 0.9; margin-bottom: 0.5rem;">#{idx+1}</div>
                <div style="font-size: 0.9rem; margin-bottom: 1rem; word-wrap: break-word;">{name}</div>
                <div style="font-size: 2.2rem; font-weight: 900; margin: 0.5rem 0;">{winrate:.1f}%</div>
                <div style="font-size: 0.75rem; opacity: 0.85;">Win Rate</div>
            </div>
            """, unsafe_allow_html=True)
