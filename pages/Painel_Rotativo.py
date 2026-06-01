import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. CSS ESTÁVEL
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:15px; text-align:center; font-size:25px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:9999; display: flex; justify-content: space-between; align-items: center; }
    .btn-home { color:#fff; text-decoration:none; font-weight:bold; border:1px solid #fff; padding:5px 10px; border-radius:5px; font-size:16px; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 150px; color: #000; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:18px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .conteudo { margin-top: 80px; }
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

# 2. BARRA PRETA FORA DO CONTAINER (Não some nunca)
sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'''<div class="barra-preta">
    <a href="/" class="btn-home">🏠 HOME</a>
    <span>{sup_ou_pausa} | {int(espera - tempo_passado)}s</span>
    <span style="visibility:hidden">HOME</span>
</div>''', unsafe_allow_html=True)

# 3. CONTAINER DE LIMPEZA (Só limpa o que está abaixo da barra)
placeholder = st.empty()
with placeholder.container():
    st.markdown('<div class="conteudo">', unsafe_allow_html=True)
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora_local}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
