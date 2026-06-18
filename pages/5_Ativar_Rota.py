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

# 🔗 LINK DA ABA COMPILADO (Mude o GID para o número exato da aba Compilado)
URL_COMPILADO = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"

# 🧠 MEMÓRIA CACHE: Lê a planilha a cada 5 minutos para não travar a TV
@st.cache_data(ttl=300)
def carregar_bases():
    mapa = {}
    try:
        df_comp = pd.read_csv(URL_COMPILADO, dtype=str)
        df_comp.columns = [str(c).strip().upper() for c in df_comp.columns]
        
        # Procura dinamicamente as colunas de NOME e BASE
        col_nome = next((c for c in df_comp.columns if 'NOME' in c or 'RECURSO' in c or 'TÉCN' in c or 'TECN' in c), None)
        col_base = next((c for c in df_comp.columns if 'BASE' in c or 'POLO' in c or 'LOCAL' in c), None)
        
        if col_nome and col_base:
            for _, row in df_comp.iterrows():
                nome = str(row[col_nome]).strip().upper()
                base = str(row[col_base]).strip().upper()
                if nome != 'NAN' and base != 'NAN':
                    mapa[nome] = base
    except Exception as e:
        pass # Se falhar, devolve o dicionário vazio e o sistema não quebra
    return mapa

# Carrega o mapa de bases
mapa_bases = carregar_bases()

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    
    col_tipos = [c for c in df.columns if 'TIPO' in str(c).upper()]
    col_status = [c for c in df.columns if 'STATUS' in str(c).upper()]
    col_recurso = 'Recurso' if 'Recurso' in df.columns else df.columns[0]

    if col_tipos and col_status:
        df['BUSCA_TIPO'] = ""
        for c in col_tipos: df['BUSCA_TIPO'] += df[c].fillna('').astype(str).str.upper() + " "
            
        df['BUSCA_STATUS'] = ""
        for c in col_status: df['BUSCA_STATUS'] += df[c].fillna('').astype(str).str.upper() + " "
        
        # Filtro: Base + Pendente/Concluído
        filtro_base = df['BUSCA_TIPO'].str.contains('BASE', na=False)
        filtro_status = df['BUSCA_STATUS'].str.contains('PEND|ABERTO|CONCLU', na=False)
        
        df_tela = df[filtro_base & filtro_status].copy()

        # Listas separadas para o Layout
        lista_abc = []
        lista_sp = []

        for _, row in df_tela.iterrows():
            nome = str(row[col_recurso]).strip().upper()
            status_texto = str(row['BUSCA_STATUS']).strip()
            
            badge = "✅ CONCLUÍDO" if 'CONCLU' in status_texto else "⏳ PENDENTE"
            display_text = f"{nome} ({badge})"
            
            # Cruzamento Inteligente: Pergunta à planilha de qual base o técnico é
            base_do_tecnico = mapa_bases.get(nome, "SP") # Se não achar o nome, joga para SP por padrão
            
            if "ABC" in base_do_tecnico:
                lista_abc.append(display_text)
            else:
                lista_sp.append(display_text)

        # Remove duplicados e ordena
        lista_abc = sorted(list(set(lista_abc)))
        lista_sp = sorted(list(set(lista_sp)))
        
        total_tecnicos = len(lista_abc) + len(lista_sp)
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {total_tecnicos}</h4>", unsafe_allow_html=True)
        st.divider()

        if total_tecnicos > 0:
            c1, c2, c3, c4 = st.columns(4)
            
            # Divide ABC nas colunas 1 e 2
            meio_abc = (len(lista_abc) + 1) // 2
            abc_col1 = lista_abc[:meio_abc]
            abc_col2 = lista_abc[meio_abc:]
            
            # Divide SP nas colunas 3 e 4
            meio_sp = (len(lista_sp) + 1) // 2
            sp_col1 = lista_sp[:meio_sp]
            sp_col2 = lista_sp[meio_sp:]

            with c1:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (1/2)</h3>', unsafe_allow_html=True)
                for n in abc_col1: st.markdown(f'🏃‍♂️ **{n}**')
            with c2:
                st.markdown('<h3 style="color:#008080;">🏢 ABC (2/2)</h3>', unsafe_allow_html=True)
                for n in abc_col2: st.markdown(f'🏃‍♂️ **{n}**')
            with c3:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (1/2)</h3>', unsafe_allow_html=True)
                for n in sp_col1: st.markdown(f'🏃‍♂️ **{n}**')
            with c4:
                st.markdown('<h3 style="color:#c62828;">🏙️ SP (2/2)</h3>', unsafe_allow_html=True)
                for n in sp_col2: st.markdown(f'🏃‍♂️ **{n}**')
        else:
            st.success("✅ Nenhum técnico pendente ou concluído na base no momento!")
            
    else:
        st.warning("⚠️ Colunas não encontradas.")
else:
    st.error("⚠️ Ficheiro rota_sincronizada.csv não encontrado. Aguarde a sincronização.")
