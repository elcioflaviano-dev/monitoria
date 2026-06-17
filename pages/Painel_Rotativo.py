import streamlit as st
import pandas as pd
import os
import time
import base64
from datetime import datetime, timedelta

# [MANTENHA TODAS AS SUAS CONFIGURAÇÕES DE CAMINHOS, LISTAS FIXAS E CSS IGUAIS AO SEU BACKUP QUE FUNCIONA]

# =========================================================================
# ⚙️ MÁQUINA DE TEMPO E ESTADOS (FLUXO SEM INDICADORES)
# =========================================================================
if "idx" not in st.session_state: 
    st.session_state.idx = 0
    st.session_state.last_time = time.time()

agora_br = datetime.utcnow() - timedelta(hours=3)
antes_0830 = (agora_br.hour < 8) or (agora_br.hour == 8 and agora_br.minute < 30)

# TEMPOS: 0: Base(60s), 1: Pendentes(30s), 2: Relógio(60s), 4: Branca(1s)
esperas = {0: 60, 1: 30, 2: 60, 4: 1}

if time.time() - st.session_state.last_time > esperas.get(st.session_state.idx, 30):
    if antes_0830:
        st.session_state.idx = 0
    else:
        # CICLO ATUALIZADO: 0 -> 4 -> 1 -> 4 -> 2 -> 4 -> 0
        fluxo = {0: 4, 4: 1, 1: 4, 4: 2, 2: 4, 4: 0}
        st.session_state.idx = fluxo.get(st.session_state.idx, 0)
            
    st.session_state.last_time = time.time()
    st.session_state.novo_ciclo = True
    st.rerun()

# =========================================================================
# RENDERIZAÇÃO DAS TELAS
# =========================================================================

# TELA 4: TELA BRANCA DE LIMPEZA (GHOSTING KILLER)
if st.session_state.idx == 4:
    st.markdown('<div style="height: 100vh; width: 100vw; background-color: #ffffff;"></div>', unsafe_allow_html=True)

# TELA 0: TÉCNICOS NA BASE
elif st.session_state.idx == 0:
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">🚀 TÉCNICOS EM BASE</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)
    # [COLE AQUI SEU CÓDIGO DA TELA 0]

# TELA 1: CONTRATOS PENDENTES
elif st.session_state.idx == 1: 
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">CONTRATOS PENDENTES</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)
    # [COLE AQUI SEU CÓDIGO DA TELA 1]

# TELA 2: RELÓGIO
elif st.session_state.idx == 2:
    st.markdown(f'''<div class="topo-container">
        <div class="topo-esquerda">{logo_html}</div>
        <div class="topo-centro">HORÁRIO</div>
        <div class="topo-direita"><a href="/" class="botao-home">🏠 HOME</a></div>
    </div>''', unsafe_allow_html=True)
    
    st.markdown(f'''
    <div class="relogio-container">
        <div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div>
        <div class="data-media">{datetime.now().strftime("%d/%m/%Y")}</div>
    </div>
    ''', unsafe_allow_html=True)
