import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página e força layout 100% compacto
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Injeta CSS customizado para enxugar espaços e fixar tamanhos
st.markdown("""
    <style>
        /* Reduz margens do Streamlit */
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        
        /* Reduz tamanhos dos títulos de blocos */
        .title-abc-sp { font-size: 20px !important; font-weight: 800 !important; margin-bottom: 5px !important; text-align: center; }
        
        /* Caixa de Pendentes Compacta */
        .compact-box {
            background-color: #ffebee;
            border: 2px solid #ef9a9a;
            border-radius: 6px;
            padding: 8px;
            text-align: center;
        }
        .compact-label { font-size: 11px !important; font-weight: bold; color: #c62828; }
        .compact-value { font-size: 28px !important; font-weight: 900; color: #b71c1c; line-height: 1.1; }
        
        /* Tabela Compacta Interna */
        .scroll-table {
            max-height: 120px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            background: #fff;
        }
    </style>
""", unsafe_allow_html=True)

# Título Principal Enxuto
st.markdown(
    '<h1 style="font-size: 28px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 5px; margin-bottom: 2px;">⏳ TEC1 PENDENTES</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA INTELIGENTE
df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === PASSO 1: LIMPEZA DE LINHAS VAZIAS ===
    col_tecnico_check = 'Login do Técnico' if 'Login do Técnico' in df.columns else None
    if not col_tecnico_check:
        for c in df.columns:
            if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                col_tecnico_check = c
                break
                
    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
    
    if 'Contrato' in df.columns:
        df = df[df['Contrato'].fillna('').astype(str).str.strip() != ''].copy()

    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    df['Status_Atividade_Upper'] = df['STATUS_ATIVIDADE'].fillna('').astype(str).str.upper().str.strip() if 'STATUS_ATIVIDADE' in df.columns else ''
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Activity_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]

    # PASSO 2: FILTRAGEM PRÉVIA DOS CONTRATOS PENDENTES
    df_limpo['P_COUNT'] = df_limpo['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
    df_validos = df_limpo[df_limpo['P_COUNT'] > 0].copy()
        
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_validos.columns else None
    if not col_janela:
        for c in df_validos.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): col_janela = c; break
            
    if col_janela is not None and not df_validos.empty:
        df_validos['Intervalo_Tratado'] = df_validos[col_janela].fillna('').astype(str).str.strip()
        df_janelas_filtradas = df_validos[(df_validos['Intervalo_Tratado'] != '') & (df_validos['Intervalo_Tratado'].str.len() <= 7)].copy()
        opcoes_janela = sorted(df_janelas_filtradas['Intervalo_Tratado'].dropna().unique())
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_validos[df_validos['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_validos.copy()
    else:
        df_tela = df_validos.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem contratos pendentes para esta janela.")
    else:
        # Identifica o nome ou login do recurso
        col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
        if not col_rec:
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper(): col_rec = c; break
        df_tela['Recurso_Tratado'] = df_tela[col_rec].fillna('TÉCNICO').astype(str).str.upper() if col_rec else 'TÉCNICO'

        # Define quem vai aparecer no topo do cartão
        if 'SUPERVISOR' in df_tela.columns:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela.apply(
                lambda r: str(r['Recurso_Tratado']).upper() if str(r['SUPERVISOR']).strip().upper() in ['#N/A', 'NAN', '', 'PENDENTE CADASTRO'] else str(r['SUPERVISOR']).upper(), axis=1
            )
        else:
            df_tela['SUPERVISOR_MOSTRAR'] = df_tela['Recurso_Tratado']
            
        df_tela['SUPERVISOR_MOSTRAR'] = df_tela['SUPERVISOR_MOSTRAR'].astype(str).str.upper().str.strip()

        # Divisão Regional utilizando as travas de segurança da Home
        cond_sp = (
            df_tela['REGIAO_BASE'].fillna('').astype(str).str.upper().str.strip().str.contains('SÃO PAULO|SP', na=False) |
            df_tela['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN', na=False)
        )
        
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        # Renderização em Duas Colunas Lado a Lado
        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                supervisores_abc = sorted(df_abc['SUPERVISOR_MOSTRAR'].unique())
                for supervisor in supervisores_abc:
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    # Container ultra compacto: Caixa vermelha à esquerda, Lista à direita
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:13px; font-weight:bold; margin-bottom:4px; color:#111;">👤 {supervisor}</div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.markdown(f'<div class="compact-box"><div class="compact-label">PENDENTES</div><div class="compact-value">{total_pendentes}</div></div>', unsafe_allow_html=True)
                        with c2:
                            df_mini = df_super[['Contrato', 'Recurso_Tratado']].rename(columns={'Contrato':'Contrato', 'Recurso_Tratado':'Técnico'})
                            # Renderiza como DataFrame nativo mas super achatado para não criar scroll na página principal
                            st.dataframe(df_mini, use_container_width=True, hide_index=True, height=65)
            else:
                st.info("Nenhum pendente no ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                supervisores_sp = sorted(df_sp['SUPERVISOR_MOSTRAR'].unique())
                for supervisor in supervisores_sp:
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    total_pendentes = df_super['P_COUNT'].sum()
                    
                    # Container ultra compacto: Caixa vermelha à esquerda, Lista à direita
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:13px; font-weight:bold; margin-bottom:4px; color:#111;">👤 {supervisor}</div>', unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.markdown(f'<div class="compact-box"><div class="compact-label">PENDENTES</div><div class="compact-value">{total_pendentes}</div></div>', unsafe_allow_html=True)
                        with c2:
                            df_mini = df_super[['Contrato', 'Recurso_Tratado']].rename(columns={'Contrato':'Contrato', 'Recurso_Tratado':'Técnico'})
                            st.dataframe(df_mini, use_container_width=True, hide_index=True, height=65)
            else:
                st.info("Nenhum pendente em SP.")

    # MODO TV AUTOMÁTICO
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#certidao"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Insira os arquivos na página inicial primeiro.")
