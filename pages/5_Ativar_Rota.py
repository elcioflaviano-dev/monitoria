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

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_master = st.session_state.get('df_rota_ativa', None)

df_ativar = None
if df_master is not None and not df_master.empty:
    # Cria uma cópia isolada para trabalhar
    df_temp = df_master.copy()
    
    # Identificação dinâmica das colunas conforme o arquivo enviado
    col_tipo = 'Tipo de Atividade' if 'Tipo de Atividade' in df_temp.columns else ('Tipo de A' if 'Tipo de A' in df_temp.columns else 'TIPO_ATIVIDADE_COL')
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_temp.columns else ('Status da' if 'Status da' in df_temp.columns else 'Status da Atividade')
    
    # Se não achou pelos nomes aproximados, caça por índice ou palavra-chave
    if col_tipo not in df_temp.columns:
        for c in df_temp.columns:
            if 'TIPO DE A' in str(c).upper() or 'TIPO ATIV' in str(c).upper(): col_tipo = c; break
            
    if col_status not in df_temp.columns:
        for c in df_temp.columns:
            if 'STATUS DA' in str(c).upper() or 'STATUS_AT' in str(c).upper(): col_status = c; break

    # Extrai as colunas brutas em formato de texto limpo
    lista_recurso = [str(x).strip() for x in pd.DataFrame(df_temp['Recurso']).iloc[:, 0].fillna('N/A').tolist()] if 'Recurso' in df_temp.columns else ['N/A'] * len(df_temp)
    lista_supervisor = [str(x).upper().strip() for x in pd.DataFrame(df_temp['SUPERVISOR']).iloc[:, 0].fillna('').tolist()] if 'SUPERVISOR' in df_temp.columns else [''] * len(df_temp)
    lista_tipo_ativ = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_tipo]).iloc[:, 0].fillna('').tolist()] if col_tipo in df_temp.columns else [''] * len(df_temp)
    lista_status_at = [str(x).upper().strip() for x in pd.DataFrame(df_temp[col_status]).iloc[:, 0].fillna('').tolist()] if col_status in df_temp.columns else [''] * len(df_temp)

    # Monta o esqueleto inicial
    df_ativar = pd.DataFrame({
        'Recurso_Original': lista_recurso,
        'SUPERVISOR_ORIGINAL': lista_supervisor,
        'Tipo_Atividade_Upper': lista_tipo_ativ,
        'Status_Conclusao_Upper': lista_status_at
    })
    
    # 🌟 PASSO MÁSTER (PROCV INTERNO): Mapeia o supervisor real de cada técnico usando as linhas preenchidas
    df_mapeamento_sup = df_ativar[
        (df_ativar['SUPERVISOR_ORIGINAL'] != '') & 
        (~df_ativar['SUPERVISOR_ORIGINAL'].isin(['N/A', 'NAN', '#N/A']))
    ].groupby('Recurso_Original')['SUPERVISOR_ORIGINAL'].first().reset_index(name='SUPERVISOR_VALIDO')
    
    # Cruza de volta para preencher as linhas vazias do "Na Base"
    df_ativar = pd.merge(df_ativar, df_mapeamento_sup, on='Recurso_Original', how='left')
    df_ativar['SUPERVISOR'] = df_ativar['SUPERVISOR_VALIDO'].fillna(df_ativar['SUPERVISOR_ORIGINAL']).str.upper().str.strip()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
if df_ativar is not None:
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada com PROCV interno de Supervisor ativo</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 13px; font-weight: bold; margin-bottom: 20px;">⚠️ Aguardando upload dos arquivos na página inicial</div>', unsafe_allow_html=True)

# Layout de cor para a linha de totalizador
def destacar_linha_total(row):
    try:
        if "TOTAL" in str(row.iloc[0]).upper():
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except:
        pass
    return [''] * len(row)

# --- PROCESSAMENTO DOS FILTROS OPERACIONAIS ---
if df_ativar is not None and not df_ativar.empty:
    
    # 1. Filtra apenas as linhas que contêm "BASE" no tipo de atividade
    df_filtrado = df_ativar[df_ativar['Tipo_Atividade_Upper'].str.contains("BASE", na=False)].copy()
    
    # 2. Remove supervisores inválidos ou nulos após o cruzamento do PROCV
    df_filtrado = df_filtrado[
        (~df_filtrado['SUPERVISOR'].isin(['#N/A', 'N/A', '', 'NAN', 'NAN', None])) & 
        (df_filtrado['SUPERVISOR'].notna())
    ].copy()
    
    # 3. Filtra estritamente o que está com status PENDENTE na largada
    df_pendentes_na_base = df_filtrado[df_filtrado['Status_Conclusao_Upper'].str.contains("PEND", na=False)].copy()
    
    # Agrupa e gera a listagem limpa por Supervisor e Técnico
    if not df_pendentes_na_base.empty:
        df_lista = df_pendentes_na_base.groupby(['SUPERVISOR', 'Recurso_Original']).size().reset_index()
        df_lista = df_lista.rename(columns={'SUPERVISOR': 'Supervisor', 'Recurso_Original': 'Técnico Pendente'})
        df_lista = df_lista[['Supervisor', 'Técnico Pendente']]
        
        # Filtro antiferrugem contra lixo de string
        df_lista = df_lista[(df_lista['Técnico Pendente'] != 'N/A') & (df_lista['Técnico Pendente'] != '') & (df_lista['Técnico Pendente'].str.upper() != 'NAN')]
    else:
        df_lista = pd.DataFrame(columns=['Supervisor', 'Técnico Pendente'])

    # Divisão Regional Padrão (Francisco/Alan = SP, o restante é ABC)
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
