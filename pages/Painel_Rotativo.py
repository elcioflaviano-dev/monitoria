import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# CONFIGURAÇÕES
URL_PLANILHA = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# CONFIGURAÇÃO DE TELA (Menu escondido)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS AGRESSIVO (Oculta menu e define o design do topo)
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 0 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; height: 100px; }
    .topo-esquerda { display: flex; justify-content: flex-start; align-items: center; height: 100%; }
    .topo-centro { font-size: 45px; font-weight: 900; text-align: center; white-space: nowrap; }
    .topo-direita { display: flex; justify-content: flex-end; align-items: center; }
    .botao-home { color: #fff; font-size: 18px; font-weight: bold; border: 2px solid #fff; padding: 8px 15px; border-radius: 5px; text-decoration: none; }
    
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px; text-align: center; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin: 10px; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; }
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; }
    .card-indicador { background:#ffffff; border-radius:8px; padding:15px; text-align:center; border: 2px solid #ddd; }
</style>""", unsafe_allow_html=True)

# LÓGICA DO LOGO
def carregar_logo():
    caminho = "logo.png"
    if not os.path.exists(caminho): caminho = os.path.join("pages", "logo.png")
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" style="height: 80px;">'
    return ""

logo_html = carregar_logo()
topo_html = lambda titulo: f'''<div class="topo-container">
    <div class="topo-esquerda">{logo_html}</div>
    <div class="topo-centro">{titulo}</div>
    <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
</div>'''

# LÓGICA DA PLAYLIST
if "idx" not in st.session_state: st.session_state.idx = 2
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

ordem_telas = [2, 1, 2, 3]
if time.time() - st.session_state.last_time > 30:
    st.session_state.idx = (st.session_state.idx + 1) % len(ordem_telas)
    st.session_state.last_time = time.time()
    st.rerun()

tela_atual = ordem_telas[st.session_state.idx]

# =========================================================================
# TELAS
# =========================================================================

# TELA 1: CONTRATOS PENDENTES
if tela_atual == 1:
    st.markdown(topo_html("CONTRATOS PENDENTES"), unsafe_allow_html=True)
    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        sups = sorted(df['SUPERVISOR'].dropna().unique().tolist()) if 'SUPERVISOR' in df.columns else []
        cols = st.columns(len(sups) if sups else 1)
        for i, sup in enumerate(sups):
            qtd = len(df[df['SUPERVISOR'].astype(str).str.contains(str(sup), na=False)])
            with cols[i]:
                st.markdown(f'<div class="box-contagem"><div class="box-nome">{sup}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)

# TELA 2: RELÓGIO
elif tela_atual == 2:
    st.markdown(topo_html("HORÁRIO"), unsafe_allow_html=True)
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# TELA 3: INDICADORES
elif tela_atual == 3:
    st.markdown(topo_html("📈 INDICADORES DA EQUIPE"), unsafe_allow_html=True)
    try:
        df_ind = pd.read_excel(URL_PLANILHA, engine='openpyxl')
        df_ind.columns = df_ind.columns.str.strip().str.upper()
        # Aqui você desenha seus cards (respeitando o layout do seu backup anterior)
        st.write("Indicadores carregados com sucesso do SharePoint.")
    except Exception as e:
        st.error(f"Erro ao carregar do SharePoint: {e}")

time.sleep(1)
st.rerun()
