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
    df.columns = [str(c).strip() for c in df.columns]
    
    # 🛠️ MAPEAMENTO EXATO BASEADO NAS LINHAS DO SEU PRINT
    col_tecnico_check = 'Recurso' if 'Recurso' in df.columns else df.columns[0]
    col_status_real = 'Status da Atividade' if 'Status da Atividade' in df.columns else 'STATUS_ATIVIDADE'
    col_supervisor = 'SUPERVISOR' if 'SUPERVISOR' in df.columns else 'Supervisor'
    col_tipo_real = 'Tipo de Atividade' if 'Tipo de Atividade' in df.columns else df.columns[-1]
    
    col_janela = None
    for c in df.columns:
        if 'JANELA' in str(c).upper() or 'INTERVALO' in str(c).upper(): 
            col_janela = c
            break

    if col_tecnico_check:
        df = df[df[col_tecnico_check].fillna('').astype(str).str.strip() != ''].copy()

    # Tratamento de textos em caixa alta para evitar erros de leitura
    df['Status_Pure_Upper'] = df[col_status_real].fillna('').astype(str).str.upper().str.strip()
    df['Tipo_Pure_Upper'] = df[col_tipo_real].fillna('').astype(str).str.upper().str.strip()
    
    # 🔥 O FILTRO PERFEITO: Tipo de Atividade igual a "NA BASE" e Status igual a "PENDENTE"
    condicao_retido_pátio = (df['Tipo_Pure_Upper'] == 'NA BASE') & \
                            (df['Status_Pure_Upper'].str.contains('PENDENTE|EM ABERTO|ABERTO|PEND', na=False))
    
    df_tela = df[condicao_retido_pátio].copy()

    if df_tela.empty:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.success("🎉 100% da equipe liberada para a rua! Nenhum técnico com 'Na Base' pendente.")
    else:
        # Padronização invisível de supervisores para a divisão regional (Guarulhos/ABC vs SP)
        df_tela['SUP_REF'] = df_tela[col_supervisor].fillna('MAICON').astype(str).str.upper().str.strip()
        df_tela['SUP_REF'] = df_tela['SUP_REF'].apply(lambda x: 'ALAN' if 'ALAN' in str(x) else ('FRANCISCO' if 'FRANCISCO' in str(x) else x))

        # Divisão regional idêntica aos outros painéis do seu sistema
        cond_sp = df_tela['SUP_REF'].str.contains('FRANCISCO|ALAN', na=False)
        df_sp = df_tela[cond_sp].copy()
        df_abc = df_tela[~cond_sp].copy()

        col_coluna_abc, col_coluna_sp = st.columns(2)
        
        with col_coluna_abc:
            st.markdown('<div class="title-abc-sp">ABC / GUARULHOS</div>', unsafe_allow_html=True)
            if not df_abc.empty:
                # Ordena e remove duplicados do mesmo técnico para listar o nome uma única vez
                df_abc_limpo = df_abc.drop_duplicates(subset=[col_tecnico_check]).sort_values(col_tecnico_check)
                for _, linha in df_abc_limpo.iterrows():
                    janela_texto = linha.get(col_janela, "N/A") if col_janela else "N/A"
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
                # Ordena e remove duplicados do mesmo técnico para listar o nome uma única vez
                df_sp_limpo = df_sp.drop_duplicates(subset=[col_tecnico_check]).sort_values(col_tecnico_check)
                for _, linha in df_sp_limpo.iterrows():
                    janela_texto = linha.get(col_janela, "N/A") if col_janela else "N/A"
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
