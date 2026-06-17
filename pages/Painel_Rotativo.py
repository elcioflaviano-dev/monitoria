import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# [MANTENHA SUAS CONFIGURAÇÕES DE CAMINHOS E CSS COMO ESTÃO]
# ... (Seu CSS e definições de logo) ...

# --- MOTOR DE ÁUDIO REFORÇADO ---
JS_MOTOR_AUDIO = """
<script>
function anunciar(texto) {
    let synth = window.speechSynthesis;
    let msg = new SpeechSynthesisUtterance(texto);
    msg.lang = 'pt-BR';
    msg.rate = 1.0;
    msg.volume = 1.0;
    synth.speak(msg);
}
</script>
"""

# --- LÓGICA DE ROTAÇÃO E VOZ ---
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()
    st.session_state.falou = False

# [MANTENHA A SUA LÓGICA DE TEMPO E ESPERAS]
esperas = {0: 60, 1: 45, 2: 30}
if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    fluxo = {0: 1, 1: 2, 2: 0}
    st.session_state.idx = fluxo.get(st.session_state.idx, 0)
    st.session_state.last_time = time.time()
    st.session_state.falou = False # Reseta a fala para a nova tela
    st.rerun()

# --- RENDERIZAÇÃO E CHAMADA DE VOZ ---
if st.session_state.idx == 0:
    # ... SEU CÓDIGO DA TELA 0 ...
    if not st.session_state.falou:
        st.components.v1.html(JS_MOTOR_AUDIO + f"<script>anunciar('Técnicos na base. Conferir pendências.');</script>", height=0)
        st.session_state.falou = True

elif st.session_state.idx == 1:
    # ... SEU CÓDIGO DA TELA 1 (PENDENTES) ...
    # Exemplo de como chamar a voz aqui:
    if not st.session_state.falou:
        st.components.v1.html(JS_MOTOR_AUDIO + f"<script>anunciar('Contratos pendentes. Atenção aos prazos.');</script>", height=0)
        st.session_state.falou = True

elif st.session_state.idx == 2:
    # RELÓGIO
    st.markdown(f'<div style="text-align:center; font-size:150px;">{datetime.now().strftime("%H:%M")}</div>', unsafe_allow_html=True)
