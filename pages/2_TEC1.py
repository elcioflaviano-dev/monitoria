import streamlit as st
import pandas as pd

# 1. Configuração da página ampla (Igual ao seu original)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 20px; margin-bottom: 5px;">⏳ TÉCNICOS PENDENTES (TEC1 / TEC 1)</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Monitoramento de profissionais sem equipe vinculada ou pendentes de cadastro</div>', unsafe_allow_html=True)

# 🔄 Puxa o DataFrame do estado da sessão (Memória global do seu app)
df = st.session_state.get('df_rota_ativa', None)

if df is not None and not df.empty:
    # 🌟 CORREÇÃO CIRÚRGICA (Preservando o comportamento do seu backup):
    # Forçamos o astype(str) antes de chamar o .str para que o Pandas nunca mais dê o erro de Attribute
    df['Recurso_Upper'] = df['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df['Supervisor_Upper'] = df['SUPERVISOR'].fillna('#N/A').astype(str).str.upper().str.strip()
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    
    # 📑 Filtros originais do seu layout anterior
    df_bloco = df[
        (df['Supervisor_Upper'] == '#N/A') | 
        (df['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False))
    ].copy()
    
    if not df_bloco.empty:
        if 'QTD_OS_COL' in df_bloco.columns:
            df_bloco['QTD_OS_NUM'] = pd.to_numeric(df_bloco['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
        else:
            df_bloco['QTD_OS_NUM'] = 1
            
        # Agrupamento e exibição idênticos ao seu modelo anterior
        tabela_pendentes = df_bloco.groupby(['REGIAO_BASE', 'Recurso'])['QTD_OS_NUM'].sum().reset_index()
        tabela_pendentes = tabela_pendentes.rename(columns={
            'REGIAO_BASE': 'Base Detectada',
            'Recurso': 'Técnico / Login',
            'QTD_OS_NUM': 'Quantidade O.S'
        }).sort_values(by='Quantidade O.S', ascending=False)
        
        st.dataframe(tabela_pendentes, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 Nenhum técnico pendente (TEC1 ou #N/A) encontrado na rota atual!")
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial primeiro.")
