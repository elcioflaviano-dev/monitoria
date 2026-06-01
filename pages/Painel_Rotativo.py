import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS FIXO E AGRESSIVO
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .barra-preta { background:#000; color:#fff; padding:10px; display:flex; justify-content:space-between; align-items:center; position:fixed; top:0; left:0; width:100%; z-index:9999; }
    .btn-home { color:#fff; text-decoration:none; font-weight:bold; border:1px solid #fff; padding:5px 10px; border-radius:5px; }
    .conteudo-principal { margin-top: 70px; }
    .card-c { background:#eee; padding:8px; border-radius:4px; font-size:16px; font-weight:bold; border-left:5px solid #cc6600; margin:5px; }
    .hora-gigante { font-size: 150px; font-weight:900; text-align:center; margin-top: 100px; }
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

# LIMPEZA TOTAL DA TELA
placeholder = st.empty()

with placeholder.container():
    # 1. BARRA PRETA SEMPRE VISÍVEL
    sup_ou_pausa = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    st.markdown(f'''<div class="barra-preta">
        <a href="/" target="_self" class="btn-home">🏠 HOME</a>
        <span>EQUIPE: {sup_ou_pausa} | {int(espera - tempo_passado)}s</span>
    </div>''', unsafe_allow_html=True)

    # 2. CONTEÚDO
    st.markdown('<div class="conteudo-principal">', unsafe_allow_html=True)
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
        
        # Fala (apenas no início)
        if tempo_passado < 0.5:
            st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        st.markdown(f'<div class="hora-gigante">{datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
