import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Filtro: Na Base + Pendente
    df_tela = df[
        (df['Tipo de Atividade.1'].str.contains('NA BASE', na=False, case=False)) & 
        (df['Status da Atividade'].str.contains('PENDENTE', na=False, case=False))
    ].copy()

    nomes_na_base = sorted(df_tela['Recurso'].unique().tolist())

    # 1. Múltipla seleção para SP
    st.markdown("### 🛠️ Configuração de Base")
    tecnicos_sp_selecionados = st.multiselect(
        "Selecione os técnicos que pertencem a SÃO PAULO (SP):",
        options=nomes_na_base,
        default=st.session_state.get("selecionados_sp", [])
    )
    st.session_state["selecionados_sp"] = tecnicos_sp_selecionados

    # 2. Exibição dividida
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### 🏢 ABC / GUARULHOS')
        for nome in nomes_na_base:
            if nome not in tecnicos_sp_selecionados:
                st.markdown(f'🏃‍♂️ {nome}')
                
    with col2:
        st.markdown('### 🏙️ SÃO PAULO (SP)')
        for nome in tecnicos_sp_selecionados:
            st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado. Vá na página inicial e suba o arquivo.")
