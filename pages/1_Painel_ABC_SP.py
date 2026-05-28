import streamlit as st
import pandas as pd
import altair as alt  
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

# 🌟 ALTERADO: Agora o sistema herda os dados atualizados que você carregou via Upload na Home
df_dash = st.session_state.get('df_rota_ativa', None)

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO ---
if df_dash is not None:
    data_rota_texto = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Dados atualizados via Upload em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Aguardando sincronização de dados</div>', unsafe_allow_html=True)

if df_dash is not None and not df_dash.empty:
    
    # === HIGIENIZAÇÃO DOS DADOS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    
    # Ajuste para identificar a coluna de status tratada ou original
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_dash.columns else 'Status da Atividade'
    df_dash['Status_Atividade_Upper'] = df_dash[col_status].fillna('').astype(str).str.upper().str.strip()
    
    cond_contrato_valido = (
        (df_dash['Contrato_Limpo'] != '') & 
        (df_dash['Contrato_Limpo'] != 'nan') & 
        (~df_dash['Contrato_Limpo'].str.contains('#N/A', case=False, na=False)) &
        (~df_dash['Status_Atividade_Upper'].str.contains('SUSPENSO', case=False, na=False))
    )
    
    # Identifica coluna Tipo de Atividade dinamicamente
    col_tipo_ativ = 'Tipo de Atividade' if 'Tipo de Atividade' in df_dash.columns else 'TIPO DE ATIVIDADE'
    if col_tipo_ativ in df_dash.columns:
        cond_contrato_valido = cond_contrato_valido & (~df_dash[col_tipo_ativ].fillna('').astype(str).str.contains('Refeicao', case=False, na=False))
        
    df_dash_filtrado = df_dash[cond_contrato_valido].copy()
    df_dash_filtrado['Contrato_Limpo'] = df_dash_filtrado['Contrato_Limpo'].apply(lambda x: str(x).split('.')[0].strip())

    df_dash_filtrado['Cidade_Tratada'] = df_dash_filtrado['Cidade'].fillna('NÃO INFORMADA').astype(str).str.upper().str.strip() if 'Cidade' in df_dash_filtrado.columns else 'NÃO INFORMADA'
    
    col_tarefas = 'QTD_OS_COL' if 'QTD_OS_COL' in df_dash_filtrado.columns else 'Total de tarefas'
    df_dash_filtrado['Total_OS_Num'] = pd.to_numeric(df_dash_filtrado[col_tarefas], errors='coerce').fillna(0).astype(int) if col_tarefas in df_dash_filtrado.columns else 1

    col_intervalo = 'Janela de Serviço' if 'Janela de Serviço' in df_dash_filtrado.columns else 'Intervalo de Tempo'
    df_dash_filtrado['Intervalo_Tratado'] = df_dash_filtrado[col_intervalo].fillna('').astype(str).str.strip() if col_intervalo in df_dash_filtrado.columns else ''

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
    # BLOCO 2: GRÁFICOS ANALÍTICOS (ALTAIR)
    # ==========================================
    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            st.markdown("#### 🌆 Volume Total de O.S. por Cidade")
            df_cidades_os = df_dash_filtrado.groupby('Cidade_Tratada')['Total_OS_Num'].sum().reset_index()
            df_cidades_os.columns = ['Cidade', 'Total OS']
            df_cidades_os = df_cidades_os.sort_values(by='Total OS', ascending=False)
            
            if not df_cidades_os.empty:
                barras_cidade = alt.Chart(df_cidades_os).mark_bar(color='#008080').encode(
                    x=alt.X('Cidade:N', sort='-y', title='Cidade'),
                    y=alt.Y('Total OS:Q', title='Volume de O.S.')
                )
                textos_cidade = barras_cidade.mark_text(
                    align='center', baseline='bottom', dy=-4, fontWeight='bold'
                ).encode(text='Total OS:Q')
                
                st.altair_chart(barras_cidade + textos_cidade, use_container_width=True)
            else:
                st.caption("Nenhum dado de O.S. por cidade disponível.")

    with g2:
        with st.container(border=True):
            st.markdown("#### 🕒 Média de O.S. por Janela de Atendimento")
            if not df_janelas_validas.empty:
                df_janelas_grafico = df_janelas_validas.groupby('Intervalo_Tratado')['Total_OS_Num'].mean().reset_index()
                df_janelas_grafico.columns = ['Janela Horário', 'Média de OS']
                df_janelas_grafico['Média de OS'] = df_janelas_grafico['Média de OS'].round(2)
                df_janelas_grafico = df_janelas_grafico.sort_values(by='Média de OS', ascending=False)
                
                barras_janela = alt.Chart(df_janelas_grafico).mark_bar(color='#ff9800').encode(
                    x=alt.X('Janela Horário:N', sort='-y', title='Janela de Horário'),
                    y=alt.Y('Média de OS:Q', title='Média de O.S.')
                )
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
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro para gerar os gráficos.")
