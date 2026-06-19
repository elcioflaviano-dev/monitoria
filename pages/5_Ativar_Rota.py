import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS DE LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    
    # 1. IDENTIFICAÇÃO DINÂMICA
    col_recurso = next((c for c in df.columns if 'RECURSO' in c.upper()), df.columns[0])
    col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)
    
    # Identifica todas as colunas que têm "TIPO" no nome
    cols_tipo = [c for c in df.columns if 'TIPO' in c.upper()]

    if col_status and cols_tipo:
        # 2. FILTRAGEM MULTI-COLUNA
        # Cria uma máscara que verifica se "BASE" existe em QUALQUER das colunas de tipo
        mask_base = df[cols_tipo].apply(lambda row: row.astype(str).str.contains('BASE', case=False, na=False).any(), axis=1)
        mask_status = df[col_status].fillna('').astype(str).str.contains('PEND', case=False, na=False)
        
        df_tela = df[mask_base & mask_status].copy()
        nomes_na_base = sorted(df_tela[col_recurso].dropna().unique().tolist())
        
        # 3. EXIBIÇÃO
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
        st.divider()
        
        if nomes_na_base:
            cols = st.columns(4)
            for i, nome in enumerate(nomes_na_base):
                with cols[i % 4]:
                    st.markdown(f'🏃‍♂️ **{nome}**')
        else:
            st.success("✅ Nenhum técnico pendente na base neste momento.")
    else:
        st.error(f"⚠️ Não encontrei colunas de Status ou Tipo. Colunas: {list(df.columns)}")
else:
    st.error("⚠️ 'rota_sincronizada.csv' não encontrado.")
