import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# CONFIGURAÇÕES
# Se o link der erro de acesso, baixe o arquivo para a pasta do projeto e troque o link pelo nome do arquivo (ex: "base_tecnicos.xlsx")
URL_EXCEL = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 1. CARREGAR MAPA DE BASES DO EXCEL
@st.cache_data(ttl=600)
def carregar_mapa_bases():
    try:
        # Tenta ler o arquivo Excel
        df = pd.read_excel(URL_EXCEL, engine='openpyxl')
        df.columns = df.columns.str.strip() # Remove espaços nos nomes das colunas
        
        # Cria dicionário Técnico -> Base
        # Garantindo que os nomes estejam em maiúsculo para comparação
        return dict(zip(df['Técnico'].str.strip().str.upper(), df['Base'].str.strip().str.upper()))
    except Exception as e:
        st.error(f"Erro ao ler o arquivo Excel: {e}. Verifique se o link está público ou se o arquivo está na pasta.")
        return {}

mapa_bases = carregar_mapa_bases()

# 2. PROCESSAR TÉCNICOS NO CSV
if os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        df.columns = df.columns.str.strip() # Remove espaços nos nomes das colunas
        
        # Filtragem solicitada
        # Tipo de Atividade3 == "Na Base"
        # Status da Atividade == "pendente"
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
            
            # Busca a base no dicionário gerado do Excel
            # Se não encontrar, assume que é SP (Leste)
            base_tecnico = mapa_bases.get(nome_clean, "LESTE") 
            
            if "ABC" in str(base_tecnico).upper():
                lista_abc.append(nome_clean)
            else:
                lista_sp.append(nome_clean)
        
        # Exibição
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
        st.divider()
        
        c1, c2, c3, c4 = st.columns(4)
        
        # Exibe ABC
        with c1:
            st.markdown('### 🏢 ABC (1/2)')
            for n in sorted(lista_abc[:(len(lista_abc)+1)//2]): st.markdown(f'🏃‍♂️ {n}')
        with c2:
            st.markdown('### 🏢 ABC (2/2)')
            for n in sorted(lista_abc[(len(lista_abc)+1)//2:]): st.markdown(f'🏃‍♂️ {n}')
            
        # Exibe SP
        with c3:
            st.markdown('### 🏙️ SP (1/2)')
            for n in sorted(lista_sp[:(len(lista_sp)+1)//2]): st.markdown(f'🏃‍♂️ {n}')
        with c4:
            st.markdown('### 🏙️ SP (2/2)')
            for n in sorted(lista_sp[(len(lista_sp)+1)//2:]): st.markdown(f'🏃‍♂️ {n}')
        
        if len(nomes_na_base) == 0:
            st.info("✅ Todos os técnicos estão em atividade. Nenhum pendente na base.")

    except KeyError as e:
        st.error(f"Erro: A coluna {e} não foi encontrada no CSV. Verifique se os nomes das colunas no arquivo CSV são exatamente: 'Recurso', 'Tipo de Atividade3' e 'Status da Atividade'.")
        st.write("Colunas detectadas no CSV:", list(df.columns))
else:
    st.error(f"⚠️ O arquivo '{ARQUIVO_ROTA_DISCO}' não foi encontrado na pasta do projeto.")
