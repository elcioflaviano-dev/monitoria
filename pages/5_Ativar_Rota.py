import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 1. Leitura idêntica à sua página de Certidão
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        # Lemos exatamente como você faz no outro arquivo
        df_master = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df_master.columns = df_master.columns.str.strip()
    except:
        df_master = pd.DataFrame()
else:
    df_master = pd.DataFrame()

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if not df_master.empty:
    # 2. Garantir que as colunas necessárias existam
    # Ajuste os nomes abaixo conforme os nomes exatos que aparecem no seu CSV completo
    col_status_at = 'Status da Atividade' # Ou o nome exato que aparece no seu CSV
    col_tipo_at = 'Tipo de Atividade'     # No seu CSV, verifique se é "Tipo de Atividade" ou ".1"
    col_recurso = 'Recurso'
    col_sup = 'SUPERVISOR'

    # Filtro: Na Base + Pendente
    df_master['Status_Limpo'] = df_master[col_status_at].fillna('').str.upper()
    df_master['Tipo_Limpo'] = df_master[col_tipo_at].fillna('').str.upper()
    
    # Filtro robusto
    cond_base = df_master['Tipo_Limpo'].str.contains('NA BASE', na=False)
    cond_pend = df_master['Status_Limpo'].str.contains('PENDENTE', na=False)
    
    df_tela = df_master[cond_base & cond_pend].copy()

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        # 3. Separação por Supervisor (como você faz no seu código de certidão)
        df_tela = df_tela[~df_tela[col_sup].fillna('').isin(['', 'N/A', 'NAN'])]
        supervisores = sorted(df_tela[col_sup].unique())
        
        col1, col2 = st.columns(2)
        
        # Exibir supervisores e técnicos
        for i, super_nome in enumerate(supervisores):
            target_col = col1 if i % 2 == 0 else col2
            with target_col:
                with st.container(border=True):
                    st.markdown(f"**{str(super_nome).upper()}**")
                    tecnicos = df_tela[df_tela[col_sup] == super_nome][col_recurso].unique()
                    for tec in tecnicos:
                        st.markdown(f"🏃‍♂️ {tec}")
else:
    st.info("ℹ️ Aguardando dados operacionais no arquivo rota_sincronizada.csv.")
