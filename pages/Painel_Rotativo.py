import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para o layout fixo
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .header-fixed { background:#000; color:#fff; padding:15px; position:fixed; top:0; left:0; width:100%; z-index:9999; }
    .content-area { margin-top: 100px; padding: 20px; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Lógica de tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time
if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# --- TOPO FIXO (Colunas para nome e botão) ---
header_placeholder = st.empty()
with header_placeholder.container():
    st.markdown('<div class="header-fixed">', unsafe_allow_html=True)
    col1, col2 = st.columns([8, 1])
    sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    col1.markdown(f'<h1 style="margin:0; color:#fff;">{sup}</h1>', unsafe_allow_html=True)
    col2.markdown('<a href="/" style="color:#fff; text-decoration:none; font-weight:bold; font-size:20px;">🏠 HOME</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- CONTEÚDO (Duas colunas para contratos) ---
st.markdown('<div class="content-area">', unsafe_allow_html=True)
if st.session_state.idx < len(SUPERVISORES):
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        
        # Grade de 2 colunas para os contratos
        cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        st.error("Arquivo rota_sincronizada.csv não encontrado.")
else:
    hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
