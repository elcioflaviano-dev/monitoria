import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO (À PROVA DE QUEDAS DE SESSÃO)
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (30 Segundos para monitoramento de largada)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_ativar" not in st.session_state:
        st.session_state["last_refresh_ativar"] = time.time()
    
    st.text_input("refresh_trigger_ativ", value=str(st.session_state["last_refresh_ativar"]), label_visibility="collapsed")
    
    if time.time() - st.session_state["last_refresh_ativar"] > 30:
        st.session_state["last_refresh_ativar"] = time.time()
        st.rerun()

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">🚀 ATIVAR ROTA - LARGADA MATINAL</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA MEMÓRIA DO SISTEMA
df_master = st.session_state.get('df_rota_ativa', None)

df_ativar = None
if df_master is not None and not df_master.empty:
    df_temp = df_master.copy()
    
    # Identificação dinâmica das colunas conforme o cabeçalho do Excel
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else ('Tipo de A' if 'Tipo de A' in df_temp.columns else 'TIPO_ATIVIDADE_COL')
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else ('Status da' if 'Status da' in df_temp.columns else 'Status da Atividade')
    col_login = 'Login' if 'Login' in df_temp.columns else ('Login do' in df_temp.columns or None)
    
    # Busca aproximada caso os nomes variem
    if col_tipo not in df_temp.columns:
        for c in df_temp.columns:
            if 'TIPO DE A' in str(c).upper() or 'TIPO ATIV' in str(c).upper(): col_tipo = c; break
            
    if col_status not in df_temp.columns:
        for c in df_temp.columns:
            if 'STATUS DA' in str(c).upper() or 'STATUS_AT' in str(c).upper(): col_status = c; break

    if not col_login:
        for c in df_temp.columns:
            if 'LOGIN' in str(c).upper(): col_login = c; break

    # Extrai as colunas brutas do arquivo de upload
    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_temp['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_temp.columns else ['N/A'] * len(df_temp)
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_temp['SUPERVISOR']).iloc[:, 0].fillna('').tolist()] if 'SUPERVISOR' in df_temp.columns else [''] * len(df_temp)
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_tipo]).iloc[:, 0].fillna('').tolist()] if col_tipo in df_temp.columns else [''] * len(df_temp)
    lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_status]).iloc[:, 0].fillna('').tolist()] if col_status in df_temp.columns else [''] * len(df_temp)
    lista_logins_brutos = [str(x).strip() for x in pd.DataFrame(df_temp[col_login]).iloc[:, 0].fillna('').tolist()] if col_login else [''] * len(df_temp)

    # Monta a base de conferência inicial
    df_ativar = pd.DataFrame({
        'Recurso_Original': lista_recurso,
        'SUPERVISOR_ORIGINAL': lista_supervisor,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at,
        'Login_Original': lista_logins_brutos
    })
    
    # 🌟 MÁSTER PROCV PELO NOME DO TÉCNICO ('Recurso_Original')
    df_dados_validos = df_ativar[
        (df_ativar['SUPERVISOR_ORIGINAL'] != '') & 
        (~df_ativar['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A'])) &
        (df_ativar['Login_Original'] != '') &
        (~df_ativar['Login_Original'].isin(['N/A', 'NAN', '#N/A']))
    ].groupby('Recurso_Original').first().reset_index()
    
    df_mapeamento = df_dados_validos[['Recurso_Original', 'SUPERVISOR_ORIGINAL', 'Login_Original']].rename(
        columns={'SUPERVISOR_ORIGINAL': 'SUPERVISOR_VALIDO', 'Login_Original': 'LOGIN_VALIDO'}
    )
    
    # Cruza os dados de volta pelo nome do técnico
    df_ativar = pd.merge(df_ativar, df_mapeamento, on='Recurso_Original', how='left')
    
    # Define os valores finais (usa o procv por nome se a linha original estiver em branco)
    df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_VALIDO'].fillna(df_ativar['SUPERVISOR_ORIGINAL']).str.upper().str.strip()
    df_ativar['Login_Final'] = df_ativar['LOGIN_VALIDO'].fillna(df_ativar['Login_Original']).str.strip()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Monitorando status PENDENTE com PROCV de Login e Supervisor por Nome ativo</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except:
        pass
    return [''] * len(row)

# --- FILTRAGEM OPERACIONAL DIRETA ---
if df_ativar is not None and not df_ativar.empty:
    
    # 1. Filtra estritamente as linhas que são "NA BASE" ou contêm "BASE"
    df_base_linhas = df_ativar[df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
    
    # 2. Dessas linhas de "Na Base", captura APENAS as que estão com status PENDENTE de verdade
    df_pendentes_reais = df_base_linhas[df_base_linhas['Status_Conclusao_Upper'].str.contains("PEND", na=False)].copy()
    
    # Agrupa e gera a tabela para exibição por Supervisor, Login e Técnico
    if not df_pendentes_reais.empty:
        df_lista = df_pendentes_reais.groupby(['SUPERVISOR', 'Login_Final', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Login_Final': 'Login', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Login', 'Técnico Pendente']]
        
        # Filtro de segurança contra lixo de string
        df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'] != '') & (df_lista['Técnico Pendente'].str.upper() != 'NAN')]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Login', 'Técnico Pendente'])

    # Divisão Regional Padr (Francisco/Alan = SP, o restante é ABC)
    df_sp = df_lista[df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_lista[~df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 SEÇÃO ABC
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
    # 🔵 SEÇÃO SÃO PAULO (SP)
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
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
