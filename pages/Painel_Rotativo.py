import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS Ajustado: Topo colorido, com margem para não cortar o nome
st.markdown("""<style>
    [data-testid="stSidebar"] { display: none !important; }
    .topo-container { 
        background: #003366; /* Cor azul escura */
        color: white; 
        padding: 30px 20px; /* Mais espaço para não cortar o nome */
        display: flex; 
        justify-content: space-between; 
        align-items: center;
        border-radius: 0 0 15px 15px;
    }
    .nome-sup { font-size: 50px; font-weight: 900; }
    .card-c { background:#eee; padding:15px; border-radius:8px; font-size:16px; border-left:8px solid #cc6600; margin:5px; }
    .hora-gigante { font-size: 150px; text-align:center; margin-top: 100px; }
    .grid-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
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

# Container único para limpar a tela totalmente a cada ciclo
painel = st.empty()

with painel.container():
    sup = SUPERVISORES[st.session_state.idx] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"
    
    # TOPO COLORIDO E SEM CORTE
    st.markdown(f'''
        <div class="topo-container">
            <div class="nome-sup">{sup}</div>
            <a href="/" style="color:#fff; text-decoration:none; border:2px solid #fff; padding:10px 20px; border-radius:5px; font-weight:bold; font-size:18px;">🏠 HOME</a>
        </div>
    ''', unsafe_allow_html=True)
    
    # CONTEÚDO
    if st.session_state.idx < len(SUPERVISORES):
        if os.path.exists("rota_sincronizada.csv"):
            df = pd.read_csv("rota_sincronizada.csv", dtype=str)
            if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
            
            # FILTRO ULTRA-RIGOROSO: Remove espaços e converte para maiúsculo
            # Também garante que não estamos pegando o supervisor errado
            pendentes = df[
                (df['SUPERVISOR'].astype(str).str.strip().str.upper() == sup.strip().upper()) & 
                (df['Status da Atividade'].astype(str).str.contains('PENDENTE', case=False, na=False))
            ]
            
            st.title(f"🔴 {len(pendentes)} PENDENTES")
            
            # Grade de 2 colunas para otimizar espaço
            st.markdown('<div class="grid-cards">', unsafe_allow_html=True)
            for _, row in pendentes.iterrows():
                st.markdown(f'<div class="card-c">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "TÉC").upper()}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if tempo_passado < 0.5:
                st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
        else:
            st.error("Arquivo não encontrado.")
    else:
        hora = (datetime.utcnow() - timedelta(hours=3)).strftime("%H:%M:%S")
        st.markdown(f'<div class="hora-gigante">{hora}</div>', unsafe_allow_html=True)

time.sleep(1); st.rerun()
