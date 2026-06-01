import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 1. CSS ESTÁVEL (Sem CSS externo dinâmico que quebra o layout)
st.markdown("""<style>
    .barra-topo { background:#000; color:#fff; padding:15px; text-align:center; font-size:28px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:999; }
    .card-c { background:#eee; padding:10px; margin:5px; border-radius:5px; border-left:5px solid #cc6600; font-size:16px; font-weight:bold; }
    .container-conteudo { margin-top: 80px; }
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

# 2. Renderização Centralizada
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    st.markdown(f'<div class="barra-topo">{sup} | {int(espera - tempo_passado)}s</div>', unsafe_allow_html=True)
    
    # Leitura e Filtro Estrito
    df = pd.read_csv("rota_sincronizada.csv", dtype=str)
    if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
    
    # FILTRO RIGOROSO: Só mostra deste supervisor e pendente
    pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup) & 
                   (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
    
    st.markdown('<div class="container-conteudo">', unsafe_allow_html=True)
    st.title(f"🔴 {len(pendentes)} PENDENTES")
    
    # Grade de 2 colunas para os contratos
    cols = st.columns(2)
    for i, (_, row) in enumerate(pendentes.iterrows()):
        cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fala
    st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)

else:
    # Modo Pausa
    st.markdown('<div class="barra-topo">PAUSA (40s)</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="text-align:center; margin-top:200px; font-size:150px;">{(datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M")}</h1>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
