import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# CSS DE LIMPEZA
st.markdown("""
    <style>
    [data-testid="stHeader"], .stDeployButton, footer, #MainMenu, [data-testid="stSidebar"] { visibility: hidden !important; }
    .stApp { background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

# LISTAS DE SEGURANÇA (Mantenha as suas listas aqui)
LISTA_SP_FIXA = [...] # Mantenha a sua lista original aqui
LISTA_ABC_FIXA = [...] # Mantenha a sua lista original aqui

# Inicializa estados
if "novos_sp" not in st.session_state: st.session_state["novos_sp"] = []
if "novos_abc" not in st.session_state: st.session_state["novos_abc"] = []

ARQUIVO_ROTA = "rota_sincronizada.csv"

# LÓGICA PRINCIPAL: Lê o arquivo diretamente
if os.path.exists(ARQUIVO_ROTA):
    df = pd.read_csv(ARQUIVO_ROTA, dtype=str)
    df.columns = df.columns.str.strip().str.upper()

    # Busca automática das colunas (Procura termos chave)
    col_recurso = next((c for c in df.columns if any(x in c for x in ['RECURSO', 'NOME', 'TÉCN'])), df.columns[0])
    col_tipo = next((c for c in df.columns if 'TIPO' in c), None)
    col_status = next((c for c in df.columns if 'STATUS' in c), None)

    if col_tipo and col_status:
        # Filtro Inteligente: "BASE" no tipo E ("PEND" ou "ABERTO") no status
        df['TIPO_X'] = df[col_tipo].fillna('').astype(str).str.upper()
        df['STAT_X'] = df[col_status].fillna('').astype(str).str.upper()
        
        df_tela = df[
            df['TIPO_X'].str.contains('BASE', na=False) & 
            df['STAT_X'].str.contains('PEND|ABERTO', na=False)
        ].copy()

        # Normaliza nomes
        nomes_na_base = [str(n).strip().upper() for n in df_tela[col_recurso].unique() if pd.notna(n)]
        
        # Consolida listas
        lista_sp = [n.upper() for n in LISTA_SP_FIXA] + [n.upper() for n in st.session_state["novos_sp"]]
        lista_abc = [n.upper() for n in LISTA_ABC_FIXA] + [n.upper() for n in st.session_state["novos_abc"]]

        nomes_abc = [n for n in nomes_na_base if n in lista_abc or n not in lista_sp]
        nomes_sp = [n for n in nomes_na_base if n in lista_sp]

        # Exibição
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        def exibir_lista(lista, col, titulo):
            with col:
                st.markdown(f'### {titulo}')
                for n in lista: st.markdown(f'🏃‍♂️ **{n}** ⏳ PENDENTE')

        meio_abc = (len(nomes_abc) + 1) // 2
        meio_sp = (len(nomes_sp) + 1) // 2
        
        exibir_lista(nomes_abc[:meio_abc], c1, "🏢 ABC (1/2)")
        exibir_lista(nomes_abc[meio_abc:], c2, "🏢 ABC (2/2)")
        exibir_lista(nomes_sp[:meio_sp], c3, "🏙️ SP (1/2)")
        exibir_lista(nomes_sp[meio_sp:], c4, "🏙️ SP (2/2)")

        # Inclusão Manual
        with st.expander("➕ Incluir Novo Técnico"):
            c_a, c_b, c_c = st.columns([2, 1, 1])
            nome_i = c_a.text_input("Nome:").upper()
            base_i = c_b.selectbox("Base:", ["SP", "ABC"])
            if c_c.button("Adicionar"):
                if nome_i:
                    if base_i == "SP": st.session_state["novos_sp"].append(nome_i)
                    else: st.session_state["novos_abc"].append(nome_i)
                    st.rerun()
    else:
        st.error(f"Erro: Colunas não encontradas. Verifique o seu CSV. Colunas: {list(df.columns)}")
else:
    st.error("⚠️ Ficheiro 'rota_sincronizada.csv' não encontrado.")
