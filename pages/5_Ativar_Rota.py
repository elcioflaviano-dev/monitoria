import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 2. Carregar Estilos Globais do style.css
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">🚀 ATIVAR ROTA - LARGADA MATINAL</h1>', unsafe_allow_html=True)

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (30 segundos)
if "last_refresh_ativar" not in st.session_state:
    st.session_state["last_refresh_ativar"] = time.time()

if time.time() - st.session_state["last_refresh_ativar"] > 30:
    st.session_state["last_refresh_ativar"] = time.time()
    st.rerun()

# 🔄 HERANÇA INTELIGENTE: Puxa o arquivo carregado na Home
df_master = None
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# =============================================================================
# 📋 TABELA MATRIZ PARA O PROCV INTERNO (Mapeado estritamente com os técnicos)
# =============================================================================
def realizar_procv_inteligente(nome_planilha):
    nome_u = str(nome_planilha).upper().strip()
    
    # Dicionário de cruzamento por Substring baseado nos nomes reais da planilha
    cadastro_recs = {
        "ADRIEL": {"login": "L_ADRIEL", "supervisor": "ALAN"},
        "AIRON": {"login": "L_AIRON", "supervisor": "ALAN"},
        "ALAN": {"login": "L_ALAN_R", "supervisor": "FRANCISCO"},
        "ALEX": {"login": "L_ALEX", "supervisor": "FRANCISCO"},
        "ALINE": {"login": "L_ALINE", "supervisor": "FRANCISCO"},
        "AMANDA": {"login": "L_AMANDA", "supervisor": "ALAN"},
        "DEBORA": {"login": "L_DEBORA", "supervisor": "ALAN"},
        "EDER": {"login": "L_EDER", "supervisor": "FRANCISCO"},
        "ELIAS": {"login": "L_ELIAS", "supervisor": "ALAN"},
        "ENOQUE": {"login": "L_ENOQUE", "supervisor": "FRANCISCO"},
        "MAICON": {"login": "L_MAICON", "supervisor": "MAICON SUPERVISOR"},
        "MARCOS": {"login": "L_MARCOS", "supervisor": "MARCOS SUPERVISOR"},
        "NELSON": {"login": "L_NELSON", "supervisor": "NELSON SUPERVISOR"}
    }
    
    for chave, dados in cadastro_recs.items():
        if chave in nome_u:
            return dados["login"], dados["supervisor"]
            
    return "-", "ABC_GERAL"

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    # Padroniza as colunas removendo espaços e deixando a grafia idêntica à planilha
    df_temp.columns = [str(c).strip() for c in df_temp.columns]
    
    # Trava os alvos com precisão baseada no cabeçalho real do seu Excel
    col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
    col_status = 'Status da Atividade' if 'Status da Atividade' in df_temp.columns else 'STATUS_ATIVIDADE'
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else df_temp.columns[-1]

    # Cria as listas de processamento bruto forçando limpeza absoluta de strings
    lista_recurso = [str(x).strip() for x in df_temp[col_recurso].fillna('N/A').tolist()]
    lista_tipo_ativ = [str(x).upper().strip() for x in df_temp[col_tipo].fillna('').tolist()]
    lista_status_at = [str(x).upper().strip() for x in df_temp[col_status].fillna('').tolist()]

    df_ativar = pd.DataFrame({
        'Recurso_Original': lista_recurso,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at
    })
    
    # Aplica o PROCV Inteligente por substring de nome
    logins_calculados = []
    supervisores_calculados = []
    
    for nome in df_ativar['Recurso_Original']:
        log, sup = realizar_procv_inteligente(nome)
        logins_calculados.append(log)
        supervisores_calculados.append(sup)
        
    df_ativar['SUPERVISOR'] = supervisores_calculados
    df_ativar['Login_Final'] = logins_calculados

# --- SUBTÍTULO ---
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 PROCV por Substring Ativo • Filtrando Estritamente O Status Pendente</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando o arquivo de rota na Página Inicial.</div>', unsafe_allow_html=True)

def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except: pass
    return [''] * len(row)

# --- FILTRAGEM DA MONITORIA DA LARGADA ---
if df_ativar is not None and not df_ativar.empty:
    
    # 1. Filtra as linhas de Largada do tipo "NA BASE"
    df_base_linhas = df_ativar[df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
    
    # 2. 🔥 AJUSTE CRÍTICO: Filtra usando o método parcial str.contains para evitar quebras por minúsculo/espaços
    df_pendentes_reais = df_base_linhas[df_base_linhas['Status_Conclusao_Upper'].str.contains("PENDENTE", na=False, case=False)].copy()
    
    if not df_pendentes_reais.empty:
        df_lista = df_pendentes_reais.groupby(['SUPERVISOR', 'Login_Final', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Login_Final': 'Login', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Login', 'Técnico Pendente']]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Login', 'Técnico Pendente'])

    # Divisão regional estável baseada nos supervisores
    df_sp = df_lista[df_lista['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_lista[~df_lista['Supervisor'].str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 REGIÃO ABC
    # ==========================================
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 PENDENTES DO "NA BASE" - REGIÃO ABC</h2></div>', unsafe_allow_html=True)
    
    if not df_abc.empty:
        st.dataframe(df_abc, use_container_width=True, hide_index=True)
        tot_tecs_abc = df_abc['Técnico Pendente'].nunique()
        df_tot_abc = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Login": "-", "Técnico Pendente": f"{tot_tecs_abc} Técnicos com Na Base Pendente"}])
        st.dataframe(df_tot_abc.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
    else:
        st.success("✅ 100% da equipe ABC realizou a largada do 'Na Base'!")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # 🔵 REGIÃO SÃO PAULO (SP)
    # ==========================================
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 PENDENTES DO "NA BASE" - REGIÃO SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
    
    if not df_sp.empty:
        st.dataframe(df_sp, use_container_width=True, hide_index=True)
        tot_tecs_sp = df_sp['Técnico Pendente'].nunique()
        df_tot_sp = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Login": "-", "Técnico Pendente": f"{tot_tecs_sp} Técnicos com Na Base Pendente"}])
        st.dataframe(df_tot_sp.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
    else:
        st.success("✅ 100% da equipe SP realizou a largada do 'Na Base'!")
else:
    st.warning("👈 Carregue o arquivo de rota na página inicial para liberar a visualização.")
