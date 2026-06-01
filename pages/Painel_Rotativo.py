import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS para travar o layout
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:35px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:999; }
    .hora-gigante { font-size: 180px; font-weight:900; text-align:center; margin-top: 150px; color: #000; }
    .main-grid { margin-top: 80px; display: grid; grid-template-columns: 1fr 2fr; gap: 20px; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:18px; font-weight:bold; border-left:5px solid #cc6600; }
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

# Espaço reservado para limpar a tela
tela = st.empty()

with tela.container():
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
        st.markdown(f'<div class="barra-preta">{sup}</div>', unsafe_allow_html=True)
        
        # Carregamento de dados
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.markdown('<div class="main-grid">', unsafe_allow_html=True)
        st.markdown(f"<h2>{len(pendentes)} PENDENTES</h2>", unsafe_allow_html=True)
        
        # Lista simples na direita
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Fala
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        # Modo Hora com ajuste de -3 horas
        hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")
        st.markdown(f'<div class="hora-gigante">{hora_local}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
