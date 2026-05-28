import streamlit as st
import pandas as pd
import requests
import io

# 1. Configuração global da página ampla
st.set_page_config(
    page_title="Painel de Produtividade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Carregar Estilos Globais (CSS)
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 PAINEL DE PRODUTIVIDADE OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Controle integrado de performance por blocos regionais e supervisão</div>', unsafe_allow_html=True)

# === MOTOR MÁSTER DE CARGA: EVITA AMBIGUIDADE DE COLUNAS ===
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
                        # Força todos os cabeçalhos a virarem texto simples imediatamente
                        df_individual.columns = [str(c).strip().replace('\xa0', ' ') for c in df_individual.columns]
                        lista_dfs.append(df_individual)
                        
                except Exception as err_arquivo:
                    st.sidebar.error(f"Erro no arquivo {arquivo.name}: {err_arquivo}")
                    continue
            
            if not lista_dfs:
                st.sidebar.error("⚠️ Nenhum arquivo pôde ser lido.")
                return None
                
            # Une todas as tabelas brutas
            df_bruto = pd.concat(lista_dfs, ignore_index=True)
            
            # 🌟 SOLUÇÃO DA AMBIGUIDADE: Convertemos os cabeçalhos para uma lista nativa de Strings do Python.
            # Isso impede que o Pandas tente analisar séries/vetores inteiros na verificação de texto.
            lista_colunas_reais = [str(c) for c in df_bruto.columns]
            colunas_mapeadas = {}
            
            for col in lista_colunas_reais:
                col_upper = col.upper().strip()
                
                # Procura a coluna do login/técnico
                if 'LOGIN' in col_upper or 'USER' in col_upper or 'RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper:
                    colunas_mapeadas[col] = 'ID_Tecnico_Bruto'
                # Procura a coluna de status da atividade
                elif 'STATUS' in col_upper and 'OS' not in col_upper:
                    colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
                # Procura a coluna de tipo de O.S
                elif 'TIPO O.S 1' in col_upper or 'TIPO DE OS' in col_upper or 'TIPO ATIVIDADE' in col_upper:
                    colunas_mapeadas[col] = 'Tipo O.S 1'
                # Procura a coluna de baixa/status os 1
                elif 'STATUS DA O.S 1' in col_upper or 'STATUS OS 1' in col_upper or 'BAIXA' in col_upper:
                    colunas_mapeadas[col] = 'STATUS_OS1'
                # Procura a coluna de total de tarefas
                elif 'TOTAL DE TAREFAS' in col_upper or 'TOTAL TAREFAS' in col_upper or 'VOLUME' in col_upper or 'QTD' in col_upper:
                    colunas_mapeadas[col] = 'QTD_OS_COL'
                # Procura a coluna de categoria/capacidade
                elif 'CATEGORIA' in col_upper or 'CAPACIDADE' in col_upper:
                    colunas_mapeadas[col] = 'CATEGORIA_CAPACIDADE'
            
            df_bruto = df_bruto.rename(columns=colunas_mapeadas)
            
            if 'ID_Tecnico_Bruto' in df_bruto.columns:
                df_bruto['Login_Match'] = df_bruto['ID_Tecnico_Bruto'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else 'N/A')
                df_bruto['Recurso'] = df_bruto['ID_Tecnico_Bruto'].apply(lambda x: str(x).strip() if pd.notna(x) else 'N/A')
            else:
                st.sidebar.error("❌ Coluna de identificação do técnico (Login/Recurso) não localizada nos arquivos.")
                return None

            # 🧠 BUSCA ABA "SUPERVISORES" NO GOOGLE SHEETS
            url_base = "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/export?format=csv&gid=0"
            res_aux = requests.get(url_base, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            
            if res_aux.status_code == 200:
                df_aux = pd.read_csv(io.StringIO(res_aux.text))
                
                # Isola cabeçalhos da aba auxiliar como lista de texto puro
                df_aux.columns = [str(c).strip().upper() for c in df_aux.columns]
                
                # Mapeia as colunas usando lambdas seguras
                df_aux['LOGIN_MATCH'] = df_aux['LOGIN'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else '')
                df_aux = df_aux.rename(columns={'SUPERVISOR': 'SUPERVISOR_MAP', 'BASE': 'BASE_MAP', 'NOME': 'NOME_MAP'})
                df_aux = df_aux[['LOGIN_MATCH', 'NOME_MAP', 'SUPERVISOR_MAP', 'BASE_MAP']].drop_duplicates()
                
                # Realiza o PROCV (Merge) seguro
                df_final = pd.merge(df_bruto, df_aux, left_on='Login_Match', right_on='LOGIN_MATCH', how='left')
                
                df_final['Recurso'] = df_final['NOME_MAP'].fillna(df_final['Recurso'])
                df_final['SUPERVISOR'] = df_final['SUPERVISOR_MAP'].fillna('#N/A')
                df_final['REGIAO_BASE'] = df_final['BASE_MAP'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else 'N/A')
                
                # Descarta colunas temporárias geradas no merge
                df_final = df_final.drop(columns=['Login_Match', 'LOGIN_MATCH', 'NOME_MAP', 'SUPERVISOR_MAP', 'BASE_MAP', 'ID_Tecnico_Bruto'], errors='ignore')
                
                st.sidebar.success(f"✅ {len(lista_dfs)} arquivo(s) processado(s) com sucesso!")
                st.session_state['df_rota_ativa'] = df_final
                return df_final
            else:
                st.sidebar.error("❌ Erro ao conectar com a aba de supervisores do Google Sheets.")
                return None
        except Exception as e:
            st.sidebar.error(f"❌ Erro geral no motor de carga: {e}")
            return None
            
    return st.session_state.get('df_rota_ativa', None)

df_master = carregar_dados_sistema()

# Lógica de classificação (Regra Máster do Excel)
def classificar_status_excel(baixa, status_at):
    baixa = str(baixa).upper().strip()
    status_at = str(status_at).upper().strip()
    codigos_ne = ["101", "106", "110", "112", "113", "125", "203", "205", "206", "301", "305", "306", "402", "100"]
    for cod in codigos_ne:
        if baixa.startswith(cod) or f"{cod} -" in baixa: return "O.S NE"
    if "PENDENTE" in baixa or "INICIADO" in baixa or "EM ROTA" in baixa or "PENDENTE" in status_at: return "EM ABERTO"
    return "PRODUTIVO"

# Renderizador de Blocos na tela
def processar_bloco_regional(df_bloco, nome_bloco):
    st.markdown(f'<div style="background-color:#005088; padding:8px 15px; color:white; font-weight:bold; font-size:18px; border-radius:4px; margin-top:20px; margin-bottom:10px;">{nome_bloco}</div>', unsafe_allow_html=True)
    
    df_bloco['Supervisor_Upper'] = df_bloco['SUPERVISOR'].apply(lambda x: str(x).strip().upper())
    df_bloco['Status_Atividade_Upper'] = df_bloco['STATUS_ATIVIDADE'].apply(lambda x: str(x).strip().upper() if pd.notna(x) else '')
    df_bloco['Recurso_Upper'] = df_bloco['Recurso'].apply(lambda x: str(x).strip().upper())
    
    df_bloco = df_bloco[(~df_bloco['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & (df_bloco['Status_Atividade_Upper'] != "SUSPENSO")].copy()
    df_bloco = df_bloco[~df_bloco['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)].copy()
    
    if df_bloco.empty:
        st.info(f"Nenhum dado ativo para a regional {nome_bloco} neste arquivo.")
        return
        
    if 'QTD_OS_COL' in df_bloco.columns:
        df_bloco['QTD_OS_NUM'] = pd.to_numeric(df_bloco['QTD_OS_COL'], errors='coerce').fillna(0).astype(int)
    else:
        df_bloco['QTD_OS_NUM'] = 1
        
    df_bloco['Status_Calculado'] = df_bloco.apply(lambda r: classificar_status_excel(r['STATUS_OS1'], r['STATUS_ATIVIDADE']), axis=1)
    
    matriz = df_bloco.groupby(['SUPERVISOR', 'Status_Calculado'])['QTD_OS_NUM'].sum().unstack(fill_value=0).reset_index()
    
    for col in ['PRODUTIVO', 'O.S NE', 'EM ABERTO']:
        if col not in matriz.columns: matriz[col] = 0
        
    matriz['Total Geral'] = matriz['PRODUTIVO'] + matriz['O.S NE'] + matriz['EM ABERTO']
    matriz['Quebra (%)'] = matriz.apply(
        lambda r: round((r['O.S NE'] / (r['PRODUTIVO'] + r['O.S NE'])) * 100, 1) if (r['PRODUTIVO'] + r['O.S NE']) > 0 else 0.0, axis=1
    )
    
    matriz = matriz[['SUPERVISOR', 'PRODUTIVO', 'O.S NE', 'EM ABERTO', 'Total Geral', 'Quebra (%)']]
    
    st.dataframe(
        matriz.style.format({'Quebra (%)': '{:.1f}%'}).background_gradient(subset=['Quebra (%)'], cmap='Reds', vmin=0, vmax=35),
        use_container_width=True, hide_index=True
    )

# EXIBIÇÃO EM TELA
if df_master is not None:
    df_abc = df_master[df_master['REGIAO_BASE'] == 'ABC'].copy()
    df_gua = df_master[df_master['REGIAO_BASE'] == 'GUARULHOS'].copy()
    df_sp = df_master[df_master['REGIAO_BASE'].isin(['SÃO PAULO', 'SP'])].copy()
    
    processar_bloco_regional(df_abc, "📍 BLOCO REGIONAL - ABCDM")
    processar_bloco_regional(df_gua, "📍 BLOCO REGIONAL - GUARULHOS")
    processar_bloco_regional(df_sp, "📍 BLOCO REGIONAL - SÃO PAULO")
else:
    st.warning("👈 Use o menu lateral esquerdo para fazer o upload dos ficheiros de rota (.xlsx ou .csv).")
