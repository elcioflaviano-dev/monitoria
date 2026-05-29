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

# 🔄 HERANÇA INTELIGENTE
df_master = st.session_state.get('df_rota_ativa', None)

df_ativar = None
if df_master is not None and not df_master.empty:
    # 🌟 EXTRAÇÃO BLINDADA: Garante a captura isolada das colunas mesmo se houver duplicidade no Excel
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_master.columns else 'TIPO_ATIVIDADE_COL'
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_master.columns else 'Status da Atividade'
    
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_master['SUPERVISOR']).iloc[:, 0].fillna('N/A').tolist()] if 'SUPERVISOR' in df_master.columns else ['N/A'] * len(df_master)
    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_master['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_master.columns else ['N/A'] * len(df_master)
    
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_tipo]).iloc[:, 0].fillna('').tolist()] if col_tipo in df_master.columns else [''] * len(df_master)
    lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_master[col_status]).iloc[:, 0].fillna('').tolist()] if col_status in df_master.columns else [''] * len(df_master)

    # Reconstrói a base limpa para a tela de largada
    df_ativar = pd.DataFrame({
        'SUPERVISOR': lista_supervisor,
        'Recurso_Original': lista_recurso,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at
    })

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
    
    # 🌟 CORREÇÃO MÁSTER DO FILTRO: Captura "NA BASE" ou "BASE" de forma flexível e tolerante a falhas
    cond_tipo_base = df_ativar['Tipo_Activity_Upper'].str.contains("BASE", na=False) if 'Tipo_Activity_Upper' in df_ativar.columns else df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)
    
    df_filtrado = df_ativar[cond_tipo_base].copy()
    
    # Limpeza de supervisores inválidos ou nulos
    df_filtrado = df_filtrado[
        (~df_filtrado['SUPERVISOR'].isin(['#N/A', 'N/A', '', 'NAN', 'NAN', None])) & 
        (df_filtrado['SUPERVISOR'].notna())
    ].copy()
    
    # Remove suspensos da contagem
    df_filtrado = df_filtrado[df_filtrado['Status_Conclusao_Upper'] != "SUSPENSO"].copy()
    
    # 🌟 AJUSTE DE CAPTURA DE PENDENTES: Considera "PENDENTE" ou o status vazio/inicial sem travar a largada
    cond_pendente = (
        df_filtrado['Status_Conclusao_Upper'].str.contains("PEND", na=False) | 
        (df_filtrado['Status_Conclusao_Upper'] == "")
    )
    df_pendentes_na_base = df_filtrado[cond_pendente].copy()
    
    # Agrupa para consolidar a listagem por Supervisor e Técnico único
    if not df_pendentes_na_base.empty:
        df_lista = df_pendentes_na_base.groupby(['SUPERVISOR', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Técnico Pendente']]
        
        # Garante que não suba técnico fantasma ou nulo
        df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'] != '') & (df_lista['Técnico Pendente'] != 'NAN')]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Técnico Pendente'])

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
