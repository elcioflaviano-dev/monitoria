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
# 📋 TABELA MATRIZ PARA O PROCV INTERNO
# =============================================================================
@st.cache_data
def obtener_matriz_procv():
    dados_cadastro = {
        "RECURSO_NOME": [
            "MAICON", "MARCOS ROBERTO", "NELSON", 
            "ALAN DE ANDRADE DIAS", "FRANCISCO GERALDO CARVALHO JUNIOR"
        ],
        "LOGIN_PROCV": [
            "L_MAICON", "L_MARCOS", "L_NELSON", 
            "L_ALAN_DIAS", "L_FRANCISCO"
        ],
        "SUPERVISOR_PROCV": [
            "MAICON SUPERVISOR", "MARCOS SUPERVISOR", "NELSON SUPERVISOR", 
            "ALAN", "FRANCISCO"
        ]
    }
    return pd.DataFrame(dados_cadastro)

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    # 🛠️ PASSO CRÍTICO: Limpa os nomes de todas as colunas tirando espaços e deixando em MAIÚSCULO
    df_temp.columns = [str(c).upper().strip() for c in df_temp.columns]
    
    # Mapeamento dinâmico e inteligente por palavra-chave para evitar KEYERROR
    col_recurso = None
    col_status = None
    col_tipo = None

    for c in df_temp.columns:
        if 'RECURSO' in c or 'TECNICO' in c or 'NOME' in c:
            col_recurso = c
        if 'STATUS' in c:
            col_status = c
        if 'TIPO' in c or 'ATIVIDADE' in c:
            col_tipo = c

    # Fallbacks de segurança extrema caso as palavras-chave falhem completamente
    if not col_recurso: col_recurso = df_temp.columns[0]
    if not col_status: col_status = df_temp.columns[3] if len(df_temp.columns) > 3 else df_temp.columns[0]
    if not col_tipo: col_tipo = df_temp.columns[-1]

    # Extrai as listas usando os cabeçalhos dinâmicos mapeados com segurança
    lista_recurso = [str(x).strip() for x in df_temp[col_recurso].fillna('N/A').tolist()]
    lista_tipo_ativ = [str(x).upper().strip() for x in df_temp[col_tipo].fillna('').tolist()]
    lista_status_at = [str(x).upper().strip() for x in df_temp[col_status].fillna('').tolist()]

    # Monta a estrutura base limpa para a tela
    df_base = pd.DataFrame({
        'Recurso_Original': lista_recurso,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at
    })
    
    # Limpa o nome do técnico para fazer a busca do PROCV (Ex: "ADRIEL 01/06" vira "ADRIEL")
    df_base['Chave_Busca'] = df_base['Recurso_Original'].str.split().str[0].str.upper().str.strip()
    
    # Executa o PROCV na nossa tabela interna
    df_matriz = obtener_matriz_procv()
    df_matriz['Chave_Busca'] = df_matriz['RECURSO_NOME'].str.upper().str.strip()
    
    df_ativar = pd.merge(df_base, df_matriz, on='Chave_Busca', how='left')
    
    # Preenche com valores padrão se o técnico não estiver cadastrado no dicionário acima
    df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_PROCV'].fillna('ABC_GERAL').str.upper()
    df_ativar['Login_Final'] = df_ativar['LOGIN_PROCV'].fillna('-')

# --- SUBTÍTULO ---
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 PROCV Automático de Login e Supervisor por Nome do Técnico Ativo</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando o arquivo de rota na Página Inicial.</div>', unsafe_allow_html=True)

def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except: pass
    return [''] * len(row)

# --- FILTRAGEM DA MONITORIA DA LARGADA MATINAL ---
if df_ativar is not None and not df_ativar.empty:
    
    # 1. Filtra as linhas de Largada do tipo "NA BASE"
    df_base_linhas = df_ativar[df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
    
    # 2. Captura apenas as linhas que estão com status "PENDENTE" de verdade
    df_pendentes_reais = df_base_linhas[df_base_linhas['Status_Conclusao_Upper'].str.contains("PEND", na=False)].copy()
    
    if not df_pendentes_reais.empty:
        df_lista = df_pendentes_reais.groupby(['SUPERVISOR', 'Login_Final', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Login_Final': 'Login', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Login', 'Técnico Pendente']]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Login', 'Técnico Pendente'])

    # Divisão regional estável baseada no supervisor trazido pelo PROCV
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
