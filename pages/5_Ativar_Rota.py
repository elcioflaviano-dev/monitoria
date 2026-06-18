import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# CSS PARA LIMPEZA DA INTERFACE (MENU LATERAL MANTIDO VISÍVEL)
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color: #008080; text-align: center;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if os.path.exists(ARQUIVO_ROTA_DISCO):
    df = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🔍 BUSCA DINÂMICA DAS COLUNAS (Sem depender de nomes cravados)
    col_tipo = next((c for c in df.columns if 'TIPO' in c.upper() and 'ATIV' in c.upper() and df[c].astype(str).str.contains('BASE', case=False, na=False).any()), None)
    if not col_tipo:
        col_tipo = 'Tipo de Atividade.1' if 'Tipo de Atividade.1' in df.columns else ('Tipo de Atividade' if 'Tipo de Atividade' in df.columns else None)

    col_status = next((c for c in df.columns if 'STATUS' in c.upper()), None)
    col_recurso = 'Recurso' if 'Recurso' in df.columns else df.columns[0]

    if col_tipo and col_status and col_recurso:
        
        # 🎯 FILTRO DIRETO NO EXCEL: "BASE" e "PENDENTE/ABERTO"
        filtro_base = df[col_tipo].astype(str).str.contains('BASE', na=False, case=False)
        filtro_pendente = df[col_status].astype(str).str.contains('PEND|ABERTO', na=False, case=False)
        
        df_tela = df[filtro_base & filtro_pendente].copy()

        # 👤 EXTRAÇÃO EXCLUSIVA DA COLUNA RECURSO (Sem listas fixas)
        nomes_na_base = sorted(df_tela[col_recurso].dropna().astype(str).str.strip().unique().tolist())
        total_tecnicos = len(nomes_na_base)
        
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total de Pendências: {total_tecnicos}</h4>", unsafe_allow_html=True)
        st.divider()

        if total_tecnicos > 0:
            c1, c2, c3, c4 = st.columns(4)
            
            # Matemática para dividir a lista automaticamente em 4 colunas iguais
            tamanho_bloco = (total_tecnicos + 3) // 4
            blocos = [nomes_na_base[i:i + tamanho_bloco] for i in range(0, total_tecnicos, tamanho_bloco)]
            while len(blocos) < 4: blocos.append([]) # Garante que não dá erro se houver poucos técnicos

            with c1:
                for n in blocos[0]: st.markdown(f'🏃‍♂️ **{n}**')
            with c2:
                for n in blocos[1]: st.markdown(f'🏃‍♂️ **{n}**')
            with c3:
                for n in blocos[2]: st.markdown(f'🏃‍♂️ **{n}**')
            with c4:
                for n in blocos[3]: st.markdown(f'🏃‍♂️ **{n}**')
        else:
            st.success("✅ Nenhum técnico pendente na base no momento!")
            
    else:
        st.warning("⚠️ Colunas 'Tipo de Atividade', 'Status' ou 'Recurso' não encontradas no Excel.")
else:
    st.error("⚠️ Ficheiro rota_sincronizada.csv não encontrado. Aguarde a sincronização.")
