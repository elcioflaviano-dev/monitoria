import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # 1. LEITURA BRUTA (Ignora cabeçalhos pois eles estão quebrando o filtro)
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, header=None, dtype=str)
    
    # 2. LIMPEZA DE LIXO (Remove linhas que são datas ou cabeçalhos repetidos)
    # Filtramos apenas linhas que têm pelo menos 10 colunas, eliminando as linhas "sujas"
    df = df[df.count(axis=1) > 10].copy()
    
    # 3. EXTRAÇÃO DE DADOS (Baseado na sua estrutura)
    # NOME = Coluna 1, STATUS = Coluna 2, TIPO = Coluna 22, SUPERVISOR = Coluna 10 (Ajuste se necessário!)
    df_clean = df[[1, 2, 22, 10]].copy()
    df_clean.columns = ['NOME', 'STATUS', 'TIPO', 'SUPERVISOR']
    
    # Padronização
    df_clean = df_clean.apply(lambda x: x.str.strip().str.upper())
    
    # 4. FILTRO DE QUEM ESTÁ NA BASE E PENDENTE
    df_tela = df_clean[
        (df_clean['TIPO'].str.contains('NA BASE', na=False)) & 
        (df_clean['STATUS'].str.contains('PENDENTE', na=False))
    ].drop_duplicates(subset=['NOME'])
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)
    
    # 5. SEPARAÇÃO (SP vs ABC)
    col1, col2 = st.columns(2)
    
    # Lista SP: Supervisores Alan ou Francisco
    sp_mask = df_tela['SUPERVISOR'].str.contains('ALAN|FRANCISCO', na=False)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in df_tela[~sp_mask]['NOME']:
            st.markdown(f'🏃‍♂️ {nome}')
            
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in df_tela[sp_mask]['NOME']:
            st.markdown(f'🏃‍♂️ {nome}')
            
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
