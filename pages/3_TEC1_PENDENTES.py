import streamlit as st
import pandas as pd

# 1. Configuração da página ampla (Mantendo o padrão do seu projeto)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 20px; margin-bottom: 5px;">⏳ LISTAGEM DE TÉCNICOS PENDENTES</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Visualização detalhada de profissionais sem supervisor ou identificados como TEC1</div>', unsafe_allow_html=True)

# 🔄 3. HERANÇA INTELIGENTE: Puxa a tabela unificada e tratada da Home (streamlit_app.py)
df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    # Cria uma cópia local segura para trabalhar sem afetar as outras telas
    df = df_master.copy()
    
    # 🌟 CORREÇÃO DO KEYERROR: Garantimos que o Pandas trate os nomes de colunas padronizados da Home
    # Se por acaso a coluna 'SUPERVISOR' não existir, criamos como '#N/A' para evitar o travamento
    if 'SUPERVISOR' not in df.columns:
        df['SUPERVISOR'] = '#N/A'
        
    # Encontra a coluna de recurso/técnico gerada na Home
    col_recurso_reais = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    
    # Tratamento absoluto das strings para o filtro funcionar liso
    df['Recurso_Upper'] = df[col_recurso_reais].fillna('N/A').astype(str).str.upper().str.strip()
    df['Supervisor_Upper'] = df['SUPERVISOR'].fillna('#N/A').astype(str).str.upper().str.strip()
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
    
    # 📑 FILTRO OPERACIONAL DA TELA: Captura quem está sem supervisor (#N/A) ou é técnico de teste (TEC1)
    df_filtrado = df[
        (df['Supervisor_Upper'] == '#N/A') | 
        (df['Supervisor_Upper'] == 'PENDENTE CADASTRO') |
        (df['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False))
    ].copy()
    
    if not df_filtrado.empty:
        # Padroniza volumes se a coluna de quantidade existir
        if 'QTD_OS_COL' in df_filtrado.columns:
            df_filtrado['QTD_OS_NUM'] = pd.to_numeric(df_filtrado['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
        else:
            df_filtrado['QTD_OS_NUM'] = 1

        st.markdown(f"### ⚠️ Foram localizados **{df_filtrado['Recurso_Upper'].nunique()}** técnicos pendentes de amarração.")
        st.info("💡 Dica: Copie o login/nome do técnico listado abaixo e insira na aba 'SUPERVISORES' do seu Google Sheets para vinculá-lo a um supervisor real.")
        
        # Consolida e agrupa a quantidade de ordens abertas presas com esses profissionais
        regiao_col = 'REGIAO_BASE' if 'REGIAO_BASE' in df_filtrado.columns else df_filtrado.columns[0]
        
        tabela_exibicao = df_filtrado.groupby([regiao_col, col_recurso_reais])['QTD_OS_NUM'].sum().reset_index()
        tabela_exibicao = tabela_exibicao.rename(columns={
            regiao_col: 'Região Detectada',
            col_recurso_reais: 'Login / Identificação do Técnico',
            'QTD_OS_NUM': 'Quantidade de O.S.'
        }).sort_values(by='Quantidade de O.S.', ascending=False)
        
        # Exibe a tabela organizada na tela
        st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)
        
    else:
        st.success("🎉 Excelente! Todos os técnicos ativos na rota possuem um supervisor e base vinculados corretamente no Google Sheets.")
else:
    st.warning("👈 Dados da rota ativa não localizados. Por favor, acesse a página inicial (streamlit_app.py) primeiro e faça o upload dos arquivos da rota do dia.")
