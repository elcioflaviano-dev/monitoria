import streamlit as st
import pandas as pd
import time
import os
import requests
import io

st.set_page_config(page_title="Painel de Produtividade", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

# CSS PARA LIMPEZA DA INTERFACE
st.markdown("""
    <style>
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"
URL_PLANILHA_MASTER = "https://totaltecnologia-my.sharepoint.com/:x:/g/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/IQBPzXoLVti8RJTgULiXf-nQAcrWXLiLMfks1IgJPO4nJeg?download=1"

def carregar_dados_nuvem():
    st.sidebar.markdown("### 🔄 SINCRONIZAÇÃO AUTOMÁTICA")
    st.sidebar.info("A procurar dados em tempo real na nuvem...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': '*/*'
        }
        
        sessao = requests.Session()
        resposta = sessao.get(URL_PLANILHA_MASTER, headers=headers, allow_redirects=True, timeout=20)
        
        if resposta.status_code != 200:
            st.sidebar.error(f"Erro HTTP: {resposta.status_code}")
            return None

        ficheiro_excel = io.BytesIO(resposta.content)
        
        # =====================================================================
        # 📊 PARTE A: PROCESSA E SINCRONIZA A ABA DO CONSULTIVO (NOVO!)
        # =====================================================================
        try:
            df_cons_bruto = pd.read_excel(ficheiro_excel, sheet_name='CONSULTIVO', engine='openpyxl')
            if not df_cons_bruto.empty:
                df_cons_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_cons_bruto.columns]
                # Salva o CSV do consultivo na nuvem
                df_cons_bruto.to_csv("consultivo_sincronizado.csv", index=False)
        except Exception as e_cons:
            st.sidebar.warning(f"Aba CONSULTIVO não processada: {e_cons}")

        # Retorna o ponteiro do arquivo para o início para ler a Rota
        ficheiro_excel.seek(0)

        # =====================================================================
        # 🗺️ PARTE B: PROCESSA E SINCRONIZA A ABA DA ROTA (SEU CÓDIGO ORIGINAL)
        # =====================================================================
        df_bruto = pd.read_excel(ficheiro_excel, sheet_name='ROTA', engine='openpyxl')
        
        if df_bruto.empty:
            return None

        df_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_bruto.columns]
        
        cols_sup = [c for c in df_bruto.columns if 'SUPERV' in str(c).upper()]
        valores_supervisor = df_bruto[cols_sup[-1]].values if cols_sup else None
        
        cols_base = [c for c in df_bruto.columns if 'BASE' in str(c).upper() or 'REGIAO' in str(c).upper() or 'REGIÃO' in str(c).upper()]
        valores_base = df_bruto[cols_base[-1]].values if cols_base else None

        colunas_mapeadas = {}
        for col in list(df_bruto.columns):
            col_upper = str(col).upper()
            if col_upper in ['LOGIN DO TÉCNICO', 'LOGIN DO TECNICO', 'LOGIN']: 
                colunas_mapeadas[col] = 'Login do Técnico'
            elif 'STATUS' in col_upper and 'ATIVIDADE' in col_upper: 
                colunas_mapeadas[col] = 'Status da Atividade'
            elif 'TIPO' in col_upper and 'ATIVIDADE' in col_upper:
                if '3' in col_upper:
                    colunas_mapeadas[col] = 'Tipo de Atividade3'
                else:
                    colunas_mapeadas[col] = 'Tipo de Atividade'
            elif col_upper in ['RECURSO', 'RECURS', 'TECNICO', 'NOME', 'TÉCNICO']: 
                colunas_mapeadas[col] = 'Recurso'
            elif 'TOTAL DE TAREFAS' in col_upper: 
                colunas_mapeadas[col] = 'QTD_OS_COL'
        
        df_final = df_bruto.rename(columns=colunas_mapeadas)
        df_final = df_final.loc[:, ~df_final.columns.duplicated(keep='first')]
        
        if valores_supervisor is not None:
            df_final['SUPERVISOR'] = valores_supervisor
        else:
            df_final['SUPERVISOR'] = 'NÃO IDENTIFICADO'

        if valores_base is not None:
            df_final['REGIAO_BASE'] = valores_base
        else:
            df_final['REGIAO_BASE'] = 'GERAL'

        df_final['SUPERVISOR'] = df_final['SUPERVISOR'].fillna('NÃO IDENTIFICADO').astype(str).str.strip().str.upper()
        df_final['SUPERVISOR'] = df_final['SUPERVISOR'].replace(['NAN', 'N/A', 'NULL', '', '-', '0', '0.0'], 'NÃO IDENTIFICADO')

        df_final['REGIAO_BASE'] = df_final['REGIAO_BASE'].fillna('NÃO DEFINIDA').astype(str).str.strip().str.upper()
        df_final['REGIAO_BASE'] = df_final['REGIAO_BASE'].replace(['NAN', 'N/A', 'NULL', '', '-', '0', '0.0'], 'NÃO DEFINIDA')

        if 'Recurso' not in df_final.columns and 'Login do Técnico' in df_final.columns:
            df_final['Recurso'] = df_final['Login do Técnico']

        st.session_state['df_rota_ativa'] = df_final
        df_final.to_csv(ARQUIVO_ROTA_DISCO, index=False)
        
        st.sidebar.success("✅ Sincronizado com o Excel!")
        return df_final

    except Exception as e:
        st.sidebar.error(f"❌ Erro na nuvem: {e}")
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            st.sidebar.warning("A usar base local.")
            return pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        return None

if "last_refresh_main" not in st.session_state:
    st.session_state["last_refresh_main"] = time.time()
    
if time.time() - st.session_state["last_refresh_main"] > 60:
    st.session_state["last_refresh_main"] = time.time()
    st.rerun()

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 PAINEL DE PRODUTIVIDADE OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Controle integrado por blocos regionais</div>', unsafe_allow_html=True)

df_master = carregar_dados_nuvem()

if df_master is not None and not df_master.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align: center; padding: 25px 10px;">
                <h2 style="color: #2e7d32; font-size: 28px; margin-bottom: 10px;">🚀 SINCRONIZAÇÃO 100% EXCEL ATIVA!</h2>
                <p style="color: #444; font-size: 16px; margin-bottom: 20px;">
                    {len(df_master)} contratos lidos e mapeados perfeitamente.
                </p>
                <div style="display: inline-block; background-color: #e8f5e9; color: #1b5e20; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                    🎯 Painéis e TV da Monitoria Prontos
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Navegue pelo menu lateral. O painel puxará os dados do Excel automaticamente a cada 60 segundos.")
else:
    st.warning("⏳ A tentar estabelecer ligação com a planilha Master na nuvem...")
