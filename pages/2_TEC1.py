import streamlit as st
import pandas as pd
from datetime import datetime

# Configura a página para ocupar toda a largura da tela (Igual ao original)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Abre e injeta o arquivo style.css externo
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado e ajustado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# 🔄 HERANÇA INTELIGENTE: Puxa o DataFrame unificado da memória global (Home)
df_master = st.session_state.get('df_rota_ativa', None)

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em tempo real via Upload</div>', unsafe_allow_html=True)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # === 🌟 ALINHAMENTO DE COLUNAS OPERACIONAIS 🌟 ===
    # Mapeia dinamicamente para garantir que o Pandas ache os nomes corretos
    col_status = 'STATUS_ATIVIDADE' if 'STATUS_ATIVIDADE' in df.columns else ('Status da Atividade' if 'Status da Atividade' in df.columns else None)
    
    if col_status:
        df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
    else:
        df['Status_Atividade_Upper'] = ''
        
    # FILTRAGEM INTELIGENTE: Remove apenas status suspensos (não joga fora os #N/A para não sumir com os dados)
    df_limpo = df[df['Status_Atividade_Upper'] != 'SUSPENSO'].copy()
    
    # Remove as marcações operacionais de almoço (Refeicao)
    if 'Tipo de Atividade' in df_limpo.columns:
        df_limpo['Tipo_Atividade_Str'] = df_limpo['Tipo de Atividade'].fillna('').astype(str)
        df_limpo = df_limpo[~df_limpo['Tipo_Atividade_Str'].str.contains('Refeicao', case=False, na=False)]
        
    # Tratamento e montagem do filtro dinâmico de Janelas Válidas
    col_janela = None
    for c in df_limpo.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper():
            col_janela = c
            break
            
    if col_janela is not None:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        df_janelas_validas = df_limpo[
            (df_limpo['Intervalo_Tratado'] != '') & 
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('PADRAO'))
        ]
        opcoes_janela = sorted(df_janelas_validas['Intervalo_Tratado'].unique())
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_limpo.copy()
            janela_sel = "N/A"
    else:
        df_tela = df_limpo.copy()
        janela_sel = "N/A"

    # Se a tabela de exibição estiver vazia, avisa o usuário sem quebrar
    if df_tela.empty:
        st.warning("⚠️ Não existem dados correspondentes para os filtros aplicados nesta janela.")
    else:
        # Garantia de preenchimento dos campos nulos para exibição nos cartões
        if 'SUPERVISOR' not in df_tela.columns:
            df_tela['SUPERVISOR'] = 'SEM SUPERVISOR'
        else:
            df_tela['SUPERVISOR'] = df_tela['SUPERVISOR'].fillna('SEM SUPERVISOR').replace({'#N/A': 'PENDENTE CADASTRO', 'nan': 'SEM SUPERVISOR'})
            
        if 'REGIAO_BASE' not in df_tela.columns:
            df_tela['REGIAO_BASE'] = 'SP'

        # 🌟 SEPARAÇÃO PRECISA POR COLUNA REGIONAL (ABC vs SÃO PAULO)
        df_abc = df_tela[df_tela['REGIAO_BASE'] == 'ABC'].copy()
        df_sp = df_tela[df_tela['REGIAO_BASE'].isin(['SÃO PAULO', 'SP', 'GUARULHOS', 'N/A'])].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            
            supervisores_abc = df_abc['SUPERVISOR'].dropna().unique() if not df_abc.empty else []
            if len(supervisores_abc) > 0:
                for supervisor in sorted(supervisores_abc):
                    df_super = df_abc[df_abc['SUPERVISOR'] == supervisor]
                    
                    pendentes = len(df_super[df_super['Status_Atividade_Upper'] == 'PENDENTE'])
                    em_rota = len(df_super[df_super['Status_Atividade_Upper'] == 'EM ROTA'])
                    iniciados = len(df_super[df_super['Status_Atividade_Upper'] == 'INICIADO'])
                    total = len(df_super)
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2:
                            st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3:
                            st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum supervisor ativo no ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO / GUARULHOS</div>', unsafe_allow_html=True)
            
            supervisores_sp = df_sp['SUPERVISOR'].dropna().unique() if not df_sp.empty else []
            if len(supervisores_sp) > 0:
                for supervisor in sorted(supervisores_sp):
                    df_super = df_sp[df_sp['SUPERVISOR'] == supervisor]
                    
                    pendentes = len(df_super[df_super['Status_Atividade_Upper'] == 'PENDENTE'])
                    em_rota = len(df_super[df_super['Status_Atividade_Upper'] == 'EM ROTA'])
                    iniciados = len(df_super[df_super['Status_Atividade_Upper'] == 'INICIADO'])
                    total = len(df_super)
                    
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                        
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2:
                            st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3:
                            st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum supervisor ativo em SP nesta janela.")

    # MODO TV AUTOMÁTICO
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#3-tec1-pendentes";
        }, 30000);
        </script>
    """, height=0)
else:
    st.warning("👈 Por favor, faça o upload dos arquivos de rota na página inicial (streamlit_app.py) primeiro.")
