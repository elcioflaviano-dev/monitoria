import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">🚀 PAINEL DE CONTROLE - UPLOAD DE ROTAS</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 16px; margin-bottom: 30px;">Suba um ou mais arquivos de rota para alimentar todo o sistema simultaneamente.</div>', unsafe_allow_html=True)

# 1. Ativa a opção de múltiplos arquivos (accept_multiple_files=True)
arquivos_upload = st.file_uploader(
    "Arraste ou selecione os arquivos Excel das Rotas (.xlsx)", 
    type=["xlsx"], 
    accept_multiple_files=True
)

# Inicializa a base na sessão se não existir
if 'df_rota_ativa' not in st.session_state:
    st.session_state['df_rota_ativa'] = None

if arquivos_upload:
    lista_dfs = []
    
    for arquivo in arquivos_upload:
        try:
            # openpyxl garante a leitura correta do formato zip/xlsx do Excel
            df_individual = pd.read_excel(arquivo, engine="openpyxl")
            if not df_individual.empty:
                lista_dfs.append(df_individual)
        except Exception as e:
            st.error(f"❌ Erro ao ler o arquivo {arquivo.name}: {e}")
            
    if lista_dfs:
        try:
            # Junta todos os arquivos de rota subidos em um único DataFrame
            df_consolidado = pd.concat(lista_dfs, ignore_index=True)
            
            # Remove linhas totalmente vazias ou sem contrato
            if 'Contrato' in df_consolidado.columns:
                df_consolidado = df_consolidado.dropna(subset=['Contrato'])
                # Remove contratos duplicados na base consolidada do dia
                df_consolidado = df_consolidado.drop_duplicates(subset=['Contrato'], keep='first')
            
            # Converte tudo para string para evitar quebras de formato nas outras páginas
            df_consolidado = df_consolidado.astype(str)
            
            # SALVAMENTO PERSISTENTE NA SESSÃO DO SISTEMA
            st.session_state['df_rota_ativa'] = df_consolidado
            
            st.success(f"✅ Sucesso! {len(lista_dfs)} arquivo(s) unificado(s). Total de {len(df_consolidado)} contratos únicos carregados na memória do sistema.")
            
        except Exception as e:
            st.error(f"❌ Erro na consolidação das rotas: {e}")

# Exibe o status da base atual para o usuário ter certeza que o sistema guardou
if st.session_state['df_rota_ativa'] is not None:
    st.info(f"🔄 Base de Dados Ativa: Sistema alimentado com {len(st.session_state['df_rota_ativa'])} linhas. Pode navegar livremente pelas outras páginas.")
    with st.expander("🔍 Visualizar Amostra dos Dados Carregados"):
        st.dataframe(st.session_state['df_rota_ativa'].head(10), use_container_width=True)
else:
    st.warning("⚠️ Nenhuma rota carregada no momento. Por favor, faça o upload dos arquivos acima.")
