import streamlit as st
import pandas as pd
import os
import time

# Configuração da página ampla
st.set_page_config(layout="wide", page_title="INDICADORES", initial_sidebar_state="collapsed")

# CSS PARA LIMPEZA DA INTERFACE E ESTILIZAÇÃO DO TEC1
st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    .block-container { padding-top: 15px !important; }
    
    .title-abc-sp { font-size: 24px !important; font-weight: 900 !important; margin-bottom: 10px !important; text-align: center; color: #005088; }
    .super-bar { background-color: #f0f2f6; padding: 6px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; color: #333; margin-top: 12px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #008080; }
    .super-bar.sp { border-left: 5px solid #b30000; }
    .super-total { background-color: #ffffff; color: #c62828; padding: 2px 10px; border-radius: 4px; font-size: 13px; font-weight: 900; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .item-linha { font-size: 15px; padding: 6px 12px; border-bottom: 1px solid #eee; color: #222; display: flex; align-items: center; }
    .item-contrato { font-weight: 900; color: #cc6600; font-size: 16px; width: 110px; }
    .item-tecnico { font-weight: bold; color: #444; flex-grow: 1; }
    .badge-falta { background-color: #ffebee; color: #c62828; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #ffcdd2; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: pass

if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_ind" not in st.session_state: st.session_state["last_refresh_ind"] = time.time()
    if time.time() - st.session_state["last_refresh_ind"] > 60:
        st.session_state["last_refresh_ind"] = time.time()
        st.rerun()

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #005088; text-align: center; margin-top: 5px; margin-bottom: 25px;">📊 INDICADORES OPERACIONAIS</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🔍 RADAR AUTOMÁTICO DE COLUNAS
    col_nr35 = next((c for c in reversed(df.columns) if 'NR35' in c.upper() or 'NR-35' in c.upper()), None)
    col_cert = next((c for c in reversed(df.columns) if 'CERTID' in c.upper() or 'ELEGIVEL' in c.upper() or 'ELEGÍVEL' in c.upper()), None)
    col_bst  = next((c for c in reversed(df.columns) if 'BST' in c.upper() or 'STEERING' in c.upper() or 'BAND' in c.upper()), None)
    
    col_tecnico = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    
    # Limpeza de Contratos
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()

    # =========================================================================
    # 1. FILTRAR APENAS CONTRATOS PRODUTIVOS / CONCLUÍDOS
    # =========================================================================
    df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
    df_produtivo = df[df['Status_Atividade_Upper'].str.contains('CONCL|PRODUTIVO|INIC|EXEC', na=False)].copy()

    # =========================================================================
    # 2. CARDS DE KPI (Cálculo sobre técnicos em campo)
    # =========================================================================
    df_tec = df_produtivo.drop_duplicates(subset=[col_tecnico]).copy()
    total_tecnicos = len(df_tec) if len(df_tec) > 0 else 1

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">🪜 NR35 (ESCADA)</p>', unsafe_allow_html=True)
            if col_nr35:
                df_tec[col_nr35] = df_tec[col_nr35].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_nr35] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#008080; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
            else:
                st.error("Coluna NR35 não detetada")
                
    with c2:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">📜 CERTIDÃO DE ATENDIMENTO</p>', unsafe_allow_html=True)
            if col_cert:
                df_tec[col_cert] = df_tec[col_cert].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_cert] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#005088; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
            else:
                st.error("Coluna Certidão não detetada")
                
    with c3:
        with st.container(border=True):
            st.markdown('<p style="font-size:14px; font-weight:bold; color:#555; text-align:center; text-transform:uppercase;">📶 BAND STEERING ATIVO</p>', unsafe_allow_html=True)
            if col_bst:
                df_tec[col_bst] = df_tec[col_bst].fillna('-').astype(str).str.upper().str.strip()
                aptos = len(df_tec[df_tec[col_bst] == 'SIM'])
                pct = (aptos / total_tecnicos) * 100
                st.markdown(f'<h2 style="font-size:46px; font-weight:900; color:#b30000; text-align:center; margin:5px 0;">{pct:.0f}%</h2>', unsafe_allow_html=True)
            else:
                st.error("Coluna BST não detetada")

    st.markdown("<br><hr><br>", unsafe_allow_html=True)

    # =========================================================================
    # 3. MOTOR DE PENDÊNCIAS (Layout TEC1)
    # =========================================================================
    st.markdown('<h2 style="font-size: 26px; font-weight: 900; color: #cc6600; text-align: center; margin-bottom: 20px;">🚨 COBRANÇA DE INDICADORES (NÃO ENVIADOS)</h2>', unsafe_allow_html=True)

    # Função para descobrir o que falta em cada contrato
    def verificar_faltas(row):
        faltas = []
        if col_nr35 and pd.Series(str(row.get(col_nr35, ''))).str.upper().str.contains('NÃO|NAO|FALTA').any():
            faltas.append('NR35')
        if col_cert and pd.Series(str(row.get(col_cert, ''))).str.upper().str.contains('NÃO|NAO|FALTA').any():
            faltas.append('CERTIDÃO')
        if col_bst and pd.Series(str(row.get(col_bst, ''))).str.upper().str.contains('NÃO|NAO|FALTA').any():
            faltas.append('BST')
        return " + ".join(faltas)

    df_produtivo['Faltas_Indicadores'] = df_produtivo.apply(verificar_faltas, axis=1)
    
    # Filtra APENAS quem tem faltas
    df_pendentes = df_produtivo[df_produtivo['Faltas_Indicadores'] != ''].copy()

    if df_pendentes.empty:
        st.success("🎉 Excelente! Todos os contratos produtivos estão com os indicadores preenchidos e enviados.")
    else:
        # Mapeamento Inteligente de Supervisores (IDÊNTICO AO TEC1)
        if col_supervisor in df_pendentes.columns:
            df_pendentes['SUPERVISOR_MOSTRAR'] = df_pendentes[col_supervisor].fillna('').astype(str).str.upper().str.strip()
        else:
            df_pendentes['SUPERVISOR_MOSTRAR'] = ''

        def vincular_supervisor_tecnico(row):
            nome_u = str(row.get(col_tecnico, '')).upper().strip()
            sup_orig = str(row.get('SUPERVISOR_MOSTRAR', '')).upper().strip()
            
            if sup_orig not in ['NÃO IDENTIFICADO', 'NAN', 'N/A', '', 'NULL', '#N/A', '0', '0.0']:
                if "MARCOS" in sup_orig and "ROBERTO" not in sup_orig: return "MARCOS ROBERTO"
                if "EDSON" in sup_orig and "MARCO" not in sup_orig: return "EDSON MARCO"
                return sup_orig

            if "ADRIEL" in nome_u or "AMANDA" in nome_u or "DEBORA" in nome_u or "ELIAS" in nome_u or "AIRON" in nome_u: return "ALAN"
            if "ALINE" in nome_u or "ALEX" in nome_u or "EDER" in nome_u or "ENOQUE" in nome_u: return "FRANCISCO"
            if "MARCOS" in nome_u: return "MARCOS ROBERTO"
            if "NELSON" in nome_u: return "NELSON"
            if "JOAO" in nome_u or "MIRON" in nome_u: return "JOAO CARLOS MIRON"
                
            return "EDSON MARCO"

        df_pendentes['SUPERVISOR_MOSTRAR'] = df_pendentes.apply(vincular_supervisor_tecnico, axis=1)

        # Divisão Regional
        cond_sp = df_pendentes['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN|JOAO|MIRON', na=False)
        df_sp = df_pendentes[cond_sp].copy()
        df_abc = df_pendentes[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        # --- RENDERIZAÇÃO LADO ABC ---
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                for supervisor in sorted(df_abc['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_abc[df_abc['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar">👤 {supervisor} <span class="super-total">Faltas: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        tec_nome = str(linha.get(col_tecnico, "TÉCNICO")).upper()
                        contrato = linha.get("Contrato", "N/A")
                        faltas = linha.get("Faltas_Indicadores")
                        st.markdown(f'''
                            <div class="item-linha">
                                <span class="item-contrato">📄 {contrato}</span> 
                                <span class="item-tecnico">👤 {tec_nome}</span>
                                <span class="badge-falta">❌ Faltam: {faltas}</span>
                            </div>
                        ''', unsafe_allow_html=True)
            else: 
                st.info("Nenhuma pendência de indicador no ABC.")

        # --- RENDERIZAÇÃO LADO SÃO PAULO ---
        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp" style="color:#b30000;">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                for supervisor in sorted(df_sp['SUPERVISOR_MOSTRAR'].unique()):
                    df_super = df_sp[df_sp['SUPERVISOR_MOSTRAR'] == supervisor]
                    st.markdown(f'<div class="super-bar sp">👤 {supervisor} <span class="super-total">Faltas: {len(df_super)}</span></div>', unsafe_allow_html=True)
                    for _, linha in df_super.iterrows():
                        tec_nome = str(linha.get(col_tecnico, "TÉCNICO")).upper()
                        contrato = linha.get("Contrato", "N/A")
                        faltas = linha.get("Faltas_Indicadores")
                        st.markdown(f'''
                            <div class="item-linha">
                                <span class="item-contrato">📄 {contrato}</span> 
                                <span class="item-tecnico">👤 {tec_nome}</span>
                                <span class="badge-falta">❌ Faltam: {faltas}</span>
                            </div>
                        ''', unsafe_allow_html=True)
            else: 
                st.info("Nenhuma pendência de indicador em SP.")

else:
    st.warning("⏳ Aguardando dados da página inicial para processar os indicadores...")
