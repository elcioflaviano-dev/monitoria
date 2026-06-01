import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

st.markdown('<div style="background:#000; color:#fff; padding:15px; text-align:center; font-size:24px;">TV MODE - PAINEL ATIVO</div>', unsafe_allow_html=True)

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # Exibe algo simples para confirmar que o script roda
    st.write("Dados carregados com sucesso!")
    st.dataframe(df.head(5))
    
    # Botão de voltar
    st.markdown('<a href="/" target="_self">🏠 VOLTAR PARA A HOME</a>', unsafe_allow_html=True)

else:
    st.error(f"Arquivo {ARQUIVO_ROTA_DISCO} não encontrado.")

# Removi o st.rerun() propositalmente para você ver se o layout aparece
