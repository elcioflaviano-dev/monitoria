import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="auto")

# CSS: Restaurado o menu lateral (removi o comando de ocultar)
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        # Tenta ler com auto-detecção de separador
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        
        # DEBUG: Isso vai mostrar exatamente como o arquivo está a ser lido
        st.write("### Diagnóstico do Arquivo")
        st.write("Colunas identificadas pelo Pandas:", list(df.columns))
        st.write("Primeiras 3 linhas do arquivo:", df.head(3))
        
        # Se você vê números como '0', '1', '2' nas colunas, o arquivo NÃO tem cabeçalho.
        # Se o seu arquivo não tem cabeçalho, a solução é nomear manualmente.
        
        # Lógica de tentativa de busca (Ajustada para ser menos rígida)
        # Se as colunas forem "0, 1, 2...", o seu CSV está mal formatado ou sem header.
        
        col_recurso = next((c for c in df.columns if 'RECURSO' in str(c).upper()), None)
        col_tipo = next((c for c in df.columns if 'TIPO' in str(c).upper()), None)
        col_status = next((c for c in df.columns if 'STATUS' in str(c).upper()), None)

        if col_tipo and col_status and col_recurso:
            # Filtro
            df_tela = df[
                (df[col_tipo].fillna('').astype(str).str.strip().str.lower() == 'na base') & 
                (df[col_status].fillna('').astype(str).str.strip().str.lower() == 'pendente')
            ].copy()

            nomes = sorted(df_tela[col_recurso].dropna().unique().tolist())
            
            st.markdown(f"### Total na Base: {len(nomes)}")
            for n in nomes: st.markdown(f'🏃‍♂️ {n}')
        else:
            st.error("⚠️ Não encontrei colunas com nome 'Recurso', 'Tipo' ou 'Status'. Veja a lista acima e verifique se o arquivo está correto.")
            
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")
