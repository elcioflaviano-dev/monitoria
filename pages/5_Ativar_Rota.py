import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # 🛠️ Nomes de colunas exatos baseados na sua foto
    COL_TEC = 'Login do Técnico'
    COL_STATUS = 'Status da Atividade'
    COL_TIPO = 'Tipo de Atividade.1' 
    COL_CIDADE = 'Cidade'
    COL_JANELA = 'Janela de Serviço'
    
    # 🔥 Filtro de "Na Base" + "pendente"
    # Convertemos para string e forçamos o strip para remover espaços invisíveis
    df_tela = df[
        (df[COL_TIPO].fillna('').astype(str).str.strip() == 'Na Base') & 
        (df[COL_STATUS].fillna('').astype(str).str.strip().str.lower() == 'pendente')
    ].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        # Função para dividir por região
        def definir_regiao(cidade):
            if pd.isna(cidade): return 'ABC'
            cidade = str(cidade).upper()
            if 'SAO PAULO' in cidade or 'SÃO PAULO' in cidade:
                return 'SP'
            return 'ABC'

        df_tela['REGIAO'] = df_tela[COL_CIDADE].apply(definir_regiao)
        
        # Remove duplicados de técnicos
        df_tela = df_tela.drop_duplicates(subset=[COL_TEC])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h2 style="color: #005088; text-align: center;">ABC / GUARULHOS</h2>', unsafe_allow_html=True)
            for _, row in df_tela[df_tela['REGIAO'] == 'ABC'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[COL_TEC]}</b> <span style="float:right; font-size: 14px;">{row[COL_JANELA]}</span>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h2 style="color: #005088; text-align: center;">SÃO PAULO (SP)</h2>', unsafe_allow_html=True)
            for _, row in df_tela[df_tela['REGIAO'] == 'SP'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[COL_TEC]}</b> <span style="float:right; font-size: 14px;">{row[COL_JANELA]}</span>', unsafe_allow_html=True)
else:
    st.warning("Arquivo não encontrado. Carregue o relatório completo.")
