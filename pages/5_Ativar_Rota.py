import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lendo sem cabeçalhos para respeitar os índices 3 e 22
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 🛠️ Mapeamento fixo pelo índice
    # Coluna 3: Status da Atividade | Coluna 22: Tipo de Atividade
    df_tela = df[
        (df[22].fillna('').astype(str).str.contains('Na Base', case=False, na=False)) & 
        (df[3].fillna('').astype(str).str.contains('pendente', case=False, na=False))
    ].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 100% da equipe liberada para a rua!")
    else:
        # Exibição dos dados
        st.write(f"Total de técnicos na base: {len(df_tela)}")
        
        # Como o arquivo exportado está simplificado, exibimos o que está na coluna 1 (Login)
        for _, row in df_tela.iterrows():
            st.markdown(f'🏃‍♂️ Técnico ID: <b>{row[1]}</b>', unsafe_allow_html=True)
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
