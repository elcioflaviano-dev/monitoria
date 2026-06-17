import streamlit as st
import time
from datetime import datetime, timedelta

# 1. SETTINGS OBRIGATÓRIOS (NO TOPO)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS "CAMISA DE FORÇA" (NÃO ALTERAR)
st.markdown("""
<style>
    /* Bloqueia qualquer transbordamento da página */
    html, body, [data-testid="stAppViewContainer"] {
        width: 100% !important;
        overflow-x: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Força o container principal a não ultrapassar a tela */
    .block-container {
        max-width: 100% !important;
        padding: 0 !important;
    }

    /* Estilo do Topo */
    .topo-container { 
        background: #003366; 
        color: white; 
        padding: 20px; 
        text-align: center; 
        font-size: 40px; 
        font-weight: 900;
        width: 100%;
        margin-bottom: 20px;
    }
    
    /* Proteção para Tabelas e Blocos */
    .stDataFrame, .box-contagem {
        width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE ROTAÇÃO (ROBUSTA)
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

# Ajuste o tempo conforme necessário
esperas = {0: 45, 1: 45, 2: 30, 3: 45} 
agora = datetime.utcnow() - timedelta(hours=3)

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    prox = {0: 1, 1: 2, 2: 3, 3: 0}
    st.session_state.idx = prox.get(st.session_state.idx, 0)
    if st.session_state.idx == 3 and agora.hour < 9: st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.rerun()

# 4. CONTAINER PRINCIPAL (ISOLAMENTO)
with st.container():
    if st.session_state.idx == 0:
        st.markdown('<div class="topo-container">TÉCNICOS EM BASE</div>', unsafe_allow_html=True)
        # [COLE AQUI SEU CÓDIGO DA TELA 0]

    elif st.session_state.idx == 1:
        st.markdown('<div class="topo-container">CONTRATOS PENDENTES</div>', unsafe_allow_html=True)
        # [COLE AQUI SEU CÓDIGO DA TELA 1]

    elif st.session_state.idx == 2:
        st.markdown(f'''<div style="text-align:center; padding-top:150px;">
            <div style="font-size:250px; font-weight:bold; color:#003366;">{datetime.now().strftime("%H:%M:%S")}</div>
        </div>''', unsafe_allow_html=True)

    elif st.session_state.idx == 3:
        st.markdown('<div class="topo-container">INDICADORES OPERACIONAIS</div>', unsafe_allow_html=True)
        # [COLE AQUI SEU CÓDIGO DA TELA 3]
