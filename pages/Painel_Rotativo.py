import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para barra fixa no topo e botão fixo no rodapé
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    /* Barra preta topo */
    .barra-preta { background:#000; color:#fff; padding:20px; text-align:center; font-size:45px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:9999; }
    /* Botão home rodapé */
    .btn-home-rodape { position:fixed; bottom:10px; left:20px; z-index:9999; }
    .btn-home-rodape a { color:#fff; text-decoration:none; background:#333; padding:10px 20px; border-radius:5px; font-weight:bold; font-size:18px; }
    
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:18px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .hora-gigante { font-size: 180px; text-align:center; margin-top: 100px; }
    .conteudo-principal { margin-top: 100px; margin-bottom: 50px; }
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

# 1. RENDERIZAÇÃO DO TOPO (Nome do Supervisor)
sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'<div class="barra-preta">{sup}</div>', unsafe_allow_html=True)

# 2. BOTÃO HOME NO RODAPÉ
st.markdown('<div class="btn-home-rodape"><a href="/">🏠 HOME</a></div>', unsafe_allow_html=True)

# 3. CONTEÚDO
st.markdown('<div class="conteudo-principal">', unsafe_allow_html=True)
if st.session_state.idx < len(SUPERVISORES):
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
else:
    hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
