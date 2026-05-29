import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">🚀 PAINEL DE CONTROLE - UPLOAD DE ROTAS</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 16px; margin-bottom: 30px;">Suba um ou mais arquivos de rota para alimentar todo o sistema simultaneamente.</div>', unsafe_allow_html=True)

# === GESTÃO DO BANCO DE DADOS LOCAL DE CERTIDÕES ===
ARQUIVO_BANCO = "banco_certidoes.csv"

def carregar_banco_historico():
    colunas_padrao = ["Data/Hora", "Contrato", "Status", "Supervisor", "Recurso", "Intervalo de Tempo", "Observação"]
    if os.path.exists(ARQUIVO_BANCO):
        try:
            df_hist = pd.read_csv(ARQUIVO_BANCO, dtype=str)
            return df_hist[[c for c in df_hist.columns if c in colunas_padrao]]
        except:
            return pd.DataFrame(columns=colunas_padrao)
    return pd.DataFrame(columns=colunas_padrao)

# Garante que o histórico de auditoria permaneça carregado na memória global do sistema
if "historico_certidoes" not in st.session_state:
    st.session_state["historico_certidoes"] = carregar_banco_historico()

# === PROCESSO DE UPLOAD MÚLTIPLO DE ROTAS ===
arquivos_upload = st.file_uploader(
    "Arraste ou selecione os arquivos Excel das Rotas (.xlsx)", 
    type=["xlsx"], 
    accept_multiple_files=True
)

if 'df_rota_ativa' not in st.session_state:
    st.session_state['df_rota_ativa'] = None

if arquivos_upload:
    lista_dfs = []
    
    for arquivo in arquivos_upload:
        try:
            df_individual = pd.read_excel(arquivo, engine="openpyxl")
            if not df_individual.empty:
                lista_dfs.append(df_individual)
        except Exception as e:
            st.error(f"❌ Erro ao ler o arquivo {arquivo.name}: {e}")
            
    if lista_dfs:
        try:
            df_consolidado = pd.concat(lista_dfs, ignore_index=True)
            
            if 'Contrato' in df_consolidado.columns:
                df_consolidado = df_consolidado.dropna(subset=['Contrato'])
                df_consolidado = df_consolidado.drop_duplicates(subset=['Contrato'], keep='first')
            
            df_consolidado = df_consolidado.astype(str)
            
            # Alimenta a variável global usada por todas as subpáginas do sistema
            st.session_state['df_rota_ativa'] = df_consolidado
            
            st.success(f"✅ Sucesso! {len(lista_dfs)} arquivo(s) unificado(s). Total de {len(df_consolidado)} contratos únicos carregados na memória do sistema.")
            
        except Exception as e:
            st.error(f"❌ Erro na consolidação das rotas: {e}")

# Exibe o status consolidado da base
if st.session_state['df_rota_ativa'] is not None:
    st.info(f"🔄 Base de Dados Ativa: Sistema alimentado com {len(st.session_state['df_rota_ativa'])} linhas. Pode navegar livremente pelas outras páginas.")
    with st.expander("🔍 Visualizar Amostra dos Dados Carregados"):
        st.dataframe(st.session_state['df_rota_ativa'].head(10), use_container_width=True)
else:
    st.warning("⚠️ Nenhuma rota carregada no momento. Por favor, faça o upload dos arquivos acima.")
