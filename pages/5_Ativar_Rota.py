import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    # Padroniza colunas
    df.columns = [str(c).strip() for c in df.columns]
    
    # BUSCA DINÂMICA MAIS PRECISA
    # Procura a primeira coluna que contenha 'STATUS'
    col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)
    # Procura a coluna que contenha 'TIPO' (prioriza a que tem conteúdo relevante)
    col_tipo = next((c for c in df.columns if 'TIPO' in c.upper()), None)
    col_recurso = 'Recurso' # Como visto no seu print
    
    if col_status and col_tipo:
        # AQUI ESTÁ A CORREÇÃO: Filtramos diretamente nas colunas encontradas
        # Normalizamos para string e removemos espaços para garantir o match
        df['TIPO_CLEAN'] = df[col_tipo].fillna('').astype(str).str.upper()
        df['STATUS_CLEAN'] = df[col_status].fillna('').astype(str).str.upper()
        
        # Filtro: Contém "BASE" e contém "PENDENTE"
        df_tela = df[
            df['TIPO_CLEAN'].str.contains('BASE', na=False) & 
            df['STATUS_CLEAN'].str.contains('PENDENTE', na=False)
        ].copy()
        
        # DEBUG (Só aparece se der 0, para você saber o que está acontecendo)
        if df_tela.empty:
            st.warning("⚠️ Nenhum técnico encontrado com os critérios.")
            st.write("Colunas detectadas:", list(df.columns))
            st.write("Exemplo de dados na coluna de Tipo:", df[col_tipo].unique())
            st.write("Exemplo de dados na coluna de Status:", df[col_status].unique())
        
        # Exibição
        nomes = df_tela[col_recurso].unique()
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes)}</h4>", unsafe_allow_html=True)
        st.divider()
        
        if len(nomes) > 0:
            c1, c2, c3, c4 = st.columns(4)
            cols = [c1, c2, c3, c4]
            for i, nome in enumerate(nomes):
                with cols[i % 4]:
                    st.markdown(f'🏃‍♂️ **{nome}** ⏳ PENDENTE')
    else:
        st.error(f"Não encontrei colunas de Status ({col_status}) ou Tipo ({col_tipo}).")
else:
    st.error("Ficheiro rota_sincronizada.csv não encontrado.")
