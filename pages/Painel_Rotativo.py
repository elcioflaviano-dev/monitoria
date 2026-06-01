import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import os  # Import garantido

# Configuração fixa
st.set_config = st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS Minimalista e Robusto
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .header-painel { background:#000; color:#fff; padding:15px; text-align:center; font-size:30px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:9999; }
    .content-painel { margin-top: 80px; }
    .card-c { background:#eee; padding:10px; border-radius:5px; font-size:16px; border-left:5px solid #cc6600; margin:5px; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 100px; color: #000; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Tempo
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
tempo_passado = time.time() - st.session_state.last_time

if tempo_passado > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# Barra Superior (Sempre visível)
sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'<div class="header-painel">SUPERVISOR: {sup_ou_pausa} | {int(espera - tempo_passado)}s <a href="/" style="color:#fff; font-size:16px; margin-left:20px;">(HOME)</a></div>', unsafe_allow_html=True)

# Conteúdo
st.markdown('<div class="content-painel">', unsafe_allow_html=True)
if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    
    # Verificação de segurança para o arquivo
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        
        pendentes = df[(df['SUPERVISOR'].str.strip().str.upper() == sup.strip().upper()) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.title(f"🔴 {len(pendentes)} PENDENTES")
        cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            cols[i % 2].markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
    else:
        st.error("Arquivo rota_sincronizada.csv não localizado.")
else:
    # Relógio na pausa
    hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora_local}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
