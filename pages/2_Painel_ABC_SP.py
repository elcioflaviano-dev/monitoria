import streamlit as st
import pandas as pd
import requests
import io
import os
import altair as alt  # Adicionado para habilitar a plotagem de valores nas barras
from datetime import datetime

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📊 PAINEL ABC SP - DASHBOARDS</h1>', unsafe_allow_html=True)

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
            
        data_header = resposta.headers.get('Date')
        if data_header:
            try:
                dt_gmt = pd.to_datetime(data_header)
                if dt_gmt.tz is None:
                    dt_brasil = dt_gmt.tz_localize('UTC').tz_convert('America/Sao_Paulo')
                else:
                    dt_brasil = dt_gmt.tz_convert('America/Sao_Paulo')
                st.session_state['data_da_rota_dash'] = dt_brasil.strftime('%d/%m/%Y às %H:%M:%S')
            except:
                st.session_state['data_da_rota_dash'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        else:
            st.session_state['data_da_rota_dash'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')

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
            elif 'CIDADE' in col_upper and 'Cidade' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Cidade'
            elif ('TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper) and 'Total de tarefas' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Total de tarefas'
            elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper) and 'Tipo de Atividade' not in colunas_mapeadas.values():
                colunas_mapeadas[col] = 'Tipo de Atividade'
        
        df_final = df_final.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            
        return df_final
    except:
        return None

df_dash = buscar_base_rotas_online()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO ---
data_rota_texto = st.session_state.get('data_da_rota_dash', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Dados atualizados em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

if df_dash is not None and not df_dash.empty:
    
    # === HIGIENIZAÇÃO CRÍTICA DOS DADOS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_Atividade_Upper'] = df_dash['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    
    # Remove nulos, refeições e contratos suspensos
    cond_contrato_valido = (
        (df_dash['Contrato_Limpo'] != '') & 
        (df_dash['Contrato_Limpo'] != 'nan') & 
        (~df_dash['Contrato_Limpo'].str.contains('#N/A', case=False, na=False)) &
        (~df_dash['Status_Atividade_Upper'].str.contains('SUSPENSO', case=False, na=False))
    )
    
    if 'Tipo de Atividade' in df_dash.columns:
        cond_contrato_valido = cond_contrato_valido & (~df_dash['Tipo de Atividade'].fillna('').astype(str).str.contains('Refeicao', case=False, na=False))
        
    df_dash_filtrado = df_dash[cond_contrato_valido].copy()
    df_dash_filtrado['Contrato_Limpo'] = df_dash_filtrado['Contrato_Limpo'].apply(lambda x: x.split('.')[0].strip())

    if 'Cidade' in df_dash_filtrado.columns:
        df_dash_filtrado['Cidade_Tratada'] = df_dash_filtrado['Cidade'].fillna('NÃO INFORMADA').astype(str).str.upper().str.strip()
    else:
        df_dash_filtrado['Cidade_Tratada'] = 'NÃO INFORMADA'

    if 'Total de tarefas' in df_dash_filtrado.columns:
        df_dash_filtrado['Total_OS_Num'] = pd.to_numeric(df_dash_filtrado['Total de tarefas'], errors='coerce').fillna(0).astype(int)
    else:
        df_dash_filtrado['Total_OS_Num'] = 0

    if 'Intervalo de Tempo' in df_dash_filtrado.columns:
        df_dash_filtrado['Intervalo_Tratado'] = df_dash_filtrado['Intervalo de Tempo'].fillna('').astype(str).str.strip()
    else:
        df_dash_filtrado['Intervalo_Tratado'] = ''

    # === FILTRO DE SUPERVISOR ===
    if 'SUPERVISOR' in df_dash_filtrado.columns:
        lista_supervisores = ["TODOS"] + sorted(df_dash_filtrado['SUPERVISOR'].dropna().unique())
        supervisor_sel = st.sidebar.selectbox("Filtrar por Supervisor:", lista_supervisores)
        
        if supervisor_sel != "TODOS":
            df_dash_filtrado = df_dash_filtrado[df_dash_filtrado['SUPERVISOR'] == supervisor_sel]

    # ==========================================
    # BLOCO 1: KPIs
    # ==========================================
    total_contratos = df_dash_filtrado['Contrato_Limpo'].nunique()
    total_geral_os = df_dash_filtrado['Total_OS_Num'].sum()
    media_os_por_contrato = df_dash_filtrado['Total_OS_Num'].mean() if total_contratos > 0 else 0.0

    df_janelas_validas = df_dash_filtrado[
        (df_dash_filtrado['Intervalo_Tratado'] != '') & 
        (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
        (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('PADRAO'))
    ]
    
    if not df_janelas_validas.empty:
        media_os_janelas_reais = df_janelas_validas.groupby('Intervalo_Tratado')['Total_OS_Num'].mean().mean()
    else:
        media_os_janelas_reais = 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">📋 Total Contratos</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#008080;">{total_contratos}</div>', unsafe_allow_html=True)
    with m2:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🛠️ Volume Total OS</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#333;">{total_geral_os}</div>', unsafe_allow_html=True)
    with m3:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🧮 Média OS / Contrato</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#008080;">{media_os_por_contrato:.2f}</div>', unsafe_allow_html=True)
    with m4:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">⏳ Média OS / Janela Real</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#ff9800;">{media_os_janelas_reais:.2f}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # BLOCO 2: GRÁFICOS AVANÇADOS COM RÓTULOS (ALTAIR)
    # ==========================================
    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            st.markdown("#### 🌆 Volume de Contratos por Cidade")
            df_cidades = df_dash_filtrado.groupby('Cidade_Tratada')['Contrato_Limpo'].nunique().reset_index()
            df_cidades.columns = ['Cidade', 'Contratos']
            df_cidades = df_cidades.sort_values(by='Contratos', ascending=False)
            
            if not df_cidades.empty:
                # Cria a barra do gráfico
                barras_cidade = alt.Chart(df_cidades).mark_bar(color='#008080').encode(
                    x=alt.X('Cidade:N', sort='-y', title='Cidade'),
                    y=alt.Y('Contratos:Q', title='Qtd Contratos')
                )
                # Cria o rótulo com o valor no topo
                textos_cidade = barras_cidade.mark_text(
                    align='center', baseline='bottom', dy=-4, fontWeight='bold'
                ).encode(text='Contratos:Q')
                
                # Renderiza a fusão do gráfico com o texto
                st.altair_chart(barras_cidade + textos_cidade, use_container_width=True)
            else:
                st.caption("Nenhum dado de cidade disponível.")

    with g2:
        with st.container(border=True):
            st.markdown("#### 🕒 Média de O.S. por Janela de Atendimento (Com Contratos Ativos)")
            if not df_janelas_validas.empty:
                df_janelas_grafico = df_janelas_validas.groupby('Intervalo_Tratado')['Total_OS_Num'].mean().reset_index()
                df_janelas_grafico.columns = ['Janela Horário', 'Média de OS']
                df_janelas_grafico['Média de OS'] = df_janelas_grafico['Média de OS'].round(2)
                df_janelas_grafico = df_janelas_grafico.sort_values(by='Média de OS', ascending=False)
                
                # Cria a barra do gráfico
                barras_janela = alt.Chart(df_janelas_grafico).mark_bar(color='#ff9800').encode(
                    x=alt.X('Janela Horário:N', sort='-y', title='Janela de Horário'),
                    y=alt.Y('Média de OS:Q', title='Média de O.S.')
                )
                # Cria o rótulo com o valor no topo
                textos_janela = barras_janela.mark_text(
                    align='center', baseline='bottom', dy=-4, fontWeight='bold'
                ).encode(text='Média de OS:Q')
                
                st.altair_chart(barras_janela + textos_janela, use_container_width=True)
            else:
                st.info("Nenhuma janela com contrato ativo identificada para cálculo.")

    # ==========================================
    # BLOCO 3: DETALHAMENTO DA TABELA ANALÍTICA
    # ==========================================
    with st.container(border=True):
        st.markdown("#### 🔍 Visão Analítica Consolidada")
        if 'SUPERVISOR' in df_dash_filtrado.columns:
            df_analitico = df_dash_filtrado.groupby(['SUPERVISOR', 'Cidade_Tratada']).agg(
                Contratos_Unicos=('Contrato_Limpo', 'nunique'),
                Total_Tarefas_OS=('Total_OS_Num', 'sum'),
                Media_OS_Contrato=('Total_OS_Num', 'mean')
            ).reset_index()
            
            df_analitico.columns = ['Supervisor', 'Cidade', 'Contratos Únicos', 'Soma Total OS', 'Média OS/Contrato']
            st.dataframe(df_analitico.sort_values(by='Contratos Únicos', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_dash_filtrado[['Contrato_Limpo', 'Cidade_Tratada', 'Total_OS_Num']], use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Não foi possível carregar os dados online da planilha para gerar os dashboards.")
