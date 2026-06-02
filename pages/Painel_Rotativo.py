import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS: 4 Colunas e Topo Colorido
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { background: #003366; color: white; padding: 25px; border-radius: 0 0 15px 15px; display: flex; justify-content: space-between; align-items: center; }
    .nome-sup { font-size: 45px; font-weight: 900; }
    .card-c { background:#f9f9f9; padding:8px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; margin:4px; border:1px solid #ddd; }
    /* Grade de 4 colunas */
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 20px; }
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

# --- ESTRUTURA "LIMPA-TUDO" ---
painel = st.empty()

with painel.container():
    sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    
    # Topo
    st.markdown(f'''<div class="topo-container">
        <div class="nome-sup">{sup}</div>
        <a href="/" style="color:#fff; font-size:18px; font-weight:bold; border:2px solid #fff; padding:8px 15px; border-radius:5px; text-decoration:none;">🏠 HOME</a>
    </div>''', unsafe_allow_html=True)
    
    # Conteúdo
    if st.session_state.idx < len(SUPERVISORES):
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
            
            # FILTRO CORRIGIDO: Usa 'contains' para ignorar variações de escrita e espaços
            pendentes = df[
                (df['SUPERVISOR'].fillna('').str.contains(sup, case=False, na=False)) & 
                (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))
            ]
            
            st.subheader(f"🔴 {len(pendentes)} PENDENTES")
            
            # Grade de 4 colunas
            st.markdown('<div class="grid-4">', unsafe_allow_html=True)
            for _, row in pendentes.iterrows():
                st.markdown(f'<div class="card-c">📄 {row["Contrato"]}<br>👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if tempo_passado < 0.5:
                st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
        else:
            st.error("Arquivo não encontrado.")
    else:
        hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
