import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Carregamento e Limpeza inicial
df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None
if df_master is not None and 'Contrato' in df_master.columns:
    df_master['Contrato'] = df_master['Contrato'].str.replace('.0', '', regex=False)

SUPERVISORES = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Sessão
if "idx" not in st.session_state: st.session_state.idx = 0
if "tela" not in st.session_state: st.session_state.tela = "CENARIO"

# Lógica de Tempo: 5s por tela, 40s no final
tempo_agora = time.time()
if "last_time" not in st.session_state: st.session_state.last_time = tempo_agora

# Define o tempo de espera
espera = 5 if st.session_state.idx < len(SUPERVISORES) else 40

if tempo_agora - st.session_state.last_time >= espera:
    if st.session_state.tela == "CENARIO":
        st.session_state.tela = "CONTRATOS"
    else:
        st.session_state.tela = "CENARIO"
        st.session_state.idx = (st.session_state.idx + 1) % (len(SUPERVISORES) + 1)
    st.session_state.last_time = tempo_agora
    st.rerun()

sup = SUPERVISORES[st.session_state.idx % len(SUPERVISORES)]
if st.session_state.idx >= len(SUPERVISORES):
    st.markdown("<h1>⏳ AGUARDANDO PRÓXIMO CICLO...</h1>", unsafe_allow_html=True)
    time.sleep(1); st.rerun()

# CSS (Sem menu, faixa preta no topo)
st.markdown("""<style>
    section[data-testid="stSidebar"] { display: none; }
    .top-bar { background: #000; color: #fff; padding: 20px; text-align: center; font-size: 30px; font-weight: bold; }
    .card { background: #f0f0f0; padding: 20px; border-left: 10px solid #cc6600; margin: 10px; font-size: 24px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

st.markdown(f'<div class="top-bar">EQUIPE: {sup} | TELA: {st.session_state.tela}</div>', unsafe_allow_html=True)

if df_master is not None:
    df_sup = df_master[df_master['SUPERVISOR'].str.contains(sup, case=False, na=False)]
    pendentes = df_sup[df_sup['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False)]
    
    if st.session_state.tela == "CENARIO":
        p_total = len(pendentes)
        st.metric("🔴 PENDENTES", p_total)
        # Fala curta
        st.components.v1.html(f"<script>var m=new SpeechSynthesisUtterance('Supervisor {sup}, {p_total} pendentes.'); window.speechSynthesis.speak(m);</script>", height=0)
    else:
        for _, row in pendentes.iterrows():
            st.markdown(f'<div class="card">📄 {row["Contrato"]} | 👤 {row.get("Recurso", "Técnico")}</div>', unsafe_allow_html=True)
else:
    st.warning("Carregando...")

time.sleep(1)
st.rerun()
