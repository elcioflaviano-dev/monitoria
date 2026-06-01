import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# Lista dos técnicos que você sabe que são de SP (Adicione todos aqui)
TECNICOS_SP = [
    "FABIO OLIVEIRA CAMPOS FARIAS", 
    "JANAILSON RICARDO FERREIRA DOS SANTOS",
    "ADRIEL ALEXANDER DE LIMA" # Exemplo, adicione os demais
]

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Filtro fixo de Na Base + Pendente
    df_tela = df[
        (df['Tipo de Atividade.1'].astype(str).str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].astype(str).str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in nomes_na_base:
            if nome not in TECNICOS_SP:
                st.markdown(f'🏃‍♂️ {nome}')
                
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in nomes_na_base:
            if nome in TECNICOS_SP:
                st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado. Vá na página inicial e suba o arquivo.")
