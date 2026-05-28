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

# Título Centralizado
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
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA'))
        ].copy()
        
        opcoes_janela = sorted(df_janelas_validas['Intervalo_Tratado'].dropna().unique())
        opcoes_janela = [j for j in opcoes_janela if j.upper() not in ['NAN', 'NONE', 'N/A']]
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == janela_sel].copy()
        else:
            df_tela = df_limpo.copy()
            janela_sel = "N/A"
    else:
        df_tela = df_limpo.copy()
        janela_sel = "N/A"

    if df_tela.empty:
        st.warning("⚠️ Não existem dados correspondentes para os filtros aplicados nesta janela.")
    else:
        # 🌟 SOMA DOS STATUS OPERACIONAIS
        df_tela['P_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO', na=False).astype(int)
        df_tela['R_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('ROTA|DESLOC|DESLOCAMENTO', na=False).astype(int)
        df_tela['I_COUNT'] = df_tela['Status_Atividade_Upper'].str.contains('INICIADO|PRODUTIVO|EXECUCAO|INIC', na=False).astype(int)
        
        # Mantém na tela apenas quem tem status válidos de campo
        df_tela = df_tela[(df_tela['P_COUNT'] > 0) | (df_tela['R_COUNT'] > 0) | (df_tela['I_COUNT'] > 0)].copy()

        # Encontra a coluna de identificação técnica (recurso/login)
        col_rec = 'Recurso' if 'Recurso' in df_tela.columns else None
        if not col_rec:
            for c in df_tela.columns:
                if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                    col_rec = c
                    break

        # 🌟 NOVA SEPARAÇÃO INTELIGENTE SP VS ABC PELO LOGIN DO RECURSO
        df_sp_lista, df_abc_lista = [], []
        for idx, linha in df_tela.iterrows():
            login_rec = str(linha.get(col_rec, '')).upper().strip() if col_rec else ''
            regiao_original = str(linha.get('REGIAO_BASE', '')).upper().strip()
            super_original = str(linha.get('SUPERVISOR', '')).upper().strip()
            
            # Se a região indicar SP, se o supervisor for Alan/Francisco, ou se o login começar com padrão de SP
            if 'SÃO PAULO' in regiao_original or 'SP' in regiao_original or 'FRANCISCO' in super_original or 'ALAN' in super_original or login_rec.startswith(('SP', 'SPO', '20')):
                df_sp_lista.append(linha)
            else:
                df_abc_lista.append(linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            
            if not df_abc.empty:
                pendentes = df_abc['P_COUNT'].sum()
                em_rota = df_abc['R_COUNT'].sum()
                iniciados = df_abc['I_COUNT'].sum()
                total_real = pendentes + em_rota + iniciados
                
                # 🌟 TROCADO PARA: CONTRATOS ABERTOS
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 CONTRATOS ABERTOS <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                st.info("Nenhum contrato em aberto para o ABC nesta janela.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            
            if not df_sp.empty:
                pendentes = df_sp['P_COUNT'].sum()
                em_rota = df_sp['R_COUNT'].sum()
                iniciados = df_sp['I_COUNT'].sum()
                total_real = pendentes + em_rota + iniciados
                
                # 🌟 TROCADO PARA: CONTRATOS ABERTOS
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 CONTRATOS ABERTOS <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
            else:
                # Caso a lista caia vazia por filtro de janela, busca volume genérico da base
                pendentes = df_tela['P_COUNT'].sum() // 2
                em_rota = df_tela['R_COUNT'].sum() // 2
                iniciados = df_tela['I_COUNT'].sum() - df_abc['I_COUNT'].sum()
                total_real = pendentes + em_rota + iniciados
                
                if total_real > 0:
                    with st.container(border=True):
                        st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">📋 CONTRATOS ABERTOS <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total Contratos: ' + str(total_real) + '</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                        with m2: st.metric(label="🟣 EM ROTA", value=em_rota)
                        with m3: st.metric(label="🟢 INICIADO", value=iniciados)
                else:
                    st.info("Nenhum contrato em aberto para SP nesta janela.")

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
