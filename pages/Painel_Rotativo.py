import streamlit as st
import time

# Lista de caminhos para as páginas (devem ser os nomes dos arquivos na pasta pages)
paginas = ["1_Maicon", "2_Nelson", "3_Marcos_Roberto", "4_Alan", "5_Francisco", "6_Hora"]

if "idx" not in st.session_state:
    st.session_state.idx = 0

# Tempo de exibição (5 segundos por supervisor)
time.sleep(5)

# Alterna para a próxima página
st.session_state.idx = (st.session_state.idx + 1) % len(paginas)
st.switch_page(f"pages/{paginas[st.session_state.idx]}.py")
