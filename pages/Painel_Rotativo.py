import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# [MANTENHA SUAS CONFIGURAÇÕES DE CAMINHO E LOGO IGUAIS]

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS ESSENCIAL (Manter o que você já tem)
st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    .topo-container { background: #003366; color: white; padding: 20px; text-align: center; font-size: 40px; font-weight: 900; }
</style>""", unsafe_allow_html=True)

# ⚙️ MÁQUINA DE TEMPO REFORÇADA
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

# TEMPOS: 0: Base(60s), 1: Pendentes(30s), 2: Relógio(60s), 3: Indicadores(30s)
esperas = {0: 60, 1: 30, 2: 60, 3: 30}
agora = datetime.utcnow() - timedelta(hours=3)

# CICLO DE ROTAÇÃO
if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    # Lógica simples: 0 -> 1 -> 2 -> 3 -> 0
    prox = {0: 1, 1: 2, 2: 3, 3: 0}
    st.session_state.idx = prox.get(st.session_state.idx, 0)
    
    # Se for antes das 09:00, pula a tela 3 (Indicadores)
    if st.session_state.idx == 3 and agora.hour < 9:
        st.session_state.idx = 0
        
    st.session_state.last_time = time.time()
    st.rerun()

# 🔊 MOTOR DE ÁUDIO (Reinjetado toda vez para não perder a voz)
def tocar_voz(texto):
    st.components.v1.html(f"""
        <script>
            let synth = window.speechSynthesis;
            let msg = new SpeechSynthesisUtterance("{texto}");
            msg.lang = 'pt-BR';
            synth.speak(msg);
        </script>
    """, height=0)

# --- RENDERIZAÇÃO DAS TELAS ---
if st.session_state.idx == 0:
    st.markdown('<div class="topo-container">TÉCNICOS NA BASE</div>', unsafe_allow_html=True)
    # [COLE AQUI SEU CÓDIGO DA TELA 0]

elif st.session_state.idx == 1:
    st.markdown('<div class="topo-container">CONTRATOS PENDENTES</div>', unsafe_allow_html=True)
    # [COLE AQUI SEU CÓDIGO DA TELA 1]

elif st.session_state.idx == 2:
    st.markdown(f'''<div style="text-align:center; padding-top:100px;">
        <div style="font-size:200px; font-weight:bold;">{datetime.now().strftime("%H:%M:%S")}</div>
    </div>''', unsafe_allow_html=True)

elif st.session_state.idx == 3:
    st.markdown('<div class="topo-container">INDICADORES OPERACIONAIS</div>', unsafe_allow_html=True)
    # [COLE AQUI SEU CÓDIGO DA TELA 3]
