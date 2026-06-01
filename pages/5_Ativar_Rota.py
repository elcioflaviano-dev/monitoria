import streamlit as st
import pandas as pd
import os
import time

# 1. Configuração da página ampla para a TV
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔄 HERANÇA INTELIGENTE VIA DISCO RÍGIDO
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try: 
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except: 
        pass

# 🚀 REFRESH AUTOMÁTICO PARA A TV (30 Segundos)
if 'df_rota_ativa' in st.session_state and st.session_state['df_rota_ativa'] is not None:
    if "last_refresh_ativar" not in st.session_state: 
        st.session_state["last_refresh_ativar"] = time.time()
    if time.time() - st.session_state["last_refresh_ativar"] > 30:
        st.session_state["last_refresh_ativar"] = time.time()
        st.rerun()

st.markdown("""
    <style>
        .block-container { padding-top: 10px !important; padding-bottom: 5px !important; }
        .stDeployButton { display:none; }
        .title-abc-sp { font-size: 26px !important; font-weight: 800 !important; margin-bottom: 15px !important; text-align: center; color: #005088; border-bottom: 3px solid #008080; padding-bottom: 5px; }
        .item-linha-tec { font-size: 20px; padding: 10px 15px; border-bottom: 1px solid #eee; color: #111; font-family: sans-serif; }
        .item-nome-tecnico { font-weight: 900; color: #008080; }
        .item-janela-tec { float: right; font-size: 16px; background-color: #e0f2f1; color: #004d40; padding: 2px 10px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="font-size: 36px; font-weight: 900; color: #008080; text-align: center; margin-top: 5px; margin-bottom: 25px;">🚀 TÉCNICOS EM BASE</h1>', unsafe_allow_html=True)

df_master = st.session_state.get('df_rota_ativa', None)

if df_master is not None and not df_master.empty:
    df = df_master.copy()
    
    # Remove espaços invisíveis das colunas vindas do arquivo
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🛠️ MAPEAMENTO DAS OUTRAS COLUNAS FIXAS DA SUA PLANILHA
    col_tecnico_check = 'Login do Técnico'
    col_status_real = 'Status da Atividade'
    col_supervisor = 'SUPERVISOR'
    col_janela = 'Janela de Serviço'

    if col_tecnico_check in df.columns and col_status_real in df.columns:
        # Limpa linhas vazias
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()
        
        # Padroniza a coluna de status para checar o pendente
        df['Status_Pure_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
        
        # 🔥 MOTOR DE BUSCA EM MATRIZ COMPLETA 🔥
        # Varre absolutamente todas as colunas da linha procurando pela expressão "NA BASE"
        contem_na_base = df.astype(str).apply(lambda row: row.str.upper().str.strip().eq('NA BASE').any(), axis=1)
        
        # O filtro cruza: qualquer coluna contendo "NA BASE" + coluna de status igual a "PENDENTE"
        condicao_retido = contem_na_base & (df['Status_Pure_Upper'] == 'PENDENTE')
        df_tela = df[condicao_retido].copy()
    else:
        df_tela = pd.DataFrame()

    if df_tela.empty:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.success("🎉 100% da equipe liberada para a rua! Nenhum técnico com 'Na Base' pendente encontrado no arquivo.")
    else:
        # Mapeamento estável de supervisores para a divisão das colunas regionais
        if col_supervisor in df_tela.columns:
            df_tela['SUP_REF'] = df_tela[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()
        else:
            df_tela['SUP_REF'] = 'MAICON'
            
        df_tela['SUP_REF'] = df_tela['SUP_REF'].replace({'#N/A': 'MAICON', 'NAN': 'MAICON', '': 'MAICON'})
        df_tela['SUP_REF'] = df_tela['SUP_REF'].apply(lambda x: 'ALAN' if 'ALAN' in str(x) else ('FRANCISCO' if 'FRANCISCO' in str(x) else x))

        # Divisão Regional
        cond_sp = df_tela['SUP_REF'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC / GUARULHOS</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                df_abc_limpo = df_abc.drop_duplicates(subset=[col_tecnico_check]).sort_values(col_tecnico_check)
                for _, linha in df_abc_limpo.iterrows():
                    janela_texto = linha.get(col_janela, "N/A") if col_janela in df_abc.columns else "N/A"
                    st.markdown(f'''
                        <div class="item-linha-tec">
                            🏃‍♂️ <span class="item-nome-tecnico">{str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</span>
                            <span class="item-janela-tec">Janela: {janela_texto}</span>
                        </div>
                    ''', unsafe_allow_html=True)
            else: 
                st.info("Nenhum técnico retido em base na região do ABC.")

        with col_coluna_sp:
            st.markdown('<div class="title-abc-sp">SÃO PAULO (SP)</div>', unsafe_allow_html=True)
            if not df_sp.empty:
                df_sp_limpo = df_sp.drop_duplicates(subset=[col_tecnico_check]).sort_values(col_tecnico_check)
                for _, linha in df_sp_limpo.iterrows():
                    janela_texto = linha.get(col_janela, "N/A") if col_janela in df_sp.columns else "N/A"
                    st.markdown(f'''
                        <div class="item-linha-tec">
                            🏃‍♂️ <span class="item-nome-tecnico">{str(linha.get(col_tecnico_check, "TÉCNICO")).upper()}</span>
                            <span class="item-janela-tec">Janela: {janela_texto}</span>
                        </div>
                    ''', unsafe_allow_html=True)
            else: 
                st.info("Nenhum técnico retido em base na região de SP.")
else: 
    st.warning("👈 Por favor, insira os arquivos de rota na página inicial primeiro.")
