"""
================================================================================
DASHBOARD DE MONITORAMENTO DE JOGOS — BOTAFOGO FSA
Departamento de Scouting | Jogadores Cadastrados por Jogo & Analista
================================================================================
Conecta ao Google Sheets e gera análises cruzadas entre:
  - Lista de Jogos (ID_Jogo ↔ Analista)
  - Observações (ID_Jogo ↔ ID_Jogador)
  - Cadastro de Jogadores (dados do jogador)
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

st.set_page_config(
    page_title="Monitoramento de Jogos | Botafogo FSA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Google Sheets ID
SHEET_ID = "13u44MBj2zP-x0hssu_7UXrpI7AE-pF24rzr8qDTt4cE"

# ============================================================================
# PALETA DE CORES
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

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": COLORS["card"],
        "plot_bgcolor": COLORS["card"],
        "font": {"color": COLORS["text"], "family": "Inter, sans-serif", "size": 12},
        "xaxis": {
            "gridcolor": COLORS["grid"],
            "zerolinecolor": COLORS["grid"],
            "tickfont": {"color": COLORS["text_muted"], "size": 11},
        },
        "yaxis": {
            "gridcolor": COLORS["grid"],
            "zerolinecolor": COLORS["grid"],
            "tickfont": {"color": COLORS["text_muted"], "size": 11},
        },
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
        "hoverlabel": {
            "bgcolor": "#1E1E24",
            "bordercolor": COLORS["card_border"],
            "font": {"color": COLORS["text"], "size": 12},
        },
    }
}


# ============================================================================
# CSS CUSTOMIZADO
# ============================================================================

def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* === GLOBAL === */
    .stApp { background-color: #0C0C0F; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #EDEDEF; }

    /* === HEADER === */
    .dashboard-header {
        background: linear-gradient(135deg, #151518 0%, #1a1a20 100%);
        border: 1px solid #2A2A32;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .header-icon {
        width: 48px; height: 48px;
        background: rgba(200,16,46,0.15);
        border: 1px solid rgba(200,16,46,0.3);
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px;
    }
    .header-title {
        font-size: 22px; font-weight: 700; color: #EDEDEF;
        letter-spacing: -0.02em; margin: 0;
    }
    .header-sub {
        font-size: 12px; color: #8B8B96;
        font-family: 'Courier New', monospace; letter-spacing: 0.05em;
    }

    /* === KPI CARDS === */
    .kpi-row { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }
    .kpi-card {
        flex: 1; min-width: 160px;
        background: #151518;
        border: 1px solid #2A2A32;
        border-radius: 12px;
        padding: 18px 22px;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #3A3A44; }
    .kpi-label {
        font-size: 10px; text-transform: uppercase;
        letter-spacing: 0.12em; color: #8B8B96;
        font-family: 'Courier New', monospace;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 30px; font-weight: 700;
        line-height: 1; color: #EDEDEF;
    }
    .kpi-sub { font-size: 11px; color: #5A5A65; margin-top: 4px; }
    .kpi-value.red { color: #C8102E; }
    .kpi-value.green { color: #2EC4B6; }
    .kpi-value.amber { color: #F4A261; }
    .kpi-value.blue { color: #457B9D; }

    /* === SECTION TITLES === */
    .section-title {
        display: flex; align-items: center; gap: 10px;
        margin: 28px 0 16px 0;
    }
    .section-title span {
        font-size: 14px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.06em;
        color: #EDEDEF; font-family: 'Courier New', monospace;
    }
    .section-title .line { flex: 1; height: 1px; background: #2A2A32; }

    /* === TABS === */
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

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: #111114; border-right: 1px solid #2A2A32;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: #8B8B96; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.1em;
    }

    /* === TABLE === */
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

    /* === BAR INDICATOR === */
    .bar-cell { display: flex; align-items: center; gap: 8px; }
    .bar-fill {
        height: 6px; border-radius: 3px;
        background: linear-gradient(90deg, #C8102E, #F4A261);
    }

    /* === METRICS (override Streamlit) === */
    [data-testid="stMetric"] {
        background: #151518 !important;
        border: 1px solid #2A2A32;
        border-radius: 12px; padding: 16px !important;
    }
    [data-testid="stMetricLabel"] { color: #8B8B96 !important; font-size: 11px !important; }
    [data-testid="stMetricValue"] { color: #EDEDEF !important; }

    /* === HIDE DEFAULT === */
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# CARREGAMENTO DE DADOS VIA GOOGLE SHEETS (CSV EXPORT)
# ============================================================================

@st.cache_data(ttl=300)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Carrega aba do Google Sheets via export CSV público."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data
def load_from_xlsx(file_bytes):
    """Carrega todas as abas de um arquivo .xlsx local."""
    jogos = pd.read_excel(file_bytes, sheet_name="Lista de Jogos")
    obs = pd.read_excel(file_bytes, sheet_name="Observações")
    jogadores = pd.read_excel(file_bytes, sheet_name="Cadastro de Jogadores")
    return jogos, obs, jogadores


def load_all_data():
    """Carrega e processa todas as abas necessárias."""

    # Tentar Google Sheets primeiro
    df_jogos = load_sheet("Lista de Jogos")
    if not df_jogos.empty:
        df_obs = load_sheet("Observações")
        df_jogadores = load_sheet("Cadastro de Jogadores")
    else:
        # Fallback: verificar se há xlsx em session_state (upload)
        if "xlsx_data" in st.session_state:
            df_jogos, df_obs, df_jogadores = load_from_xlsx(st.session_state["xlsx_data"])
        else:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Limpar e tipificar
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
# FUNÇÕES DE CÁLCULO
# ============================================================================

def compute_metrics(df_jogos, df_obs):
    """Calcula todas as métricas cruzadas."""
    metrics = {}

    # Totais
    metrics["total_jogos"] = len(df_jogos)
    metrics["jogos_vistos"] = len(df_jogos[df_jogos.get("Visto", pd.Series()) == "OK"]) if "Visto" in df_jogos.columns else 0
    metrics["total_obs"] = len(df_obs)
    metrics["jogadores_unicos"] = df_obs["ID_Jogador"].nunique() if "ID_Jogador" in df_obs.columns else 0

    # Jogadores por jogo
    if "ID_Jogo" in df_obs.columns:
        jog_por_jogo = df_obs.groupby("ID_Jogo")["ID_Jogador"].count().reset_index()
        jog_por_jogo.columns = ["ID_Jogo", "Jogadores_Cadastrados"]
        metrics["jogos_com_obs"] = len(jog_por_jogo)
    else:
        jog_por_jogo = pd.DataFrame(columns=["ID_Jogo", "Jogadores_Cadastrados"])
        metrics["jogos_com_obs"] = 0

    # Merge com jogos para ter analista
    if "ID_Jogo" in df_jogos.columns:
        df_merged = df_jogos.merge(jog_por_jogo, on="ID_Jogo", how="left")
        df_merged["Jogadores_Cadastrados"] = pd.to_numeric(df_merged["Jogadores_Cadastrados"], errors="coerce").fillna(0).astype(int)
    else:
        df_merged = df_jogos.copy()
        df_merged["Jogadores_Cadastrados"] = 0

    # Por analista
    analista_col = "Analista" if "Analista" in df_jogos.columns else None
    visto_col = "Visto" if "Visto" in df_jogos.columns else None

    analista_stats = []
    if analista_col:
        for analista in df_jogos[analista_col].dropna().unique():
            mask_a = df_merged[analista_col] == analista
            total = mask_a.sum()
            vistos = (df_merged.loc[mask_a, visto_col] == "OK").sum() if visto_col else 0
            jog_obs = df_merged.loc[mask_a, "Jogadores_Cadastrados"].sum()
            media = round(jog_obs / max(vistos, 1), 1)

            # Jogos vistos sem observação
            vistos_sem_obs = 0
            if visto_col:
                vistos_sem_obs = ((df_merged.loc[mask_a, visto_col] == "OK") & (df_merged.loc[mask_a, "Jogadores_Cadastrados"] == 0)).sum()

            analista_stats.append({
                "Analista": analista,
                "Jogos": total,
                "Vistos": vistos,
                "Pendentes": total - vistos,
                "Pct_Vistos": round(vistos / max(total, 1) * 100, 1),
                "Jogadores_Obs": int(jog_obs),
                "Media_por_Jogo": media,
                "Vistos_Sem_Obs": int(vistos_sem_obs),
            })

    df_analistas = pd.DataFrame(analista_stats)

    # Por campeonato
    camp_col = None
    for c in ["Camp.", "Campeonato", "Competição"]:
        if c in df_jogos.columns:
            camp_col = c
            break

    camp_stats = []
    if camp_col:
        for camp in df_jogos[camp_col].dropna().unique():
            mask_c = df_merged[camp_col] == camp
            total_c = mask_c.sum()
            jog_obs_c = df_merged.loc[mask_c, "Jogadores_Cadastrados"].sum()
            jogos_com = (df_merged.loc[mask_c, "Jogadores_Cadastrados"] > 0).sum()
            media_c = round(jog_obs_c / max(jogos_com, 1), 1)

            camp_stats.append({
                "Campeonato": camp,
                "Total_Jogos": total_c,
                "Jogos_Com_Obs": int(jogos_com),
                "Jogadores_Obs": int(jog_obs_c),
                "Media": media_c,
            })

    df_camps = pd.DataFrame(camp_stats)
    if not df_camps.empty:
        df_camps = df_camps.sort_values("Jogadores_Obs", ascending=False)

    # Posições observadas
    pos_col = None
    for c in ["Posição", "Posicao"]:
        if c in df_obs.columns:
            pos_col = c
            break

    df_posicoes = pd.DataFrame()
    if pos_col:
        df_posicoes = df_obs[pos_col].value_counts().reset_index()
        df_posicoes.columns = ["Posição", "Quantidade"]

    # Top jogos
    top_jogos = df_merged.nlargest(15, "Jogadores_Cadastrados")

    return metrics, df_merged, df_analistas, df_camps, df_posicoes, top_jogos


# ============================================================================
# COMPONENTES HTML
# ============================================================================

def render_header():
    st.markdown("""
    <div class="dashboard-header">
        <div class="header-icon">⚽</div>
        <div>
            <h1 class="header-title">Monitoramento de Jogos</h1>
            <div class="header-sub">Botafogo FSA — Jogadores Cadastrados por Jogo & Analista</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_kpis(metrics):
    jogos_com = metrics.get("jogos_com_obs", 0)
    total = metrics.get("total_jogos", 1)
    pct = round(jogos_com / max(total, 1) * 100, 1)

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-label">Total de Jogos</div>
            <div class="kpi-value">{metrics.get('total_jogos', 0)}</div>
            <div class="kpi-sub">monitorados</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Jogos Vistos</div>
            <div class="kpi-value green">{metrics.get('jogos_vistos', 0)}</div>
            <div class="kpi-sub">{round(metrics.get('jogos_vistos',0)/max(total,1)*100,1)}% conclusão</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Jogos c/ Observações</div>
            <div class="kpi-value amber">{jogos_com}</div>
            <div class="kpi-sub">{pct}% dos jogos</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Observações</div>
            <div class="kpi-value red">{metrics.get('total_obs', 0)}</div>
            <div class="kpi-sub">registros totais</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Jogadores Únicos</div>
            <div class="kpi-value blue">{metrics.get('jogadores_unicos', 0)}</div>
            <div class="kpi-sub">na shadow list</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_title(icon, text):
    st.markdown(f"""
    <div class="section-title">
        <span>{icon} {text}</span>
        <div class="line"></div>
    </div>
    """, unsafe_allow_html=True)


