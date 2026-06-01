import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lemos sem cabeçalho (header=None) para evitar conflitos de nomes duplicados
    # dtype=str garante que nenhum número seja tratado como cálculo
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 🔍 Mapeamento fixo pelas posições que identificamos:
    # 1: RECURSO (Nome) | 2: STATUS | 22: TIPO (Na Base)
    # iloc[1:] pula a linha do cabeçalho que veio junto nos dados brutos
    df_clean = df.iloc[1:, [1, 2, 22]].copy()
    df_clean.columns = ['NOME', 'STATUS', 'TIPO']
    
    # 🔥 LIMPEZA PROFUNDA: Remove espaços invisíveis e padroniza para busca
    df_clean['NOME'] = df_clean['NOME'].fillna('').str.strip()
    df_clean['STATUS'] = df_clean['STATUS'].fillna('').str.strip().str.lower()
    df_clean['TIPO'] = df_clean['TIPO'].fillna('').str.strip().str.upper()
    
    # Filtro: Tipo contém "NA BASE" E Status igual a "pendente"
    df_tela = df_clean[
        (df_clean['TIPO'].str.contains('NA BASE', na=False)) & 
        (df_clean['STATUS'] == 'pendente')
    ].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
        # Debug opcional: se quiser ver o que ele está lendo, descomente a linha abaixo:
        # st.write(df_clean.head(10)) 
    else:
        st.markdown('<h2 style="color: #005088; text-align: center;">TÉCNICOS PENDENTES</h2>', unsafe_allow_html=True)
        for nome in df_tela['NOME'].unique():
            if nome:
                st.markdown(f'🏃‍♂️ <b>{nome}</b>', unsafe_allow_html=True)
            
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
