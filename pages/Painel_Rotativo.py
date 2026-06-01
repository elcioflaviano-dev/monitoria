import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
TEMPO_ROTACAO_SEGUNDOS = 8 

# Carregamento de dados
df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str) if os.path.exists(ARQUIVO_ROTA_DISCO) else None

# Controle de sessão
if "last_rotacao_tv" not in st.session_state: st.session_state["last_rotacao_tv"] = time.time()
if "index_supervisor_tv" not in st.session_state: st.session_state["index_supervisor_tv"] = 0
if "sub_painel_tv" not in st.session_state: st.session_state["sub_painel_tv"] = "CENARIO"
if "chave_fala_gatilho" not in st.session_state: st.session_state["chave_fala_gatilho"] = ""

SUPERVISORES_CICLO = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# Relógio de alternação
tempo_decorrido = time.time() - st.session_state["last_rotacao_tv"]
if tempo_decorrido >= TEMPO_ROTACAO_SEGUNDOS:
    if st.session_state["sub_painel_tv"] == "CENARIO":
        st.session_state["sub_painel_tv"] = "CONTRATOS"
    else:
        st.session_state["sub_painel_tv"] = "CENARIO"
        st.session_state["index_supervisor_tv"] = (st.session_state["index_supervisor_tv"] + 1) % len(SUPERVISORES_CICLO)
    st.session_state["last_rotacao_tv"] = time.time()
    st.rerun()

supervisor_atual = SUPERVISORES_CICLO[st.session_state["index_supervisor_tv"]]
sub_tela_atual = st.session_state["sub_painel_tv"]
supervisor_titulo = "FRANCISCO" if "FRANCISCO" in supervisor_atual else supervisor_atual

# CSS (Mantenha o seu estilo aqui)
st.markdown("<style>/* Seu estilo CSS permanece aqui */</style>", unsafe_allow_html=True)

# Processamento
if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df['P_COUNT'] = df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False).astype(int)
    df['R_COUNT'] = df['Status da Atividade'].fillna('').str.contains('ROTA', case=False, na=False).astype(int)
    df['I_COUNT'] = df['Status da Atividade'].fillna('').str.contains('INICIADO', case=False, na=False).astype(int)
    
    df_supervisor = df[df['SUPERVISOR'].str.contains(supervisor_atual, case=False, na=False)].copy()
    
    if sub_tela_atual == "CENARIO":
        st.markdown(f"## 👤 SUPERVISÃO: {supervisor_titulo}")
        c1, c2, c3 = st.columns(3)
        c1.metric("🔴 PENDENTES", int(df_supervisor["P_COUNT"].sum()))
        c2.metric("🟣 EM ROTA", int(df_supervisor["R_COUNT"].sum()))
        c3.metric("🟢 INICIADO", int(df_supervisor["I_COUNT"].sum()))

        # Gatilho de fala
        id_fala = f"{supervisor_titulo}_{int(df_supervisor['P_COUNT'].sum())}"
        if st.session_state["chave_fala_gatilho"] != id_fala:
            frase = f"Supervisor {supervisor_titulo}, possui {int(df_supervisor['P_COUNT'].sum())} pendentes."
            st.components.v1.html(f'<script>var msg = new SpeechSynthesisUtterance("{frase}"); msg.lang="pt-BR"; window.speechSynthesis.speak(msg);</script>', height=0)
            st.session_state["chave_fala_gatilho"] = id_fala

    else:
        st.markdown(f"## ⏳ PENDENTES: {supervisor_titulo}")
        pendentes = df_supervisor[df_supervisor['P_COUNT'] > 0]
        if not pendentes.empty:
            st.dataframe(pendentes[['Contrato', 'Recurso']], use_container_width=True)
        else:
            st.success("Tudo limpo!")
else:
    st.warning("Carregue o arquivo de rota.")

time.sleep(1)
st.rerun()