def get_badge_class(analista):
    mapping = {"Caio": "badge-red", "Cassio": "badge-green", "Gabriel": "badge-blue"}
    return mapping.get(analista, "badge-amber")


# ============================================================================
# GRÁFICOS PLOTLY
# ============================================================================

def chart_layout(fig, title="", height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=COLORS["text"]), x=0.02),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"], family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["text_muted"], size=11)),
        yaxis=dict(gridcolor=COLORS["grid"], zerolinecolor=COLORS["grid"],
                   tickfont=dict(color=COLORS["text_muted"], size=11)),
        margin=dict(l=50, r=20, t=50, b=40),
        height=height,
        hoverlabel=dict(bgcolor="#1E1E24", bordercolor=COLORS["card_border"],
                        font=dict(color=COLORS["text"], size=12)),
        legend=dict(font=dict(color=COLORS["text_muted"], size=11)),
    )
    return fig


def plot_analistas_bar(df_analistas):
    if df_analistas.empty:
        return go.Figure()
    colors = [ANALISTA_COLORS.get(a, COLORS["amber"]) for a in df_analistas["Analista"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_analistas["Analista"], y=df_analistas["Jogadores_Obs"],
        name="Jogadores Obs.", marker_color=colors,
        text=df_analistas["Jogadores_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=13, family="Inter"),
    ))
    fig.add_trace(go.Bar(
        x=df_analistas["Analista"], y=df_analistas["Vistos"],
        name="Jogos Vistos", marker_color=[c.replace(")", ",0.35)").replace("rgb", "rgba") if "rgb" in c else c + "59" for c in colors],
        text=df_analistas["Vistos"], textposition="outside",
        textfont=dict(color=COLORS["text_muted"], size=12),
    ))
    fig.update_layout(barmode="group", bargap=0.3)
    return chart_layout(fig, "Jogadores Observados vs. Jogos Vistos")


def plot_analistas_radar(df_analistas):
    if df_analistas.empty:
        return go.Figure()
    categories = ["% Vistos", "Jogadores Obs.", "Média/Jogo", "Volume"]
    fig = go.Figure()

    for _, row in df_analistas.iterrows():
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
            r=vals, theta=categories + [categories[0]],
            name=nome, line=dict(color=color, width=2),
            fill="toself", fillcolor=color.replace(")", ",0.08)") if ")" in color else color + "14",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["card"],
            radialaxis=dict(visible=False, range=[0, 100]),
            angularaxis=dict(tickfont=dict(color=COLORS["text_muted"], size=12)),
        ),
    )
    return chart_layout(fig, "Perfil Comparativo", height=400)


