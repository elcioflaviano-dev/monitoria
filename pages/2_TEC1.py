import streamlit as st
import pandas as pd

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 20px; margin-bottom: 5px;">⏳ TÉCNICOS PENDENTES (TEC1 / TEC 1)</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Monitoramento de profissionais sem equipe vinculada ou pendentes de cadastro</div>', unsafe_allow_html=True)

# 🔄 3. HERANÇA INTELIGENTE: Busca os arquivos que você já subiu na página principal (streamlit_app.py)
df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    # Cria uma cópia local segura para trabalhar
    df = df_master.copy()
    
    # Garantia absoluta de tratamento como string nas colunas vitais
    df['Recurso_Upper'] = df['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df['Supervisor_Upper'] = df['SUPERVISOR'].fillna('#N/A').astype(str).str.upper().str.strip()
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    
    # 🌟 FILTRO DA TELA: Captura quem caiu no #N/A (não achou no PROCV) ou quem está marcado como técnico de teste (TEC1)
    df_pendentes = df[
        (df['Supervisor_Upper'] == '#N/A') | 
        (df['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False))
    ].copy()
    
    if not df_pendentes.empty:
        # Padroniza volumes se a coluna de quantidade existir
        if 'QTD_OS_COL' in df_pendentes.columns:
            df_pendentes['QTD_OS_NUM'] = pd.to_numeric(df_pendentes['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
        else:
            df_pendentes['QTD_OS_NUM'] = 1

        st.markdown(f"### ⚠️ Foram localizados **{df_pendentes['Recurso_Upper'].nunique()}** técnicos sem vínculo correto.")
        st.info("💡 Dica: Se o login do técnico estiver aparecendo na lista abaixo, adicione o login e o nome dele na aba 'supervisores' da sua planilha principal do Google Sheets para corrigir automaticamente nos próximos uploads.")
        
        # Consolida o volume de ordens que estão "presas" com esses profissionais
        tabela_exibicao = df_pendentes.groupby(['REGIAO_BASE', 'Recurso'])['QTD_OS_NUM'].sum().reset_index()
        tabela_exibicao = tabela_exibicao.rename(columns={
            'REGIAO_BASE': 'Base Detectada',
            'Recurso': 'Login / Identificação do Técnico',
            'QTD_OS_NUM': 'Quantidade de O.S. na Rota'
        }).sort_values(by='Quantidade de O.S. na Rota', ascending=False)
        
        # Exibe a tabela formatada
        st.dataframe(tabela_exibicao, use_container_width=True, hide_index=True)
        
    else:
        st.success("🎉 Excelente! Todos os técnicos mapeados nos arquivos de rotas possuem supervisores e bases vinculadas corretamente na planilha auxiliar.")
else:
    st.warning("⚠️ Dados da rota ativa não localizados. Por favor, acesse a página inicial (streamlit_app.py) primeiro e faça o upload dos arquivos da rota do dia.")
