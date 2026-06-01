import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
    except:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=';', dtype=str)

    df.columns = df.columns.str.strip()

    # Identifica as colunas chaves
    col_nome = next((c for c in df.columns if 'Login' in c or 'Recurso' in c), df.columns[0])
    col_status = 'Status da Atividade'
    col_tipo = 'Tipo de Atividade.1'
    col_supervisor = next((c for c in df.columns if 'SUPERVISOR' in c.upper()), None)

    # 1. Encontra todos os nomes dos técnicos que estão "Na Base" e "pendente"
    # Mesmo que a linha não tenha login, se ela tem um nome na coluna de Recurso, pegamos o nome
    base_mask = df[col_tipo].str.contains('Na Base', case=False, na=False) & \
                df[col_status].str.contains('pendente', case=False, na=False)
    
    nomes_na_base = df[base_mask][col_nome].unique()

    # 2. Agora criamos um DataFrame apenas com esses técnicos, trazendo o supervisor deles
    # Buscamos o supervisor em qualquer outra linha onde esse nome apareça
    df_result = pd.DataFrame(nomes_na_base, columns=[col_nome])
    
    # Fazemos um merge para trazer o supervisor baseado no nome do técnico
    df_supervisor = df[[col_nome, col_supervisor]].drop_duplicates(subset=[col_nome])
    df_final = df_result.merge(df_supervisor, on=col_nome, how='left')

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_final.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        def definir_regiao(row):
            sup = str(row[col_supervisor]).upper() if col_supervisor and pd.notna(row[col_supervisor]) else ""
            if 'ALAN' in sup or 'FRANCISCO' in sup: 
                return 'SP'
            return 'ABC'

        df_final['REGIAO'] = df_final.apply(definir_regiao, axis=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 style="color: #005088; text-align: center;">ABC / GUARULHOS</h2>', unsafe_allow_html=True)
            for _, row in df_final[df_final['REGIAO'] == 'ABC'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[col_nome]}</b>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h2 style="color: #005088; text-align: center;">SÃO PAULO (SP)</h2>', unsafe_allow_html=True)
            for _, row in df_final[df_final['REGIAO'] == 'SP'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[col_nome]}</b>', unsafe_allow_html=True)
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
