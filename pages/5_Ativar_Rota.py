import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA OCULTAR MENU E CABEÇALHOS
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# CONFIGURAÇÕES
# Link do seu Excel no SharePoint
URL_EXCEL = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 1. CARREGAR MAPA DE BASES (Excel do SharePoint)
@st.cache_data(ttl=300)
def carregar_mapa_bases():
    try:
        # Usando openpyxl para ler o Excel
        df = pd.read_excel(URL_EXCEL, engine='openpyxl')
        # Limpar espaços nos nomes das colunas
        df.columns = df.columns.str.strip()
        # Dicionário Técnico -> Base
        return dict(zip(df['Técnico'].str.strip().str.upper(), df['Base'].str.strip().str.upper()))
    except Exception as e:
        st.error(f"Erro ao ler Excel do SharePoint: {e}")
        return {}

mapa_bases = carregar_mapa_bases()

# 2. PROCESSAR TÉCNICOS NA BASE (Arquivo CSV local)
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        # Limpar espaços nas colunas do CSV
        df.columns = df.columns.str.strip()
        
        # Filtro:
        # Coluna 'Tipo de Atividade3' == 'Na Base'
        # Coluna 'Status da Atividade' == 'pendente'
        # Coluna 'Recurso' == nome
        filtro = (
            (df['Tipo de Atividade3'].str.strip().str.lower() == 'na base') & 
            (df['Status da Atividade'].str.strip().str.lower() == 'pendente')
        )
        
        df_tela = df[filtro].copy()
        
        # Listas para separação
        lista_abc = []
        lista_sp = []
        
        nomes_na_base = df_tela['Recurso'].dropna().unique()
        
        for nome in nomes_na_base:
            nome_clean = str(nome).strip().upper()
            # Busca a base no dicionário (gerado do Excel)
            base_tecnico = mapa_bases.get(nome_clean, "LESTE") # Default Leste/SP
            
            if "ABC" in base_tecnico.upper():
                lista_abc.append(nome_clean)
            else:
                lista_sp.append(nome_clean)
        
        # Exibição
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
        st.divider()
        
        c1, c2, c3, c4 = st.columns(4)
        def exibir_col(lista, col, titulo):
            with col:
                st.markdown(f'### {titulo}')
                for n in sorted(lista): st.markdown(f'🏃‍♂️ **{n}**')
        
        exibir_col(lista_abc[:(len(lista_abc)+1)//2], c1, "🏢 ABC (1/2)")
        exibir_col(lista_abc[(len(lista_abc)+1)//2:], c2, "🏢 ABC (2/2)")
        exibir_col(lista_sp[:(len(lista_sp)+1)//2], c3, "🏙️ SP (1/2)")
        exibir_col(lista_sp[(len(lista_sp)+1)//2:], c4, "🏙️ SP (2/2)")
        
        if len(nomes_na_base) == 0:
            st.success("✅ Nenhum técnico pendente na base no momento!")

    except KeyError as e:
        st.error(f"Erro de coluna: A coluna {e} não foi encontrada no CSV. Verifique se o nome está exatamente igual.")
        st.write("Colunas detectadas no CSV:", list(df.columns))
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")
