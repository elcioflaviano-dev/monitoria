import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA: Puxa o DataFrame unificado da memória global (Home)
df_master = st.session_state.get('df_rota_ativa', None)

st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔍 Modo Diagnóstico Ativado</div>', unsafe_allow_html=True)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === 🛠️ PAINEL DE INFORMAÇÕES DO SEU ARQUIVO ===
    st.header("📋 Diagnóstico do Arquivo Carregado")
    st.write("Abaixo estão as colunas reais que o Pandas encontrou no seu arquivo de upload:")
    st.code(list(df.columns))
    
    st.write("Amostra dos dados carregados (primeiras 3 linhas):")
    st.dataframe(df.head(3))
    
    st.markdown("---")
    
    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df.columns else ('Status da Atividade' if 'Status da Atividade' in df.columns else None)
    
    if col_status:
        df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
    else:
        df['Status_Atividade_Upper'] = ''
        
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Tratamento da Janela
    col_janela = None
    for c in df_limpo.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
            col_janela = c
            break
            
    if col_janela is not None:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        opcoes_janela = sorted(df_limpo['Intervalo_Tratado'].dropna().unique())
        opcoes_janela = [j for j in opcoes_janela if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_limpo.copy()
    else:
        df_tela = df_limpo.copy()

    # CONTAGEM
    df_tela['P_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_tela['R_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
    df_tela['I_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
    
    df_tela = df_tela[(df_tela['P_COUNT'] > 0) | (df_tela['R_COUNT'] > 0) | (df_tela['I_COUNT'] > 0)].copy()

    # Tenta achar supervisor
    col_super_bruto = None
    for c in df_tela.columns:
        if 'SUPERVISOR' in str(c).upper() or 'SUPER' in str(c).upper():
            col_super_bruto = c
            break
            
    if col_super_bruto:
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela[col_super_bruto].fillna('PENDENTE CADASTRO').astype(str).str.upper().str.strip()
    else:
        df_tela['SUPERVISOR_MOSTRAR'] = 'PENDENTE CADASTRO'

    # Separação basica para visualização
    df_abc = df_tela[~df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)].copy()
    df_sp = df_tela[df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)].copy()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Visualização ABC")
        if not df_abc.empty:
            st.write(df_abc.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum())
    with col2:
        st.subheader("Visualização SP")
        if not df_sp.empty:
            st.write(df_sp.groupby('SUPERVISOR_MOSTRAR')[['P_COUNT', 'R_COUNT', 'I_COUNT']].sum())

else:
    st.warning("👈 Por favor, faça o upload dos arquivos na página inicial primeiro.")
