import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS "Firme"
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:40px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:999; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 150px; color: #333; }
    .main-grid { margin-top: 90px; display: grid; grid-template-columns: 1fr 2fr; gap: 10px; }
    .card-c { background:#eee; padding:8px; border-radius:4px; font-size:16px; font-weight:bold; border-left:4px solid #cc6600; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Lógica de Tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# Renderização
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    st.markdown(f'<div class="barra-preta">{sup}</div>', unsafe_allow_html=True)
    
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.markdown('<div class="main-grid">', unsafe_allow_html=True)
        st.markdown(f"<h2>{len(pendentes)} PENDENTES</h2>", unsafe_allow_html=True)
        
        # Grade de contratos sem duplicação
        cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
else:
    # Modo Pausa
    st.markdown(f'<div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
