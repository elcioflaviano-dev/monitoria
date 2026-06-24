import streamlit as st
st.title("Diagnóstico de Sistema")
st.write("O código está rodando!")
st.write(f"Hora atual no servidor: {__import__('datetime').datetime.now()}")
