import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES
# =========================================================================
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
ARQUIVO_INDICADORES = "indicadores_data.csv"
ARQUIVO_LOGO = "logo.png"
if not os.path.exists(ARQUIVO_LOGO): ARQUIVO_LOGO = os.path.join("pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Funções auxiliares (Logo, Nome Visual)
def carregar_logo_html(caminho):
    if os.path.exists(caminho):
        try:
            with open(caminho, "rb") as f:
                return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" style="height: 100px;">'
        except: return ""
    return ""

def obter_nome_visual(nome):
    n = str(nome).upper()
    if 'FRANCISCO' in n: return "FRANCISCO"
    if 'MARCOS' in n: return "MARCOS ROBERTO"
    return n.split()[0]

logo_html = carregar_logo_html(ARQUIVO_LOGO)

# Estilização
st.markdown("""<style>
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 0 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; height: 100px; }
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px; text-align: center; border-radius: 8px; margin: 10px; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; }
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; height: 70vh; justify-content: center; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; }
    .card-indicador { background:#ffffff; border-radius:8px; padding:15px; text-align:center; border: 2px solid #ddd; }
</style>""", unsafe_allow_html=True)

# =========================================================================
# LÓGICA DA PLAYLIST (ROTAÇÃO)
# =========================================================================
if "idx" not in st.session_state: st.session_state.idx = 2
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Playlist: Relógio -> Pendentes -> Relógio -> Indicadores
ordem_telas = [2, 1, 2, 3] 

if time.time() - st.session_state.last_time > 30:
    st.session_state.idx = (st.session_state.idx + 1) % len(ordem_telas)
    st.session_state.last_time = time.time()
    st.rerun()

tela_atual = ordem_telas[st.session_state.idx]

# =========================================================================
# TELA 1: CONTRATOS PENDENTES (Com supervisores corrigidos)
# =========================================================================
if tela_atual == 1:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">CONTRATOS PENDENTES</div><div></div></div>', unsafe_allow_html=True)
    
    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        
        # Garante que temos a lista de supervisores
        sups = sorted(df['SUPERVISOR'].dropna().unique().tolist()) if 'SUPERVISOR' in df.columns else []
        
        cols = st.columns(len(sups) if sups else 1)
        for i, sup in enumerate(sups):
            qtd = len(df[df['SUPERVISOR'].astype(str).str.contains(sup, na=False)])
            with cols[i]:
                st.markdown(f'<div class="box-contagem"><div class="box-nome">{obter_nome_visual(sup)}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)

# =========================================================================
# TELA 2: RELÓGIO
# =========================================================================
elif tela_atual == 2:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">HORÁRIO</div><div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# =========================================================================
# TELA 3: INDICADORES
# =========================================================================
elif tela_atual == 3:
    st.markdown(f'<div class="topo-container"><div class="topo-esquerda">{logo_html}</div><div class="topo-centro">📈 INDICADORES</div><div></div></div>', unsafe_allow_html=True)
    
    if os.path.exists(ARQUIVO_INDICADORES):
        df_ind = pd.read_csv(ARQUIVO_INDICADORES)
        st.write("Dados carregados dos indicadores:", df_ind) # Debug visual
    else:
        st.warning("Arquivo de indicadores não encontrado na pasta raiz.")

time.sleep(1)
st.rerun()
