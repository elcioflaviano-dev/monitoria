import streamlit as st
import time
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)

# 1. MÁGICA: O Python olha a pasta 'pages' e pega o nome EXATO dos arquivos que estão lá
try:
    arquivos_na_pasta = os.listdir("pages")
    
    # Filtra para pegar apenas os arquivos .py e ignora o próprio Painel_Rotativo
    paginas = [f for f in arquivos_na_pasta if f.endswith(".py") and f != "Painel_Rotativo.py"]
    paginas.sort() # Organiza em ordem alfabética
    
except FileNotFoundError:
    st.error("❌ A pasta 'pages' não foi encontrada pelo sistema.")
    st.stop()

# Se não achou nenhum arquivo .py
if not paginas:
    st.error("❌ A pasta 'pages' está vazia ou não contém os arquivos dos supervisores.")
    st.write("Arquivos que o sistema está enxergando nesta pasta:", arquivos_na_pasta)
    st.stop()

# 2. Lógica de controle de tempo e alternância
if "idx" not in st.session_state:
    st.session_state.idx = 0

# Tempo que cada supervisor fica na tela (ex: 5 segundos)
time.sleep(5)

# Avança para o próximo da lista que ele encontrou
st.session_state.idx = (st.session_state.idx + 1) % len(paginas)

# 3. Monta o caminho perfeito e troca a página
arquivo_destino = f"pages/{paginas[st.session_state.idx]}"

try:
    st.switch_page(arquivo_destino)
except Exception as e:
    st.error(f"⚠️ Erro ao tentar abrir a página {arquivo_destino}. Detalhe: {e}")
