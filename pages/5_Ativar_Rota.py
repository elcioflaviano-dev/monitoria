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
    
    # 🔍 BUSCA DINÂMICA DAS COLUNAS (Lê todas as colunas de Tipo e Status)
    col_tipos = [c for c in df.columns if 'TIPO' in str(c).upper() and 'ATIV' in str(c).upper()]
    col_status = next((c for c in df.columns if 'STATUS' in str(c).upper()), None)
    col_recurso = 'Recurso' if 'Recurso' in df.columns else df.columns[0]

    if col_tipos and col_status and col_recurso:
        
        # Junta o texto de todas as colunas de "Tipo" (pega o Tipo_1, Tipo_2, etc)
        df['BUSCA_TIPO'] = df[col_tipos].fillna('').astype(str).agg(' '.join, axis=1).str.upper()
        df['BUSCA_STATUS'] = df[col_status].fillna('').astype(str).str.upper()
        
        # 🎯 FILTRO EXATO: Tem "BASE" e o status é "PENDENTE" ou "CONCLUÍDO"
        filtro_base = df['BUSCA_TIPO'].str.contains('BASE', na=False)
        filtro_status = df['BUSCA_STATUS'].str.contains('PEND|ABERTO|CONCLU', na=False)
        
        df_tela = df[filtro_base & filtro_status].copy()

        # 👤 EXTRAÇÃO COM AVISO VISUAL DE STATUS
        tecnicos_display = []
        for _, row in df_tela.iterrows():
            nome = str(row[col_recurso]).strip().upper()
            status_real = str(row[col_status]).strip().upper()
            
            # Adiciona uma tag visual ao lado do nome
            if 'CONCLU' in status_real:
                badge = "✅ CONCLUÍDO"
            else:
                badge = "⏳ PENDENTE"
                
            tecnicos_display.append(f"{nome} ({badge})")

        # Remove duplicados e ordena alfabeticamente
        tecnicos_display = sorted(list(set(tecnicos_display)))
        total_tecnicos = len(tecnicos_display)
        
        st.markdown(f"<h4 style='text-align: center; color: #555;'>Total na Base: {total_tecnicos}</h4>", unsafe_allow_html=True)
        st.divider()

        if total_tecnicos > 0:
            c1, c2, c3, c4 = st.columns(4)
            
            # Divide a lista em 4 blocos iguais
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
        st.warning("⚠️ Colunas 'Tipo de Atividade', 'Status da Atividade' ou 'Recurso' não encontradas no Excel.")
else:
    st.error("⚠️ Ficheiro rota_sincronizada.csv não encontrado. Aguarde a sincronização.")
