import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(layout="wide", page_title="INDICADORES", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stHeader"] { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    .block-container { padding-top: 15px !important; }
    
    .title-abc-sp { font-size: 24px !important; font-weight: 900 !important; margin-bottom: 15px !important; text-align: center; color: #008080; }
    
    .falta-box { background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 6px; padding: 12px 5px; text-align: center; margin-bottom: 5px; }
    .falta-label { font-size: 12px; font-weight: bold; color: #c62828; text-transform: uppercase; margin-bottom: 6px; }
    .falta-value { font-size: 32px; font-weight: 900; color: #b30000; line-height: 1; }
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
    
    col_nr35 = next((c for c in reversed(df.columns) if 'NR35' in c.upper() or 'NR-35' in c.upper()), None)
    col_cert = next((c for c in reversed(df.columns) if 'CERTID' in c.upper() or 'ELEGIVEL' in c.upper() or 'ELEGÍVEL' in c.upper()), None)
    col_bst  = next((c for c in reversed(df.columns) if 'BST' in c.upper() or 'STEERING' in c.upper() or 'BAND' in c.upper()), None)
    
    col_tecnico = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    col_status = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    
    if 'Contrato' in df.columns:
        df['Contrato'] = df['Contrato'].fillna('').astype(str).apply(lambda x: x.split('.')[0] if '.' in x else x).str.strip()

    df['Status_Atividade_Upper'] = df[col_status].fillna('').astype(str).str.upper().str.strip()
    df_produtivo = df[df['Status_Atividade_Upper'].str.contains('CONCL|PRODUTIVO|INIC|EXEC', na=False)].copy()

    if 'Contrato' in df_produtivo.columns and not df_produtivo.empty:
        df_produtivo = df_produtivo[df_produtivo['Contrato'] != '']
        df_produtivo = df_produtivo.drop_duplicates(subset=['Contrato'])

    df_produtivo['FALTA_NR35'] = 0
    if col_nr35: df_produtivo['FALTA_NR35'] = df_produtivo[col_nr35].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)
    
    df_produtivo['FALTA_CERT'] = 0
    if col_cert: df_produtivo['FALTA_CERT'] = df_produtivo[col_cert].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)
    
    df_produtivo['FALTA_BST'] = 0
    if col_bst: df_produtivo['FALTA_BST'] = df_produtivo[col_bst].fillna('').astype(str).str.upper().str.contains('NÃO|NAO|FALTA', na=False).astype(int)

    df_produtivo['TOTAL_FALTAS'] = df_produtivo['FALTA_NR35'] + df_produtivo['FALTA_CERT'] + df_produtivo['FALTA_BST']
    df_pendentes = df_produtivo[df_produtivo['TOTAL_FALTAS'] > 0].copy()

    if df_pendentes.empty:
        st.success("🎉 Excelente! Todos os contratos produtivos do ABC estão com os indicadores preenchidos e enviados.")
    else:
        if col_supervisor in df_pendentes.columns:
            df_pendentes['SUPERVISOR_MOSTRAR'] = df_pendentes[col_supervisor].fillna('').astype(str).str.upper().str.strip()
        else:
            df_pendentes['SUPERVISOR_MOSTRAR'] = ''

        def vincular_supervisor_tecnico(row):
            nome_u = str(row.get(col_tecnico, '')).upper().strip()
            sup_orig = str(row.get('SUPERVISOR_MOSTRAR', '')).upper().strip()
            
            if sup_orig not in ['NÃO IDENTIFICADO', 'NAN', 'N/A', '', 'NULL', '#N/A', '0', '0.0']:
                if "MARCOS" in sup_orig: return "MARCOS ROBERTO"
                if "MARCO" in sup_orig: return "MAICON"
                if "NELSON" in sup_orig: return "NELSON"
                return sup_orig

            if "MARCOS" in nome_u: return "MARCOS ROBERTO"
            if "NELSON" in nome_u: return "NELSON"
                
            return "EDSON MARCO"

        df_pendentes['SUPERVISOR_MOSTRAR'] = df_pendentes.apply(vincular_supervisor_tecnico, axis=1)

        # Filtra os dados de São Paulo
        cond_sp = df_pendentes['SUPERVISOR_MOSTRAR'].str.contains('FRANCISCO|ALAN|JOAO|MIRON', na=False)
        df_abc = df_pendentes[~cond_sp].copy()

        st.markdown('<div class="title-abc-sp">REGIONAL ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            matriz_abc = df_abc.groupby('SUPERVISOR_MOSTRAR')[['FALTA_NR35', 'FALTA_CERT', 'FALTA_BST']].sum().reset_index()
            cols = st.columns(len(matriz_abc) if len(matriz_abc) > 0 else 1)
            
            for i, supervisor in enumerate(sorted(matriz_abc['SUPERVISOR_MOSTRAR'].unique())):
                with cols[i]:
                    dados_super = matriz_abc[matriz_abc['SUPERVISOR_MOSTRAR'] == supervisor].iloc[0]
                    f_nr35 = int(dados_super['FALTA_NR35'])
                    f_cert = int(dados_super['FALTA_CERT'])
                    f_bst = int(dados_super['FALTA_BST'])
                    total_falhas = f_nr35 + f_cert + f_bst
                    
                    with st.container(border=True):
                        st.markdown(f'<div style="font-size:20px; font-weight:bold; margin-bottom:10px; color:#333;">📋 {supervisor} <span style="float:right; font-size:14px; background-color:#ffcdd2; padding:2px 8px; border-radius:4px; color:#b30000;">Total Faltas: {total_falhas}</span></div>', unsafe_allow_html=True)
                        m1, m2, m3 = st.columns(3)
                        with m1: st.markdown(f'<div class="falta-box"><div class="falta-label">🪜 Faltam NR35</div><div class="falta-value">{f_nr35}</div></div>', unsafe_allow_html=True)
                        with m2: st.markdown(f'<div class="falta-box"><div class="falta-label">📜 Falta Cert.</div><div class="falta-value">{f_cert}</div></div>', unsafe_allow_html=True)
                        with m3: st.markdown(f'<div class="falta-box"><div class="falta-label">📶 Falta BST</div><div class="falta-value">{f_bst}</div></div>', unsafe_allow_html=True)
        else: 
            st.info("Nenhuma pendência de indicador no ABC.")

else:
    st.warning("⏳ Aguardando dados da página inicial para processar os indicadores...")
