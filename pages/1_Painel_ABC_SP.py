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

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE (FUSO BRASÍLIA) ===
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
            if 'SUPERVISOR' in col_upper and 'SUPERVISOR' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'SUPERVISOR'
            elif ('INTERVALO' in col_upper or 'TEMPO' in col_upper) and 'Intervalo de Tempo' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper) and 'Status da Atividade' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Status da Atividade'
            elif 'CONTRATO' in col_upper and 'Contrato' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Contrato'
            elif 'TIPO' in col_upper and 'Tipo de Atividade' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Tipo de Atividade'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper) and 'Recurso' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Recurso'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_dash = buscar_base_rotas_online()

data_rota_texto = st.session_state.get('data_da_rota_dash', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Dados atualizados: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

# --- FUNÇÃO INTERNA PARA CALCULAR OS INDICADORES + LINHA DE TOTAL ---
def calcular_metricas_regiao(df_regiao):
    lista_consolidada = []
    lista_matriz = []
    
    supervisores = [s for s in df_regiao['Supervisor_Upper'].unique() if s != 'N/A' and s != '']
    if not supervisores:
        return pd.DataFrame(), pd.DataFrame()

    # Variáveis acumuladoras para a linha de Total Geral do Excel
    tot_cancelados = 0
    tot_em_aberto = 0
    tot_os_ne = 0
    tot_produtivo = 0
    tot_geral_base = 0
    tot_tecnicos_unicos = df_regiao['Recurso_Upper'].nunique() if not df_regiao.empty else 0
    
    for sup in sorted(supervisores):
        df_sup = df_regiao[df_regiao['Supervisor_Upper'] == sup]
        
        cancelados = len(df_sup[df_sup['Status_Atividade_Upper'] == 'CANCELADO'])
        em_aberto = len(df_sup[df_sup['Status_Atividade_Upper'] == 'PENDENTE'])
        os_ne = len(df_sup[df_sup['Status_Atividade_Upper'] == 'NÃO EXECUTADO'])
        produtivo = len(df_sup[df_sup['Status_Atividade_Upper'] == 'INICIADO']) + len(df_sup[df_sup['Status_Atividade_Upper'].str.contains('CONCLU', na=False)])
        total_geral = len(df_sup)
        
        # Acumula os totais
        tot_cancelados += cancelados
        tot_em_aberto += em_aberto
        tot_os_ne += os_ne
        tot_produtivo += produtivo
        tot_geral_base += total_geral
        
        denominador_quebra = produtivo + os_ne
        quebra_pct = (os_ne / denominador_quebra) if denominador_quebra > 0 else 0.0
        eficiencia_pct = (produtivo / total_geral) if total_geral > 0 else 0.0
        projecao = int(produtivo * 1.35)  
        total_tecnicos = df_sup['Recurso_Upper'].nunique()
        media_equipe = (produtivo / total_tecnicos) if total_tecnicos > 0 else 0.0
        
        lista_consolidada.append({
            "Rótulos de Linha": sup, "cancelado": cancelados, "Em aberto": em_aberto,
            "O.S NE": os_ne, "Produtivo": produtivo, "Total Geral": total_geral,
            "QUEBRA": f"{quebra_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_pct*100:.2f}%",
            "PROJEÇÃO": int(projecao), "TOTAL TÉCNICOS": int(total_tecnicos), "MEDIA EQUIPE": f"{media_equipe:.2f}"
        })
        
        # Df da matriz de serviços
        row_matriz = {"MONITOR": sup}
        for serv in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
            df_serv = df_sup[df_sup['Tipo_Servico'] == serv]
            t_serv = len(df_serv)
            ne_serv = len(df_serv[df_serv['Status_Atividade_Upper'] == 'NÃO EXECUTADO'])
            p_serv = len(df_serv[df_serv['Status_Atividade_Upper'] == 'INICIADO']) + len(df_serv[df_serv['Status_Atividade_Upper'].str.contains('CONCLU', na=False)])
            
            denom_q_serv = p_serv + ne_serv
            row_matriz[serv] = (ne_serv / denom_q_serv * 100) if denom_q_serv > 0 else 0.0
            
        row_matriz["QUEBRA GERAL"] = quebra_pct * 100
        lista_matriz.append(row_matriz)
        
    # 🛠️ INJEÇÃO EXATA DA LINHA DO TOTAL GERAL DA BASE OPERACIONAL
    denom_q_total = tot_produtivo + tot_os_ne
    quebra_total_pct = (tot_os_ne / denom_q_total) if denom_q_total > 0 else 0.0
    eficiencia_total_pct = (tot_produtivo / tot_geral_base) if tot_geral_base > 0 else 0.0
    projecao_total = int(tot_produtivo * 1.35)
    media_total_equipe = (tot_produtivo / tot_tecnicos_unicos) if tot_tecnicos_unicos > 0 else 0.0

    lista_consolidada.append({
        "Rótulos de Linha": "Total Geral", "cancelado": tot_cancelados, "Em aberto": tot_em_aberto,
        "O.S NE": tot_os_ne, "Produtivo": tot_produtivo, "Total Geral": tot_geral_base,
        "QUEBRA": f"{quebra_total_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_total_pct*100:.2f}%",
        "PROJEÇÃO": int(projecao_total), "TOTAL TÉCNICOS": int(tot_tecnicos_unicos), "MEDIA EQUIPE": f"{media_total_equipe:.2f}"
    })

    # Linha total para a matriz de serviços
    row_total_matriz = {"MONITOR": "Total Geral"}
    for serv in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
        df_serv_total = df_regiao[df_regiao['Tipo_Servico'] == serv]
        t_s = len(df_serv_total)
        ne_s = len(df_serv_total[df_serv_total['Status_Atividade_Upper'] == 'NÃO EXECUTADO'])
        p_s = len(df_serv_total[df_serv_total['Status_Atividade_Upper'] == 'INICIADO']) + len(df_serv_total[df_serv_total['Status_Atividade_Upper'].str.contains('CONCLU', na=False)])
        
        denom_s = p_s + ne_s
        row_total_matriz[serv] = (ne_s / denom_s * 100) if denom_s > 0 else 0.0
    row_total_matriz["QUEBRA GERAL"] = quebra_total_pct * 100
    lista_matriz.append(row_total_matriz)
        
    return pd.DataFrame(lista_consolidada), pd.DataFrame(lista_matriz)

# --- CORPO PRINCIPAL DO RENDER ---
if df_dash is not None and not df_dash.empty:
    
    # === PREPARAÇÃO GLOBAL DOS DADOS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_Atividade_Upper'] = df_dash['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Supervisor_Upper'] = df_dash['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Recurso_Upper'] = df_dash['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    
    cond_validos = (df_dash['Contrato_Limpo'] != '') & (df_dash['Contrato_Limpo'] != 'nan')
    if 'Tipo de Atividade' in df_dash.columns:
        cond_validos = cond_validos & (~df_dash['Tipo de Atividade'].str.contains('Refeicao', case=False, na=False))
    df_global = df_dash[cond_validos].copy()

    df_global['Tipo_Servico'] = 'SERVIÇO'
    if 'Tipo de Atividade' in df_global.columns:
        df_global.loc[df_global['Tipo de Atividade'].str.contains('Instala', case=False, na=False), 'Tipo_Servico'] = 'INSTALAÇÃO'
        df_global.loc[df_global['Tipo de Atividade'].str.contains('Migra', case=False, na=False), 'Tipo_Servico'] = 'MIGRAÇÃO'
        df_global.loc[df_global['Tipo de Atividade'].str.contains('MP', case=False, na=False), 'Tipo_Servico'] = 'MP'
        df_global.loc[df_global['Tipo de Atividade'].str.contains('PME', case=False, na=False), 'Tipo_Servico'] = 'PME'
        df_global.loc[df_global['Tipo de Atividade'].str.contains('GPON', case=False, na=False), 'Tipo_Servico'] = 'GPON'

    # Divisão física regional
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
        
        # Filtra o Total Geral do gráfico para não poluir o visual das barras
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
        
        # Filtra o Total Geral do gráfico
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
