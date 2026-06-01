import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Leitura robusta
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
    df.columns = df.columns.str.strip()
    
    # 1. Filtra linhas com "Na Base" e "pendente" (sem olhar coluna específica)
    mask = df.apply(lambda row: row.astype(str).str.contains('Na Base', case=False, na=False).any(), axis=1) & \
           df.apply(lambda row: row.astype(str).str.contains('pendente', case=False, na=False).any(), axis=1)
    
    df_base = df[mask].copy()
    
    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_base.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # 2. Captura o Nome do Técnico (coluna LOGIN) e o Supervisor (coluna SUPERVISOR)
        # Se a coluna 'LOGIN' não existir, pegamos a primeira coluna
        col_nome = 'LOGIN' if 'LOGIN' in df.columns else df.columns[1]
        col_sup = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else None
        
        # 3. Cria lista de técnicos identificados
        lista_final = df_base[[col_nome]].drop_duplicates()
        
        # Cruzamento para trazer o supervisor (se existir)
        if col_sup:
            df_sup = df[[col_nome, col_sup]].drop_duplicates(subset=[col_nome])
            lista_final = lista_final.merge(df_sup, on=col_nome, how='left')

        # Função de divisão regional
        def get_regiao(row):
            sup = str(row[col_sup]).upper() if col_sup and pd.notna(row[col_sup]) else ""
            if 'ALAN' in sup or 'FRANCISCO' in sup or 'SÃO PAULO' in sup: 
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
