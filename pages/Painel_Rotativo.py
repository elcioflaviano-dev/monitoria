import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configura o layout como wide
st.set_page_config(layout="wide")

# CSS para limpar a área principal e estilizar os cards
st.markdown("""<style>
    /* Esconde o botão de fechar sidebar */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
    /* Estilo dos Cards */
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 10px; }
    .hora-gigante { font-size: 120px; font-weight:900; text-align:center; margin-top: 50px; }
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

# 1. SIDEBAR: Nome do Supervisor e Botão Home
with st.sidebar:
    st.markdown("## PAINEL DE GESTÃO")
    sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    st.info(f"### Supervisor: {sup_ou_pausa}")
    st.write(f"Tempo: {int(espera - tempo_passado)}s")
    st.markdown("---")
    # Botão Home que força recarregamento
    if st.button("🏠 IR PARA O INÍCIO"):
        st.rerun()

# 2. ÁREA PRINCIPAL
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        st.markdown('<div class="grid-cards">', unsafe_allow_html=True)
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        st.error("Arquivo não encontrado.")
else:
    hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora_local}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
