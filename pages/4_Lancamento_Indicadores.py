import streamlit as st
import pandas as pd
import os
import time

# Configuração da página ampla
st.set_page_config(layout="wide", page_title="INDICADORES", initial_sidebar_state="collapsed")

# CSS PARA LIMPEZA DA INTERFACE
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    .block-container { padding-top: 15px !important; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Recupera a base sincronizada do disco
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

# Sistema de auto-refresh para a TV da Monitoria (60 segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_ind" not in st.session_state: st.session_state["last_refresh_ind"] = time.time()
    if time.time() - st.session_state["last_refresh_ind"] > 60:
        st.session_state["last_refresh_ind"] = time.time()
        st.rerun()

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #005088; text-align: center; margin-top: 5px; margin-bottom: 25px;">📊 INDICADORES</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🔍 RADAR AUTOMÁTICO: Localiza as colunas de fórmulas de trás para a frente
    col_nr35 = next((c for c in reversed(df.columns) if 'NR35' in c.upper() or 'NR-35' in c.upper()), None)
    col_cert = next((c for c in reversed(df.columns) if 'CERTID' in c.upper() or 'ELEGIVEL' in c.upper() or 'ELEGÍVEL' in c.upper()), None)
    col_bst  = next((c for c in reversed(df.columns) if 'BST' in c.upper() or 'STEERING' in c.upper() or 'BAND' in c.upper()), None)
    
    col_tecnico = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'

    # Filtro opcional por Supervisor na barra lateral
    if col_supervisor in df.columns:
        df[col_supervisor] = df[col_supervisor].fillna('NÃO IDENTIFICADO').astype(str).str.upper()
        lista_sups = ["TODOS"] + sorted(df[col_supervisor].unique().tolist())
        sup_sel = st.sidebar.selectbox("Filtrar por Supervisor:", lista_sups)
        if sup_sel != "TODOS":
            df = df[df[col_supervisor] == sup_sel]

    # Isola uma linha por técnico para calcular o indicador real da equipa (sem duplicar por OS)
    df_tec = df.drop_duplicates(subset=[col_tecnico]).copy()
    total_tecnicos = len(df_tec) if len(df_tec) > 0 else 1

    # =========================================================================
    # 📊 RENDERIZAÇÃO DOS CARDS DE KPI (TOPO)
    # =========================================================================
    c1, c2, c3 = st.columns(3)
    
    with c1:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">🪜 NR35 (ESCADA)</p>', unsafe_allow_html=True)
            if col_nr35:
                df_tec[col_nr35] = df_tec[col_nr35].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_nr35] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#008080; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:12px; color:#777; text-align:center;">{aptos} de {len(df_tec)} técnicos OK</p>', unsafe_allow_html=True)
            else:
                st.error("Coluna NR35 não detetada")
                
    with c2:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">📜 CERTIDÃO DE ATENDIMENTO</p>', unsafe_allow_html=True)
            if col_cert:
                df_tec[col_cert] = df_tec[col_cert].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_cert] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#005088; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:12px; color:#777; text-align:center;">{aptos} de {len(df_tec)} técnicos OK</p>', unsafe_allow_html=True)
            else:
                st.error("Coluna Certidão não detetada")
                
    with c3:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">📶 BAND STEERING</p>', unsafe_allow_html=True)
            if col_bst:
                df_tec[col_bst] = df_tec[col_bst].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_bst] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#b30000; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="font-size:12px; color:#777; text-align:center;">{aptos} de {len(df_tec)} técnicos OK</p>', unsafe_allow_html=True)
            else:
                st.error("Coluna BST não detetada")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # =========================================================================
    # 📋 GRADE DETALHADA NOMINAL
    # =========================================================================
    st.markdown('<div style="background-color:#555; padding:4px 15px; border-radius:4px; margin-bottom:10px;"><h3 style="color:white; margin:0px; font-size:15px; font-weight: bold; text-transform:uppercase;">📋 Relatório Nominal de Auditoria</h3></div>', unsafe_allow_html=True)
    
    # Monta as colunas dinamicamente para exibição limpa
    colunas_grid = [col_tecnico]
    if col_supervisor in df_tec.columns: colunas_grid.append(col_supervisor)
    if col_nr35: colunas_grid.append(col_nr35)
    if col_cert: colunas_grid.append(col_cert)
    if col_bst: colunas_grid.append(col_bst)
    
    df_exibir = df_tec[colunas_grid].copy()
    
    # Padroniza visualização da tabela para maiúsculas
    for c in df_exibir.columns:
        df_exibir[c] = df_exibir[c].fillna('-').astype(str).str.upper()

    st.dataframe(df_exibir, use_container_width=True, hide_index=True)

else:
    st.warning("⏳ Aguardando dados da página inicial para processar os indicadores...")
