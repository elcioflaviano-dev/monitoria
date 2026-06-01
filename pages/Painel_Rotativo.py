import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
TEMPO_ROTACAO_SEGUNDOS = 15

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
df_master = None
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try: df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

# 🚀 CONTROLADOR DE SESSÃO
if "last_rotacao_tv" not in st.session_state: st.session_state["last_rotacao_tv"] = time.time()
if "index_supervisor_tv" not in st.session_state: st.session_state["index_supervisor_tv"] = 0
if "sub_painel_tv" not in st.session_state: st.session_state["sub_painel_tv"] = "CENARIO"
if "chave_fala_gatilho" not in st.session_state: st.session_state["chave_fala_gatilho"] = ""

SUPERVISORES_CICLO = ["MAICON", "NELSON", "MARCOS ROBERTO", "ALAN", "FRANCISCO GERALDO CARVALHO JUNIOR"]

# ⏱️ RELÓGIO DE ALTERNAÇÃO
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

# CSS E BARRA FIXA
st.markdown("""<style>
    section[data-testid="stSidebar"], div[data-testid="stSidebarCollapseButton"] { display: none !important; }
    .barra-status-tv { position: fixed; top: 0; left: 0; right: 0; z-index: 999995; background-color: #111; color: #fff; padding: 10px 20px; font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; }
    .title-supervisor-tv { font-size: 42px !important; font-weight: 900 !important; color: #005088; text-align: center; }
    .item-linha-tv { font-size: 21px; padding: 8px; border-bottom: 1px solid #eee; }
    .item-contrato-tv { font-weight: 900; color: #cc6600; }
    .custom-pendente-box { background-color: #ffcccc; border: 2px solid #ff9999; border-radius: 6px; padding: 20px; text-align: center; }
    .custom-pendente-value { font-size: 50px; font-weight: 900; color: #b30000; }
    .card-meta-tv { background-color: #f8f9fa; border-radius: 6px; padding: 20px; text-align: center; border-top: 5px solid #6c757d; }
    .card-meta-value { font-size: 50px; font-weight: 900; }
</style>""", unsafe_allow_html=True)

st.markdown(f'''<div class="barra-status-tv"><div>📺 TV MODE • EQUIPE: {supervisor_titulo} • TELA: {sub_tela_atual}</div></div>''', unsafe_allow_html=True)

# PROCESSAMENTO
if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    
    # Cálculos P, R, I
    df['P_COUNT'] = df['Status da Atividade'].fillna('').str.contains('PENDENTE', case=False, na=False).astype(int)
    df['R_COUNT'] = df['Status da Atividade'].fillna('').str.contains('ROTA', case=False, na=False).astype(int)
    df['I_COUNT'] = df['Status da Atividade'].fillna('').str.contains('INICIADO', case=False, na=False).astype(int)
    
    # Padronização Supervisor
    def padronizar(nome):
        nome = str(nome).upper()
        if 'ALAN' in nome or 'FRANCISCO' in nome: return 'SP'
        return 'ABC'

    df['SUPERVISOR_MOSTRAR'] = df['SUPERVISOR'].apply(padronizar)
    
    # Filtro Supervisor Atual
    df_supervisor_atual = df[df['SUPERVISOR'].str.contains(supervisor_atual, case=False, na=False)].copy()

    if sub_tela_atual == "CENARIO":
        st.markdown(f'<div class="title-supervisor-tv">👤 SUPERVISÃO: {supervisor_titulo}</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">{int(df_supervisor_atual["P_COUNT"].sum())}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="card-meta-tv"><div class="card-meta-label">🟣 EM ROTA</div><div class="card-meta-value">{int(df_supervisor_atual["R_COUNT"].sum())}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="card-meta-tv"><div class="card-meta-label">🟢 INICIADO</div><div class="card-meta-value">{int(df_supervisor_atual["I_COUNT"].sum())}</div></div>', unsafe_allow_html=True)

    else:
        st.markdown(f'<div class="title-supervisor-tv" style="color: #cc6600;">⏳ CONTRATOS PENDENTES</div>', unsafe_allow_html=True)
        pendentes = df_supervisor_atual[df_supervisor_atual['P_COUNT'] > 0].sort_values('Contrato')
        
        if not pendentes.empty:
            # DESTAQUE RODAPÉ (CONTRATO MAIS ANTIGO)
            antigo = pendentes.iloc[0]
            st.error(f"### 🚨 PRIORIDADE MÁXIMA: Contrato {antigo.get('Contrato')} (Técnico: {antigo.get(col_tecnico_check)})")
            
            st.divider()
            col1, col2 = st.columns(2)
            for idx, linha in enumerate(pendentes.iterrows()):
                target = col1 if idx % 2 == 0 else col2
                target.markdown(f'<div class="item-linha-tv">📄 <span class="item-contrato-tv">{linha[1].get("Contrato")}</span> | 👤 {linha[1].get(col_tecnico_check)}</div>', unsafe_allow_html=True)
        else:
            st.success("🎉 Tudo limpo!")

else:
    st.warning("Carregue o arquivo de rota na página inicial.")

time.sleep(1)
st.rerun()
