import streamlit as st
import pandas as pd
import os

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 1. MAPEAMENTO (Substitua o 'X' pelo índice da coluna do Supervisor que você vai me dizer)
    # Coluna 0 = Nome do Técnico | Coluna X = Nome do Supervisor
    COL_NOME = 0
    COL_SUP =   # <--- ME DIGA QUAL É ESSE NÚMERO
    
    # Criamos um dicionário técnico -> supervisor
    df_mapa = df[[COL_NOME, COL_SUP]].dropna().drop_duplicates(subset=[COL_NOME])
    mapa_tecnicos = dict(zip(df_mapa[COL_NOME], df_mapa[COL_SUP]))
    
    st.write("Mapa de técnicos carregado com sucesso!")
    st.write(f"Total de técnicos mapeados: {len(mapa_tecnicos)}")
else:
    st.error("Arquivo não encontrado.")
