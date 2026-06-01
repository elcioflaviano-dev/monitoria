import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# Puxa os dados que já foram carregados pela página principal/certidão
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Filtro: Na Base + Pendente
    # Ajuste os nomes das colunas conforme sua planilha real
    df_tela = df[
        (df['Tipo de Atividade.1'].str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].str.contains('PENDENTE', na=False, case=False))
    ].copy()

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # Exibição simples sem filtro de supervisor
        st.markdown('### 👤 Técnicos Pendentes na Base')
        for nome in df_tela['Recurso'].unique():
            st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado. Vá na página inicial e suba o arquivo.")
