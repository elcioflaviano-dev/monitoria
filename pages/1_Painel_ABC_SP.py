import streamlit as st
import pandas as pd

# 1. Configuração da página ampla padrão para tabelas gerenciais
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais (CSS)
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #005088; text-align: center; margin-top: 15px; margin-bottom: 5px;">📊 PAINEL TOA - PERFORMANCE REGIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 20px;">Acompanhamento macro de produção, ordens não efetuadas (NE) e taxa de quebra</div>', unsafe_allow_html=True)

# 🔄 3. HERANÇA INTELIGENTE: Puxa o DataFrame unificado da memória global (Home)
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

# Função Máster para Renderizar as Tabelas Executivas por Bloco
def processar_tabela_gerencial(df_bloco, nome_bloco):
    st.markdown(f'<div style="background-color:#005088; padding:6px 12px; color:white; font-weight:bold; font-size:18px; border-radius:4px; margin-top:15px; margin-bottom:10px;">{nome_bloco}</div>', unsafe_allow_html=True)
    
    if df_bloco.empty:
        st.info(f"Nenhum dado ativo para {nome_bloco} neste arquivo.")
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
        
    # Identifica volumes
    if 'QTD_OS_COL' in df_bloco.columns:
        df_bloco['QTD_OS_NUM'] = pd.to_numeric(df_bloco['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_bloco['QTD_OS_NUM'] = 1
        
    # Aplica a classificação de colunas
    df_bloco['Status_Calculado'] = df_bloco.apply(lambda r: classificar_status_excel(r['STATUS_OS1'], r['STATUS_ATIVIDADE']), axis=1)
    
    # Agrupamento e pivotagem para gerar a matriz gerencial igual ao Excel
    matriz = df_bloco.groupby(['SUPERVISOR', 'Status_Calculado'])['QTD_OS_NUM'].sum().unstack(fill_value=0).reset_index()
    
    # Garante a existência das colunas padrão
    for col in ['PRODUTIVO', 'O.S NE', 'EM ABERTO']:
        if col not in matriz.columns: matriz[col] = 0
        
    # Cálculos das métricas de diretoria
    matriz['Total Geral'] = matriz['PRODUTIVO'] + matriz['O.S NE'] + matriz['EM ABERTO']
    matriz['Quebra (%)'] = matriz.apply(
        lambda r: round((r['O.S NE'] / (r['PRODUTIVO'] + r['O.S NE'])) * 100, 1) if (r['PRODUTIVO'] + r['O.S NE']) > 0 else 0.0, axis=1
    )
    
    # Ordenação e seleção de colunas final
    matriz = matriz[['SUPERVISOR', 'PRODUTIVO', 'O.S NE', 'EM ABERTO', 'Total Geral', 'Quebra (%)']].sort_values(by='Total Geral', ascending=False)
    
    # Renderiza a tabela executiva limpa na tela
    st.dataframe(
        matriz.style.format({'Quebra (%)': '{:.1f}%'}),
        use_container_width=True, hide_index=True
    )

if df_master is not None and not df_master.empty:
    # Separação das bases usando as regras de PROCV da Home
    df_master['SUPERVISOR_CHECK'] = df_master['SUPERVISOR'].fillna('').astype(str).str.upper().str.strip()
    df_master['BASE_CHECK'] = df_master['REGIAO_BASE'].fillna('').astype(str).str.upper().str.strip()
    
    # Filtros de divisão regional por bloco
    cond_sp = df_master['BASE_CHECK'].isin(['SÃO PAULO', 'SP']) | df_master['SUPERVISOR_CHECK'].isin(['FRANCISCO', 'ALAN'])
    
    df_abc = df_master[~cond_sp].copy()
    df_sp = df_master[cond_sp].copy()
    
    # Renderiza os blocos TOA tradicionais na tela
    processar_tabela_gerencial(df_abc, "📍 BLOCO REGIONAL - ABCDM")
    processar_tabela_gerencial(df_sp, "📍 BLOCO REGIONAL - SÃO PAULO")

    # MODO TV AUTOMÁTICO (Aponta para a rota sequencial correta)
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#2-tec1"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
