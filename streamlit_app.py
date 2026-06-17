import streamlit as st
import pandas as pd
import time
import os

st.set_page_config(
    page_title="Painel de Produtividade",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS PARA LIMPEZA DA INTERFACE
st.markdown("""
    <style>
    .stDeployButton { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_ROTA_DISCO = "rota_sincronizada.csv"

# 🔴 COLOQUE AQUI O LINK DIRETO PARA O SEU EXCEL (.XLSM) NA NUVEM
URL_PLANILHA_MASTER = "https://totaltecnologia-my.sharepoint.com/personal/elcio_nunes_totaltecnologia_onmicrosoft_com/_layouts/15/Doc.aspx?sourcedoc=%7B0B7ACD4F-D856-44BC-94E0-50B8977FE9D0%7D&file=Indicadores_Online_Automatico.xlsm&action=download"

def carregar_dados_nuvem():
    st.sidebar.markdown("### 🔄 SINCRONIZAÇÃO AUTOMÁTICA")
    st.sidebar.info("A procurar dados em tempo real na nuvem...")
    
    try:
        # Lê especificamente a aba "rota" do seu ficheiro Excel
        # Se o nome da aba for diferente, altere 'rota' para o nome exato.
        df_bruto = pd.read_excel(URL_PLANILHA_MASTER, sheet_name='rota', engine='openpyxl')
        
        if df_bruto.empty:
            st.sidebar.error("A aba 'rota' da planilha mestre está vazia.")
            return None

        # Remove colunas duplicadas e limpa os nomes
        df_bruto = df_bruto.loc[:, ~df_bruto.columns.duplicated()]
        df_bruto.columns = [str(c).strip().replace('\xa0', ' ') for c in df_bruto.columns]
        
        # Mapeamento para preservar os nomes cruciais que os outros painéis usam
        colunas_mapeadas = {}
        for col in list(df_bruto.columns):
            col_upper = str(col).upper().strip()
            if col_upper in ['LOGIN DO TÉCNICO', 'LOGIN DO TECNICO', 'LOGIN']:
                colunas_mapeadas[col] = 'Login do Técnico'
            elif col_upper in ['STATUS DA ATIVIDADE', 'STATUS_ATIVIDADE', 'STATUS']:
                colunas_mapeadas[col] = 'Status da Atividade'
            elif col_upper in ['TIPO DE ATIVIDADE', 'TIPO_ATIVIDADE', 'TIPO']:
                colunas_mapeadas[col] = 'Tipo de Atividade'
            elif col_upper in ['RECURSO', 'RECURS', 'TECNICO', 'NOME']:
                colunas_mapeadas[col] = 'Recurso'
            elif 'TOTAL DE TAREFAS' in col_upper:
                colunas_mapeadas[col] = 'QTD_OS_COL'
        
        df_final = df_bruto.rename(columns=colunas_mapeadas)
        
        # Garante que as colunas de supervisão e base existem e estão limpas
        if 'SUPERVISOR' in df_final.columns:
            df_final['SUPERVISOR'] = df_final['SUPERVISOR'].fillna('#N/A').astype(str).str.strip().str.upper()
            df_final['SUPERVISOR'] = df_final['SUPERVISOR'].replace(['NAN', 'N/A', 'NULL', ''], 'NÃO IDENTIFICADO')
        else:
            df_final['SUPERVISOR'] = 'NÃO IDENTIFICADO'

        if 'REGIAO_BASE' not in df_final.columns:
            if 'BASE' in df_final.columns:
                df_final['REGIAO_BASE'] = df_final['BASE'].fillna('N/A').astype(str).str.strip().str.upper()
            else:
                df_final['REGIAO_BASE'] = 'GERAL'

        # Guarda o ficheiro fisicamente para as outras páginas lerem (O CSV Mestre)
        st.session_state['df_rota_ativa'] = df_final
        df_final.to_csv(ARQUIVO_ROTA_DISCO, index=False)
        
        st.sidebar.success("✅ Base sincronizada com sucesso!")
        return df_final

    except Exception as e:
        st.sidebar.error(f"❌ Erro ao buscar dados na nuvem: {e}")
        # Se a internet falhar, tenta usar a última base salva no disco local
        if os.path.exists(ARQUIVO_ROTA_DISCO):
            st.sidebar.warning("A usar a última base salva no sistema local.")
            return pd.read_csv(ARQUIVO_ROTA_DISCO, dtype=str)
        return None

# 🚀 MOTOR DE REFRESH DA PÁGINA INICIAL (60 SEGUNDOS)
if "last_refresh_main" not in st.session_state:
    st.session_state["last_refresh_main"] = time.time()
    
if time.time() - st.session_state["last_refresh_main"] > 60:
    st.session_state["last_refresh_main"] = time.time()
    st.rerun()

st.markdown('<h1 style="font-size: 34px; font-weight: 900; color: #005088; text-align: center; margin-top: 20px; margin-bottom: 5px;">📊 PAINEL DE PRODUTIVIDADE OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;">Controle integrado de performance por blocos regionais e supervisão</div>', unsafe_allow_html=True)

# Chama a função que lê do Excel
df_master = carregar_dados_nuvem()

if df_master is not None and not df_master.empty:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align: center; padding: 25px 10px;">
                <h2 style="color: #2e7d32; font-size: 28px; margin-bottom: 10px;">🚀 SINCRONIZAÇÃO ATIVA!</h2>
                <p style="color: #444; font-size: 16px; margin-bottom: 20px;">
                    {len(df_master)} contratos lidos da nuvem e atualizados no sistema.
                </p>
                <div style="display: inline-block; background-color: #e8f5e9; color: #1b5e20; padding: 8px 20px; border-radius: 20px; font-weight: bold; font-size: 14px;">
                    🎯 Dados Prontos e Sincronizados com a TV da Monitoria
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 Use o menu lateral esquerdo para navegar entre os painéis operacionais. Este painel irá se atualizar sozinho a cada 60 segundos lendo a planilha Excel Master.")
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.warning("⏳ A tentar estabelecer ligação com a planilha Master na nuvem... Verifique se o link está correto.")
