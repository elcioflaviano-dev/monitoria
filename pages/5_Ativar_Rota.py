import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS PARA LIMPEZA DA INTERFACE
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        # A MUDANÇA MAIS IMPORTANTE: engine='python' e sep=None fazem o Pandas 
        # auto-detectar se o arquivo usa vírgula, ponto e vírgula ou tabulação.
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', dtype=str)
        
        # Limpar espaços nos nomes das colunas e colocar tudo em maiúsculo para facilitar
        df.columns = [str(c).strip() for c in df.columns]
        
        # DEBUG: Se as colunas estiverem estranhas, vamos vê-las aqui
        # st.write("Colunas encontradas:", list(df.columns))

        # Procura as colunas essenciais
        col_recurso = next((c for c in df.columns if 'RECURSO' in c.upper()), df.columns[0])
        col_tipo = next((c for c in df.columns if 'TIPO' in c.upper() and 'ATIVIDADE' in c.upper()), None)
        col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)

        if col_tipo and col_status:
            # Filtro robusto (ignora maiúsculas/minúsculas e espaços)
            df_tela = df[
                (df[col_tipo].str.strip().str.lower() == 'na base') & 
                (df[col_status].str.strip().str.lower() == 'pendente')
            ].copy()

            nomes_na_base = sorted(df_tela[col_recurso].dropna().unique().tolist())

            # Exibição
            st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
            st.divider()

            if len(nomes_na_base) > 0:
                c1, c2, c3, c4 = st.columns(4)
                cols = [c1, c2, c3, c4]
                # Divide a lista em 4 colunas
                for i, nome in enumerate(nomes_na_base):
                    with cols[i % 4]:
                        st.markdown(f'🏃‍♂️ **{nome}**')
            else:
                st.success("✅ Nenhum técnico pendente na base neste momento!")
        else:
            st.error("⚠️ Não foi possível identificar as colunas 'Tipo de Atividade' ou 'Status'.")
            st.write("Colunas encontradas no seu arquivo:", list(df.columns))
            
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")
