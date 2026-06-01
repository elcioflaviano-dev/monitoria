import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS: Layout usando Grade de Tabela para garantir que nada suba ou desça
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Layout fixo: Topo (80px) e Conteúdo (resto) */
    .app-grid { display: grid; grid-template-rows: 80px 1fr; height: 100vh; width: 100vw; overflow: hidden; }
    
    .topo-fixo { background:#000; color:#fff; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; }
    .nome-sup { font-size: 40px; font-weight: 900; }
    .btn-home { color:#fff; text-decoration:none; font-size:20px; font-weight:bold; border: 2px solid #fff; padding: 5px 15px; border-radius: 5px; }
    
    .conteudo-scroll { overflow-y: auto; padding: 20px; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .grid-contratos { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Lógica de Tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# RENDERIZAÇÃO USANDO GRID
st.markdown('<div class="app-grid">', unsafe_allow_html=True)

# 1. TOPO FIXO
sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'''
    <div class="topo-fixo">
        <div class="nome-sup">{sup}</div>
        <a href="/" class="btn-home">HOME</a>
    </div>
''', unsafe_allow_html=True)

# 2. CONTEÚDO COM SCROLL
st.markdown('<div class="conteudo-scroll">', unsafe_allow_html=True)
if st.session_state.idx < len(SUPERVISORES):
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        st.markdown('<div class="grid-contratos">', unsafe_allow_html=True)
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        st.error("Arquivo não encontrado.")
else:
    hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True) # Fecha grid e scroll

time.sleep(1); st.rerun()
