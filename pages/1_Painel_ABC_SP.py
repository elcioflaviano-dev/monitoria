import streamlit as st
import pandas as pd
import altair as alt  
from datetime import datetime, timedelta

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Customização CSS para deixar os títulos de bases bem destacados
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 16px !important; }
    
    .section-base-title {
        background-color: #005088;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        font-size: 18px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📊 PAINEL ABC SP - DASHBOARDS</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_dash = st.session_state.get('df_rota_ativa', None)

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO ---
if df_dash is not None:
    data_rota_texto = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Dados updated via Upload em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Aguardando sincronização de dados</div>', unsafe_allow_html=True)

if df_dash is not None and not df_dash.empty:
    
    # === HIGIENIZAÇÃO DOS DADOS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_dash.columns else 'Status da Atividade'
    df_dash['Status_Atividade_Upper'] = df_dash[col_status].fillna('').astype(str).str.upper().str.strip()
    
    cond_contrato_valido = (
        (df_dash['Contrato_Limpo'] != '') & 
        (df_dash['Contrato_Limpo'] != 'nan') & 
        (~df_dash['Contrato_Limpo'].str.contains('#N/A', case=False, na=False)) &
        (~df_dash['Status_Atividade_Upper'].str.contains('SUSPENSO', case=False, na=False))
    )
    
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

    # Identificação da coluna de recurso/técnico e base
    col_recurso = 'Recurso' if 'Recurso' in df_dash_filtrado.columns else df_dash_filtrado.columns[0]
    col_base_operacional = 'REGIAO_BASE' if 'REGIAO_BASE' in df_dash_filtrado.columns else ('Cidade' if 'Cidade' in df_dash_filtrado.columns else 'GERAL')
    
    if col_base_operacional not in df_dash_filtrado.columns:
        df_dash_filtrado['REGIAO_BASE'] = 'BASE GERAL'
        col_base_operacional = 'REGIAO_BASE'
    else:
        df_dash_filtrado[col_base_operacional] = df_dash_filtrado[col_base_operacional].fillna('NÃO DEFINIDA').astype(str).str.upper().str.strip()
        df_dash_filtrado[col_base_operacional] = df_dash_filtrado[col_base_operacional].replace({'NAN': 'NÃO DEFINIDA', '': 'NÃO DEFINIDA', '#N/A': 'NÃO DEFINIDA'})

    # === FILTRO DE SUPERVISOR ===
    if 'SUPERVISOR' in df_dash_filtrado.columns:
        lista_supervisores = ["TODOS"] + sorted(df_dash_filtrado['SUPERVISOR'].dropna().unique())
        supervisor_sel = st.sidebar.selectbox("Filtrar por Supervisor:", lista_supervisores)
        
        if supervisor_sel != "TODOS":
            df_dash_filtrado = df_dash_filtrado[df_dash_filtrado['SUPERVISOR'] == supervisor_sel]

    # =========================================================================
    # 🌟 BLOCO 1 SEPARADO POR BASES OPERACIONAIS (CONFORME SOLICITADO)
    # =========================================================================
    bases_disponiveis = sorted(df_dash_filtrado[col_base_operacional].unique())
    
    for base in bases_disponiveis:
        # Isola os dados exclusivos da base atual
        df_base_atual = df_dash_filtrado[df_dash_filtrado[col_base_operacional] == base]
        
        # Cria a barra divisória com o nome da base
        st.markdown(f'<div class="section-base-title">📍 BASE OPERACIONAL: {base}</div>', unsafe_allow_html=True)
        
        # Cálculos específicos da Base
        base_contratos = df_base_atual['Contrato_Limpo'].nunique()
        base_total_os = df_base_atual['Total_OS_Num'].sum()
        base_qtd_tecnicos = df_base_atual[col_recurso].nunique() if col_recurso in df_base_atual.columns else 1
        if base_qtd_tecnicos == 0: base_qtd_tecnicos = 1
        
        # Novas médias baseadas no número de técnicos ativos daquela base
        media_contratos_por_tec = base_contratos / base_qtd_tecnicos
        media_os_por_tec = base_total_os / base_qtd_tecnicos
        
        # Renderiza os 4 cards da Base Lado a Lado
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">📋 Total Contratos</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#008080;">{base_contratos}</div>', unsafe_allow_html=True)
        with m2:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🛠️ Volume Total OS</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#333;">{base_total_os}</div>', unsafe_allow_html=True)
        with m3:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">👤 Média Contratos / Téc</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#008080;">{media_contratos_por_tec:.2f}</div>', unsafe_allow_html=True)
        with m4:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">⚡ Média OS / Téc</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#ff9800;">{media_os_por_tec:.2f}</div>', unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # BLOCO 2: GRÁFICOS ANALÍTICOS GERAIS
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
            df_janelas_validas = df_dash_filtrado[
                (df_dash_filtrado['Intervalo_Tratado'] != '') & 
                (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
                (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('PADRAO'))
            ]
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
