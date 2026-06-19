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

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE: Pega o DF que já está carregado na memória
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    df = st.session_state['df_rota_ativa']
    
    # Garantir nomes de colunas limpos (sem espaços extras)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Verificação de segurança das colunas (para evitar KeyError)
    col_recurso = 'Recurso'
    col_tipo = 'Tipo de Atividade3'
    col_status = 'Status da Atividade'
    
    if col_tipo in df.columns and col_status in df.columns and col_recurso in df.columns:
        # Filtro: Base "Na Base" e Status "pendente"
        filtro = (
            (df[col_tipo].astype(str).str.strip().str.lower() == 'na base') & 
            (df[col_status].astype(str).str.strip().str.lower() == 'pendente')
        )
        
        df_tela = df[filtro].copy()
        nomes_na_base = sorted(df_tela[col_recurso].dropna().unique().tolist())
        
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {len(nomes_na_base)}</h4>", unsafe_allow_html=True)
        st.divider()
        
        # Estrutura de exibição (4 colunas)
        if len(nomes_na_base) > 0:
            c1, c2, c3, c4 = st.columns(4)
            # Simplificação: Divide a lista em 4 partes
            n = len(nomes_na_base)
            part = (n + 3) // 4
            
            for i, col in enumerate([c1, c2, c3, c4]):
                with col:
                    inicio = i * part
                    fim = (i + 1) * part
                    lista_parcial = nomes_na_base[inicio:fim]
                    for nome in lista_parcial:
                        st.markdown(f'🏃‍♂️ **{nome}**')
        else:
            st.success("✅ Nenhum técnico pendente na base no momento!")
            
    else:
        st.error(f"Erro: Colunas não encontradas no arquivo.")
        st.write("Colunas detectadas:", list(df.columns))

else:
    st.error("⚠️ Nenhum dado carregado. Certifique-se de que a página de processamento (ou o Painel) carregou os dados primeiro.")
