import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # Pega as colunas [1, 2, 22] e limpa
    df_clean = df.iloc[1:, [1, 2, 22]].copy()
    df_clean.columns = ['NOME', 'STATUS', 'TIPO']
    
    # LIMPEZA EXTRA: Remove espaços em branco antes/depois e coloca tudo em minúsculo
    df_clean['STATUS'] = df_clean['STATUS'].fillna('').str.strip().str.lower()
    df_clean['TIPO'] = df_clean['TIPO'].fillna('').str.strip().str.upper()

    st.write("--- DIAGNÓSTICO DE DADOS ---")
    
    # Mostra o que existe de único nas colunas para a gente comparar
    st.write("Status únicos encontrados:", df_clean['STATUS'].unique())
    st.write("Tipos únicos encontrados:", df_clean['TIPO'].unique())
    
    # Mostra as primeiras 20 linhas processadas
    st.dataframe(df_clean.head(20))
    
else:
    st.error("Arquivo não encontrado.")
