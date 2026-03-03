"""
================================================================================
DASHBOARD DE MONITORAMENTO DE JOGOS — BOTAFOGO FSA
Departamento de Scouting | Jogadores Cadastrados por Jogo & Analista
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# ============================================================================
# CONFIGURACAO
# ============================================================================

st.set_page_config(
    page_title="Monitoramento de Jogos | Botafogo FSA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

SHEET_ID = "13u44MBj2zP-x0hssu_7UXrpI7AE-pF24rzr8qDTt4cE"

# ============================================================================
# PALETA
# ============================================================================

COLORS = {
    "bg": "#0C0C0F",
    "card": "#151518",
    "card_border": "#2A2A32",
    "text": "#EDEDEF",
    "text_muted": "#8B8B96",
    "red": "#C8102E",
    "red_dim": "rgba(200,16,46,0.15)",
    "green": "#2EC4B6",
    "green_dim": "rgba(46,196,182,0.15)",
    "amber": "#F4A261",
    "amber_dim": "rgba(244,162,97,0.15)",
    "blue": "#457B9D",
    "blue_dim": "rgba(69,123,157,0.15)",
    "purple": "#7C3AED",
    "grid": "#1E1E24",
}

ANALISTA_COLORS = {
    "Caio": COLORS["red"],
    "Cassio": COLORS["green"],
    "Gabriel": COLORS["blue"],
}

POS_COLORS = [
    COLORS["red"], COLORS["green"], COLORS["amber"], COLORS["blue"],
    COLORS["purple"], "#E76F51", "#A8DADC", "#264653", "#B5838D",
    "#6D6875", "#FFB4A2", "#F07167", "#00B4D8", "#90BE6D",
]


# ============================================================================
# CSS
# ============================================================================

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp { background-color: #0C0C0F; }
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #EDEDEF; }
        .dashboard-header {
            background: linear-gradient(135deg, #151518 0%, #1a1a20 100%);
            border: 1px solid #2A2A32; border-radius: 12px;
            padding: 24px 32px; margin-bottom: 24px;
            display: flex; align-items: center; gap: 20px;
        }
        .header-icon {
            width: 48px; height: 48px;
            background: rgba(200,16,46,0.15); border: 1px solid rgba(200,16,46,0.3);
            border-radius: 12px; display: flex; align-items: center;
            justify-content: center; font-size: 24px;
        }
        .header-title {
            font-size: 22px; font-weight: 700; color: #EDEDEF;
            letter-spacing: -0.02em; margin: 0;
        }
        .header-sub {
            font-size: 12px; color: #8B8B96;
            font-family: 'Courier New', monospace; letter-spacing: 0.05em;
        }
        .kpi-row { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
        .kpi-card {
            flex: 1; min-width: 160px; background: #151518;
            border: 1px solid #2A2A32; border-radius: 12px;
            padding: 18px 22px; transition: border-color 0.2s;
        }
        .kpi-card:hover { border-color: #3A3A44; }
        .kpi-label {
            font-size: 10px; text-transform: uppercase;
            letter-spacing: 0.12em; color: #8B8B96;
            font-family: 'Courier New', monospace; margin-bottom: 6px;
        }
        .kpi-value { font-size: 30px; font-weight: 700; line-height: 1; color: #EDEDEF; }
        .kpi-sub { font-size: 11px; color: #5A5A65; margin-top: 4px; }
        .kpi-value.red { color: #C8102E; }
        .kpi-value.green { color: #2EC4B6; }
        .kpi-value.amber { color: #F4A261; }
        .kpi-value.blue { color: #457B9D; }
        .section-title {
            display: flex; align-items: center; gap: 10px;
            margin: 28px 0 16px 0;
        }
        .section-title span {
            font-size: 14px; font-weight: 600; text-transform: uppercase;
            letter-spacing: 0.06em; color: #EDEDEF;
            font-family: 'Courier New', monospace;
        }
        .section-title .line { flex: 1; height: 1px; background: #2A2A32; }
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px; background: transparent; padding: 0;
            border-bottom: 1px solid #2A2A32;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent; border: 1px solid transparent;
            border-radius: 8px 8px 0 0; color: #8B8B96;
            font-weight: 500; font-size: 13px; padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background: #151518; color: #EDEDEF;
            border-color: #2A2A32; border-bottom-color: #151518;
        }
        section[data-testid="stSidebar"] {
            background: #111114; border-right: 1px solid #2A2A32;
        }
        .styled-table {
            width: 100%; border-collapse: collapse;
            background: #151518; border-radius: 12px; overflow: hidden;
            border: 1px solid #2A2A32;
        }
        .styled-table th {
            padding: 12px 16px; text-align: left;
            font-size: 10px; text-transform: uppercase;
            letter-spacing: 0.1em; color: #8B8B96;
            font-family: 'Courier New', monospace; font-weight: 600;
            background: #121215; border-bottom: 1px solid #2A2A32;
        }
        .styled-table td {
            padding: 10px 16px; font-size: 13px; color: #EDEDEF;
            border-bottom: 1px solid #1E1E24;
        }
        .styled-table tr:hover td { background: #1C1C22; }
        .badge {
            font-size: 11px; padding: 2px 8px; border-radius: 4px;
            font-weight: 500; display: inline-block;
        }
        .badge-red { background: rgba(200,16,46,0.15); color: #C8102E; }
        .badge-green { background: rgba(46,196,182,0.15); color: #2EC4B6; }
        .badge-blue { background: rgba(69,123,157,0.15); color: #457B9D; }
        .badge-amber { background: rgba(244,162,97,0.15); color: #F4A261; }
        .bar-cell { display: flex; align-items: center; gap: 8px; }
        .bar-fill {
            height: 6px; border-radius: 3px;
            background: linear-gradient(90deg, #C8102E, #F4A261);
        }
        [data-testid="stMetric"] {
            background: #151518 !important;
            border: 1px solid #2A2A32; border-radius: 12px; padding: 16px !important;
        }
        [data-testid="stMetricLabel"] { color: #8B8B96 !important; font-size: 11px !important; }
        [data-testid="stMetricValue"] { color: #EDEDEF !important; }
        #MainMenu, footer, header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================================
# DADOS
# ============================================================================

@st.cache_data(ttl=300)
def load_sheet(sheet_name):
    url = (
        "https://docs.google.com/spreadsheets/d/"
        + SHEET_ID
        + "/gviz/tq?tqx=out:csv&sheet="
        + sheet_name.replace(" ", "%20")
    )
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_from_xlsx(file_bytes):
    jogos = pd.read_excel(file_bytes, sheet_name="Lista de Jogos")
    obs = pd.read_excel(file_bytes, sheet_name="Observações")
    jogadores = pd.read_excel(file_bytes, sheet_name="Cadastro de Jogadores")
    return jogos, obs, jogadores


def load_all_data():
    df_jogos = load_sheet("Lista de Jogos")
    if not df_jogos.empty:
        df_obs = load_sheet("Observações")
        df_jogadores = load_sheet("Cadastro de Jogadores")
    elif "xlsx_data" in st.session_state:
        df_jogos, df_obs, df_jogadores = load_from_xlsx(st.session_state["xlsx_data"])
    else:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if not df_jogos.empty:
        df_jogos.columns = df_jogos.columns.str.strip()
        if "ID_Jogo" in df_jogos.columns:
            df_jogos["ID_Jogo"] = pd.to_numeric(df_jogos["ID_Jogo"], errors="coerce")
        if "Data" in df_jogos.columns:
            df_jogos["Data"] = pd.to_datetime(df_jogos["Data"], errors="coerce", dayfirst=True)

    if not df_obs.empty:
        df_obs.columns = df_obs.columns.str.strip()
        if "ID_Jogo" in df_obs.columns:
            df_obs["ID_Jogo"] = pd.to_numeric(df_obs["ID_Jogo"], errors="coerce")
        if "ID_Jogador" in df_obs.columns:
            df_obs["ID_Jogador"] = pd.to_numeric(df_obs["ID_Jogador"], errors="coerce")

    if not df_jogadores.empty:
        df_jogadores.columns = df_jogadores.columns.str.strip()

    return df_jogos, df_obs, df_jogadores


# ============================================================================
# METRICAS
# ============================================================================

def compute_metrics(df_jogos, df_obs):
    metrics = {}
    metrics["total_jogos"] = len(df_jogos)

    if "Visto" in df_jogos.columns:
        metrics["jogos_vistos"] = int((df_jogos["Visto"] == "OK").sum())
    else:
        metrics["jogos_vistos"] = 0

    metrics["total_obs"] = len(df_obs)

    if "ID_Jogador" in df_obs.columns:
        metrics["jogadores_unicos"] = int(df_obs["ID_Jogador"].nunique())
    else:
        metrics["jogadores_unicos"] = 0

    # Jogadores por jogo
    if "ID_Jogo" in df_obs.columns:
        jog_por_jogo = df_obs.groupby("ID_Jogo")["ID_Jogador"].count().reset_index()
        jog_por_jogo.columns = ["ID_Jogo", "Jogadores_Cadastrados"]
        metrics["jogos_com_obs"] = len(jog_por_jogo)
    else:
        jog_por_jogo = pd.DataFrame(columns=["ID_Jogo", "Jogadores_Cadastrados"])
        metrics["jogos_com_obs"] = 0

    # Merge
    if "ID_Jogo" in df_jogos.columns:
        df_merged = df_jogos.merge(jog_por_jogo, on="ID_Jogo", how="left")
        df_merged["Jogadores_Cadastrados"] = (
            pd.to_numeric(df_merged["Jogadores_Cadastrados"], errors="coerce")
            .fillna(0)
            .astype(int)
        )
    else:
        df_merged = df_jogos.copy()
        df_merged["Jogadores_Cadastrados"] = 0

    # Por analista
    analista_col = "Analista" if "Analista" in df_jogos.columns else None
    visto_col = "Visto" if "Visto" in df_jogos.columns else None
    analista_stats = []

    if analista_col:
        for analista in df_jogos[analista_col].dropna().unique():
            mask = df_merged[analista_col] == analista
            total = int(mask.sum())
            vistos = int((df_merged.loc[mask, visto_col] == "OK").sum()) if visto_col else 0
            jog_obs = int(df_merged.loc[mask, "Jogadores_Cadastrados"].sum())
            media = round(jog_obs / max(vistos, 1), 1)
            vistos_sem = 0
            if visto_col:
                vistos_sem = int(
                    ((df_merged.loc[mask, visto_col] == "OK") & (df_merged.loc[mask, "Jogadores_Cadastrados"] == 0)).sum()
                )
            analista_stats.append({
                "Analista": analista,
                "Jogos": total,
                "Vistos": vistos,
                "Pendentes": total - vistos,
                "Pct_Vistos": round(vistos / max(total, 1) * 100, 1),
                "Jogadores_Obs": jog_obs,
                "Media_por_Jogo": media,
                "Vistos_Sem_Obs": vistos_sem,
            })

    df_analistas = pd.DataFrame(analista_stats)

    # Por campeonato
    camp_col = None
    for c in ["Camp.", "Campeonato"]:
        if c in df_jogos.columns:
            camp_col = c
            break

    camp_stats = []
    if camp_col:
        for camp in df_jogos[camp_col].dropna().unique():
            mask = df_merged[camp_col] == camp
            total_c = int(mask.sum())
            jog_obs_c = int(df_merged.loc[mask, "Jogadores_Cadastrados"].sum())
            jogos_com = int((df_merged.loc[mask, "Jogadores_Cadastrados"] > 0).sum())
            media_c = round(jog_obs_c / max(jogos_com, 1), 1)
            camp_stats.append({
                "Campeonato": camp,
                "Total_Jogos": total_c,
                "Jogos_Com_Obs": jogos_com,
                "Jogadores_Obs": jog_obs_c,
                "Media": media_c,
            })

    df_camps = pd.DataFrame(camp_stats)
    if not df_camps.empty:
        df_camps = df_camps.sort_values("Jogadores_Obs", ascending=False)

    # Posicoes
    pos_col = None
    for c in ["Posição", "Posicao"]:
        if c in df_obs.columns:
            pos_col = c
            break

    df_posicoes = pd.DataFrame()
    if pos_col:
        df_posicoes = df_obs[pos_col].value_counts().reset_index()
        df_posicoes.columns = ["Posicao", "Quantidade"]

    top_jogos = df_merged.nlargest(15, "Jogadores_Cadastrados")

    return metrics, df_merged, df_analistas, df_camps, df_posicoes, top_jogos


# ============================================================================
# HTML HELPERS
# ============================================================================

def render_header():
    st.markdown(
        '<div class="dashboard-header">'
        '<div class="header-icon">⚽</div>'
        "<div>"
        '<h1 class="header-title">Monitoramento de Jogos</h1>'
        '<div class="header-sub">Botafogo FSA &mdash; Jogadores Cadastrados por Jogo &amp; Analista</div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_kpis(metrics):
    total = max(metrics.get("total_jogos", 1), 1)
    jogos_com = metrics.get("jogos_com_obs", 0)
    pct_vistos = round(metrics.get("jogos_vistos", 0) / total * 100, 1)
    pct_obs = round(jogos_com / total * 100, 1)

    html = (
        '<div class="kpi-row">'
        '<div class="kpi-card">'
        '<div class="kpi-label">Total de Jogos</div>'
        '<div class="kpi-value">' + str(metrics.get("total_jogos", 0)) + "</div>"
        '<div class="kpi-sub">monitorados</div></div>'
        '<div class="kpi-card">'
        '<div class="kpi-label">Jogos Vistos</div>'
        '<div class="kpi-value green">' + str(metrics.get("jogos_vistos", 0)) + "</div>"
        '<div class="kpi-sub">' + str(pct_vistos) + "% conclus&atilde;o</div></div>"
        '<div class="kpi-card">'
        '<div class="kpi-label">Jogos c/ Obs.</div>'
        '<div class="kpi-value amber">' + str(jogos_com) + "</div>"
        '<div class="kpi-sub">' + str(pct_obs) + "% dos jogos</div></div>"
        '<div class="kpi-card">'
        '<div class="kpi-label">Observa&ccedil;&otilde;es</div>'
        '<div class="kpi-value red">' + str(metrics.get("total_obs", 0)) + "</div>"
        '<div class="kpi-sub">registros totais</div></div>'
        '<div class="kpi-card">'
        '<div class="kpi-label">Jogadores &Uacute;nicos</div>'
        '<div class="kpi-value blue">' + str(metrics.get("jogadores_unicos", 0)) + "</div>"
        '<div class="kpi-sub">na shadow list</div></div>'
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def section_title(icon, text):
    st.markdown(
        '<div class="section-title"><span>'
        + icon + " " + text
        + '</span><div class="line"></div></div>',
        unsafe_allow_html=True,
    )


def badge_class(analista):
    return {"Caio": "badge-red", "Cassio": "badge-green", "Gabriel": "badge-blue"}.get(
        analista, "badge-amber"
    )


# ============================================================================
# GRAFICOS PLOTLY
# ============================================================================

def _layout(fig, title="", height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=COLORS["text"]), x=0.02),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif", size=12),
        xaxis=dict(
            gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
            tickfont=dict(color=COLORS["text_muted"], size=11),
        ),
        margin=dict(l=50, r=20, t=50, b=40),
        height=height,
        hoverlabel=dict(
            bgcolor="#1E1E24", bordercolor=COLORS["card_border"],
            font=dict(color=COLORS["text"], size=12),
        ),
        legend=dict(font=dict(color=COLORS["text_muted"], size=11)),
    )
    return fig
    

def hex_to_rgba(hex_color, alpha=0.35):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return "rgba(" + str(r) + "," + str(g) + "," + str(b) + "," + str(alpha) + ")"


def plot_analistas_bar(df_a):
    if df_a.empty:
        return go.Figure()
    colors = [ANALISTA_COLORS.get(a, COLORS["amber"]) for a in df_a["Analista"]]
    dim = [hex_to_rgba(c, 0.35) for c in colors]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_a["Analista"], y=df_a["Jogadores_Obs"], name="Jogadores Obs.",
        marker_color=colors, text=df_a["Jogadores_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=13),
    ))
    fig.add_trace(go.Bar(
        x=df_a["Analista"], y=df_a["Vistos"], name="Jogos Vistos",
        marker_color=dim, text=df_a["Vistos"], textposition="outside",
        textfont=dict(color=COLORS["text_muted"], size=12),
    ))
    fig.update_layout(barmode="group", bargap=0.3)
    return _layout(fig, "Jogadores Observados vs. Jogos Vistos")


def plot_analistas_radar(df_a):
    if df_a.empty:
        return go.Figure()
    cats = ["% Vistos", "Jogadores Obs.", "Media/Jogo", "Volume"]
    fig = go.Figure()
    for _, row in df_a.iterrows():
        nome = row["Analista"]
        vals = [
            row["Pct_Vistos"],
            min(100, row["Jogadores_Obs"] / 0.5),
            min(100, row["Media_por_Jogo"] / 5 * 100),
            min(100, row["Jogos"] / 50 * 100),
        ]
        vals.append(vals[0])
        color = ANALISTA_COLORS.get(nome, COLORS["amber"])
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]], name=nome,
            line=dict(color=color, width=2),
            fill="toself", fillcolor=hex_to_rgba(color, 0.08),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=False, range=[0, 100]),
            angularaxis=dict(tickfont=dict(color=COLORS["text_muted"], size=12)),
        ),
    )
    return _layout(fig, "Perfil Comparativo", height=400)


def plot_camps_bar(df_c):
    if df_c.empty:
        return go.Figure()
    df = df_c.head(12).sort_values("Jogadores_Obs")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Campeonato"], x=df["Jogadores_Obs"], orientation="h",
        name="Jogadores", marker_color=COLORS["amber"],
        text=df["Jogadores_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.add_trace(go.Bar(
        y=df["Campeonato"], x=df["Jogos_Com_Obs"], orientation="h",
        name="Jogos c/ Obs.", marker_color=COLORS["blue"],
        text=df["Jogos_Com_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text_muted"], size=11),
    ))
    fig.update_layout(barmode="group", bargap=0.25)
    return _layout(fig, "Jogadores Observados por Campeonato", height=max(300, len(df) * 35 + 80))


def plot_camps_media(df_c):
    if df_c.empty:
        return go.Figure()
    df = df_c[df_c["Jogos_Com_Obs"] >= 2].sort_values("Media", ascending=False)
    if df.empty:
        return go.Figure()
    mean_val = df["Media"].mean()
    fig = go.Figure(go.Bar(
        x=df["Campeonato"], y=df["Media"], marker_color=COLORS["green"],
        text=df["Media"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=12),
    ))
    fig.add_hline(
        y=mean_val, line_dash="dash", line_color=COLORS["text_muted"], opacity=0.5,
        annotation_text="Media: " + str(round(mean_val, 1)),
        annotation_font_color=COLORS["text_muted"],
    )
    return _layout(fig, "Media de Jogadores por Jogo (min. 2 jogos c/ obs.)")


def plot_posicoes_bar(df_p):
    if df_p.empty:
        return go.Figure()
    df = df_p.sort_values("Quantidade")
    fig = go.Figure(go.Bar(
        y=df["Posicao"], x=df["Quantidade"], orientation="h",
        marker_color=POS_COLORS[: len(df)],
        text=df["Quantidade"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
    ))
    return _layout(fig, "Distribuicao por Posicao", height=max(280, len(df) * 32 + 60))


def plot_posicoes_donut(df_p):
    if df_p.empty:
        return go.Figure()
    fig = go.Figure(go.Pie(
        labels=df_p["Posicao"], values=df_p["Quantidade"],
        hole=0.55, marker=dict(colors=POS_COLORS[: len(df_p)], line=dict(width=0)),
        textposition="inside", textinfo="percent",
        textfont=dict(size=11, color="#fff"),
        hovertemplate="<b>%{label}</b><br>%{value} jogadores<br>%{percent}<extra></extra>",
    ))
    fig = _layout(fig, "Proporcao por Posicao", height=380)
    fig.update_layout(showlegend=True, legend=dict(font=dict(color=COLORS["text_muted"], size=11)))
    return fig


def plot_timeline(df_m):
    if df_m.empty or "Data" not in df_m.columns:
        return go.Figure()
    df = df_m[df_m["Data"].notna()].copy()
    if df.empty:
        return go.Figure()
    df["Ano_Semana"] = df["Data"].dt.strftime("%Y-W%U")
    weekly = (
        df.groupby("Ano_Semana")
        .agg(Jogos=("ID_Jogo", "count"), Jogadores=("Jogadores_Cadastrados", "sum"), Data_Ref=("Data", "min"))
        .reset_index()
        .sort_values("Data_Ref")
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly["Data_Ref"], y=weekly["Jogadores"],
        mode="lines+markers", name="Jogadores Obs.",
        line=dict(color=COLORS["red"], width=2),
        marker=dict(size=6, color=COLORS["red"]),
        fill="tozeroy", fillcolor=COLORS["red_dim"],
    ))
    fig.add_trace(go.Scatter(
        x=weekly["Data_Ref"], y=weekly["Jogos"],
        mode="lines+markers", name="Jogos",
        line=dict(color=COLORS["blue"], width=2, dash="dot"),
        marker=dict(size=5, color=COLORS["blue"]),
    ))
    return _layout(fig, "Evolucao Semanal", height=320)


# ============================================================================
# TABELA TOP JOGOS
# ============================================================================

def render_top_jogos(top):
    mandante_col = "Mandante" if "Mandante" in top.columns else "F"
    visitante_col = "Visitante" if "Visitante" in top.columns else "I"
    camp_col = next((c for c in ["Camp.", "Campeonato"] if c in top.columns), None)

    rows = ""
    for i, (_, row) in enumerate(top.iterrows()):
        mand = str(row.get(mandante_col, ""))
        visit = str(row.get(visitante_col, ""))
        m_col = next((c for c in ["M", "Gols_M"] if c in top.columns), None)
        v_col = next((c for c in ["V", "H", "Gols_V"] if c in top.columns), None)
        placar = "-"
        if m_col and v_col:
            try:
                placar = str(int(float(row[m_col]))) + "x" + str(int(float(row[v_col])))
            except (ValueError, TypeError):
                pass
        camp = str(row.get(camp_col, "")) if camp_col else ""
        analista = str(row.get("Analista", "")) if "Analista" in top.columns else ""
        jog = int(row.get("Jogadores_Cadastrados", 0))
        data = row.get("Data", "")
        if pd.notna(data):
            try:
                data = pd.to_datetime(data).strftime("%d/%m/%Y")
            except Exception:
                data = str(data)[:10]
        else:
            data = ""
        bcls = badge_class(analista)
        bar_w = min(120, jog * 16)
        bg = "#121215" if i % 2 == 0 else "transparent"
        rows += (
            '<tr style="background:' + bg + '">'
            '<td style="font-weight:700;color:#5A5A65;font-family:Courier New">' + str(i + 1) + "</td>"
            '<td style="font-weight:600">' + mand + " " + placar + " " + visit + "</td>"
            '<td><span class="badge badge-amber">' + camp + "</span></td>"
            '<td><span class="badge ' + bcls + '">' + analista + "</span></td>"
            '<td style="font-family:Courier New;color:#8B8B96;font-size:12px">' + str(data) + "</td>"
            "<td>"
            '<div class="bar-cell">'
            '<div class="bar-fill" style="width:' + str(bar_w) + 'px"></div>'
            '<span style="font-weight:700;font-size:14px">' + str(jog) + "</span>"
            "</div></td></tr>"
        )
    st.markdown(
        '<table class="styled-table"><thead><tr>'
        "<th>#</th><th>Jogo</th><th>Campeonato</th>"
        "<th>Analista</th><th>Data</th><th>Jogadores</th>"
        "</tr></thead><tbody>" + rows + "</tbody></table>",
        unsafe_allow_html=True,
    )


# ============================================================================
# CARDS DE ANALISTA
# ============================================================================

def render_analista_card(nome, row):
    color = ANALISTA_COLORS.get(nome, COLORS["amber"])
    st.markdown(
        '<div style="background:' + COLORS["card"] + ";border:1px solid " + COLORS["card_border"]
        + ";border-top:3px solid " + color + ';border-radius:12px;padding:20px">'
        '<div style="font-size:18px;font-weight:700">' + nome + "</div>"
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 20px;margin-top:16px">'
        "<div>"
        '<div style="font-size:10px;color:' + COLORS["text_muted"] + ';text-transform:uppercase;letter-spacing:0.1em">Jogos</div>'
        '<div style="font-size:24px;font-weight:700;color:' + color + '">'
        + str(row["Vistos"])
        + '<span style="font-size:13px;color:' + COLORS["text_muted"] + '">/' + str(row["Jogos"]) + "</span></div>"
        "</div><div>"
        '<div style="font-size:10px;color:' + COLORS["text_muted"] + ';text-transform:uppercase;letter-spacing:0.1em">Jogadores</div>'
        '<div style="font-size:24px;font-weight:700;color:' + color + '">' + str(row["Jogadores_Obs"]) + "</div>"
        "</div><div>"
        '<div style="font-size:10px;color:' + COLORS["text_muted"] + ';text-transform:uppercase;letter-spacing:0.1em">Media/Jogo</div>'
        '<div style="font-size:24px;font-weight:700;color:' + color + '">' + str(row["Media_por_Jogo"]) + "</div>"
        "</div><div>"
        '<div style="font-size:10px;color:' + COLORS["text_muted"] + ';text-transform:uppercase;letter-spacing:0.1em">% Vistos</div>'
        '<div style="font-size:24px;font-weight:700;color:' + color + '">' + str(row["Pct_Vistos"]) + "%</div>"
        "</div></div></div>",
        unsafe_allow_html=True,
    )


# ============================================================================
# MAIN
# ============================================================================

def main():
    inject_css()
    render_header()

    with st.spinner("Conectando ao Google Sheets..."):
        df_jogos, df_obs, df_jogadores = load_all_data()

    if df_jogos.empty:
        st.warning("Nao foi possivel conectar ao Google Sheets via URL publica.")
        st.info(
            "**Opcoes para carregar os dados:**\n\n"
            "1. **Publicar a planilha na web**: Arquivo > Compartilhar > Publicar na web > CSV\n"
            "2. **Upload manual**: Faca o upload do arquivo `.xlsx` abaixo"
        )
        uploaded = st.file_uploader("Upload da planilha (.xlsx)", type=["xlsx"])
        if uploaded:
            st.session_state["xlsx_data"] = uploaded
            st.cache_data.clear()
            st.rerun()
        st.stop()

    # Sidebar
    with st.sidebar:
        st.markdown("### Filtros")
        st.markdown("---")

        analista_col = "Analista" if "Analista" in df_jogos.columns else None
        camp_col = next((c for c in ["Camp.", "Campeonato"] if c in df_jogos.columns), None)

        sel_analistas = []
        if analista_col:
            analistas = sorted(df_jogos[analista_col].dropna().unique())
            sel_analistas = st.multiselect("Analista", analistas, default=analistas)

        sel_camps = []
        if camp_col:
            camps = sorted(df_jogos[camp_col].dropna().unique())
            sel_camps = st.multiselect("Campeonato", camps, default=camps)

        st.markdown("---")
        st.markdown("##### Periodo")
        date_range = None
        if "Data" in df_jogos.columns and df_jogos["Data"].notna().any():
            min_d = df_jogos["Data"].min().date()
            max_d = df_jogos["Data"].max().date()
            date_range = st.date_input("Intervalo", value=(min_d, max_d), min_value=min_d, max_value=max_d)

        st.markdown("---")
        if st.button("Atualizar Dados", use_container_width=True, key="btn_refresh"):
            st.cache_data.clear()
            st.rerun()

    # Filtros
    df_jf = df_jogos.copy()
    if sel_analistas and analista_col:
        df_jf = df_jf[df_jf[analista_col].isin(sel_analistas)]
    if sel_camps and camp_col:
        df_jf = df_jf[df_jf[camp_col].isin(sel_camps)]
    if date_range and len(date_range) == 2 and "Data" in df_jf.columns:
        df_jf = df_jf[(df_jf["Data"].dt.date >= date_range[0]) & (df_jf["Data"].dt.date <= date_range[1])]

    df_of = df_obs.copy()
    if "ID_Jogo" in df_of.columns and "ID_Jogo" in df_jf.columns:
        df_of = df_of[df_of["ID_Jogo"].isin(df_jf["ID_Jogo"].dropna().unique())]

    metrics, df_merged, df_analistas, df_camps, df_posicoes, top_jogos = compute_metrics(df_jf, df_of)

    render_kpis(metrics)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Visao Geral", "Analistas", "Campeonatos", "Top Jogos", "Alertas",
    ])

    # TAB 1 — Visao Geral
    with tab1:
        section_title("📈", "EVOLUCAO SEMANAL")
        st.plotly_chart(plot_timeline(df_merged), width="stretch", key="c_timeline")

        section_title("⚽", "DISTRIBUICAO POR POSICAO")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_posicoes_bar(df_posicoes), width="stretch", key="c_pos_bar")
        with c2:
            st.plotly_chart(plot_posicoes_donut(df_posicoes), width="stretch", key="c_pos_donut")

    # TAB 2 — Analistas
    with tab2:
        if not df_analistas.empty:
            section_title("📊", "COMPARATIVO")
            cols = st.columns(len(df_analistas))
            for idx, (_, row) in enumerate(df_analistas.iterrows()):
                with cols[idx]:
                    render_analista_card(row["Analista"], row)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                section_title("📊", "JOGADORES OBS. vs JOGOS VISTOS")
                st.plotly_chart(plot_analistas_bar(df_analistas), width="stretch", key="c_an_bar")
            with c2:
                section_title("🕸", "PERFIL RADAR")
                st.plotly_chart(plot_analistas_radar(df_analistas), width="stretch", key="c_an_radar")

    # TAB 3 — Campeonatos
    with tab3:
        if not df_camps.empty:
            c1, c2 = st.columns(2)
            with c1:
                section_title("📊", "JOGADORES POR CAMPEONATO")
                st.plotly_chart(plot_camps_bar(df_camps), width="stretch", key="c_camp_bar")
            with c2:
                section_title("🎯", "MEDIA POR JOGO")
                st.plotly_chart(plot_camps_media(df_camps), width="stretch", key="c_camp_media")

            section_title("📋", "TABELA DETALHADA")
            st.dataframe(
                df_camps.rename(columns={
                    "Total_Jogos": "Total",
                    "Jogos_Com_Obs": "C/ Obs.",
                    "Jogadores_Obs": "Jogadores",
                    "Media": "Media/Jogo",
                }),
                width="stretch", hide_index=True, key="df_camps",
                column_config={"Media/Jogo": st.column_config.NumberColumn(format="%.1f")},
            )

    # TAB 4 — Top Jogos
    with tab4:
        section_title("🏆", "JOGOS COM MAIS JOGADORES CADASTRADOS")
        render_top_jogos(top_jogos)

    # TAB 5 — Alertas
    with tab5:
        visto_col = "Visto" if "Visto" in df_merged.columns else None

        section_title("⚠", "JOGOS VISTOS SEM OBSERVACOES")
        st.markdown(
            '<div style="font-size:13px;color:#8B8B96;margin-bottom:16px">'
            "Jogos marcados como <b>OK</b> (vistos) mas sem nenhum jogador cadastrado."
            "</div>",
            unsafe_allow_html=True,
        )

        if visto_col:
            df_alert = df_merged[(df_merged[visto_col] == "OK") & (df_merged["Jogadores_Cadastrados"] == 0)]
            disp = _display_cols(df_alert)
            if not df_alert.empty:
                sort_col = "Data" if "Data" in disp else "ID_Jogo"
                st.dataframe(df_alert[disp].sort_values(sort_col), width="stretch", hide_index=True, key="df_sem_obs")
                st.warning("**" + str(len(df_alert)) + " jogos** vistos sem nenhuma observacao registrada.")
            else:
                st.success("Todos os jogos vistos possuem observacoes cadastradas.")

        section_title("📋", "JOGOS PENDENTES (NAO VISTOS)")
        if visto_col:
            df_pend = df_merged[df_merged[visto_col] != "OK"]
            if "Data" in df_pend.columns:
                df_pend = df_pend[df_pend["Data"] < pd.Timestamp.now()]
            disp = _display_cols(df_pend)
            if not df_pend.empty:
                sort_col = "Data" if "Data" in disp else "ID_Jogo"
                st.dataframe(df_pend[disp].sort_values(sort_col), width="stretch", hide_index=True, key="df_pendentes")
                st.info("**" + str(len(df_pend)) + " jogos** ja realizados e ainda nao vistos.")
            else:
                st.success("Nenhum jogo pendente!")

    # Footer
    st.markdown(
        '<div style="margin-top:40px;padding-top:16px;border-top:1px solid #2A2A32;'
        'display:flex;justify-content:space-between;padding-bottom:20px">'
        '<span style="font-size:11px;color:#8B8B96;font-family:Courier New">'
        "Banco de Dados | Jogos | Botafogo FSA</span>"
        '<span style="font-size:11px;color:#8B8B96;font-family:Courier New">'
        "Fonte: Google Sheets (atualizacao a cada 5 min)</span></div>",
        unsafe_allow_html=True,
    )


def _display_cols(df):
    cols = ["ID_Jogo"]
    for c in ["Mandante", "Visitante", "Camp.", "Campeonato", "Analista", "Data"]:
        if c in df.columns:
            cols.append(c)
    return cols


if __name__ == "__main__":
    main()
