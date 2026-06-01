import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # 🛠️ Leitura blindada: detecta o separador e trata aspas em endereços
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
    except:
        # Fallback caso o separador seja fixo
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=';', dtype=str)

    # Limpeza de nomes de colunas
    df.columns = df.columns.str.strip()

    # 🔍 BUSCA POR CONTEÚDO (Não depende de coluna específica)
    # Procuramos 'Na Base' e 'pendente' em qualquer lugar da linha
    mask = df.apply(lambda row: row.astype(str).str.contains('Na Base', case=False, na=False).any(), axis=1) & \
           df.apply(lambda row: row.astype(str).str.contains('pendente', case=False, na=False).any(), axis=1)
    
    df_tela = df[mask].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        # Identifica colunas pelo conteúdo para exibir
        # Tenta achar colunas úteis
        col_login = next((c for c in df.columns if 'Login' in c or 'Recurso' in c), df.columns[0])
        col_janela = next((c for c in df.columns if 'Janela' in c), None)
        col_cidade = next((c for c in df.columns if 'Cidade' in c), None)

        def definir_regiao(row):
            if col_cidade and col_cidade in row:
                cidade = str(row[col_cidade]).upper()
                if 'SAO PAULO' in cidade or 'SÃO PAULO' in cidade: return 'SP'
            return 'ABC'

        df_tela['REGIAO'] = df_tela.apply(definir_regiao, axis=1)
        df_tela = df_tela.drop_duplicates(subset=[col_login])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 style="color: #005088; text-align: center;">ABC / GUARULHOS</h2>', unsafe_allow_html=True)
            for _, row in df_tela[df_tela['REGIAO'] == 'ABC'].iterrows():
                janela = f" - {row[col_janela]}" if col_janela else ""
                st.markdown(f'🏃‍♂️ <b>{row[col_login]}</b> {janela}', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h2 style="color: #005088; text-align: center;">SÃO PAULO (SP)</h2>', unsafe_allow_html=True)
            for _, row in df_tela[df_tela['REGIAO'] == 'SP'].iterrows():
                janela = f" - {row[col_janela]}" if col_janela else ""
                st.markdown(f'🏃‍♂️ <b>{row[col_login]}</b> {janela}', unsafe_allow_html=True)
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado na pasta.")
