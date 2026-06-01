import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 AUDITORIA DE CIDADES</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Filtro: Na Base + Pendente
    df_tela = df[
        (df['Tipo de Atividade.1'].str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].str.contains('PENDENTE', na=False, case=False))
    ].copy()

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # DIAGNÓSTICO: Mostra o que ele está lendo na coluna CIDADE
        st.write("Cidades detectadas na base:", df_tela['Cidade'].unique())
        
        # Exibe os técnicos e a cidade que o sistema está lendo para eles
        st.table(df_tela[['Recurso', 'Cidade']])
        
else:
    st.error("⚠️ Nenhum dado carregado.")
