import streamlit as st
import pandas as pd
import requests
import io
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

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE ===
def buscar_base_rotas_online():
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += f"&gid={gid}"
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        if resposta.status_code != 200:
            return None
            
        import zoneinfo
        fuso_sp = zoneinfo.ZoneInfo("America/Sao_Paulo")
        st.session_state['data_da_rota_ativar'] = datetime.now(fuso_sp).strftime('%d/%m/%Y às %H:%M:%S')

        conteudo_bruto = resposta.text
        linhas_puras = conteudo_bruto.splitlines()
        
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        for i, texto_linha in enumerate(linhas_puras[:30]):
            linha_upper = texto_linha.upper()
            if 'SUPERVISOR' in linha_upper or 'CONTRATO' in linha_upper or 'INTERVALO' in linha_upper or 'STATUS' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        if df_sheets is None or df_sheets.empty:
            return None

        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        df_final = df_sheets.copy()
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if ('SUPERVISOR' in col_upper or 'MONITOR' in col_upper) and 'SUPERVISOR' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'SUPERVISOR'
            elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper or 'TIPO_ATIVIDADE' in col_upper) and 'TIPO_ATIVIDADE_COL' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'TIPO_ATIVIDADE_COL'
            elif ('STATUS DA ATIVIDADE' in col_upper or 'STATUS ATIVIDADE' in col_upper or 'STATUS_ATIVIDADE' in col_upper) and 'STATUS_CONCLUSAO_COL' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'STATUS_CONCLUSAO_COL'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper) and 'Recurso' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Recurso'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_ativar = buscar_base_rotas_online()

data_rota_texto = st.session_state.get('data_da_rota_ativar', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Sincronizado em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

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
    st.warning("⚠️ Aguardando sincronização de dados estáveis do Google Sheets.")
