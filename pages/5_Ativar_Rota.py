import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 DIAGNÓSTICO DE COLUNAS</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        # Lê o CSV tentando detectar o separador automaticamente
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        
        # Limpa nomes das colunas
        df.columns = [str(c).strip() for c in df.columns]
        
        st.write("### 1. Lista Completa de Colunas Encontradas:")
        st.write(list(df.columns))
        
        st.write("---")
        st.write("### 2. Investigação de Colunas de TIPO:")
        
        colunas_tipo = [c for c in df.columns if 'TIPO' in c.upper()]
        
        if colunas_tipo:
            for col in colunas_tipo:
                st.write(f"**Coluna:** '{col}'")
                st.write("Valores únicos encontrados (primeiros 10):", df[col].unique()[:10])
                st.write("---")
        else:
            st.error("⚠️ Nenhuma coluna com a palavra 'TIPO' foi encontrada.")
            
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")
