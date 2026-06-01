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

    if df_tela.empty:
        st.success("🎉 Todos os técnicos foram liberados!")
    else:
        # Lógica de Separação por Supervisor (Independente de Cidade)
        def determinar_regiao(supervisor):
            if pd.isna(supervisor): return 'ABC'
            sup = str(supervisor).upper().strip()
            # SE FOR ALAN OU FRANCISCO, É SP. CASO CONTRÁRIO, ABC.
            if 'ALAN' in sup or 'FRANCISCO' in sup:
                return 'SP'
            return 'ABC'

        df_tela['REGIAO'] = df_tela['SUPERVISOR'].apply(determinar_regiao)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### 🏢 ABC / GUARULHOS')
            # Filtra apenas os que não são SP
            lista_abc = df_tela[df_tela['REGIAO'] == 'ABC']['Recurso'].unique()
            for nome in lista_abc:
                st.markdown(f'🏃‍♂️ {nome}')
                
        with col2:
            st.markdown('### 🏙️ SÃO PAULO (SP)')
            # Filtra apenas os que são SP
            lista_sp = df_tela[df_tela['REGIAO'] == 'SP']['Recurso'].unique()
            for nome in lista_sp:
                st.markdown(f'🏃‍♂️ {nome}')
else:
    st.error("⚠️ Nenhum dado carregado na memória.")
