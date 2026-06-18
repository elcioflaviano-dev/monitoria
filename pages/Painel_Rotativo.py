import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# CONFIGURAÇÃO DE TELA (Menu escondido desde o início)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS AGRESSIVO PARA OCULTAR O MENU LATERAL
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    
    .topo-container { background: #003366; color: white; padding: 0 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; height: 100px; }
    .box-contagem { background: #f0f2f6; border-left: 8px solid #cc6600; padding: 15px; text-align: center; border-radius: 8px; margin: 10px; }
    .box-nome { font-size: 18px; font-weight: 900; color: #003366; }
    .box-num { font-size: 65px; font-weight: 900; color: #cc6600; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; }
    .hora-gigante { font-size: 180px; font-weight: 900; color: #003366; }
    .card-indicador { background:#ffffff; border-radius:8px; padding:15px; text-align:center; border: 2px solid #ddd; }
</style>""", unsafe_allow_html=True)

# CAMINHOS CORRIGIDOS
ROOT_DIR = os.getcwd()
ARQUIVO_INDICADORES = os.path.join(ROOT_DIR, "indicadores_data.csv")
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")

# =========================================================================
# LÓGICA DE ROTAÇÃO (PLAYLIST)
# =========================================================================
if "idx" not in st.session_state: st.session_state.idx = 2
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

ordem_telas = [2, 1, 2, 3] # Relógio -> Pendentes -> Relógio -> Indicadores

if time.time() - st.session_state.last_time > 30:
    st.session_state.idx = (st.session_state.idx + 1) % len(ordem_telas)
    st.session_state.last_time = time.time()
    st.rerun()

tela_atual = ordem_telas[st.session_state.idx]

# =========================================================================
# TELA 1: CONTRATOS PENDENTES
# =========================================================================
if tela_atual == 1:
    st.markdown('<div class="topo-container"><div class="topo-centro">CONTRATOS PENDENTES</div></div>', unsafe_allow_html=True)
    if os.path.exists(ARQUIVO_ROTA_DISCO):
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        sups = sorted(df['SUPERVISOR'].dropna().unique().tolist()) if 'SUPERVISOR' in df.columns else []
        cols = st.columns(len(sups) if sups else 1)
        for i, sup in enumerate(sups):
            qtd = len(df[df['SUPERVISOR'].astype(str).str.contains(str(sup), na=False)])
            with cols[i]:
                st.markdown(f'<div class="box-contagem"><div class="box-nome">{sup}</div><div class="box-num">{qtd}</div></div>', unsafe_allow_html=True)

# =========================================================================
# TELA 2: RELÓGIO
# =========================================================================
elif tela_atual == 2:
    st.markdown('<div class="topo-container"><div class="topo-centro">HORÁRIO</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# =========================================================================
# TELA 3: INDICADORES
# =========================================================================
elif tela_atual == 3:
    st.markdown('<div class="topo-container"><div class="topo-centro">📈 INDICADORES DA EQUIPE</div></div>', unsafe_allow_html=True)
    
    # DEBUG: Mostra onde ele está a procurar o ficheiro
    st.write(f"Procurando indicadores em: {ARQUIVO_INDICADORES}")
    
    if os.path.exists(ARQUIVO_INDICADORES):
        try:
            df_ind = pd.read_csv(ARQUIVO_INDICADORES)
            st.dataframe(df_ind) # Mostra os dados para confirmar leitura
        except Exception as e:
            st.error(f"Erro ao ler CSV: {e}")
    else:
        st.error("O ficheiro 'indicadores_data.csv' não foi encontrado na pasta raiz.")

time.sleep(1)
st.rerun()
