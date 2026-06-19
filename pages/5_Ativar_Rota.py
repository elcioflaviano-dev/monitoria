import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA DA INTERFACE
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

URL_COMPILADO = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

@st.cache_data(ttl=300)
def carregar_bases():
    mapa = {}
    try:
        df_comp = pd.read_csv(URL_COMPILADO, dtype=str)
        df_comp.columns = [str(c).strip().upper() for c in df_comp.columns]
        
        # Busca dinâmica das colunas, independente do nome original
        col_nome = next((c for c in df_comp.columns if any(x in c for x in ['NOME', 'RECURSO', 'TÉCN', 'TECN'])), None)
        col_base = next((c for c in df_comp.columns if any(x in c for x in ['BASE', 'POLO', 'LOCAL'])), None)
        
        if col_nome and col_base:
            for _, row in df_comp.iterrows():
                nome = str(row[col_nome]).strip().upper()
                base = str(row[col_base]).strip().upper()
                if nome and nome != 'NAN': mapa[nome] = base
    except: pass
    return mapa

mapa_bases = carregar_bases()
ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    # Limpeza total dos dados
    df.columns = [str(c).strip().upper() for c in df.columns]
    
    # Identifica colunas automaticamente
    col_recurso = next((c for c in df.columns if any(x in c for x in ['RECURSO', 'NOME', 'TÉCN'])), df.columns[0])
    col_tipo = next((c for c in df.columns if 'TIPO' in c), None)
    col_status = next((c for c in df.columns if 'STATUS' in c), None)

    if col_tipo and col_status:
        # Normalização para filtro
        df['TIPO_NORM'] = df[col_tipo].fillna('').astype(str).str.strip().str.upper()
        df['STATUS_NORM'] = df[col_status].fillna('').astype(str).str.strip().str.upper()
        
        # Filtro: Contém 'BASE' E (Pendente OU Aberto)
        df_tela = df[
            df['TIPO_NORM'].str.contains('BASE', na=False) & 
            df['STATUS_NORM'].str.contains('PEND|ABERTO', na=False)
        ].copy()

        lista_abc = []
        lista_sp = []

        for _, row in df_tela.iterrows():
            nome = str(row[col_recurso]).strip().upper()
            base_tecnico = mapa_bases.get(nome, "SP").upper() # Default SP
            display_text = f"🏃‍♂️ **{nome}** ⏳"
            
            if "ABC" in base_tecnico: lista_abc.append(display_text)
            else: lista_sp.append(display_text)

        lista_abc = sorted(list(set(lista_abc)))
        lista_sp = sorted(list(set(lista_sp)))
        
        total = len(lista_abc) + len(lista_sp)
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {total}</h4>", unsafe_allow_html=True)
        st.divider()

        if total > 0:
            c1, c2, c3, c4 = st.columns(4)
            # Exibir ABC
            with c1:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (1/2)</h3>', unsafe_allow_html=True)
                for n in lista_abc[:(len(lista_abc)+1)//2]: st.markdown(n)
            with c2:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (2/2)</h3>', unsafe_allow_html=True)
                for n in lista_abc[(len(lista_abc)+1)//2:]: st.markdown(n)
            # Exibir SP
            with c3:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (1/2)</h3>', unsafe_allow_html=True)
                for n in lista_sp[:(len(lista_sp)+1)//2]: st.markdown(n)
            with c4:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (2/2)</h3>', unsafe_allow_html=True)
                for n in lista_sp[(len(lista_sp)+1)//2:]: st.markdown(n)
        else:
            st.success("✅ Nenhum técnico pendente na base no momento!")
    else:
        st.warning(f"⚠️ Colunas não encontradas. Colunas no arquivo: {list(df.columns)}")
else:
    st.error("⚠️ 'rota_sincronizada.csv' não encontrado. Verifique se o arquivo existe.")
