import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # Seleciona as colunas que interessam e força conversão para string
    df_debug = df.iloc[:, [3, 4, 23]].copy() 
    df_debug.columns = ['LOGIN', 'STATUS', 'TIPO']
    df_debug = df_debug.astype(str)
    
    st.write("--- DEPURADOR DE DADOS ---")
    st.write("Linhas que contêm 'Na Base' em qualquer coluna (verifique a coluna TIPO abaixo):")
    
    # Filtra linhas que contenham o termo, independente de onde esteja
    mask = df_debug.apply(lambda row: row.astype(str).str.contains('Na Base', case=False).any(), axis=1)
    df_filtrado = df_debug[mask]
    
    if not df_filtrado.empty:
        st.dataframe(df_filtrado)
    else:
        st.error("Nenhuma linha contendo o termo 'Na Base' foi encontrada. Aqui estão as 50 primeiras linhas brutas para conferência:")
        st.dataframe(df_debug.head(50))
else:
    st.error("Arquivo não encontrado.")
