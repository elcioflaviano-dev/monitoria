import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lendo o arquivo bruto
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 1. Identificar quem está "NA BASE" + "PENDENTE"
    # Convertemos a linha inteira para texto para não depender da coluna exata
    def esta_na_base(row):
        linha_texto = " ".join(row.fillna('').astype(str)).upper()
        return "NA BASE" in linha_texto and "PENDENTE" in linha_texto

    # Identifica linhas que atendem ao critério
    linhas_na_base = df[df.apply(esta_na_base, axis=1)]
    
    # Pega apenas os nomes únicos (Coluna 0, conforme o print anterior)
    nomes_pendentes = sorted(linhas_na_base[0].dropna().unique())
    
    # 2. SEPARAÇÃO POR SUPERVISOR
    # Como não temos uma lista fixa, vamos inferir pela estrutura do seu arquivo.
    # Se você me disser em qual coluna fica o supervisor, eu cravo o código.
    # Por enquanto, vou listar todos e deixar você me dar a coluna.
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)
    
    st.markdown('<h2 style="color: #005088; text-align: center;">TÉCNICOS PENDENTES</h2>', unsafe_allow_html=True)
    for nome in nomes_pendentes:
        st.markdown(f'🏃‍♂️ <b>{nome}</b>', unsafe_allow_html=True)

else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
