import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">🚀 ATIVAR ROTA - LARGADA MATINAL</h1>', unsafe_allow_html=True)

# 🌟 HERANÇA INTELIGENTE: Substitui o download antigo pelos dados reais do Upload da Home
df_master = st.session_state.get('df_rota_ativa', None)

df_ativar = None
if df_master is not None and not df_master.empty:
    df_ativar = df_master.copy()
    
    # Faz o mapeamento e alinhamento das chaves operacionais que o código original precisa
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_ativar.columns else 'TIPO_ATIVIDADE_COL'
    if col_tipo in df_ativar.columns:
        df_ativar['TIPO_ATIVIDADE_COL'] = df_ativar[col_tipo]
        
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_ativar.columns else 'Status da Atividade'
    if col_status in df_ativar.columns:
        df_ativar['STATUS_CONCLUSAO_COL'] = df_ativar[col_status]

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em tempo real via Upload de hoje</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

# 🛠️ Injetora de layout de cor para a linha de resumo consolidado
def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except:
        pass
    return [''] * len(row)

# --- CORPO PRINCIPAL DO FILTRO ---
if df_ativar is not None and not df_ativar.empty:
    
    # Padronização e higienização das strings para evitar falsos positivos
    df_ativar['Supervisor_Clean'] = df_ativar['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_ativar['Recurso_Original'] = df_ativar['Recurso'].fillna('N/A').astype(str).str.strip()
    
    if 'TIPO_ATIVIDADE_COL' in df_ativar.columns:
        df_ativar['Tipo_Atividade_Upper'] = df_ativar['TIPO_ATIVIDADE_COL'].fillna('').astype(str).str.upper().str.strip()
    else:
        df_ativar['Tipo_Atividade_Upper'] = ''
        
    if 'STATUS_CONCLUSAO_COL' in df_ativar.columns:
        df_ativar['Status_Conclusao_Upper'] = df_ativar['STATUS_CONCLUSAO_COL'].fillna('').astype(str).str.upper().str.strip()
    else:
        df_ativar['Status_Conclusao_Upper'] = ''

    # 🌟 APLICAÇÃO DOS FILTROS OPERACIONAIS DE LIMPEZA
    
    # 1. Filtra apenas as linhas que são "NA BASE"
    df_filtrado = df_ativar[df_ativar['Tipo_Atividade_Upper'] == "NA BASE"].copy()
    
    # 2. LIMPEZA 1: Ignora se o Supervisor for #N/A, N/A, em branco ou nulo
    df_filtrado = df_filtrado[
        (~df_filtrado['Supervisor_Clean'].isin(['#N/A', 'N/A', '', 'NAN'])) & 
        (df_filtrado['SUPERVISOR'].notna())
    ].copy()
    
    # 3. LIMPEZA 2: Remove da contagem quem estiver com status "SUSPENSO"
    df_filtrado = df_filtrado[df_filtrado['Status_Conclusao_Upper'] != "SUSPENSO"].copy()
    
    # 4. Mantém na lista apenas quem continua com o status como "PENDENTE"
    df_pendentes_na_base = df_filtrado[df_filtrado['Status_Conclusao_Upper'] == "PENDENTE"].copy()
    
    # Agrupa para consolidar a listagem por Supervisor e Técnico único
    df_lista = df_pendentes_na_base.groupby(['SUPERVISOR', 'Recurso_Original']).size().reset_index()
    df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Recurso_Original': 'Técnico Pendente'})
    df_lista = df_lista[['Supervisor', 'Técnico Pendente']]
    
    # Garante que não suba técnico fantasma ou nulo
    df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'] != '')]

    # Divisão Regional (Padrão Francisco/Alan para SP, restante ABC)
    df_sp = df_lista[df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc = df_lista[~df_lista['Supervisor'].fillna('').str.upper().str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 SEÇÃO ABC
    # ==========================================
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 PENDENTES DO "NA BASE" - REGIÃO ABC</h2></div>', unsafe_allow_html=True)
    
    if not df_abc.empty:
        st.dataframe(df_abc, use_container_width=True, hide_index=True)
        
        tot_tecs_abc = df_abc['Técnico Pendente'].nunique()
        df_tot_abc = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Técnico Pendente": f"{tot_tecs_abc} Técnicos sem ativação"}])
        st.dataframe(df_tot_abc.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
    else:
        st.success("✅ 100% da equipe ABC realizou a largada do 'Na Base'!")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # 🔵 SEÇÃO SÃO PAULO (SP)
    # ==========================================
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 PENDENTES DO "NA BASE" - REGIÃO SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
    
    if not df_sp.empty:
        st.dataframe(df_sp, use_container_width=True, hide_index=True)
        
        tot_tecs_sp = df_sp['Técnico Pendente'].nunique()
        df_tot_sp = pd.DataFrame([{"Supervisor": "TOTAL PENDENTE", "Técnico Pendente": f"{tot_tecs_sp} Técnicos sem ativação"}])
        st.dataframe(df_tot_sp.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
    else:
        st.success("✅ 100% da equipe SP realizou a largada do 'Na Base'!")

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
