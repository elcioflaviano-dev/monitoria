import streamlit as st
import time
import os

# Configuração básica para esconder o menu
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid="stSidebar"] { display: none !important; }</style>""", unsafe_allow_html=True)

# Lista com os nomes dos arquivos EXATAMENTE como estão na pasta pages/ (SEM o .py)
paginas = [
    "Maicon", 
    "Nelson", 
    "Marcos", 
    "Alan", 
    "Francisco", 
    "Hora"
]

if "idx" not in st.session_state:
    st.session_state.idx = 0

# Tempo de exibição
time.sleep(5)

# --- SISTEMA ANTI-TRAVAMENTO ---
# Tenta encontrar a próxima página válida. Se o nome estiver errado, pula para o próximo.
tentativas = 0
while tentativas < len(paginas):
    st.session_state.idx = (st.session_state.idx + 1) % len(paginas)
    
    nome_pagina = paginas[st.session_state.idx]
    caminho_destino = f"pages/{nome_pagina}.py"
    
    # Só tenta mudar de página se o arquivo realmente existir no servidor
    if os.path.exists(caminho_destino):
        st.switch_page(caminho_destino)
        st.stop() # Para a execução aqui
    else:
        # Se não existir, soma uma tentativa e o loop tenta o próximo nome
        tentativas += 1

# Se chegar aqui, nenhum arquivo da lista foi encontrado
st.error("⚠️ ERRO: Nenhuma página da lista foi encontrada na pasta 'pages/'. Verifique se os nomes na lista 'paginas' estão idênticos aos arquivos.")
