import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# 1. CARREGAR DADOS
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df_rota = st.session_state['df_rota_ativa']
    
    # Suponha que você tenha um arquivo 'funcionarios.csv' com colunas ['NOME', 'SUPERVISOR']
    # Se não tiver, precisamos carregar essa lista de alguma forma. 
    # Vou assumir que você tem um CSV com a referência.
    if os.path.exists("funcionarios.csv"):
        df_func = pd.read_csv("funcionarios.csv")
    else:
        st.error("⚠️ Preciso do arquivo 'funcionarios.csv' para fazer o PROCV. Suba ele na página inicial!")
        st.stop()

    # 2. FILTRO BASE + PENDENTE
    df_tela = df_rota[
        (df_rota['Tipo de Atividade.1'].str.contains('NA BASE', na=False, case=False)) & 
        (df_rota['Status da Atividade'].str.contains('PENDENTE', na=False, case=False))
    ].copy()

    # 3. O "PROCV" (Merge)
    # Amarra o Nome do Técnico da Rota com o Nome na Planilha de Funcionários
    df_final = df_tela.merge(df_func, left_on='Recurso', right_on='NOME', how='left')

    # 4. EXIBIÇÃO SEPARADA
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Filtro de SP (Alan e Francisco)
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
    st.error("⚠️ Nenhum dado de rota carregado.")
