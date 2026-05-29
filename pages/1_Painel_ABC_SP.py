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

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO ---
if df_dash is not None:
    data_rota_texto = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
    st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 25px;">🔄 Dados atualizados via Upload em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)
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

    col_recurso = 'Recurso' if 'Recurso' in df_dash_filtrado.columns else df_dash_filtrado.columns[0]
    
    # Tratamento da Base Operacional
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
    # ⏱️ MOTOR: 1º ATENDIMENTO OPERACIONAL (CARDS DO TOPO)
    # =========================================================================
    media_abc, media_sp = "--:--", "--:--"
    df_calc_atend = df_dash.copy()
    
    col_inicio_estrito = 'Início'
    for c in df_calc_atend.columns:
        c_clean = str(c).upper().strip().split('.')[0]
        if c_clean in ['INÍCIO', 'INICIO'] and '-' not in str(c) and 'DO' not in str(c).upper():
            col_inicio_estrito = c
            break

    col_supervisor_atend = 'SUPERVISOR' if 'SUPERVISOR' in df_calc_atend.columns else None
    if not col_supervisor_atend:
        for c in df_calc_atend.columns:
            if 'SUPERV' in str(c).upper(): col_supervisor_atend = c; break

    series_recurso = df_calc_atend[col_recurso] if col_recurso in df_calc_atend.columns else df_calc_atend.iloc[:, 0]
    series_status = df_calc_atend[col_status] if col_status in df_calc_atend.columns else df_calc_atend.iloc[:, 3]
    series_inicio = df_calc_atend[col_inicio_estrito] if col_inicio_estrito in df_calc_atend.columns else df_calc_atend.iloc[:, 10]
    series_supervisor = df_calc_atend[col_supervisor_atend] if col_supervisor_atend and col_supervisor_atend in df_calc_atend.columns else pd.Series([''] * len(df_calc_atend))

    df_base_atend = pd.DataFrame({
        'Técnico': [str(x).strip() for x in series_recurso.fillna('N/A').tolist()],
        'Status_OS': [str(x).lower().strip() for x in series_status.fillna('').tolist()],
        'Hora_Inicio': [tratar_horario(x) for x in series_inicio.tolist()],
        'Supervisor_Bruto': [str(x).upper().strip() for x in series_supervisor.fillna('').tolist()]
    })
    
    df_sup_map = df_base_atend[(df_base_atend['Supervisor_Bruto'] != '') & (~df_base_atend['Supervisor_Bruto'].isin(['N/A', 'NAN', '#N/A']))].groupby('Técnico')['Supervisor_Bruto'].first().reset_index(name='Sup_Valido')
    df_base_atend = pd.merge(df_base_atend, df_sup_map, on='Técnico', how='left')
    df_base_atend['Supervisor'] = df_base_atend['Sup_Valido'].fillna(df_base_atend['Supervisor_Bruto'])

    if 'SUPERVISOR' in df_dash_filtrado.columns and supervisor_sel != "TODOS":
        df_base_atend = df_base_atend[df_base_atend['Supervisor'] == supervisor_sel]

    df_filtrado_atend = df_base_atend[
        (df_base_atend['Status_OS'].str.contains('concl|inic|susp', na=False)) &
        (df_base_atend['Hora_Inicio'].notna())
    ].copy()
    
    if not df_filtrado_atend.empty:
        df_primeiros_horarios = df_filtrado_atend.sort_values('Hora_Inicio').groupby('Técnico').first().reset_index()
        cond_sp_atend = df_primeiros_horarios['Supervisor'].fillna('').str.contains("FRANCISCO|ALAN", na=False)
        
        horas_abc = df_primeiros_horarios[~cond_sp_atend]['Hora_Inicio'].tolist()
        horas_sp = df_primeiros_horarios[cond_sp_atend]['Hora_Inicio'].tolist()
        
        media_abc = calcular_media_horarios(horas_abc)
        media_sp = calcular_media_horarios(horas_sp)

    # Renderização Topo: Médias do 1º Contrato
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
    # 📊 SEÇÃO INDICADORES MACRO: ORDENADO COM TÉCNICOS NO MEIO (CARDS INVERTIDOS)
    # =========================================================================
    bases_disponiveis = sorted(df_dash_filtrado[col_base_operacional].unique())
    
    for base in bases_disponiveis:
        df_base_atual = df_dash_filtrado[df_dash_filtrado[col_base_operacional] == base]
        
        # Barra azul de cabeçalho da base
        st.markdown(f'<div class="section-base-title">📍 BASE OPERACIONAL: {base}</div>', unsafe_allow_html=True)
        
        # Cálculos específicos da Base Atual
        base_qtd_tecnicos = df_base_atual[col_recurso].nunique() if col_recurso in df_base_atual.columns else 0
        base_contratos = df_base_atual['Contrato_Limpo'].nunique()
        base_total_os = df_base_atual['Total_OS_Num'].sum()
        
        divisor_tecnicos = base_qtd_tecnicos if base_qtd_tecnicos > 0 else 1
        media_contratos_por_tec = base_contratos / divisor_tecnicos
        media_os_por_tec = base_total_os / divisor_tecnicos
        
        # Renderização organizada: Técnicos movido para a Coluna 3 (Meio)
        m1, m2, m3, m4, m5 = st.columns(5)
        
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
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🏃‍♂️ Técnicos com Rota</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#005088;">{base_qtd_tecnicos}</div>', unsafe_allow_html=True)
        with m4:
            with st.container(border=True):
                st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">👤 Média Contratos / Téc</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:28px; font-weight:900; color:#008080;">{media_contratos_por_tec:.2f}</div>', unsafe_allow_html=True)
        with m5:
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
