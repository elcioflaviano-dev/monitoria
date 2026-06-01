import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lendo sem considerar cabeçalhos para ver o que realmente está vindo
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    st.title("🔍 Auditoria de Dados Brutos")
    
    # Exibe as primeiras 5 linhas para a gente ver o que tem nelas
    st.write("Linhas brutas do arquivo (sem cabeçalhos):")
    st.dataframe(df.head(10))
    
    st.write("---")
    st.write("Para o código funcionar, precisamos identificar em qual coluna (número) está o texto 'Na Base' e em qual está o 'pendente'.")
    st.write("Olhando a tabela acima, me diga: Em qual número de coluna (0, 1, 2...) está o texto 'Na Base'?")
else:
    st.error("Arquivo não encontrado.")
