import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lemos sem cabeçalho (header=None) para que o Pandas trate tudo como dados brutos
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 🔍 Mapeamento fixo pelas posições que identificamos na sua foto:
    # Índice 1: Nome do Técnico | Índice 2: Status | Índice 22: Tipo de Atividade
    
    # Criamos um sub-dataframe apenas com essas colunas para facilitar o filtro
    # O .iloc[1:] pula a linha do cabeçalho que veio junto com os dados
    df_clean = df.iloc[1:, [1, 2, 22]].copy()
    df_clean.columns = ['NOME', 'STATUS', 'TIPO']
    
    # Limpeza dos dados
    df_clean['NOME'] = df_clean['NOME'].fillna('').str.strip()
    df_clean['STATUS'] = df_clean['STATUS'].fillna('').str.strip()
    df_clean['TIPO'] = df_clean['TIPO'].fillna('').str.strip()
    
    # 🔥 Filtro de "Na Base" + "pendente"
    df_tela = df_clean[
        (df_clean['TIPO'].str.upper() == 'NA BASE') & 
        (df_clean['STATUS'].str.lower() == 'pendente')
    ].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        st.markdown('<h2 style="color: #005088; center;">TÉCNICOS PENDENTES</h2>', unsafe_allow_html=True)
        # Exibe nomes únicos
        for nome in df_tela['NOME'].unique():
            if nome: # Garante que não imprima linhas vazias
                st.markdown(f'🏃‍♂️ <b>{nome}</b>', unsafe_allow_html=True)
            
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
