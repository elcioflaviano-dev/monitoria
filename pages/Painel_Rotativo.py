import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

# Layout Wide e sem sidebar inicial
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS AGRESSIVO: Esconde menu, fixa o topo, aumenta o nome
st.markdown("""<style>
    /* Esconde menu lateral e elementos de deploy */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], 
    div[data-testid="stSidebarCollapseButton"], .stDeployButton { display: none !important; }
    
    /* Topo fixo com nome do supervisor gigante */
    .topo-container { 
        position: fixed; top:0; left:0; width:100%; height: 100px; 
        background: #000; color: #fff; 
        display: flex; justify-content: space-between; align-items: center; 
        padding: 0 30px; z-index: 9999;
    }
    .nome-sup { font-size: 50px; font-weight: 900; text-transform: uppercase; }
    .tempo-sup { font-size: 25px; color: #ff9800; }
    
    /* Área principal */
    .main-content { margin-top: 120px; }
    .card-c { background:#eee; padding:15px; border-radius:8px; font-size:20px; font-weight:bold; border-left:8px solid #cc6600; margin:8px; }
    .grid-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(450px, 1fr)); gap: 15px; }
    .hora-gigante { font-size: 180px; font-weight:900; text-align:center; margin-top: 50px; color: #333; }
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

# --- RENDERIZAÇÃO DO TOPO (Sempre visível) ---
sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
st.markdown(f'''<div class="topo-container">
    <div class="nome-sup">{sup_ou_pausa}</div>
    <div class="tempo-sup">{int(espera - tempo_passado)} segundos</div>
    <a href="/" style="color:#fff; text-decoration:none; border:1px solid #fff; padding:10px; border-radius:5px;">🏠 INÍCIO</a>
</div>''', unsafe_allow_html=True)

# --- CONTEÚDO ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)
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
        st.error("Arquivo rota_sincronizada.csv não encontrado.")
else:
    hora_local = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
    st.markdown(f'<div class="hora-gigante">{hora_local}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
