import streamlit as st
import pandas as pd
import altair as alt  
from datetime import datetime, timedelta

# 1. Configuração da página ampla padrão
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #005088; text-align: center; margin-top: 15px; margin-bottom: 5px;">📊 PAINEL TOA - PERFORMANCE REGIONAL</h1>', unsafe_allow_html=True)

# 🔄 3. HERANÇA INTELIGENTE: Puxa o DataFrame unificado e com PROCV pronto da Home
df_master = st.session_state.get('df_rota_ativa', None)

# Regra Máster de Classificação do Excel
def classificar_status_excel(baixa, status_at):
    baixa = str(baixa).upper().strip()
    status_at = str(status_at).upper().strip()
    codigos_ne = ["101", "106", "110", "112", "113", "125", "203", "205", "206", "301", "305", "306", "402", "100"]
    for cod in codigos_ne:
        if baixa.startswith(cod) or f"{cod} -" in baixa: return "O.S NE"
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or "PENDENTE" in status_at: return "EM ABERTO"
    return "PRODUTIVO"

# Função Máster para Renderizar as Tabelas Executivas por Bloco Regional
def processar_tabela_gerencial(df_bloco, nome_bloco):
    st.markdown(f'<div style="background-color:#005088; padding:6px 12px; color:white; font-weight:bold; font-size:18px; border-radius:4px; margin-top:15px; margin-bottom:10px;">{nome_bloco}</div>', unsafe_allow_html=True)
    
    if df_bloco.empty:
        st.info(f"Nenhum dado ativo para {nome_bloco} neste bloco.")
        return
        
    df_bloco['Supervisor_Upper'] = df_bloco['SUPERVISOR'].apply(lambda x: str(x).strip().upper())
    df_bloco['Status_Atividade_Upper'] = df_bloco['STATUS_ATIVIDADE'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else '')
    df_bloco['Recurso_Upper'] = df_bloco['Recurso'].apply(lambda x: str(x).strip().upper())
    
    # Filtros operacionais originais de limpeza
    df_bloco = df_bloco[(~df_bloco['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN', 'PENDENTE CADASTRO'])) & (df_bloco['Status_Atividade_Upper'] != "SUSPENSO")].copy()
    df_bloco = df_bloco[~df_bloco['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)].copy()
    
    if df_bloco.empty:
        st.info(f"Nenhum dado consolidado para {nome_bloco} após filtros.")
        return
        
    # Identifica volumes das ordens
    if 'QTD_OS_COL' in df_bloco.columns:
        df_bloco['QTD_OS_NUM'] = pd.to_numeric(df_bloco['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_bloco['QTD_OS_NUM'] = 1
        
    # Aplica a classificação de colunas (Produtivo, NE, Aberto)
    df_bloco['Status_Calculado'] = df_bloco.apply(lambda r: classificar_status_excel(r['STATUS_OS1'], r['STATUS_ATIVIDADE']), axis=1)
    
    # Agrupamento e pivotagem para gerar a matriz gerencial igual ao Excel
    matriz = df_bloco.groupby(['SUPERVISOR', 'Status_Calculado'])['QTD_OS_NUM'].sum().unstack(fill_value=0).reset_index()
    
    for col in ['PRODUTIVO', 'O.S NE', 'EM ABERTO']:
        if col not in matriz.columns: matriz[col] = 0
        
    # Cálculos das métricas gerenciais
    matriz['Total Geral'] = matriz['PRODUTIVO'] + matriz['O.S NE'] + matriz['EM ABERTO']
    matriz['Quebra (%)'] = matriz.apply(
        lambda r: round((r['O.S NE'] / (r['PRODUTIVO'] + r['O.S NE'])) * 100, 1) if (r['PRODUTIVO'] + r['O.S NE']) > 0 else 0.0, axis=1
    )
    
    matriz = matriz[['SUPERVISOR', 'PRODUTIVO', 'O.S NE', 'EM ABERTO', 'Total Geral', 'Quebra (%)']].sort_values(by='Total Geral', ascending=False)
    
    st.dataframe(
        matriz.style.format({'Quebra (%)': '{:.1f}%'}),
        use_container_width=True, hide_index=True
    )

if df_master is not None and not df_master.empty:
    df_dash = df_master.copy()
    
    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    df_dash['Contrato_Limpo'] = df_dash['Contrato'].fillna('').astype(str).str.strip()
    df_dash['Status_Atividade_Upper'] = df_dash['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip()
    
    cond_contrato_valido = (
        (df_dash['Contrato_Limpo'] != '') & 
        (df_dash['Contrato_Limpo'] != 'nan') & 
        (~df_dash['Contrato_Limpo'].str.contains('#N/A', case=False, na=False)) &
        (~df_dash['Status_Atividade_Upper'].str.contains('SUSPENSO', case=False, na=False))
    )
    
    if 'Tipo de Atividade' in df_dash.columns:
        cond_contrato_valido = cond_contrato_valido & (~df_dash['Tipo de Atividade'].fillna('').astype(str).str.contains('Refeicao', case=False, na=False))
        
    df_dash_filtrado = df_dash[cond_contrato_valido].copy()
    df_dash_filtrado['Contrato_Limpo'] = df_dash_filtrado['Contrato_Limpo'].apply(lambda x: str(x).split('.')[0].strip())

    df_dash_filtrado['Cidade_Tratada'] = df_dash_filtrado['Cidade'].fillna('NÃO INFORMADA').astype(str).str.upper().str.strip() if 'Cidade' in df_dash_filtrado.columns else 'NÃO INFORMADA'
    df_dash_filtrado['Total_OS_Num'] = pd.to_numeric(df_dash_filtrado['QTD_OS_COL'], errors='coerce').fillna(0).astype(int) if 'QTD_OS_COL' in df_dash_filtrado.columns else 1
    df_dash_filtrado['Intervalo_Tratado'] = df_dash_filtrado['Janela de Serviço'].fillna('').astype(str).str.strip() if 'Janela de Serviço' in df_dash_filtrado.columns else ''

    # === MOTOR DE HORÁRIO AUTOMÁTICO (FUSO BRASÍLIA) ===
    if 'Intervalo_Tratado' in df_dash_filtrado.columns and not df_dash_filtrado.empty:
        hora_brasilia = (datetime.utcnow() - timedelta(hours=3)).hour
        
        if hora_brasilia < 11:
            janelas_automaticas = ['08 - 10']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela da Manhã (08 - 10)"
        elif 11 <= hora_brasilia < 15:
            janelas_automaticas = ['08 - 10', '11 - 14', '12:00 - 15:00']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela Ativa (11 - 14 / 12 - 15) + Acumulados"
        else:
            janelas_automaticas = ['08 - 10', '11 - 14', '12:00 - 15:00', '15 - 18']
            texto_status_janela = f"⏰ [Hora Local: {hora_brasilia:02d}h] - Janela da Tarde (15 - 18) + Tudo Pendente do Dia"

        # Monta o selectbox na barra lateral
        df_janelas_limpas = df_dash_filtrado[(df_dash_filtrado['Intervalo_Tratado'] != '') & (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) & (df_dash_filtrado['Intervalo_Tratado'].str.len() <= 15)].copy()
        opcoes_janela_todas = sorted(df_janelas_limpas['Intervalo_Tratado'].dropna().unique())
        
        lista_selectbox = ["AUTOMÁTICO 🔄"] + opcoes_janela_todas
        janela_sel = st.sidebar.selectbox("Filtrar por Janela:", lista_selectbox)
        
        if janela_sel == "AUTOMÁTICO 🔄":
            df_dash_filtrado = df_dash_filtrado[df_dash_filtrado['Intervalo_Tratado'].isin(janelas_automaticas)]
            st.markdown(f'<div style="text-align: center; color: #cc6600; font-size: 14px; font-weight: bold; margin-bottom: 15px;">{texto_status_janela}</div>', unsafe_allow_html=True)
        else:
            df_dash_filtrado = df_dash_filtrado[df_dash_filtrado['Intervalo_Tratado'] == janela_sel]
            st.markdown(f'<div style="text-align: center; color: #555; font-size: 14px; font-weight: bold; margin-bottom: 15px;">🎯 Filtro Manual Forçado: Janela {janela_sel}</div>', unsafe_allow_html=True)

    # === RENDIMENTO DAS TABELAS MASTER REGIONAIS (TOA) ===
    df_dash_filtrado['BASE_CHECK'] = df_dash_filtrado['REGIAO_BASE'].fillna('N/A').astype(str).str.upper().str.strip()
    df_dash_filtrado['SUPERVISOR_CHECK'] = df_dash_filtrado['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    
    # Separação rigorosa com base no cadastro do Sheets
    cond_sp = df_dash_filtrado['BASE_CHECK'].isin(['SÃO PAULO', 'SP', 'SAO PAULO']) | df_dash_filtrado['SUPERVISOR_CHECK'].isin(['FRANCISCO', 'ALAN'])
    
    df_sp_tabela = df_dash_filtrado[cond_sp].copy()
    df_abc_tabela = df_dash_filtrado[~cond_sp].copy()
    
    # Desenha as tabelas gerenciais corrigidas
    processar_tabela_gerencial(df_abc_tabela, "📍 BLOCO REGIONAL - ABCDM")
    processar_tabela_gerencial(df_sp_tabela, "📍 BLOCO REGIONAL - SÃO PAULO")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #005088; font-weight: 800;">📈 INDICADORES E ANÁLISE GRÁFICA</h3>', unsafe_allow_html=True)

    # ==========================================
    # BLOCO 1: KPIs CONSOLIDADOS
    # ==========================================
    total_contratos = df_dash_filtrado['Contrato_Limpo'].nunique()
    total_geral_os = df_dash_filtrado['Total_OS_Num'].sum()
    media_os_por_contrato = df_dash_filtrado['Total_OS_Num'].mean() if total_contratos > 0 else 0.0

    df_janelas_validas = df_dash_filtrado[
        (df_dash_filtrado['Intervalo_Tratado'] != '') & 
        (~df_dash_filtrado['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA'))
    ]
    media_os_janelas_reais = df_janelas_validas.groupby('Intervalo_Tratado')['Total_OS_Num'].mean().mean() if not df_janelas_validas.empty else 0.0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">📋 Total Contratos</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#005088;">{total_contratos}</div>', unsafe_allow_html=True)
    with m2:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🛠️ Volume Total OS</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#333;">{total_geral_os}</div>', unsafe_allow_html=True)
    with m3:
        with st.container(border=True):
            st.markdown(f'<div style="font-size:12px; font-weight:bold; color:#777; text-transform:uppercase;">🧮 Média OS / Contrato</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:28px; font-weight:900; color:#005088;">{media_os_por_contrato:.2f}</div>', unsafe_allow_html=True)
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
                barras_cidade = alt.Chart(df_cidades_os).mark_bar(color='#005088').encode(
                    x=alt.X('Cidade:N', sort='-y', title='Cidade'),
                    y=alt.Y('Total OS:Q', title='Volume de O.S.')
                )
                textos_cidade = barras_cidade.mark_text(align='center', baseline='bottom', dy=-4, fontWeight='bold').encode(text='Total OS:Q')
                st.altair_chart(barras_cidade + textos_cidade, use_container_width=True)
            else:
                st.caption("Nenhum dado de O.S. disponível.")

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
                textos_janela = barras_janela.mark_text(align='center', baseline='bottom', dy=-4, fontWeight='bold').encode(text='Média de OS:Q')
                st.altair_chart(barras_janela + textos_janela, use_container_width=True)
            else:
                st.info("Nenhuma janela identificada.")

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

    # MODO TV AUTOMÁTICO (Chama a sequência das páginas)
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#2-tec1"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