def plot_campeonatos_bar(df_camps):
    if df_camps.empty:
        return go.Figure()
    df = df_camps.head(12).sort_values("Jogadores_Obs")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df["Campeonato"], x=df["Jogadores_Obs"],
        orientation="h", name="Jogadores",
        marker_color=COLORS["amber"],
        text=df["Jogadores_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
    ))
    fig.add_trace(go.Bar(
        y=df["Campeonato"], x=df["Jogos_Com_Obs"],
        orientation="h", name="Jogos c/ Obs.",
        marker_color=COLORS["blue"],
        text=df["Jogos_Com_Obs"], textposition="outside",
        textfont=dict(color=COLORS["text_muted"], size=11),
    ))
    fig.update_layout(barmode="group", bargap=0.25)
    return chart_layout(fig, "Jogadores Observados por Campeonato", height=max(300, len(df) * 35 + 80))


def plot_media_campeonato(df_camps):
    if df_camps.empty:
        return go.Figure()
    df = df_camps[df_camps["Jogos_Com_Obs"] >= 2].sort_values("Media", ascending=False)
    if df.empty:
        return go.Figure()
    fig = go.Figure(go.Bar(
        x=df["Campeonato"], y=df["Media"],
        marker_color=COLORS["green"],
        text=df["Media"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=12),
    ))
    fig.add_hline(y=df["Media"].mean(), line_dash="dash",
                  line_color=COLORS["text_muted"], opacity=0.5,
                  annotation_text=f"Média: {df['Media'].mean():.1f}",
                  annotation_font_color=COLORS["text_muted"])
    return chart_layout(fig, "Média de Jogadores por Jogo (min. 2 jogos c/ obs.)")


