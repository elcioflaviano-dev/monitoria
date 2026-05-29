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

# Customização CSS para os Cards do 1º Atendimento (Topo) e Seções de Bases
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem !important; }
    div[data-testid="stHorizontalBlock"] { gap: 12px !important; }
    
    /* Grid dos Cards de KPI do 1º Contrato (Topo) */
    .kpi-container-atend {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-bottom: 15px;
    }
    .kpi-card-atend {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        padding: 10px 25px;
        text-align: center;
        min-width: 280px;
        border-top: 5px solid #006677;
    }
    .kpi-card-atend.abc { border-top-color: #008080; }
    .kpi-card-atend.sp { border-top-color: #b30000; }
    .kpi-title-atend { font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase; margin-bottom: 4px; }
    .kpi-value-atend { font-size: 26px; color: #111; font-weight: 900; }
    
    /* Faixa de Título das Bases Operacionais */
    .section-base-title {
        background-color: #005088;
        color: white;
        padding: 8px 15px;
        border-radius: 4px;
        font-size: 16px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📊 PAINEL ABC SP - DASHBOARDS</h1>', unsafe_allow_html=True)

# 🔄 HERANÇA INTELIGENTE DIRETA DA HOME
df_dash = st.session_state.get('df_rota_ativa', None)

# --- FUNÇÕES AUXILIARES PARA O CÁLCULO DE MÉDIAS DO 1º CONTRATO ---
def tratar_horario(val):
    if pd.isna(val) or str(val).strip() in ['', 'N/A', 'NAN', 'NaN', '00:00']:
        return None
    try:
        texto = str(val).strip().split()[-1]
        return datetime.strptime(texto, '%H:%M:%S').time()
    except:
        try:
            texto = str(val).strip().split()[-1]
            return datetime.strptime(texto, '%H:%M').time()
        except:
            return None

def calcular_media_horarios(lista_horas):
    if not lista_horas:
        return "--:--"
    total_segundos = 0
    qtd = 0
    for h in lista_horas:
        if h is not None:
            total_segundos += h.hour * 3600 + h.minute * 60 + h.second
            qtd += 1
    if qtd == 0:
        return "--:--"
    media_segundos = total_segundos / qtd
    media_time = str(timedelta(seconds=int(media_segundos)))
    return ":".join(media_time.split(":")[:2])

if df_dash is not None and not df_dash.empty:
    
    # === HIGIENIZAÇÃO INICIAL DA BASE ===
    df_working = df_dash.copy()
    df_working['Contrato_Limpo'] = df_working['Contrato'].fillna('').astype(str).str.strip()
    
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df_working.columns else 'Status da Atividade'
    df_working['Status_Atividade_Upper'] = df_working[col_status].fillna('').astype(str).str.upper().str.strip()
    
    # Localização dinâmica e forçada da coluna de Atividade
    col_tipo_atv_real = 'Tipo de Atividade'
    for c in df_working.columns:
        if 'TIPO' in str(c).upper() and 'ATIV' in str(c).upper():
            col_tipo_atv_real = c
            break
            
    df_working['Tipo_Atividade_Upper'] = df_working[col_tipo_atv_real].fillna('').astype(str).str.upper().str.strip()

    # Filtro base saudável (remove suspensos, almoço e bases vazias)
    cond_saudavel = (
        (df_working['Contrato_Limpo'] != '') & 
        (df_working['Contrato_Limpo'] != 'nan') & 
        (~df_working['Contrato_Limpo'].str.contains('#N/A', na=False)) &
        (~df_working['Status_Atividade_Upper'].str.contains('SUSPENSO', na=False)) &
        (~df_working['Tipo_Atividade_Upper'].str.contains('REFEI', na=False))
    )
    df_working = df_working[cond_saudavel].copy()

    # Identificação das colunas estruturais
    col_recurso = 'Recurso' if 'Recurso' in df_working.columns else df_working.columns[0]
    
    col_base_operacional = 'REGIAO_BASE' if 'REGIAO_BASE' in df_working.columns else ('Cidade' if 'Cidade' in df_working.columns else 'GERAL')
    if col_base_operacional not in df_working.columns:
        df_working['REGIAO_BASE'] = 'BASE GERAL'
        col_base_operacional = 'REGIAO_BASE'
    else:
        df_working[col_base_operacional] = df_working[col_base_operacional].fillna('NÃO DEFINIDA').astype(str).str.upper().str.strip()
        df_working[col_base_operacional] = df_working[col_base_operacional].replace({'NAN': 'NÃO DEFINIDA', '': 'NÃO DEFINIDA', '#N/A': 'NÃO DEFINIDA'})

    df_working['Cidade_Tratada'] = df_working['Cidade'].fillna('NÃO INFORMADA').astype(str).str.upper().str.strip() if 'Cidade' in df_working.columns else 'NÃO INFORMADA'
    
    col_tarefas = 'QTD_OS_COL' if 'QTD_OS_COL' in df_working.columns else 'Total de tarefas'
    df_working['Total_OS_Num'] = pd.to_numeric(df_working[col_tarefas], errors='coerce').fillna(0).astype(int) if col_tarefas in df_working.columns else 1
    
    col_intervalo = 'Janela de Serviço' if 'Janela de Serviço' in df_working.columns else 'Intervalo de Tempo'
    df_working['Intervalo_Tratado'] = df_working[col_intervalo].fillna('').astype(str).str.strip() if col_intervalo in df_working.columns else ''

    # Filtro Lateral de Supervisor
    if 'SUPERVISOR' in df_working.columns:
        lista_supervisores = ["TODOS"] + sorted(df_working['SUPERVISOR'].dropna().unique())
        supervisor_sel = st.sidebar.selectbox("Filtrar por Supervisor:", lista_supervisores)
        if supervisor_sel != "TODOS":
            df_working = df_working[df_working['SUPERVISOR'] == supervisor_sel]

    # =========================================================================
    # ⏱| MOTOR: 1º ATENDIMENTO OPERACIONAL (TOPO FIXADO EM 8:15 / 8:05)
    # =========================================================================
    media_abc, media_sp = "--:--", "--:--"
    
    col_inicio_estrito = 'Início'
    for c in df_working.columns:
        c_clean = str(c).upper().strip().split('.')[0]
        if c_clean in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    df_filtrado_atend = df_working.copy()
    df_filtrado_atend['Hora_Inicio_Time'] = df_filtrado_atend[col_inicio_estrito].apply(tratar_horario)
    df_filtrado_atend = df_filtrado_atend[df_filtrado_atend['Hora_Inicio_Time'].notna()]
    
    if not df_filtrado_atend.empty:
        df_primeiros_horarios = df_filtrado_atend.sort_values('Hora_Inicio_Time').groupby(col_recurso).first().reset_index()
        
        col_supervisor_check = 'SUPERVISOR' if 'SUPERVISOR' in df_primeiros_horarios.columns else df_primeiros_horarios.columns[0]
        cond_sp_atend = df_primeiros_horarios[col_supervisor_check].fillna('').astype(str).str.upper().str.contains("FRANCISCO|ALAN", na=False)
        
        horas_abc = df_primeiros_horarios[~cond_sp_atend]['Hora_Inicio_Time'].tolist()
        horas_sp = df_primeiros_horarios[cond_sp_atend]['Hora_Inicio_Time'].tolist()
        
        media_abc = calcular_media_horarios(horas_abc)
        media_sp = calcular_media_horarios(horas_sp)

    # Renderização do Topo Fixo Correto
    st.markdown(f'''
        <div class="kpi-container-atend">
            <div class="kpi-card-atend abc">
                <div class="kpi-title-atend">⏱️ Média 1º Contrato - ABC</div>
                <div class="kpi-value-atend">{media_abc}</div>
            </div>
            <div class="kpi-card-atend sp">
                <div class="kpi-title-atend">⏱️ Média 1º Contrato - SÃO PAULO</div>
                <div class="kpi-value-atend">{media_sp}</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown("<hr style='margin-top:0px; margin-bottom:15px; border-color:#eee;'>", unsafe_allow_html=True)

    # =========================================================================
    # 📊 SEÇÃO INDICADORES MACRO: 6 CARDS COM FILTRAGEM SUBTRATIVA CORRETA
    # =========================================================================
    bases_disponiveis = sorted(df_working[col_base_operacional].unique())
    
    for base in bases_disponiveis:
        df_base_atual = df_working[df_working[col_base_operacional] == base]
        
        # 1. Totais Consolidados Brutos da Rota
        base_qtd_tecnicos = df_base_atual[col_recurso].nunique()
        base_contratos_bruto = df_base_atual['Contrato_Limpo'].nunique()
        base_total_os_bruto = df_base_atual['Total_OS_Num'].sum()
        
        # 2. Varredura e isolamento de Retornos na coluna real tratada
        cond_retorno_linha = df_base_atual['Tipo_Activity_Str'].str.contains('RETORNO', case=False, na=False) if 'Tipo_Activity_Str' in df_base_atual.columns else df_base_atual['Tipo_Atividade_Upper'].str.contains('RETORNO', na=False)
        df_retornos_base = df_base_atual[cond_retorno_linha]
        
        base_total_retornos = df_retornos_base['Contrato_Limpo'].nunique()
        base_total_os_retorno = df_retornos_base['Total_OS_Num'].sum()
        
        # 3. Engenharia Líquida Subtrativa
        base_contratos_liquido = base_contratos_bruto - base_total_retornos
        base_total_os_liquido = base_total_os_bruto - base_total_os_retorno
        
        divisor_tecnicos = base_qtd_tecnicos if base_qtd_tecnicos > 0 else 1
        media_contratos_por_tec = base_contratos_liquido / divisor_tecnicos
        media_os_por_tec = base_total_os_liquido / divisor_tecnicos
        
        # Barra de Cabeçalho da Base
        st.markdown(f'<div class="section-base-title">📍 BASE OPERACIONAL: {base}</div>', unsafe_allow_html=True)
        
        # FILA 1: Totais Gerais Brutos e Técnicos no meio
        r1_c1, r1_c2, r1_c3 = st.columns(3)
        with r1_c1:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">📋 Total Geral Contratos</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#008080;">{base_contratos_bruto}</div>', unsafe_allow_html=True)
        with r1_c2:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🛠️ Volume Total OS</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#333;">{base_total_os_bruto}</div>', unsafe_allow_html=True)
        with r1_c3:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🏃‍♂️ Técnicos com Rota</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#005088;">{base_qtd_tecnicos}</div>', unsafe_allow_html=True)
                
        # FILA 2: Card de Retorno Populado e as Novas Médias Líquidas Corretas
        r2_c1, r2_c2, r2_c3 = st.columns(3)
        with r2_c1:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">⚠️ Total de Retornos</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#b30000;">{base_total_retornos}</div>', unsafe_allow_html=True)
        with r2_c2:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">👤 Média Contratos / Téc (Líquida)</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#008080;">{media_contratos_por_tec:.2f}</div>', unsafe_allow_html=True)
        with r2_c3:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">⚡ Média OS / Téc (Líquida)</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:26px; font-weight:900; color:#ff9800;">{media_os_por_tec:.2f}</div>', unsafe_allow_html=True)

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # ==========================================
    # BLOCO 2: GRÁFICOS ANALÍTICOS GERAIS
    # ==========================================
    df_dash_grafico = df_working[~df_working['Tipo_Activity_Str'].str.contains('RETORNO', case=False, na=False) if 'Tipo_Activity_Str' in df_working.columns else ~df_working['Tipo_Atividade_Upper'].str.contains('RETORNO', na=False)].copy()
    
    g1, g2 = st.columns(2)

    with g1:
        with st.container(border=True):
            st.markdown("#### 🌆 Volume Total de O.S. por Cidade")
            df_cidades_os = df_dash_grafico.groupby('Cidade_Tratada')['Total_OS_Num'].sum().reset_index()
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
            df_janelas_validas = df_dash_grafico[
                (df_dash_grafico['Intervalo_Tratado'] != '') & 
                (~df_dash_grafico['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
                (~df_dash_grafico['Intervalo_Tratado'].str.upper().str.contains('PADRAO'))
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
        if 'SUPERVISOR' in df_working.columns:
            df_analitico = df_dash_grafico.groupby(['SUPERVISOR', 'Cidade_Tratada']).agg(
                Contratos_Unicos=('Contrato_Limpo', 'nunique'),
                Total_Tarefas_OS=('Total_OS_Num', 'sum'),
                Media_OS_Contrato=('Total_OS_Num', 'mean')
            ).reset_index()
            
            df_analitico.columns = ['Supervisor', 'Cidade', 'Contratos Únicos', 'Soma Total OS', 'Média OS/Contrato']
            st.dataframe(df_analitico.sort_values(by='Contratos Únicos', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_working[['Contrato_Limpo', 'Cidade_Tratada', 'Total_OS_Num']], use_container_width=True, hide_index=True)

else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro para gerar os gráficos.")
