import streamlit as st
import pandas as pd
import os
import time
import base64
import calendar
from datetime import datetime, timedelta

# =========================================================================
# CONFIGURAÇÕES E PARÂMETROS
# =========================================================================
ROOT_DIR = os.getcwd()
ARQUIVO_ROTA_DISCO = os.path.join(ROOT_DIR, "rota_sincronizada.csv")
ARQUIVO_CONSULTIVO = os.path.join(ROOT_DIR, "consultivo_sincronizado.csv")
ARQUIVO_LOGO = os.path.join(ROOT_DIR, "logo.png")

if not os.path.exists(ARQUIVO_LOGO):
    ARQUIVO_LOGO = os.path.join(ROOT_DIR, "pages", "logo.png")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para o relógio e telas
st.markdown("""<style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .topo-container { background: #003366; color: white; padding: 10px 30px; border-radius: 0 0 15px 15px; display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; margin-bottom: 20px; }
    .topo-centro { font-size: 40px; font-weight: 900; text-align: center; }
    .relogio-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    .hora-gigante { font-size: 150px; font-weight: 900; color: #003366; }
    .data-media { font-size: 40px; color: #666; font-weight: bold; }
    .box-base { background: #e8f5e9; border-left: 10px solid #2e7d32; padding: 20px; margin-bottom: 15px; border-radius: 8px; }
    .box-base-sp { background: #e0f2f1; border-left: 10px solid #00897b; padding: 20px; margin-bottom: 15px; border-radius: 8px; }
    .sup-card { background: #ffffff; border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 8px; }
</style>""", unsafe_allow_html=True)

# Lógica de Supervisores
SUPS_ABC = ["EDSON MARCO", "MARCOS ROBERTO", "NELSON"]
SUPS_SP = ["ALAN", "FRANCISCO", "JOAO CARLOS MIRON"]
SUPERVISORES_ORDENADOS = SUPS_ABC + SUPS_SP

if "idx" not in st.session_state: 
    st.session_state.idx = 1
    st.session_state.last_time = time.time()

# Motor de Rotação (Seq: 1=Tec1, 4=Branco, 5=Consultivo, 4=Branco, 3=Indicadores, 4=Branco, 2=Relógio)
if time.time() - st.session_state.last_time > 45:
    seq = [1, 4, 5, 4, 3, 4, 2]
    st.session_state.idx = seq[(seq.index(st.session_state.idx) + 1) % len(seq)]
    st.session_state.last_time = time.time()
    st.rerun()

# RENDERIZAÇÃO DE TELAS
CONTEUDO = st.empty()
with CONTEUDO.container():

    # TELA 4: BRANCA (LIMPEZA)
    if st.session_state.idx == 4:
        st.markdown('<div style="height: 100vh; background-color: #ffffff;"></div>', unsafe_allow_html=True)

    # TELA 1: TEC1
    elif st.session_state.idx == 1:
        st.markdown('<div class="topo-container"><div class="topo-centro">TEC1 - PENDENTES</div></div>', unsafe_allow_html=True)
        st.write("Exibindo pendentes...")

    # TELA 5: CONSULTIVO
    elif st.session_state.idx == 5:
        st.markdown('<div class="topo-container"><div class="topo-centro">PERFORMANCE CONSULTIVO</div></div>', unsafe_allow_html=True)
        if os.path.exists(ARQUIVO_CONSULTIVO):
            df = pd.read_csv(ARQUIVO_CONSULTIVO, dtype=str)
            df.columns = [c.upper().strip() for c in df.columns]
            
            # Filtros Rígidos
            df = df[(df['TIPO DE TABULAÇÃO'].str.upper() == 'VENDA') & (df['BASE'].str.upper() != 'GRU')].copy()
            
            # 🔥 MOTOR UNIVERSAL: Qualquer sequência de 9 ou 10 dígitos é uma OS 🔥
            df['QTD'] = df['OBSERVACAO'].fillna('').astype(str).str.findall(r'\d{9,10}').apply(len)
            
            # Separação por Base
            df_abc = df[df['BASE'].str.upper() == 'ABC']
            df_sp = df[df['BASE'].str.upper() == 'SP']
            
            c1, c2 = st.columns(2)
            c1.metric("ABC TOTAL", df_abc['QTD'].sum())
            c2.metric("SP TOTAL", df_sp['QTD'].sum())
            st.write("Dados extraídos apenas por dígitos.")

    # TELA 3: INDICADORES
    elif st.session_state.idx == 3:
        st.markdown('<div class="topo-container"><div class="topo-centro">PRINT INDICADORES</div></div>', unsafe_allow_html=True)
        st.write("Exibindo Indicadores...")

    # TELA 2: RELÓGIO
    elif st.session_state.idx == 2:
        st.markdown('<div class="topo-container"><div class="topo-centro">HORÁRIO</div></div>', unsafe_allow_html=True)
        t = datetime.utcnow() - timedelta(hours=3)
        st.markdown(f'<div class="relogio-container"><div class="hora-gigante">{t.strftime("%H:%M:%S")}</div><div class="data-media">{t.strftime("%d/%m/%Y")}</div></div>', unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()
