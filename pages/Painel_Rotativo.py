import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS "Mata-Menu" e Ajuste de Grade
st.markdown("""<style>
    /* Força o sumiço do menu lateral */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] { display: none !important; }
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    
    .barra-preta { background:#000; color:#fff; padding:10px; text-align:center; font-size:22px; font-weight:900; position:fixed; top:0; left:0; width:100%; z-index:999; }
    .main-grid { margin-top: 60px; display: grid; grid-template-columns: 1fr 2fr; gap: 10px; }
    .lista-contratos { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
    .card-c { background:#eee; padding:5px 10px; border-radius:4px; font-size:14px; font-weight:bold; border-left:4px solid #cc6600; }
</style>""", unsafe_allow_html=True)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_time" not in st.session_state: st.session_state.last_time = time.time()

espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
if time.time() - st.session_state.last_time > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = time.time()
    st.rerun()

if st.session_state.idx < len(SUPERVISORES):
    sup = SUPERVISORES[st.session_state.idx]
    st.markdown(f'<div class="barra-preta">EQUIPE: {sup} | SEG: {int(espera - (time.time() - st.session_state.last_time))}</div>', unsafe_allow_html=True)
    
    if os.path.exists("rota_sincronizada.csv"):
        df = pd.read_csv("rota_sincronizada.csv", dtype=str)
        if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
        pendentes = df[(df['SUPERVISOR'].str.contains(sup, case=False, na=False)) & 
                       (df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False))]
        
        st.markdown('<div class="main-grid">', unsafe_allow_html=True)
        
        # Coluna Esquerda: Pendentes
        st.markdown(f"<div><h2 style='color:#b30000;'>{len(pendentes)} PENDENTES</h2></div>", unsafe_allow_html=True)
        
        # Coluna Direita: Grade de Contratos
        st.markdown('<div class="lista-contratos">', unsafe_allow_html=True)
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Fala
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    
else:
    st.markdown('<div class="barra-preta">PAINEL EM PAUSA (40s)</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