def plot_posicoes(df_posicoes):
    if df_posicoes.empty:
        return go.Figure(), go.Figure()

    colors = [COLORS["red"], COLORS["green"], COLORS["amber"], COLORS["blue"],
              COLORS["purple"], "#E76F51", "#A8DADC", "#264653", "#B5838D", "#6D6875",
              "#FFB4A2", "#F07167", "#00B4D8", "#90BE6D"]

    # Bar horizontal
    df = df_posicoes.sort_values("Quantidade")
    fig_bar = go.Figure(go.Bar(
        y=df["Posição"], x=df["Quantidade"], orientation="h",
        marker_color=colors[:len(df)],
        text=df["Quantidade"], textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
    ))
    fig_bar = chart_layout(fig_bar, "Distribuição por Posição", height=max(280, len(df) * 32 + 60))

    # Donut
    fig_donut = go.Figure(go.Pie(
        labels=df_posicoes["Posição"], values=df_posicoes["Quantidade"],
        hole=0.55, marker=dict(colors=colors[:len(df_posicoes)], line=dict(width=0)),
        textposition="inside", textinfo="percent",
        textfont=dict(size=11, color="#fff"),
        hovertemplate="<b>%{label}</b><br>%{value} jogadores<br>%{percent}<extra></extra>",
    ))
    fig_donut = chart_layout(fig_donut, "Proporção por Posição", height=380)
    fig_donut.update_layout(showlegend=True,
                            legend=dict(font=dict(color=COLORS["text_muted"], size=11)))
    return fig_bar, fig_donut


