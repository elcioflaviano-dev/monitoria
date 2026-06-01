import streamlit as st
import pandas as pd
import os
import time

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
# 📋 TABELA MATRIZ PARA O PROCV INTERNO (Adicione ou altere os técnicos aqui)
# =============================================================================
@st.cache_data
def obter_matriz_procv():
    # Cadastro de referência: Nome do Técnico -> Login e Supervisor correspondente
    dados_cadastro = {
        "RECURSO_NOME": [
            "MAICON", "MARCOS ROBERTO", "NELSON", 
            "ALAN DE ANDRADE DIAS", "FRANCISCO GERALDO CARVALHO JUNIOR",
            "ADRIEL", "AIRON HE", "ALAN ROB", "ALEX BER", "ALINE CAI", "AMANDA", "ANA LUIS"
        ],
        "LOGIN_PROCV": [
            "L_MAICON", "L_MARCOS", "L_NELSON", 
            "L_ALAN_DIAS", "L_FRANCISCO",
            "L_ADRIEL", "L_AIRON", "L_ALAN_R", "L_ALEX", "L_ALINE", "L_AMANDA", "L_ANA"
        ],
        "SUPERVISOR_PROCV": [
            "MAICON SUPERVISOR", "MARCOS SUPERVISOR", "NELSON SUPERVISOR", 
            "ALAN", "FRANCISCO",
            "ABC_SUPERV", "ABC_SUPERV", "ABC_SUPERV", "SP_SUPERV", "SP_SUPERV", "ALAN", "FRANCISCO"
        ]
    }
    return pd.DataFrame(dados_cadastro)

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    df_temp.columns = [str(c).strip() for c in df_temp.columns]
    
    # Identifica as colunas com base no seu print real
    col_recurso = 'Recurso' if 'Recurso' in df_temp.columns else df_temp.columns[0]
    col_status = 'Status' if 'Status' in df_temp.columns else 'Status'
    
    col_tipo = None
    for c in df_temp.columns:
        if 'TIPO' in str(c).upper(): col_tipo = c; break
    if not col_tipo: col_tipo = df_temp.columns[-1]

    # Cria a estrutura base com tratamento de maiúsculas para o PROCV bater certinho
    df_base = pd.DataFrame({
        'Recurso_Original': [str(x).strip() for x in df_temp[col_recurso].fillna('N/A').tolist()],
        'Tipo_Atividade_Upper': [str(x).upper().strip() for x in df_temp[col_tipo].fillna('').tolist()],
        'Status_Conclusao_Upper': [str(x).upper().strip() for x in df_temp[col_status].fillna('').tolist()]
    })
    
    # Cria uma coluna limpa (sem o código de data se houver) para bater com a matriz do PROCV
    # Exemplo: Se vier "ADRIEL 01/06/26", limpa para buscar apenas por "ADRIEL"
    df_base['Chave_Busca'] = df_base['Recurso_Original'].str.split().str[0].str.upper().str.strip()
    
    # Carrega a matriz do PROCV e faz o cruzamento de dados (Merge)
    df_matriz = obter_matriz_procv()
    df_matriz['Chave_Busca'] = df_matriz['RECURSO_NOME'].str.upper().str.strip()
    
    df_ativar = pd.merge(df_base, df_matriz, on='Chave_Busca', how='left')
    
    # Define os valores finais tratados pelo PROCV interno
    df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_PROCV'].fillna('SEM SUPERVISOR CADASTRADO').str.upper()
    df_ativar['Login_Final'] = df_ativar['LOGIN_PROCV'].fillna('NÃO ENCONTRADO')

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

    # Divisão regional inteligente baseada no supervisor trazido pelo PROCV
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
