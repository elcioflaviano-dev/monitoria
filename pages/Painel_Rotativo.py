import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { background: #003366; color: white; padding: 25px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;}
    .nome-sup { font-size: 45px; font-weight: 900; }
    .card-c { background:#f9f9f9; padding:10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; border:1px solid #ddd; margin-bottom: 10px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; color: #333; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# --- A ESTRUTURA BLINDADA ---
# limpamos TUDO antes de qualquer lógica
container_principal = st.empty()

with container_principal.container():
    sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    
    # Desenha o Topo (Colorido)
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{sup}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)
    
    # Lógica de Exibição (Separada por IF/ELSE rígido)
    if st.session_state.idx < len(SUPERVISORES):
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            df['SUPERVISOR_CLEAN'] = df['SUPERVISOR'].astype(str).str.strip().str.upper()
            
            # Filtro exato
            pendentes = df[
                (df['SUPERVISOR_CLEAN'] == sup.strip().upper()) & 
                (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))
            ]
            
            st.subheader(f"🔴 {len(pendentes)} PENDENTES")
            
            cols = st.columns(4)
            for i, (_, row) in enumerate(pendentes.iterrows()):
                with cols[i % 4]:
                    st.markdown(f'<div class="card-c">📄 {row["Contrato"]}<br>👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
            
            if tempo_passado < 0.5:
                st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
        else:
            st.error("Arquivo rota_sincronizada.csv não encontrado.")
            
    else:
        # AQUI É A PAUSA: Nenhum contrato é processado ou desenhado
        hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
