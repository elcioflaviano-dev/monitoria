import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Carrega o CSV
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    
    # Debug: Mostra as colunas detectadas (ajuda a saber se o nome da coluna mudou)
    # st.write("Colunas detectadas:", list(df.columns)) 
    
    # Tenta encontrar as colunas essenciais ignorando espaços extras
    col_recurso = next((c for c in df.columns if 'RECURSO' in c.upper()), 'Recurso')
    col_tipo = next((c for c in df.columns if 'TIPO' in c.upper() and 'ATIVIDADE' in c.upper()), None)
    col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)

    if col_tipo and col_status:
        # Normalização: Remove espaços e coloca em minúsculo para comparar
        df['TIPO_NORML'] = df[col_tipo].str.strip().str.lower()
        df['STATUS_NORML'] = df[col_status].str.strip().str.lower()
        
        # Filtro: Contém "base" E "pendente" (independente de maiúsculas/minúsculas)
        df_tela = df[
            df['TIPO_NORML'].str.contains('base', na=False) & 
            df['STATUS_NORML'].str.contains('pend', na=False)
        ].copy()
        
        # Se estiver vazio, mostra o que ele viu para debugarmos
        if df_tela.empty:
            st.warning("⚠️ Nenhum técnico encontrado com status 'Pendente' e tipo 'Base'.")
            st.write("Valores encontrados na coluna Tipo:", df['TIPO_NORML'].unique())
            st.write("Valores encontrados na coluna Status:", df['STATUS_NORML'].unique())
        
        else:
            # Lista de nomes únicos
            nomes = df_tela[col_recurso].dropna().unique()
            st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes)}</h4>", unsafe_allow_html=True)
            st.divider()
            
            c1, c2, c3, c4 = st.columns(4)
            cols = [c1, c2, c3, c4]
            
            # Exibe os nomes
            for i, nome in enumerate(nomes):
                with cols[i % 4]:
                    st.markdown(f'🏃‍♂️ **{nome.strip()}** ⏳')
    else:
        st.error(f"Erro: Colunas não identificadas. Encontrado: {list(df.columns)}")
else:
    st.error("⚠️ 'rota_sincronizada.csv' não encontrado. Verifique a pasta.")
