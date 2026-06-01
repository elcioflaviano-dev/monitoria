import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Lendo o arquivo forçando o uso da primeira linha como cabeçalho
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
    df.columns = df.columns.str.strip()
    
    # 🔍 Busca por linhas na base + pendentes
    mask = df.apply(lambda row: row.astype(str).str.contains('Na Base', case=False, na=False).any(), axis=1) & \
           df.apply(lambda row: row.astype(str).str.contains('pendente', case=False, na=False).any(), axis=1)
    
    df_base = df[mask].copy()
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_base.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # AQUI É O PULO DO GATO:
        # Forçamos o uso da segunda coluna (índice 1) para o nome, independente do cabeçalho
        col_nome = df.columns[1] 
        col_sup = 'SUPERVISOR' # Mantemos a busca pelo supervisor
        
        # Cria lista limpa
        lista_final = df_base[[col_nome]].drop_duplicates()
        
        # Se existir coluna de supervisor, cruzamos os dados
        if col_sup in df.columns:
            df_sup = df[[col_nome, col_sup]].drop_duplicates(subset=[col_nome])
            lista_final = lista_final.merge(df_sup, on=col_nome, how='left')
        else:
            lista_final[col_sup] = 'N/A'

        def get_regiao(row):
            sup = str(row[col_sup]).upper() if pd.notna(row[col_sup]) else ""
            # Regra: Alan ou Francisco = SP, caso contrário = ABC
            if 'ALAN' in sup or 'FRANCISCO' in sup: 
                return 'SP'
            return 'ABC'

        lista_final['REGIAO'] = lista_final.apply(get_regiao, axis=1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<h2 style="color: #005088; text-align: center;">ABC / GUARULHOS</h2>', unsafe_allow_html=True)
            for _, row in lista_final[lista_final['REGIAO'] == 'ABC'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[col_nome]}</b>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h2 style="color: #005088; text-align: center;">SÃO PAULO (SP)</h2>', unsafe_allow_html=True)
            for _, row in lista_final[lista_final['REGIAO'] == 'SP'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[col_nome]}</b>', unsafe_allow_html=True)
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
