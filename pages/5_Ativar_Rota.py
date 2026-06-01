import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lê o arquivo ignorando os cabeçalhos originais (que estão duplicados)
    # e define as colunas manualmente para evitar o conflito
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=0, dtype=str)
    
    # Renomeia as colunas para garantir que não haja duplicidade
    # Coluna 0: Indice, 1: Nome (RECURSO), 2: Status, 22: Tipo.1
    # Adaptamos conforme sua lista:
    df.columns = [
        'ID' if i == 0 else 
        'RECURSO' if 'RECURSO' in str(col) else 
        'STATUS_ATIVIDADE' if 'STATUS DA ATIVIDADE' in str(col).upper() else 
        'TIPO_ATIVIDADE_1' if 'TIPO DE ATIVIDADE.1' in str(col).upper() else 
        f'COL_{i}' for i, col in enumerate(df.columns)
    ]

    # 🔥 Filtro rigoroso nas colunas corretas
    mask = (df['TIPO_ATIVIDADE_1'].str.strip().str.upper() == 'NA BASE') & \
           (df['STATUS_ATIVIDADE'].str.strip().str.lower() == 'pendente')
    
    df_tela = df[mask].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # Exibe os nomes da coluna RECURSO
        st.markdown('<h2 style="color: #005088; text-align: center;">TÉCNICOS PENDENTES</h2>', unsafe_allow_html=True)
        for nome in df_tela['RECURSO'].unique():
            st.markdown(f'🏃‍♂️ <b>{nome}</b>', unsafe_allow_html=True)
            
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
