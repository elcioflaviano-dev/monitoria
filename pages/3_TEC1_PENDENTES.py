import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela (Idêntico ao TEC1)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título Centralizado no mesmo padrão visual
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #cc6600; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1 PENDENTES</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA INTELIGENTE: Puxa o DataFrame unificado da memória global (Home)
df_master = st.session_state.get('df_rota_ativa', None)

st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em tempo real via Upload</div>', unsafe_allow_html=True)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === ALINHAMENTO DE COLUNAS OPERACIONAIS ===
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df.columns else ('Status da Atividade' if 'Status da Atividade' in df.columns else None)
    
    if col_status:
        df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
    else:
        df['Status_Atividade_Upper'] = ''
        
    # Filtragem de segurança: Remove suspensos
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove as marcações operacionais de almoço (Refeicao)
    for c in df_limpo.columns:
        if 'TIPO' in str(c).upper():
            df_limpo['Tipo_Activity_Str'] = df_limpo[c].fillna('').astype(str)
            df_limpo = df_limpo[~df_limpo['Tipo_Activity_Str'].str.contains('Refeicao', case=False, na=False)]
            break
        
    # Tratamento e montagem do filtro dinâmico de Janelas
    col_janela = 'Janela de Serviço' if 'Janela de Serviço' in df_limpo.columns else None
    if not col_janela:
        for c in df_limpo.columns:
            if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
                col_janela = c
                break
            
    if col_janela is not None:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        df_janelas_validas = df_limpo[
            (df_limpo['Intervalo_Tratado'] != '') & 
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA'))
        ].copy()
        
        opcoes_janela = sorted(df_janelas_validas['Intervalo_Tratado'].dropna().unique())
        opcoes_janela = [j for j in opcoes_janela if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_limpo.copy()
    else:
        df_tela = df_limpo.copy()

    if df_tela.empty:
        st.warning("⚠️ Não existem dados correspondentes para os filtros aplicados nesta janela.")
    else:
        # 🌟 FILTRO CRÍTICO: Conta e mantém APENAS quem tem status PENDENTE ou EM ABERTO
        df_tela['P_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
        
        # Filtra a tabela para focar estritamente em pendências de campo
        df_tela = df_tela[df_tela['P_COUNT'] > 0].copy()

        # Identifica o nome ou login do recurso
        col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
        if not col_rec:
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                    col_rec = c
                    break
        df_tela['Recurso_Tratado'] = df_tela[col_rec].fillna('TÉCNICO PENDENTE').astype(str).str.upper() if col_rec else 'TÉCNICO PENDENTE'

        # Define quem vai aparecer no topo do cartão (Se tiver supervisor amarrado mostra ele, senão mostra o técnico)
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

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            
            if not df_abc.empty:
                # Agrupa e soma os contratos pendentes
                matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')['P_COUNT'].sum().reset_index()
                
                for supervisor in sorted(matriz_abc['SUPERVISOR_MOSTRAR'].unique()):
                    total_pendentes = int(matriz_abc[matriz_abc['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]['P_COUNT'])
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:18px; font-weight:bold; margin-bottom:10px;">👤 ' + str(supervisor) + ' <span style="float:right; font-size:14px; background-color:#ffebee; padding:2px 8px; border-radius:4px; color:#c62828;">Pendentes: ' + str(total_pendentes) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(total_pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2:
                            st.metric(label="🟣 EM ROTA", value=0)
                        with m3:
                            st.metric(label="🟢 INICIADO", value=0)
            else:
                st.info("Nenhum contrato pendente localizado para o ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            
            if not df_sp.empty:
                # Agrupa e soma os contratos pendentes
                matriz_sp = df_sp.groupby('SUPERVISOR_MOSTRAR')['P_COUNT'].sum().reset_index()
                
                for supervisor in sorted(matriz_sp['SUPERVISOR_MOSTRAR'].unique()):
                    total_pendentes = int(matriz_sp[matriz_sp['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]['P_COUNT'])
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:18px; font-weight:bold; margin-bottom:10px;">👤 ' + str(supervisor) + ' <span style="float:right; font-size:14px; background-color:#ffebee; padding:2px 8px; border-radius:4px; color:#c62828;">Pendentes: ' + str(total_pendentes) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(total_pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2:
                            st.metric(label="🟣 EM ROTA", value=0)
                        with m3:
                            st.metric(label="🟢 INICIADO", value=0)
            else:
                st.info("Nenhum contrato pendente localizado para SP nesta janela.")

    # MODO TV AUTOMÁTICO (Sincronizado)
    st.components.v1.html("""
        <script>
        setTimeout(function(){ window.parent.location.hash = "#certidao"; }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
