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
            # 🌟 PARAMETRIZAÇÃO CRÍTICA: Mapeia a coluna "Total de tarefas" para saber o total de OS
            elif ('TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper or 'QTD O.S' in col_upper or 'VOLUME' in col_upper) and 'QTD_OS_COL' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'QTD_OS_COL'
            elif ('CATEGORIA' in col_upper or 'CAPACIDADE' in col_upper) and 'CATEGORIA_CAPACIDADE' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'CATEGORIA_CAPACIDADE'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_dash = buscar_base_rotas_online()

data_rota_texto = st.session_state.get('data_da_rota_dash', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Dados atualizados: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

# 🛠️ Classificação de status operacionais baseada na coluna de Baixa
def classificar_status_excel(linha):
    baixa = str(linha.get('STATUS_OS1', '')).upper().strip()
    status_at = str(linha.get('STATUS_ATIVIDADE', '')).upper().strip()
    
    codigos_ne = [
        "101", "106", "110", "112", "113", "125", "203", "205", "206", "301", 
        "305", "306", "402", "103", "104", "105", "107", "108", "114", "204", 
        "302", "303", "307", "308", "312", "316", "400", "100"
    ]
    
    for cod in codigos_ne:
        if baixa.startswith(cod) or f"{cod} -" in baixa:
            return "O.S NE"
            
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or \
       "PENDENTE" in status_at or "INICIADO" in status_at or "EM ROTA" in status_at:
        return "EM ABERTO"
        
    return "PRODUTIVO"

# 🛠️ Injetora de layouts de cor para o Total Geral
def destacar_linha_total(row):
    try:
        if str(row.iloc[0]).strip() == "Total Geral":
            return ['background-color: #eae5da; font-weight: bold; color: #111111; border-top: 1px solid #b5b5b5;'] * len(row)
    except:
        pass
    return [''] * len(row)

# --- FUNÇÃO DE PROCESSAMENTO EM BLOCO ISOLADO POR TECNOLOGIA ---
def gerar_tabela_bloco_tecnologia(df_tecnologia):
    lista_bloco = []
    supervisores = [s for s in df_tecnologia['Supervisor_Upper'].unique() if s != 'N/A' and s != '']
    
    if not df_tecnologia.empty and len(supervisores) > 0:
        tot_em_aberto = 0
        tot_os_ne = 0
        tot_produtivo = 0
        tot_geral = 0
        
        for sup in sorted(supervisores):
            df_sup = df_tecnologia[df_tecnologia['Supervisor_Upper'] == sup]
            
            # 🌟 Puxa a soma real baseada nos valores numéricos da coluna "Total de tarefas"
            em_aberto = df_sup[df_sup['Classificacao_Excel'] == 'EM ABERTO']['QTD_OS_NUM'].sum()
            os_ne = df_sup[df_sup['Classificacao_Excel'] == 'O.S NE']['QTD_OS_NUM'].sum()
            produtivo = df_sup[df_sup['Classificacao_Excel'] == 'PRODUTIVO']['QTD_OS_NUM'].sum()
            total_geral = df_sup['QTD_OS_NUM'].sum()
            
            tot_em_aberto += em_aberto
            tot_os_ne += os_ne
            tot_produtivo += produtivo
            tot_geral += total_geral
            
            denom_quebra = produtivo + os_ne
            quebra_pct = (os_ne / denom_quebra * 100) if denom_quebra > 0 else 0.0
            
            lista_bloco.append({
                "Rótulos de Linha": sup,
                "Em aberto": int(em_aberto),
                "O.S NE": int(os_ne),
                "Produtivo": int(produtivo),
                "Total Geral": int(total_geral),
                "QUEBRA": f"{quebra_pct:.2f}%"
            })
            
        denom_quebra_total = tot_produtivo + tot_os_ne
        quebra_total_pct = (tot_os_ne / denom_quebra_total * 100) if denom_quebra_total > 0 else 0.0
        
        lista_bloco.append({
            "Rótulos de Linha": "Total Geral",
            "Em aberto": int(tot_em_aberto),
            "O.S NE": int(tot_os_ne),
            "Produtivo": int(tot_produtivo),
            "Total Geral": int(tot_geral),
            "QUEBRA": f"{quebra_total_pct:.2f}%"
        })
        
        df_retorno = pd.DataFrame(lista_bloco)
        return df_retorno.style.apply(destacar_linha_total, axis=1)
    return None

# --- FUNÇÃO DO RESUMO PRINCIPAL (PAINEL GERAL) ---
def calcular_metricas_regiao(df_regiao):
    lista_consolidada = []
    supervisores = [s for s in df_regiao['Supervisor_Upper'].unique() if s != 'N/A' and s != '']
    if not supervisores:
        return pd.DataFrame()

    tot_cancelados = 0
    tot_em_aberto = 0
    tot_os_ne = 0
    tot_produtivo = 0
    tot_geral_base = 0
    tot_tecnicos_unicos = df_regiao['Recurso_Upper'].nunique() if not df_regiao.empty else 0
    
    for sup in sorted(supervisores):
        df_sup = df_regiao[df_regiao['Supervisor_Upper'] == sup]
        
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
        
        denominador_quebra = produtivo + os_ne
        quebra_pct = (os_ne / denominador_quebra) if denominador_quebra > 0 else 0.0
        eficiencia_pct = 1.0 - quebra_pct
        projecao = produtivo + (em_aberto * eficiencia_pct)
        total_tecnicos = df_sup['Recurso_Upper'].nunique()
        media_equipe = (total_geral / total_tecnicos) if total_tecnicos > 0 else 0.0
        
        lista_consolidada.append({
            "Rótulos de Linha": sup, "cancelado": int(cancelados), "Em aberto": int(em_aberto),
            "O.S NE": int(os_ne), "Produtivo": int(produtivo), "Total Geral": int(total_geral),
            "QUEBRA": f"{quebra_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_pct*100:.2f}%",
            "PROJEÇÃO": int(round(projecao)), "TOTAL TÉCNICOS": int(total_tecnicos), "MEDIA EQUIPE": f"{media_equipe:.2f}"
        })
        
    denom_q_total = tot_produtivo + tot_os_ne
    quebra_total_pct = (tot_os_ne / denom_q_total) if denom_q_total > 0 else 0.0
    eficiencia_total_pct = 1.0 - quebra_total_pct
    projecao_total = tot_produtivo + (tot_em_aberto * eficiencia_total_pct)
    media_total_equipe = (tot_geral_base / tot_tecnicos_unicos) if tot_tecnicos_unicos > 0 else 0.0

    lista_consolidada.append({
        "Rótulos de Linha": "Total Geral", "cancelado": int(tot_cancelados), "Em aberto": int(tot_em_aberto),
        "O.S NE": int(tot_os_ne), "Produtivo": int(tot_produtivo), "Total Geral": int(tot_geral_base),
        "QUEBRA": f"{quebra_total_pct*100:.2f}%", "EFICIÊNCIA": f"{eficiencia_total_pct*100:.2f}%",
        "PROJEÇÃO": int(round(projecao_total)), "TOTAL TÉCNICOS": int(tot_tecnicos_unicos), "MEDIA EQUIPE": f"{media_total_equipe:.2f}"
    })
        
    return pd.DataFrame(lista_consolidada)

# --- CORE DO RENDER ---
if df_dash is not None and not df_dash.empty:
    
    if 'CATEGORIA_CAPACIDADE' in df_dash.columns:
        df_dash['Capacidade_Upper'] = df_dash['CATEGORIA_CAPACIDADE'].fillna('').astype(str).str.upper().str.strip()
    else:
        df_dash['Capacidade_Upper'] = ''
        
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_OS1_Upper'] = df_dash['STATUS_OS1'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Status_Geral_Upper'] = df_dash['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Supervisor_Upper'] = df_dash['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Recurso_Upper'] = df_dash['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Tipo_OS_Upper'] = df_dash['Tipo O.S 1'].fillna('').astype(str).str.upper().str.strip()
    
    # Converte os valores da coluna "Total de tarefas" para números inteiros
    if 'QTD_OS_COL' in df_dash.columns:
        df_dash['QTD_OS_NUM'] = pd.to_numeric(df_dash['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_dash['QTD_OS_NUM'] = 1
        
    df_dash['Classificacao_Excel'] = df_dash.apply(classificar_status_excel, axis=1)
    
    cond_validos = (df_dash['Contrato_Limpo'] != '') & (df_dash['Contrato_Limpo'] != 'nan')
    cond_validos = cond_validos & (~df_dash['Tipo_OS_Upper'].str.contains('RETORNO', na=False))
    
    df_global = df_dash[cond_validos].copy()

    # =========================================================================
    # ⚡ REGRA ULTRA RÁPIDA: CLASSIFICAÇÃO POR PALAVRAS-CHAVE DA SUA IMAGEM
    # =========================================================================
    df_global['Tipo_Servico'] = 'SERVIÇO' # Tudo cai em Serviço por padrão

    lista_base_adesao = [
        "1 - ADESAO - INSTALACAO DE ASSINATURA",
        "516 - ADESAO ENTREGA STREAMING",
        "51 - ADESAO - INSTALACAO DE ASSINATURA DIGITAL"
    ]
    lista_base_upper = [x.upper().strip() for x in lista_base_adesao]

    # 1. Bloco PME (Filtro Duplo)
    cond_classe_pme = df_global['Capacidade_Upper'].isin(["CLASSE 1", "CLASSE 1 (PME)"])
    cond_os_pme = df_global['Tipo_OS_Upper'].isin(lista_base_upper)
    df_global.loc[cond_classe_pme & cond_os_pme, 'Tipo_Servico'] = 'PME'

    # 2. Bloco N-D
    df_global.loc[df_global['Tipo_OS_Upper'].isin(lista_base_upper) & (df_global['Tipo_Servico'] != 'PME'), 'Tipo_Servico'] = 'N-D'

    # 3. Bloco GPON
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('515 - ADESAO', na=False), 'Tipo_Servico'] = 'GPON'

    # 4. Bloco MIGRAÇÃO
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('MIGRAÇÃO|MIGRACAO', na=False) & (df_global['Tipo_Servico'] == 'SERVIÇO'), 'Tipo_Servico'] = 'MIGRAÇÃO'
    
    # 5. Bloco MP
    df_global.loc[df_global['Tipo_OS_Upper'].str.contains('ASSISTENCIA TECNICA|ASSISTÊNCIA TÉCNICA|REFAZER MANUTENCAO|REFAZER MANUTENÇÃO', na=False) & (df_global['Tipo_Servico'] == 'SERVIÇO'), 'Tipo_Servico'] = 'MP'

    # 6. Bloco INSTALAÇÃO (Filtro Inteligente de Termos)
    df_global.loc[(df_global['Tipo_OS_Upper'].str.contains('INSTALACAO|INSTALAÇÃO|HABILITACAO|HABILITAÇÃO|MUDANCA DE ENDERECO|MUDANÇA DE ENDEREÇO|RETIRADA|REMOÇÃO|REMOVE', na=False)) & (df_global['Tipo_Servico'] == 'SERVIÇO'), 'Tipo_Servico'] = 'INSTALAÇÃO'
    # =========================================================================

    # Divisão Regional
    df_sp_base = df_global[df_global['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)].copy()
    df_abc_base = df_global[~df_global['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)].copy()

    # =========================================================================
    # 🔴 RENDERIZAÇÃO DA REGIÃO ABC
    # =========================================================================
    st.markdown('<div style="background-color:#008080; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 BLOCADO - REGIÃO ABC</h2></div>', unsafe_allow_html=True)
    
    df_cons_abc = calcular_metricas_regiao(df_abc_base)
    if not df_cons_abc.empty:
        st.markdown("##### 📈 Resumo Geral - Produtividade e Eficiência (ABC)")
        st.dataframe(df_cons_abc.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
        
        st.markdown("<br><h4>🧱 MATRIZ POR TECNOLOGIA (ABC)</h4>", unsafe_allow_html=True)
        
        for tecnologia in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
            df_tec = df_abc_base[df_abc_base['Tipo_Servico'] == tecnologia]
            res_bloco = gerar_tabela_bloco_tecnologia(df_tec)
            if res_bloco is not None:
                st.markdown(f"**📌 Tabela Desempenho - {tecnologia} (ABC)**")
                st.dataframe(res_bloco, use_container_width=True, hide_index=True)
                st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # =========================================================================
    # 🔵 RENDERIZAÇÃO DA REGIÃO SÃO PAULO (SP)
    # =========================================================================
    st.markdown('<div style="background-color:#b30000; padding:6px 12px; border-radius:4px; margin-bottom:15px;"><h2 style="color:white; margin:0px; font-size:22px;">📍 BLOCADO - REGIÃO SÃO PAULO (SP)</h2></div>', unsafe_allow_html=True)
    
    df_cons_sp = calcular_metricas_regiao(df_sp_base)
    if not df_cons_sp.empty:
        st.markdown("##### 📈 Resumo Geral - Produtividade e Eficiência (SP)")
        st.dataframe(df_cons_sp.style.apply(destacar_linha_total, axis=1), use_container_width=True, hide_index=True)
        
        st.markdown("<br><h4>🧱 MATRIZ POR TECNOLOGIA (SP)</h4>", unsafe_allow_html=True)
        
        for tecnologia in ['N-D', 'INSTALAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
            df_tec = df_sp_base[df_sp_base['Tipo_Servico'] == tecnologia]
            res_bloco = gerar_tabela_bloco_tecnologia(df_tec)
            if res_bloco is not None:
                st.markdown(f"**📌 Tabela Desempenho - {tecnologia} (SP)**")
                st.dataframe(res_bloco, use_container_width=True, hide_index=True)
                st.markdown("<br>", unsafe_allow_html=True)
else:
    st.warning("⚠️ Aguardando sincronização de dados estáveis do Google Sheets.")
