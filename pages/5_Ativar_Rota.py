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

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (Atualiza a largada a cada 30 segundos)
if "last_refresh_ativar" not in st.session_state:
    st.session_state["last_refresh_ativar"] = time.time()

if time.time() - st.session_state["last_refresh_ativar"] > 30:
    st.session_state["last_refresh_ativar"] = time.time()
    st.rerun()

# 🔄 HERANÇA INTELIGENTE: Puxa direto o arquivo que foi carregado na página inicial
df_master = None
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    # Mapeamento exato das colunas conforme o arquivo real enviado
    col_tipo = None
    col_status = None
    col_login = None
    
    for c in df_temp.columns:
        c_upper = str(c).upper().strip()
        if 'TIPO DE ATIVIDADE' in c_upper or 'TIPO_ATIVIDADE' in c_upper: col_tipo = c
        if 'STATUS DA ATIVIDADE' in c_upper or 'STATUS_ATIVIDADE' in c_upper: col_status = c
        if 'LOGIN' in c_upper: col_login = c

    # Fallbacks caso os nomes variem milimetricamente
    if not col_tipo: col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else df_temp.columns[0]
    if not col_status: col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else df_temp.columns[0]
    if not col_login: col_login = 'Login' if 'Login' in df_temp.columns else df_temp.columns[0]

    # Extrai as colunas tratando linhas vazias
    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_temp['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_temp.columns else ['N/A'] * len(df_temp)
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_temp['SUPERVISOR']).iloc[:, 0].fillna('').tolist()] if 'SUPERVISOR' in df_temp.columns else [''] * len(df_temp)
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_tipo]).iloc[:, 0].fillna('').tolist()] if col_tipo in df_temp.columns else [''] * len(df_temp)
    lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_status]).iloc[:, 0].fillna('').tolist()] if col_status in df_temp.columns else [''] * len(df_temp)
    lista_logins_brutos = [str(x).strip() for x in pd.DataFrame(df_temp[col_login]).iloc[:, 0].fillna('').tolist()] if col_login in df_temp.columns else [''] * len(df_temp)

    # Monta a estrutura de dados limpa
    df_ativar = pd.DataFrame({
        'Recurso_Original': lista_recurso,
        'SUPERVISOR_ORIGINAL': lista_supervisor,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at,
        'Login_Original': lista_logins_brutos
    })
    
    # PROCV automático para preencher Supervisor ou Login em branco usando o histórico do nome do técnico
    df_dados_validos = df_ativar[
        (df_ativar['SUPERVISOR_ORIGINAL'] != '') & 
        (~df_ativar['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A'])) &
        (df_ativar['Login_Original'] != '') &
        (~df_ativar['Login_Original'].isin(['N/A', 'NAN', '#N/A']))
    ].groupby('Recurso_Original').first().reset_index()
    
    if not df_dados_validos.empty:
        df_mapeamento = df_dados_validos[['Recurso_Original', 'SUPERVISOR_ORIGINAL', 'Login_Original']].rename(
            columns={'SUPERVISOR_ORIGINAL': 'SUPERVISOR_VALIDO', 'Login_Original': 'LOGIN_VALIDO'}
        )
        df_ativar = pd.merge(df_ativar, df_mapeamento, on='Recurso_Original', how='left')
        df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_VALIDO'].fillna(df_ativar['SUPERVISOR_ORIGINAL']).str.upper().str.strip()
        df_ativar['Login_Final'] = df_ativar['LOGIN_VALIDO'].fillna(df_ativar['Login_Original']).str.strip()
    else:
        df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_ORIGINAL']
        df_ativar['Login_Final'] = df_ativar['Login_Original']

# --- SUBTÍTULO DE MONITORAMENTO ---
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Lendo dados sincronizados da Página Inicial • Filtro de Largada Ativo</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando o upload do arquivo de rota ser feito na Página Inicial.</div>', unsafe_allow_html=True)

def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except: pass
    return [''] * len(row)

# --- PROCESSAMENTO DA LARGADA MATINAL ---
if df_ativar is not None and not df_ativar.empty:
    
    # 1. Filtra tudo o que for do tipo "NA BASE"
    df_base_linhas = df_ativar[df_ativar['Tipo_Activity_Str'].str.contains("BASE", na=False) if 'Tipo_Activity_Str' in df_ativar.columns else df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
    
    # 2. Desse grupo, separa apenas os que continuam com status PENDENTE
    df_pendentes_reais = df_base_linhas[df_base_linhas['Status_Conclusao_Upper'].str.contains("PEND", na=False)].copy()
    
    if not df_pendentes_reais.empty:
        df_lista = df_pendentes_reais.groupby(['SUPERVISOR', 'Login_Final', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Login_Final': 'Login', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Login', 'Técnico Pendente']]
        df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'] != '') & (df_lista['Técnico Pendente'].str.upper() != 'NAN')]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Login', 'Técnico Pendente'])

    # Separação regional usando os supervisores de referência (Alan e Francisco = SP, o restante é ABC)
    df_sp = df_lista[df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_lista[~df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 REGIAO ABC
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
    # 🔵 REGIAO SÃO PAULO (SP)
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
