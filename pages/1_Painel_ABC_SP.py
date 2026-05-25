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

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #006677; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 DESEMPENHO E QUEBRA OPERACIONAL - ABC & SP</h1>', unsafe_allow_html=True)

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE CORRIGIDA (FUSO BRASÍLIA) ===
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
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Dados atualizados em fuso local: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

if df_dash is not None and not df_dash.empty:
    
    # === TRATAMENTO BASE DOS DADOS OPERACIONAIS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_Atividade_Upper'] = df_dash['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    df_dash['Supervisor_Upper'] = df_dash['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash['Recurso_Upper'] = df_dash['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    
    # Filtra registros nulos ou almoços
    cond_validos = (df_dash['Contrato_Limpo'] != '') & (df_dash['Contrato_Limpo'] != 'nan')
    if 'Tipo de Atividade' in df_dash.columns:
        cond_validos = cond_validos & (~df_dash['Tipo de Atividade'].str.contains('Refeicao', case=False, na=False))
    df_limpo = df_dash[cond_validos].copy()

    # Mapeia tipos de O.S simplificados baseado no seu modelo (Filtros de exemplo)
    df_limpo['Tipo_Servico'] = 'SERVIÇO'
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo.loc[df_limpo['Tipo de Atividade'].str.contains('Instala', case=False, na=False), 'Tipo_Servico'] = 'INSTALAÇÃO'
        df_limpo.loc[df_limpo['Tipo de Atividade'].str.contains('Migra', case=False, na=False), 'Tipo_Servico'] = 'MIGRAÇÃO'
        df_limpo.loc[df_limpo['Tipo de Atividade'].str.contains('MP', case=False, na=False), 'Tipo_Servico'] = 'MP'
        df_limpo.loc[df_limpo['Tipo de Atividade'].str.contains('PME', case=False, na=False), 'Tipo_Servico'] = 'PME'
        df_limpo.loc[df_limpo['Tipo de Atividade'].str.contains('GPON', case=False, na=False), 'Tipo_Servico'] = 'GPON'

    # Seletor regional na barra lateral
    regiao_sel = st.sidebar.radio("Região Operacional:", ["TODOS", "ABC", "SP"])
    if regiao_sel == "ABC":
        df_limpo = df_limpo[~df_limpo['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)]
    elif regiao_sel == "SP":
        df_limpo = df_limpo[df_limpo['Supervisor_Upper'].str.contains("FRANCISCO|ALAN", na=False)]

    # ==========================================
    # FORMULAS EXCEL CONVERTIDAS PARA PYTHON (TABELA 1)
    # ==========================================
    st.markdown("### 📋 Consolidação Volumétrica por Equipe")
    
    lista_consolidada = []
    for sup in df_limpo['Supervisor_Upper'].unique():
        if sup == 'N/A': continue
        df_sup = df_limpo[df_limpo['Supervisor_Upper'] == sup]
        
        cancelados = len(df_sup[df_sup['Status_Atividade_Upper'] == 'CANCELADO'])
        em_aberto = len(df_sup[df_sup['Status_Atividade_Upper'] == 'PENDENTE'])
        os_ne = len(df_sup[df_sup['Status_Atividade_Upper'] == 'NÃO EXECUTADO'])
        produtivo = len(df_sup[df_sup['Status_Atividade_Upper'] == 'INICIADO']) + len(df_sup[df_sup['Status_Atividade_Upper'].str.contains('CONCLU', na=False)])
        total_geral = len(df_sup)
        
        # Fórmulas matemáticas idênticas ao Excel
        quebra_pct = ((cancelados + os_ne) / total_geral) if total_geral > 0 else 0.0
        eficiencia_pct = (produtivo / total_geral) if total_geral > 0 else 0.0
        projecao = int(produtivo * 1.5)  # Fator de projeção exemplo do seu Excel
        total_tecnicos = df_sup['Recurso_Upper'].nunique()
        media_equipe = (produtivo / total_tecnicos) if total_tecnicos > 0 else 0.0
        
        lista_consolidada.append({
            "MONITOR / SUPERVISOR": sup,
            "Cancelado": cancelados,
            "Em Aberto": em_aberto,
            "O.S NE": os_ne,
            "Produtivo": produtivo,
            "Total Geral": total_geral,
            "QUEBRA": f"{quebra_pct*100:.2f}%",
            "EFICIÊNCIA": f"{eficiencia_pct*100:.2f}%",
            "PROJEÇÃO": projecao,
            "TOTAL TÉCNICOS": total_tecnicos,
            "MÉDIA EQUIPE": round(media_equipe, 2)
        })
        
    df_tabela_1 = pd.DataFrame(lista_consolidada)
    if not df_tabela_1.empty:
        st.dataframe(df_tabela_1, use_container_width=True, hide_index=True)
    
    st.markdown("---")

    # ==========================================
    # MATRIZ DE QUEBRA POR TIPO DE SERVIÇO (TABELA 2 + GRÁFICO)
    # ==========================================
    st.markdown("### 📉 Desempenho - Matriz de Quebra por Serviço (%)")
    
    lista_matriz = []
    tipos_colunas = ['N-D', 'INSTAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']
    
    for sup in df_limpo['Supervisor_Upper'].unique():
        if sup == 'N/A': continue
        df_sup = df_limpo[df_limpo['Supervisor_Upper'] == sup]
        
        row_matriz = {"MONITOR": sup}
        total_quebras_sup = 0
        total_geral_sup = len(df_sup)
        
        for serv in ['N-D', 'INSTAÇÃO', 'SERVIÇO', 'MIGRAÇÃO', 'MP', 'PME', 'GPON']:
            df_serv = df_sup[df_sup['Tipo_Servico'] == serv]
            total_serv = len(df_serv)
            quebras_serv = len(df_serv[df_serv['Status_Atividade_Upper'].isin(['CANCELADO', 'NÃO EXECUTADO'])])
            total_quebras_sup += quebras_serv
            
            # % de quebra por célula
            row_matriz[serv] = (quebras_serv / total_serv * 100) if total_serv > 0 else 0.0
            
        row_matriz["QUEBRA GERAL"] = (total_quebras_sup / total_geral_sup * 100) if total_geral_sup > 0 else 0.0
        lista_matriz.append(row_matriz)
        
    df_tabela_2 = pd.DataFrame(lista_matriz)
    
    if not df_tabela_2.empty:
        # Formata para exibição visual limpa
        df_vitrine = df_tabela_2.copy()
        for col in df_vitrine.columns:
            if col != "MONITOR":
                df_vitrine[col] = df_vitrine[col].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_vitrine, use_container_width=True, hide_index=True)
        
        # Desenha o Gráfico de Barras Agrupadas do Altair baseado no seu modelo
        df_melted = df_tabela_2.melt(id_vars=["MONITOR"], var_name="Serviço", value_name="Porcentagem")
        
        grafico_quebra = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('Serviço:N', title=None),
            y=alt.Y('Porcentagem:Q', title='Taxa de Quebra (%)'),
            color=alt.Color('Serviço:N', scale=alt.Scale(scheme='tableau20')),
            column=alt.Column('MONITOR:N', title="Supervisor / Base Operacional")
        ).properties(width=150, height=300)
        
        st.altair_chart(grafico_quebra, use_container_width=False)

else:
    st.warning("⚠️ Aguardando sincronização de dados estáveis do Google Sheets.")
