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

    # 🔍 Busca robusta pelos técnicos em base
    mask = df.apply(lambda row: row.astype(str).str.contains('Na Base', case=False, na=False).any(), axis=1) & \
           df.apply(lambda row: row.astype(str).str.contains('pendente', case=False, na=False).any(), axis=1)
    
    df_tela = df[mask].copy()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados para a rua!")
    else:
        # Identifica colunas
        col_login = next((c for c in df.columns if 'Login' in c or 'Recurso' in c), df.columns[0])
        col_cidade = next((c for c in df.columns if 'Cidade' in c), None)

        def definir_regiao(row):
            if col_cidade and col_cidade in row:
                cidade = str(row[col_cidade]).upper()
                # Se contiver 'PAULO', é São Paulo. Se não, ABC/Guarulhos.
                if 'PAULO' in cidade: 
                    return 'SP'
            return 'ABC'

        df_tela['REGIAO'] = df_tela.apply(definir_regiao, axis=1)
        df_tela = df_tela.drop_duplicates(subset=[col_login])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h2 style="color: #005088; text-align: center;">ABC / GUARULHOS</h2>', unsafe_allow_html=True)
            for _, row in df_tela[df_tela['REGIAO'] == 'ABC'].iterrows():
                st.markdown(f'🏃‍♂️ <b>{row[col_login]}</b>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<h2 style="color: #005088; text-align: center;">SÃO PAULO (SP)</h2>', unsafe_allow_html=True)
            # Mostra o que ele encontrou em SP
            lista_sp = df_tela[df_tela['REGIAO'] == 'SP']
            if not lista_sp.empty:
                for _, row in lista_sp.iterrows():
                    st.markdown(f'🏃‍♂️ <b>{row[col_login]}</b>', unsafe_allow_html=True)
            else:
                st.info("Nenhum técnico identificado em SP.")
else:
    st.error("Arquivo rota_sincronizada.csv não encontrado.")