def plot_timeline(df_merged):
    """Jogadores observados por semana."""
    if df_merged.empty or "Data" not in df_merged.columns:
        return go.Figure()

    df = df_merged[df_merged["Data"].notna()].copy()
    df["Semana"] = df["Data"].dt.isocalendar().week.astype(int)
    df["Ano_Semana"] = df["Data"].dt.strftime("%Y-W%U")

    weekly = df.groupby("Ano_Semana").agg(
        Jogos=("ID_Jogo", "count"),
        Jogadores=("Jogadores_Cadastrados", "sum"),
        Data_Ref=("Data", "min"),
    ).reset_index().sort_values("Data_Ref")

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
    return chart_layout(fig, "Evolução Semanal", height=320)


# ============================================================================
# TABELA HTML DE TOP JOGOS
# ============================================================================

def render_top_jogos_table(top_jogos):
    mandante_col = "Mandante" if "Mandante" in top_jogos.columns else "F"
    visitante_col = "Visitante" if "Visitante" in top_jogos.columns else "I"
    camp_col = next((c for c in ["Camp.", "Campeonato"] if c in top_jogos.columns), None)
    analista_col = "Analista" if "Analista" in top_jogos.columns else None

    rows_html = ""
    for i, (_, row) in enumerate(top_jogos.iterrows()):
        mandante = row.get(mandante_col, "")
        visitante = row.get(visitante_col, "")

        # Placar
        m_col = next((c for c in ["M", "Gols_M"] if c in top_jogos.columns), None)
        v_col = next((c for c in ["V", "H", "Gols_V"] if c in top_jogos.columns), None)
        if m_col and v_col:
            gm = row.get(m_col, "")
            gv = row.get(v_col, "")
            try:
                placar = f"{int(float(gm))}x{int(float(gv))}"
            except (ValueError, TypeError):
                placar = "-"
        else:
            placar = "-"

        camp = row.get(camp_col, "") if camp_col else ""
        analista = row.get(analista_col, "") if analista_col else ""
        jog = int(row.get("Jogadores_Cadastrados", 0))
        data = row.get("Data", "")
        if pd.notna(data):
            try:
                data = pd.to_datetime(data).strftime("%d/%m/%Y")
            except:
                data = str(data)[:10]

        badge_cls = get_badge_class(analista)
        bar_w = min(120, jog * 16)
        bg = "#121215" if i % 2 == 0 else "transparent"

        rows_html += f"""
        <tr style="background:{bg}">
            <td style="font-weight:700;color:#5A5A65;font-family:'Courier New'">{i+1}</td>
            <td style="font-weight:600">{mandante} {placar} {visitante}</td>
            <td><span class="badge badge-amber">{camp}</span></td>
            <td><span class="badge {badge_cls}">{analista}</span></td>
            <td style="font-family:'Courier New';color:#8B8B96;font-size:12px">{data}</td>
            <td>
                <div class="bar-cell">
                    <div class="bar-fill" style="width:{bar_w}px"></div>
                    <span style="font-weight:700;font-size:14px">{jog}</span>
                </div>
            </td>
        </tr>
        """

    st.markdown(f"""
    <table class="styled-table">
        <thead><tr>
            <th>#</th><th>Jogo</th><th>Campeonato</th>
            <th>Analista</th><th>Data</th><th>Jogadores</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    inject_css()
    render_header()

    # Carregar dados
    with st.spinner("Conectando ao Google Sheets..."):
        df_jogos, df_obs, df_jogadores = load_all_data()

    if df_jogos.empty:
        st.warning("⚠️ Não foi possível conectar ao Google Sheets via URL pública.")
        st.info("""
        **Duas opções para carregar os dados:**
        1. **Publicar a planilha na web**: Arquivo → Compartilhar → Publicar na web → CSV
        2. **Upload manual**: Faça o upload do arquivo `.xlsx` abaixo
        """)
        uploaded = st.file_uploader("Upload da planilha (.xlsx)", type=["xlsx"])
        if uploaded:
            st.session_state["xlsx_data"] = uploaded
            st.cache_data.clear()
            st.rerun()
        st.stop()

    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("### ⚙️ Filtros")
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
        st.markdown("##### 📅 Período")
        if "Data" in df_jogos.columns and df_jogos["Data"].notna().any():
            min_date = df_jogos["Data"].min().date()
            max_date = df_jogos["Data"].max().date()
            date_range = st.date_input("Intervalo", value=(min_date, max_date),
                                       min_value=min_date, max_value=max_date)
        else:
            date_range = None

        st.markdown("---")
        if st.button("🔄 Atualizar Dados", use_container_width=True, key="btn_refresh"):
            st.cache_data.clear()
            st.rerun()

    # Aplicar filtros
    df_jogos_f = df_jogos.copy()
    if sel_analistas and analista_col:
        df_jogos_f = df_jogos_f[df_jogos_f[analista_col].isin(sel_analistas)]
    if sel_camps and camp_col:
        df_jogos_f = df_jogos_f[df_jogos_f[camp_col].isin(sel_camps)]
    if date_range and len(date_range) == 2 and "Data" in df_jogos_f.columns:
        df_jogos_f = df_jogos_f[
            (df_jogos_f["Data"].dt.date >= date_range[0]) &
            (df_jogos_f["Data"].dt.date <= date_range[1])
        ]

    # Filtrar observações correspondentes
    df_obs_f = df_obs.copy()
    if "ID_Jogo" in df_obs_f.columns and "ID_Jogo" in df_jogos_f.columns:
        valid_ids = df_jogos_f["ID_Jogo"].dropna().unique()
        df_obs_f = df_obs_f[df_obs_f["ID_Jogo"].isin(valid_ids)]

    # Calcular métricas
    metrics, df_merged, df_analistas, df_camps, df_posicoes, top_jogos = compute_metrics(df_jogos_f, df_obs_f)

    # KPIs
    render_kpis(metrics)

    # Tabs
    tab_overview, tab_analistas, tab_camps, tab_jogos, tab_alertas = st.tabs([
        "📊 Visão Geral",
        "👤 Analistas",
        "🏆 Campeonatos",
        "🎯 Top Jogos",
        "⚠️ Alertas",
    ])

    # --- TAB: VISÃO GERAL ---
    with tab_overview:
        section_title("📈", "EVOLUÇÃO SEMANAL")
        st.plotly_chart(plot_timeline(df_merged), width="stretch", key="chart_timeline")

        section_title("⚽", "DISTRIBUIÇÃO POR POSIÇÃO")
        col1, col2 = st.columns(2)
        fig_bar, fig_donut = plot_posicoes(df_posicoes)
        with col1:
            st.plotly_chart(fig_bar, width="stretch", key="chart_pos_bar")
        with col2:
            st.plotly_chart(fig_donut, width="stretch", key="chart_pos_donut")

    # --- TAB: ANALISTAS ---
    with tab_analistas:
        if not df_analistas.empty:
            section_title("📊", "COMPARATIVO")

            # Cards
            cols = st.columns(len(df_analistas))
            for idx, (_, row) in enumerate(df_analistas.iterrows()):
                nome = row["Analista"]
                color = ANALISTA_COLORS.get(nome, COLORS["amber"])
                with cols[idx]:
                    st.markdown(f"""
                    <div style="background:{COLORS['card']};border:1px solid {COLORS['card_border']};
                        border-top:3px solid {color};border-radius:12px;padding:20px;">
                        <div style="font-size:18px;font-weight:700">{nome}</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 20px;margin-top:16px">
                            <div>
                                <div style="font-size:10px;color:{COLORS['text_muted']};text-transform:uppercase;letter-spacing:0.1em">Jogos</div>
                                <div style="font-size:24px;font-weight:700;color:{color}">{row['Vistos']}<span style="font-size:13px;color:{COLORS['text_muted']}">/{row['Jogos']}</span></div>
                            </div>
                            <div>
                                <div style="font-size:10px;color:{COLORS['text_muted']};text-transform:uppercase;letter-spacing:0.1em">Jogadores</div>
                                <div style="font-size:24px;font-weight:700;color:{color}">{row['Jogadores_Obs']}</div>
                            </div>
                            <div>
                                <div style="font-size:10px;color:{COLORS['text_muted']};text-transform:uppercase;letter-spacing:0.1em">Média/Jogo</div>
                                <div style="font-size:24px;font-weight:700;color:{color}">{row['Media_por_Jogo']}</div>
                            </div>
                            <div>
                                <div style="font-size:10px;color:{COLORS['text_muted']};text-transform:uppercase;letter-spacing:0.1em">% Vistos</div>
                                <div style="font-size:24px;font-weight:700;color:{color}">{row['Pct_Vistos']}%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                section_title("📊", "JOGADORES OBS. vs JOGOS VISTOS")
                st.plotly_chart(plot_analistas_bar(df_analistas), width="stretch", key="chart_analistas_bar")
            with col2:
                section_title("🕸️", "PERFIL RADAR")
                st.plotly_chart(plot_analistas_radar(df_analistas), width="stretch", key="chart_analistas_radar")

    # --- TAB: CAMPEONATOS ---
    with tab_camps:
        if not df_camps.empty:
            col1, col2 = st.columns(2)
            with col1:
                section_title("📊", "JOGADORES POR CAMPEONATO")
                st.plotly_chart(plot_campeonatos_bar(df_camps), width="stretch", key="chart_camps_bar")
            with col2:
                section_title("🎯", "MÉDIA POR JOGO")
                st.plotly_chart(plot_media_campeonato(df_camps), width="stretch", key="chart_camps_media")

            section_title("📋", "TABELA DETALHADA")
            st.dataframe(
                df_camps.rename(columns={
                    "Total_Jogos": "Total", "Jogos_Com_Obs": "C/ Obs.",
                    "Jogadores_Obs": "Jogadores", "Media": "Média/Jogo"
                }),
                width="stretch", hide_index=True, key="df_camps_detail",
                column_config={
                    "Média/Jogo": st.column_config.NumberColumn(format="%.1f"),
                },
            )

    # --- TAB: TOP JOGOS ---
    with tab_jogos:
        section_title("🏆", "JOGOS COM MAIS JOGADORES CADASTRADOS")
        render_top_jogos_table(top_jogos)

    # --- TAB: ALERTAS ---
    with tab_alertas:
        section_title("⚠️", "JOGOS VISTOS SEM OBSERVAÇÕES")
        st.markdown(f"""
        <div style="font-size:13px;color:{COLORS['text_muted']};margin-bottom:16px">
            Jogos marcados como <b>OK</b> (vistos) mas sem nenhum jogador cadastrado na aba Observações.
            Indica desperdício de análise.
        </div>
        """, unsafe_allow_html=True)

        visto_col = "Visto" if "Visto" in df_merged.columns else None
        if visto_col:
            df_alert = df_merged[(df_merged[visto_col] == "OK") & (df_merged["Jogadores_Cadastrados"] == 0)]
            if not df_alert.empty:
                mandante_col = next((c for c in ["Mandante", "F"] if c in df_alert.columns), None)
                visitante_col = next((c for c in ["Visitante", "I"] if c in df_alert.columns), None)
                camp_col = next((c for c in ["Camp.", "Campeonato"] if c in df_alert.columns), None)

                display_cols = ["ID_Jogo"]
                if mandante_col:
                    display_cols.append(mandante_col)
                if visitante_col:
                    display_cols.append(visitante_col)
                if camp_col:
                    display_cols.append(camp_col)
                if "Analista" in df_alert.columns:
                    display_cols.append("Analista")
                if "Data" in df_alert.columns:
                    display_cols.append("Data")

                st.dataframe(df_alert[display_cols].sort_values("Data" if "Data" in display_cols else "ID_Jogo"),
                             width="stretch", hide_index=True, key="df_alertas_sem_obs")
                st.warning(f"**{len(df_alert)} jogos** vistos sem nenhuma observação registrada.")
            else:
                st.success("Todos os jogos vistos possuem observações cadastradas.")

        section_title("📋", "JOGOS PENDENTES (NÃO VISTOS)")
        if visto_col:
            df_pending = df_merged[df_merged[visto_col] != "OK"]
            if "Data" in df_pending.columns:
                df_pending = df_pending[df_pending["Data"] < pd.Timestamp.now()]
            if not df_pending.empty:
                st.dataframe(
                    df_pending[display_cols].sort_values("Data" if "Data" in display_cols else "ID_Jogo"),
                    width="stretch", hide_index=True, key="df_alertas_pendentes"
                )
                st.info(f"**{len(df_pending)} jogos** já realizados e ainda não vistos.")
            else:
                st.success("Nenhum jogo pendente!")

    # Footer
    st.markdown(f"""
    <div style="margin-top:40px;padding-top:16px;border-top:1px solid {COLORS['card_border']};
        display:flex;justify-content:space-between;padding-bottom:20px">
        <span style="font-size:11px;color:{COLORS['text_muted']};font-family:'Courier New'">
            Banco de Dados | Jogos | Botafogo FSA
        </span>
        <span style="font-size:11px;color:{COLORS['text_muted']};font-family:'Courier New'">
            Fonte: Google Sheets (atualização a cada 5 min)
        </span>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
