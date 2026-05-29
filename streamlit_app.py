import streamlit as st
import pandas as pd
import requests
import io
import time
import os

st.set_page_config(
    page_title="Painel de Produtividade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# Força o carregamento do arquivo do disco se a sessão limpar
if ('df_rota_ativa' not in st.session_state or st.session_state['df_rota_ativa'] is None) and os.path.exists(ARQUIVO_ROTA_DISCO):
    try:
        st.session_state['df_rota_ativa'] = pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
    except:
        pass

# 🚀 SISTEMA DE REFRESH AUTOMÁTICO PARA A TV (60 Segundos)
if st.session_state.get('df_rota_ativa') is not None:
    if "last_refresh" not in st.session_state:
        st.session_state["last_refresh"] = time.time()
    
    st.text_input("refresh_trigger", value=str(st.session_state["last_refresh"]), label_visibility="collapsed")
    time.sleep(1)
    
    if time.time() - st.session_state["last_refresh"] > 60:
        st.session_state["last_refresh"] = time.time()
        st.rerun()

try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 PAINEL DE PRODUTIVIDADE OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Controle integrado de performance por blocos regionais e supervisão</div>', unsafe_allow_html=True)

def carregar_dados_sistema():
    st.sidebar.markdown("### 📑 CARGA DA ROTA DIÁRIA")
    
    arquivos_postados = st.sidebar.file_uploader(
        "Arraste todos os arquivos da rota aqui de uma vez", 
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="uploader_global"
    )
    
    if arquivos_postados:
        lista_dfs = []
        
        try:
            for arquivo in arquivos_postados:
                try:
                    if arquivo.name.endswith('.xlsx'):
                        bytes_data = arquivo.read()
                        df_individual = pd.read_excel(io.BytesIO(bytes_data), engine='openpyxl')
                    else:
                        df_individual = pd.read_csv(arquivo, on_bad_lines='skip')
                    
                    if not df_individual.empty:
                        df_individual = df_individual.loc[:, ~df_individual.columns.duplicated()]
                        df_individual.columns = [str(c).strip().replace('\xa0', ' ') for c in df_individual.columns]
                        lista_dfs.append(df_individual)
                        
                except Exception as err_arquivo:
                    st.sidebar.error(f"Erro no arquivo {arquivo.name}: {err_arquivo}")
                    continue
            
            if not lista_dfs:
                st.sidebar.error("⚠️ Nenhum arquivo pôde ser lido.")
                return st.session_state.get('df_rota_ativa', None)
                
            df_bruto = pd.concat(lista_dfs, ignore_index=True)
            df_bruto = df_bruto.loc[:, ~df_bruto.columns.duplicated()]
            
            colunas_mapeadas = {}
            for col in list(df_bruto.columns):
                col_upper = str(col).upper().strip()
                
                if 'LOGIN DO TÉCNICO' in col_upper or 'LOGIN DO TECNICO' in col_upper:
                    colunas_mapeadas[col] = 'Login_Match'
                elif 'STATUS DA ATIVIDADE' in col_upper or 'STATUS_ATIVIDADE' in col_upper:
                    colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
                elif 'STATUS DA O.S 1' in col_upper or 'STATUS OS 1' in col_upper:
                    colunas_mapeadas[col] = 'STATUS_OS1'
                elif 'TIPO O.S 1' in col_upper or 'TIPO DE OS' in col_upper:
                    colunas_mapeadas[col] = 'Tipo O.S 1'
                elif 'TOTAL DE TAREFAS' in col_upper:
                    colunas_mapeadas[col] = 'QTD_OS_COL'
            
            df_bruto = df_bruto.rename(columns=colunas_mapeadas)
            
            if 'Login_Match' in df_bruto.columns:
                df_bruto['Login_Match_Clean'] = df_bruto['Login_Match'].fillna('').astype(str).str.strip().str.upper()
                df_bruto['Recurso'] = df_bruto['Login_Match'].fillna('').astype(str).str.strip()
            else:
                for c in df_bruto.columns:
                    if 'TECNICO' in str(c).upper() or 'LOGIN' in str(c).upper():
                        df_bruto['Login_Match_Clean'] = df_bruto[c].fillna('').astype(str).str.strip().str.upper()
                        df_bruto['Recurso'] = df_bruto[c].fillna('').astype(str).str.strip()
                        break

            url_base = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"
            res_aux = requests.get(url_base, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if res_aux.status_code == 200:
                df_aux = pd.read_csv(io.StringIO(res_aux.text))
                df_aux = df_aux.loc[:, ~df_aux.columns.duplicated()]
                
                df_aux.columns = [str(c).strip().upper() for c in df_aux.columns]
                df_aux['LOGIN_SHEETS_CLEAN'] = df_aux['LOGIN'].fillna('').astype(str).str.strip().str.upper()
                df_aux = df_aux[['LOGIN_SHEETS_CLEAN', 'SUPERVISOR', 'BASE', 'NOME']].drop_duplicates()
                
                df_final = pd.merge(df_bruto, df_aux, left_on='Login_Match_Clean', right_on='LOGIN_SHEETS_CLEAN', how='left')
                
                df_final['Recurso'] = df_final['NOME'].fillna(df_final['Recurso'])
                df_final['SUPERVISOR'] = df_final['SUPERVISOR'].fillna('#N/A').astype(str).str.strip().str.upper()
                df_final['REGIAO_BASE'] = df_final['BASE'].fillna('N/A').astype(str).str.strip().str.upper()
                
                df_final = df_final.drop(columns=['Login_Match_Clean', 'LOGIN_SHEETS_CLEAN', 'NOME', 'BASE'], errors='ignore')
                
                df_final = df_final.astype(str)
                st.sidebar.success(f"✅ {len(lista_dfs)} arquivo(s) processado(s) com sucesso!")
                
                # GUARDA NO SESSÃO E SALVA O ARQUIVO FÍSICO NO DISCO
                st.session_state['df_rota_ativa'] = df_final
                df_final.to_csv(ARQUIVO_ROTA_DISCO, index=False)
                
                return df_final
            else:
                st.sidebar.error("❌ Erro ao conectar com a aba de supervisores do Google Sheets.")
                return st.session_state.get('df_rota_ativa', None)
        except Exception as e:
            st.sidebar.error(f"❌ Erro geral no motor de carga: {e}")
            return st.session_state.get('df_rota_ativa', None)
            
    return st.session_state.get('df_rota_ativa', None)

df_master = carregar_dados_sistema()

if df_master is not None and not df_master.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align: center; padding: 25px 10px;">
                <h2 style="color: #2e7d32; font-size: 28px; margin-bottom: 10px;">🚀 UPLOAD CONCLUÍDO COM SUCESSO!</h2>
                <p style="color: #444; font-size: 16px; margin-bottom: 20px;">
                    {len(df_master)} contratos integrados e salvos em disco no sistema.
                </p>
                <div style="display: inline-block; background-color: #e8f5e9; color: #1b5e20; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                    🎯 Dados Prontos e Sincronizados com a TV da Monitoria
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Use o menu lateral esquerdo para navegar entre os painéis operacionais. Este painel irá se atualizar sozinho a cada 60 segundos.")
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.warning("👈 Aguardando os arquivos. Abra o menu lateral esquerdo expandindo a barra e arraste os ficheiros de rota diária (.xlsx ou .csv).")
