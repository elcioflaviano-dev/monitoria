import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #c62828; text-align: center;">🕵️ BUSCA DE COLUNA "BASE"</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        df.columns = [str(c).strip() for c in df.columns]
        
        st.write("### Procurando o termo 'BASE' em todas as colunas:")
        
        coluna_encontrada = False
        for col in df.columns:
            # Verifica se algum valor na coluna contém "BASE" (ignorando maiúsculas/minúsculas)
            contem_base = df[col].astype(str).str.contains('BASE', case=False, na=False).any()
            
            if contem_base:
                st.success(f"✅ A coluna **'{col}'** contém o termo 'BASE'!")
                st.write("Valores encontrados nesta coluna:", df[col].unique()[:10])
                coluna_encontrada = True
        
        if not coluna_encontrada:
            st.error("❌ Nenhuma coluna no arquivo contém o termo 'BASE'.")
            st.write("Colunas existentes:", list(df.columns))
            
    except Exception as e:
        st.error(f"Erro: {e}")
else:
    st.error("Arquivo não encontrado.")
