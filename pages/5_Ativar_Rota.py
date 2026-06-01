import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"  # Variável definida agora!

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lendo sem considerar cabeçalhos para ver o que realmente está vindo
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    st.title("🔍 Auditoria de Dados Brutos")
    
    # Exibe as primeiras 10 linhas para identificarmos as colunas
    st.write("Linhas brutas do arquivo (sem cabeçalhos):")
    st.dataframe(df.head(10))
    
    st.write("---")
    st.write("Identifique na tabela acima: Em qual **número de coluna** (0, 1, 2...) aparece o texto 'Na Base' e em qual aparece o 'pendente'?")
else:
    st.error(f"Arquivo {ARQUIVO_ROTA_DISCO} não encontrado na pasta raiz.")
