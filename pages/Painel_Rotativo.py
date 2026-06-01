import streamlit as st
import pandas as pd
import os
import time

# 1. Layout Totalmente Expandido e Sem Menu
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. CSS "Agresivo" para TV (Esconde menu, trava barra)
st.markdown("""
    <style>
        [data-testid="stSidebar"], section[data-testid="stSidebar"], div[data-testid="stSidebarCollapseButton"] { display: none !important; }
        .barra-preta { 
            position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
            background: #000; color: #fff; padding: 15px; 
            text-align: center; font-size: 24px; font-weight: 900;
        }
        .main { margin-top: 60px !important; }
        .card-c { background: #f8f9fa; border-left: 8px solid #cc6600; padding: 15px; margin: 10px 0; display: flex; justify-content: space-between; align-items: center; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "last_move" not in st.session_state: st.session_state.last_move = time.time()

# Lógica de Tempo (5s por supervisor, 40s no fim)
tempo_agora = time.time()
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40
segundos_restantes = int(espera - (tempo_agora - st.session_state.last_move))

if tempo_agora - st.session_state.last_move > espera:
    st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_move = tempo_agora
    st.rerun()

# Barra Fixa Superior com contador
st.markdown(f'<div class="barra-preta">EQUIPE: {SUPERVISORES[st.session_state.idx % len(SUPERVISORES)] if st.session_state.idx < len(SUPERVISORES) else "PAUSA"} | Segundos: {max(0, segundos_restantes)}</div>', unsafe_allow_html=True)

# Conteúdo
if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    if 'Contrato' in df.columns: df['Contrato'] = df['Contrato'].str.replace('.0', '', regex=False)
    
    if st.session_state.idx < len(SUPERVISORES):
        sup = SUPERVISORES[st.session_state.idx]
        df_sup = df[df['SUPERVISOR'].str.contains(sup, case=False, na=False)]
        pendentes = df_sup[df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False)]
        
        st.markdown(f"## 👤 {sup}")
        st.markdown(f"### Pendentes: {len(pendentes)}")
        
        # Fala (apenas quando carrega o supervisor)
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, possui {len(pendentes)} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
        
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card-c">📄 CONTRATO: {row.get("Contrato")} | 👤 {row.get("Recurso", "TÉCNICO").upper()}</div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1>⏳ AGUARDANDO PRÓXIMO CICLO...</h1>", unsafe_allow_html=True)
else:
    st.warning("Arquivo não encontrado.")

time.sleep(1)
st.rerun()
