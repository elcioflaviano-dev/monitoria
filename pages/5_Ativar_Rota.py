import streamlit as st
import pandas as pd
import os  # <--- A IMPORTAÇÃO QUE FALTAVA

st.set_page_config(layout="wide")

# 1. Carrega os dados da Rota (que já estão na memória)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df_rota = st.session_state['df_rota_ativa']
    
    # 2. Carrega a lista de Funcionários
    # Se o arquivo não existir, criamos um DataFrame vazio para não travar o app
    if os.path.exists("funcionarios.csv"):
        df_func = pd.read_csv("funcionarios.csv", dtype=str)
    else:
        st.warning("⚠️ Arquivo 'funcionarios.csv' não encontrado. Não será possível filtrar por Supervisor.")
        df_func = pd.DataFrame(columns=['NOME', 'SUPERVISOR'])

    # 3. Filtro Base + Pendente
    df_tela = df_rota[
        (df_rota['Tipo de Atividade.1'].str.contains('NA BASE', na=False, case=False)) & 
        (df_rota['Status da Atividade'].str.contains('PENDENTE', na=False, case=False))
    ].copy()

    # 4. Cruzamento (PROCV)
    # Se tivermos dados de funcionários, fazemos o merge
    if not df_func.empty:
        df_final = df_tela.merge(df_func, left_on='Recurso', right_on='NOME', how='left')
    else:
        df_final = df_tela.copy()
        df_final['SUPERVISOR'] = 'N/A'

    # 5. Exibição
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Filtro: Se for Alan ou Francisco, é SP. Senão, é ABC.
    sp_mask = df_final['SUPERVISOR'].str.contains('ALAN|FRANCISCO', na=False, case=False)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in df_final[~sp_mask]['Recurso'].unique():
            st.markdown(f'🏃‍♂️ {nome}')
            
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in df_final[sp_mask]['Recurso'].unique():
            st.markdown(f'🏃‍♂️ {nome}')

else:
    st.error("⚠️ Nenhum dado de rota carregado. Vá na página inicial e suba o arquivo.")
