import streamlit as st
import pandas as pd
import requests
import io
import altair as alt  
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 PERFORMANCE OPERACIONAL - ABC & SP</h1>', unsafe_allow_html=True)

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
        st.session_state['data_da_rota_dash'] = datetime.now(fuso_sp).strftime('%d/%m/%Y às %H:%M:%S')

        conteudo_bruto = response_text = resposta.text
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
            elif ('INTERVALO' in col_upper or 'TEMPO' in col_upper) and 'Intervalo de Tempo' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif ('BAIXA' in col_upper or 'STATUS DA O.S 1' in col_upper or 'STATUS OS 1' in col_upper) and 'STATUS_OS1' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'STATUS_OS1'
            elif 'STATUS' in col_upper and 'STATUS_ATIVIDADE' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif 'CONTRATO' in col_upper and 'Contrato' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Contrato'
            elif ('TIPO O.S 1' in col_upper or 'TIPO DE OS' in col_upper or 'TIPO ATIVIDADE' in col_upper) and 'Tipo O.S 1' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Tipo O.S 1'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper) and 'Recurso' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Recurso'
            elif ('QTD O.S' in col_upper or 'TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper or 'VOLUME' in col_upper) and 'QTD_OS_COL' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'QTD_OS_COL'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_dash = buscar_base_rotas_online()

data_rota_texto = st.session_state.get('data_da_rota_dash', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Dados atualizados: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

# 🛠️ FUNÇÃO DE MAPEAMENTO DINÂMICO BASEADO NAS PARAS ENVIADAS PELO USER
def classificar_status_excel(linha):
    baixa = str(linha.get('STATUS_OS1', '')).upper().strip()
    status_at = str(linha.get('STATUS_ATIVIDADE', '')).upper().strip()
    
    # Lista de códigos de O.S NE enviados na imagem
    codigos_ne = [
        "101", "106", "110", "112", "113", "125", "203", "205", "206", "301", 
        "305", "306", "402", "103", "104", "105", "107", "108", "114", "204", 
        "302", "303", "307", "308", "312", "316", "400", "100"
    ]
    
    # Verifica se a baixa começa com algum dos códigos de quebra
    for cod in codigos_ne:
        if baixa.startswith(cod) or f"{cod} -" in baixa:
            return "O.S NE"
            
    # Tratamento explícito das condições de Em Aberto
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or \
       "PENDENTE" in status_at or "INICIADO" in status_at or "EM ROTA" in status_at:
        return "EM ABERTO"
        
    return "PRODUTIVO"

# --- FUNÇÃO INTERNA PARA CALCULAR OS INDICADORES UTILIZANDO SOMA OPERACIONAL ---
def calcular_metricas_regiao(df_regiao):
    lista_consolidada = []
    lista_matriz = []
    
    supervisores = [s for s in df_regiao['Supervisor_Upper'].unique() if s != 'N/A' and s != '']
    if not supervisores:
        return pd.DataFrame(), pd.DataFrame()

    tot_cancelados = 0
    tot_em_aberto = 0
    tot_os_ne = 0
    tot_produtivo = 0
    tot_geral_base = 0
    tot_tecnicos_unicos = df_regiao['Recurso_Upper'].nunique() if not df_regiao.empty else 0
    
    for sup in sorted(supervisores):
        df_sup = df_regiao[df_regiao['Supervisor_Upper'] == sup]
        
        # Realiza as somas baseadas na nossa nova classificação de para
        cancelados = df_sup[df_sup['Status_Geral_Upper'] == 'CANCELADO']['QTD_OS_NUM'].sum()
        em_aberto = df_sup[df_sup['Classificacao_Excel'] == 'EM ABERTO']['QTD_OS_NUM'].sum()
        os_ne = df_sup[df_sup['Classificacao_Excel'] == 'O.S NE']['QTD_OS_NUM'].sum()
        produtivo = df_sup[df_sup['Classificacao_Excel'] == 'PRODUTIVO']['QTD_OS_NUM'].sum()
        total_geral = df_sup['QTD_OS_NUM'].sum()
        
        tot_cancelados += cancelados
        tot_em_aberto += em_aberto
        tot_os_ne += os_ne
        tot_produtivo += produtivo
        tot_geral_base += total_geral
        
        # FÓRMULA OFICIAL: QUEBRA = O.S NE / (Produtivo + O.S NE)
        denominador_quebra = produtivo + os_ne
        quebra_pct = (os_ne / denominador_quebra) if denominador_quebra > 0 else 0.0
        
        eficiencia_pct = (produtivo / total_geral) if total_geral > 0 else 0.0
        projecao = int(produtivo * 1.35)  
        total_tecnicos = df_sup['Recurso_Upper'].nunique()
        media_equipe = (produtivo / total_tecnicos) if total_tecnicos > 0 else 0.0
        
        lista_consolidada.append({
            "Rótulos de Linha": sup, "cancelado": int(cancelados), "Em aberto": int(em_aberto),
            "O.S NE": int(os_ne), "Produtivo": int(produtivo), "Total Geral": int(total_geral),
            "QUEBRA": f"{quebra_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_pct*100:.2f}%",
            "PROJEÇÃO": int(projecao), "TOTAL TÉCNICOS": int(total_tecnicos), "MEDIA EQUIPE": f"{media_equipe:.2f}"
        })
        
        # Matriz de Quebras por tipo de serviço
        row_matriz = {"MONITOR": sup}
        for serv in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
            df_serv = df_sup[df_sup['Tipo_Servico'] == serv]
            ne_serv = df_serv[df_serv['Classificacao_Excel'] == 'O.S NE']['QTD_OS_NUM'].sum()
            p_serv = df_serv[df_serv['Classificacao_Excel'] == 'PRODUTIVO']['QTD_OS_NUM'].sum()
            
            denom_q_serv = p_serv + ne_serv
            row_matriz[serv] = (ne_serv / denom_q_serv * 100) if denom_q_serv > 0 else 0.0
            
        row_matriz["QUEBRA GERAL"] = quebra_pct * 100
        lista_matriz.append(row_matriz)
        
    denom_q_total = tot_produtivo + tot_os_ne
    quebra_total_pct = (tot_os_ne / denom_q_total) if denom_q_total > 0 else 0.0
    eficiencia_total_pct = (tot_produtivo / tot_geral_base) if tot_geral_base > 0 else 0.0
    projecao_total = int(tot_produtivo * 1.35)
    media_total_equipe = (tot_produtivo / tot_tecnicos_unicos) if tot_tecnicos_unicos > 0 else 0.0

    lista_consolidada.append({
        "Rótulos de Linha": "Total Geral", "cancelado": int(tot_cancelados), "Em aberto": int(tot_em_aberto),
        "O.S NE": int(tot_os_ne), "Produtivo": int(tot_produtivo), "Total Geral": int(tot_geral_base),
        "QUEBRA": f"{quebra_total_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_total_pct*100:.2f}%",
        "PROJEÇÃO": int(projecao_total), "TOTAL TÉCNICOS": int(tot_tecnicos_unicos), "MEDIA EQUIPE": f"{media_total_equipe:.2f}"
    })

    row_total_matriz = {"MONITOR": "Total Geral"}
    for serv in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
        df_serv_total = df_regiao[df_regiao['Tipo_Servico'] == serv]
        ne_s = df_serv_total[df_serv_total['Classificacao_Excel'] == 'O.S NE']['QTD_OS_NUM'].sum()
        p_s = df_serv_total[df_serv_total['Classificacao_Excel'] == 'PRODUTIVO']['QTD_OS_NUM'].sum()
        
        denom_s = p_s + ne_s
        row_total_matriz[serv] = (ne_s / denom_s * 100) if denom_s > 0 else 0.0
    row_total_matriz["QUEBRA GERAL"] = quebra_total_pct * 100
    lista_matriz.append(row_total_matriz)
        
    return pd.DataFrame(lista_consolidada), pd.DataFrame(lista_matriz)

# --- CORPO PRINCIPAL DO RENDER ---
if df_dash is not None and not df_dash.empty:
    
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_OS1_Upper'] = df_dash['STATUS_OS1'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Status_Geral_Upper'] = df_dash['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Supervisor_Upper'] = df_dash['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Recurso_Upper'] = df_dash['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Tipo_OS_Upper'] = df_dash['Tipo O.S 1'].fillna('').astype(str).str.upper().str.strip()
    
    # Processa coluna quantitativa de O.S da tabela dinâmica
    if 'QTD_OS_COL' in df_dash.columns:
        df_dash['QTD_OS_NUM'] = pd.to_numeric(df_dash['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_dash['QTD_OS_NUM'] = 1
        
    # Executa a nova classificação cirúrgica por linha
    df_dash['Classificacao_Excel'] = df_dash.apply(classificar_status_excel, axis=1)
    
    # FILTRAGEM DINÂMICA: Limpa nulos e REMOVE ORDENS DE RETORNO
    cond_validos = (df_dash['Contrato_Limpo'] != '') & (df_dash['Contrato_Limpo'] != 'nan')
    cond_validos = cond_validos & (~df_dash['Tipo_OS_Upper'].str.contains('RETORNO', na=False))
    
    df_global = df_dash[cond_validos].copy()

    df_global['Tipo_Servico'] = 'SERVIÇO'
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('INSTALA', na=False), 'Tipo_Servico'] = 'INSTALAÇÃO'
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('MIGRA', na=False), 'Tipo_Servico'] = 'MIGRAÇÃO'
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('MP', na=False), 'Tipo_Servico'] = 'MP'
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('PME', na=False), 'Tipo_Servico'] = 'PME'
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('GPON', na=False), 'Tipo_Servico'] = 'GPON'

    df_sp_base = df_global[df_global['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc_base = df_global[~df_global['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)].copy()

    # ==========================================
    # 🔴 SEÇÃO ABC
    # ==========================================
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 BLOCADO - REGIÃO ABC</h2></div>', unsafe_allow_html=True)
    
    df_cons_abc, df_mat_abc = calcular_metricas_regiao(df_abc_base)
    
    if not df_cons_abc.empty:
        st.markdown("##### 📈 Resumo de Produtividade e Eficiência (ABC)")
        st.dataframe(df_cons_abc, use_container_width=True, hide_index=True)
        
        st.markdown("##### 📉 Desempenho - Matriz de Quebra por Tipo de Serviço (ABC)")
        df_vitrine_abc = df_mat_abc.copy()
        for col in df_vitrine_abc.columns:
            if col != "MONITOR": df_vitrine_abc[col] = df_vitrine_abc[col].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_vitrine_abc, use_container_width=True, hide_index=True)
        
        df_melt_abc = df_mat_abc[df_mat_abc['MONITOR'] != 'Total Geral'].melt(id_vars=["MONITOR"], var_name="Serviço", value_name="Porcentagem")
        graf_abc = alt.Chart(df_melt_abc).mark_bar().encode(
            x=alt.X('Serviço:N', title=None),
            y=alt.Y('Porcentagem:Q', title='Taxa de Quebra (%)'),
            color=alt.Color('Serviço:N', scale=alt.Scale(scheme='tableau10')),
            column=alt.Column('MONITOR:N', title=None)
        ).properties(width=160, height=220)
        st.altair_chart(graf_abc, use_container_width=False)
        
    else:
        st.info("Nenhum dado ativo mapeado para a região ABC.")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # 🔵 SEÇÃO SÃO PAULO (SP)
    # ==========================================
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 BLOCADO - REGIÃO SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
    
    df_cons_sp, df_mat_sp = calcular_metricas_regiao(df_sp_base)
    
    if not df_cons_sp.empty:
        st.markdown("##### 📈 Resumo de Produtividade e Eficiência (SP)")
        st.dataframe(df_cons_sp, use_container_width=True, hide_index=True)
        
        st.markdown("##### 📉 Desempenho - Matriz de Quebra por Tipo de Serviço (SP)")
        df_vitrine_sp = df_mat_sp.copy()
        for col in df_vitrine_sp.columns:
            if col != "MONITOR": df_vitrine_sp[col] = df_vitrine_sp[col].apply(lambda x: f"{x:.2f}%")
        st.dataframe(df_vitrine_sp, use_container_width=True, hide_index=True)
        
        df_melt_sp = df_mat_sp[df_mat_sp['MONITOR'] != 'Total Geral'].melt(id_vars=["MONITOR"], var_name="Serviço", value_name="Porcentagem")
        graf_sp = alt.Chart(df_melt_sp).mark_bar().encode(
            x=alt.X('Serviço:N', title=None),
            y=alt.Y('Porcentagem:Q', title='Taxa de Quebra (%)'),
            color=alt.Color('Serviço:N', scale=alt.Scale(scheme='category10')),
            column=alt.Column('MONITOR:N', title=None)
        ).properties(width=160, height=220)
        st.altair_chart(graf_sp, use_container_width=False)
        
    else:
        st.info("Nenhum dado ativo mapeado para a região SP.")

else:
    st.warning("⚠️ Aguardando sincronização de dados estáveis do Google Sheets.")
