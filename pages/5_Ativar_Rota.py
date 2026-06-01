import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Dicionário de Cidades
CIDADES_ABC = ['SANTO ANDRE', 'SAO BERNARDO DO CAMPO', 'DIADEMA', 'SAO CAETANO DO SUL', 'MAUA', 'GUARULHOS']
CIDADES_SP = ['SÃO PAULO', 'SAO PAULO']

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE (POR CIDADE)</h1>', unsafe_allow_html=True)

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
        # Função para determinar a região pela cidade
        def determinar_regiao(cidade):
            if pd.isna(cidade): return 'ABC' # Default se vazio
            c = str(cidade).upper().strip()
            if any(abc_city in c for abc_city in CIDADES_ABC):
                return 'ABC'
            elif any(sp_city in c for sp_city in CIDADES_SP):
                return 'SP'
            return 'ABC' # Qualquer outra cidade cai no ABC por segurança

        df_tela['REGIAO'] = df_tela['Cidade'].apply(determinar_regiao)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### 🏢 ABC / GUARULHOS')
            for nome in df_tela[df_tela['REGIAO'] == 'ABC']['Recurso'].unique():
                st.markdown(f'🏃‍♂️ {nome}')
                
        with col2:
            st.markdown('### 🏙️ SÃO PAULO (SP)')
            for nome in df_tela[df_tela['REGIAO'] == 'SP']['Recurso'].unique():
                st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado. Vá na página inicial e suba o arquivo de rota.")
