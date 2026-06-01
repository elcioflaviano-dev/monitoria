import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

# Tempo: 5s supervisor / 40s final
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

# CSS AJUSTADO
st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none !important; }
    .top-bar { position: fixed; top:0; left:0; width:100%; background:#000; color:#fff; padding:10px; text-align:center; font-size:20px; font-weight:900; z-index:999; }
    .box-p { background:#ffcccc; padding:15px; border-radius:10px; border:3px solid #b30000; text-align:center; }
    .valor-p { font-size: 50px; font-weight:900; color:#b30000; }
    .card-c { background:#eee; padding:8px; margin:5px 0; border-radius:4px; display:flex; justify-content:space-between; font-weight:bold; font-size:16px; }
    .container { margin-top: 60px; display: flex; gap: 20px; }
</style>""", unsafe_allow_html=True)

# Dados
df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None
if df is not None and 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)

if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    st.markdown(f'<div class="top-bar">EQUIPE: {sup} | SEG: {int(espera - (time.time() - st.session_state.last_time))}</div>', unsafe_allow_html=True)
    
    pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                   (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
    
    st.markdown('<div class="container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 3]) # Coluna esquerda menor, direita maior
    
    with col1:
        st.markdown(f'<div class="box-p"><div class="valor-p">{len(pendentes)}</div><h4>PENDENTES</h4></div>', unsafe_allow_html=True)
        # Fala
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    
    with col2:
        # Divide a lista em duas colunas internas
        sub_cols = st.columns(2)
        for i, (_, row) in enumerate(pendentes.iterrows()):
            sub_cols[i % 2].markdown(f'<div class="card-c"><span>📄 {row["Contrato"]}</span><span>👤 {row.get("Recurso", "TÉCNICO").upper()}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="top-bar">PAINEL EM PAUSA (40s)</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
