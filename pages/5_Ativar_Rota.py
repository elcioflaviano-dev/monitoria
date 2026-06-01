import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    # Tenta ler o arquivo
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, sep=None, engine='python', quotechar='"', dtype=str)
        df.columns = df.columns.str.strip()
    except:
        df = pd.DataFrame()

    st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

    # Verifica se é o arquivo completo (tem as colunas que você enviou antes)
    if 'Login do Técnico' in df.columns:
        # Lógica para o arquivo completo
        mask = df['Tipo de Atividade.1'].str.contains('Na Base', case=False, na=False) & \
               df['Status da Atividade'].str.contains('pendente', case=False, na=False)
        
        df_tela = df[mask].copy()
        
        if df_tela.empty:
            st.success("🎉 Todos os técnicos foram liberados!")
        else:
            # ... (aqui entraria a lógica que já tínhamos de separar por cidade/supervisor)
            st.write("Técnicos encontrados:", df_tela['Login do Técnico'].unique())
            
    else:
        # Lógica de erro para quando o arquivo carregado está reduzido
        st.error("⚠️ Você carregou um arquivo de exportação rápida (apenas 4 colunas).")
        st.info("Para o painel funcionar, por favor, carregue o **Relatório Completo** (com as colunas: Login do Técnico, Cidade, Supervisor, etc).")
        st.write("Colunas detectadas no arquivo atual:", df.columns.tolist())

else:
    st.warning("Arquivo não encontrado. Carregue o relatório completo.")
