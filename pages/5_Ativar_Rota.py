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
    # Remove espaços invisíveis dos nomes das colunas (Ex: " Recurso " vira "Recurso")
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🔍 BUSCA DINÂMICA SEGURA (Procura qualquer coluna com TIPO ou STATUS)
    col_tipos = [c for c in df.columns if 'TIPO' in str(c).upper()]
    col_status = [c for c in df.columns if 'STATUS' in str(c).upper()]
    col_recurso = 'Recurso' if 'Recurso' in df.columns else df.columns[0]

    if col_tipos and col_status:
        # Concatena todos os valores de "Tipo" (Tipo de Atividade, Tipo de Atividade_2, etc) manual e seguramente
        df['BUSCA_TIPO'] = ""
        for c in col_tipos:
            df['BUSCA_TIPO'] += df[c].fillna('').astype(str).str.upper() + " "
            
        # Concatena todos os Status
        df['BUSCA_STATUS'] = ""
        for c in col_status:
            df['BUSCA_STATUS'] += df[c].fillna('').astype(str).str.upper() + " "
        
        # 🎯 FILTRO EXATO: Tem "BASE" no tipo e "PEND", "ABERTO" ou "CONCLU" no status
        filtro_base = df['BUSCA_TIPO'].str.contains('BASE', na=False)
        filtro_status = df['BUSCA_STATUS'].str.contains('PEND|ABERTO|CONCLU', na=False)
        
        df_tela = df[filtro_base & filtro_status].copy()

        # 👤 EXTRAÇÃO DE TÉCNICOS COM AVISO DE STATUS
        tecnicos_display = []
        for _, row in df_tela.iterrows():
            nome = str(row[col_recurso]).strip().upper()
            status_texto = str(row['BUSCA_STATUS']).strip()
            
            if 'CONCLU' in status_texto:
                badge = "✅ CONCLUÍDO"
            else:
                badge = "⏳ PENDENTE"
                
            tecnicos_display.append(f"{nome} ({badge})")

        # Remove nomes duplicados e ordena em ordem alfabética
        tecnicos_display = sorted(list(set(tecnicos_display)))
        total_tecnicos = len(tecnicos_display)
        
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {total_tecnicos}</h4>", unsafe_allow_html=True)
        st.divider()

        if total_tecnicos > 0:
            c1, c2, c3, c4 = st.columns(4)
            
            # Matemática para dividir a lista em 4 blocos de tamanho igual
            tamanho_bloco = (total_tecnicos + 3) // 4
            blocos = [tecnicos_display[i:i + tamanho_bloco] for i in range(0, total_tecnicos, tamanho_bloco)]
            while len(blocos) < 4: blocos.append([]) 

            with c1:
                for n in blocos[0]: st.markdown(f'🏃‍♂️ **{n}**')
            with c2:
                for n in blocos[1]: st.markdown(f'🏃‍♂️ **{n}**')
            with c3:
                for n in blocos[2]: st.markdown(f'🏃‍♂️ **{n}**')
            with c4:
                for n in blocos[3]: st.markdown(f'🏃‍♂️ **{n}**')
        else:
            st.success("✅ Nenhum técnico pendente ou concluído na base no momento!")
            
    else:
        # Se falhar, diz-nos exatamente o nome que o Excel deu às colunas para podermos corrigir
        st.warning(f"⚠️ Colunas não encontradas. Colunas lidas do arquivo: {', '.join(df.columns)}")
else:
    st.error("⚠️ Ficheiro rota_sincronizada.csv não encontrado. Aguarde a sincronização.")
