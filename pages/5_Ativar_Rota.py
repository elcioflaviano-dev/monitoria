import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Carrega o arquivo e força as colunas para o padrão novo
if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # Mapeamento baseado na nova estrutura do arquivo que você enviou:
    # LOGIN está na coluna 'STATUS'
    # STATUS está na coluna 'LOGIN'
    # Vamos renomear para o código entender
    df = df.rename(columns={'STATUS': 'LOGIN_REAL', 'LOGIN': 'STATUS_REAL'})
    
    # Filtra onde o Status é 'pendente' (ignora maiúsculas)
    df_tela = df[df['STATUS_REAL'].str.contains('pendente', case=False, na=False)].copy()
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # Exibe a lista de técnicos pendentes
        df_tela = df_tela.drop_duplicates(subset=['LOGIN_REAL'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### ABC / GUARULHOS')
            # Aqui você pode filtrar por região se tiver uma coluna de cidade
            for _, row in df_tela.iterrows():
                st.markdown(f'🏃‍♂️ <b>{row["LOGIN_REAL"]}</b>', unsafe_allow_html=True)
        with col2:
            st.markdown('### SÃO PAULO (SP)')
            # A lista de SP apareceria aqui
else:
    st.warning("Arquivo não encontrado.")
