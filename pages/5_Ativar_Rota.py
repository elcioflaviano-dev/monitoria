import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # DEBUG: Mostra o que tem na coluna de tipo de atividade para a gente ver a grafia real
    st.write("Colunas encontradas:", df.columns.tolist())
    
    # Procura colunas que pareçam com 'Tipo'
    col_tipo = [c for c in df.columns if 'Tipo' in c][0]
    
    # Mostra os valores únicos que existem nessa coluna
    st.write("Valores únicos encontrados na coluna de Tipo:")
    st.write(df[col_tipo].unique())
    
    # Mostra uma amostra das linhas para vermos como o status aparece
    st.write("Amostra dos dados:")
    st.dataframe(df.head(20))
else:
    st.error("Arquivo não encontrado!")
