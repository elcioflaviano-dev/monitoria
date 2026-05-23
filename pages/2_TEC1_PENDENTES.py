import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. Configuração da página e remoção de espaços
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except:
    pass

# 3. Estilo específico para técnicos pendentes
st.markdown("""
    <style>
    .item-pendente-tv {
        background-color: #ffe6e6 !important;
        border: 2px solid #ff9999 !important;
        border-radius: 6px;
        padding: 6px 12px !important;
        margin-bottom: 6px !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        width: 100% !important;
    }
    .tecnico-nome-tv {
        color: #b30000 !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
    }
    .contrato-numero-tv {
        background-color: #b30000 !important;
        color: white !important;
        padding: 3px 10px !important;
        border-radius: 4px !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    .no-pendente-tv {
        color: #2e7d32;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        padding: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# 4. Título de Alerta
st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #b30000; text-align: center; margin-top: 25px; margin-bottom: 5px;">⚠️ TEC1 - PENDENTES</h1>', unsafe_allow_html=True)

# === FUNÇÃO DE CARGA OPERACIONAL DO GOOGLE SHEETS COM VARREDURA INTEGRA ===
def carregar_dados_automatico():
    if 'dados_rota' in st.session_state:
        return st.session_state['dados_rota']
        
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = f"https://docs.google.com/spreadsheets/d/{id_planilha}/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += f"&gid={gid}"
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        
        if resposta.status_code != 200:
            return None
            
        # === BLOCO DE SINCRONIZAÇÃO DO HORÁRIO DE BRASÍLIA ===
        data_header = resposta.headers.get('Date')
        if data_header:
            try:
                dt_gmt = pd.to_datetime(data_header)
                if dt_gmt.tz is None:
                    dt_brasil = dt_gmt.tz_localize('UTC').tz_convert('America/Sao_Paulo')
                else:
                    dt_brasil = dt_gmt.tz_convert('America/Sao_Paulo')
                st.session_state['data_da_rota'] = dt_brasil.strftime('%d/%m/%Y às %H:%M:%S')
            except:
                st.session_state['data_da_rota'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        else:
            st.session_state['data_da_rota'] = datetime.now().strftime('%d/%m/%Y às %H:%M:%S')

        conteudo_bruto = resposta.text
        if '<html' in conteudo_bruto.lower() or '<!doctype' in conteudo_bruto.lower():
            st.error("🔒 Erro de Permissão: A planilha está PRIVADA. Altere o compartilhamento no Google Sheets.")
            return None

        linhas_puras = conteudo_bruto.splitlines()
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        
        for i, linha_texto in enumerate(linhas_puras[:50]):
            linha_upper = linha_texto.upper()
            if 'SUPERVISOR' in linha_upper or 'STATUS' in linha_upper or 'JANELA' in linha_upper or 'CONTRATO' in linha_upper:
                linha_do_cabecalho_real = i
                encontrou_cabecalho = True
                break

        if encontrou_cabecalho:
            texto_corrigido = "\n".join(linhas_puras[linha_do_cabecalho_real:])
            df_sheets = pd.read_csv(io.StringIO(texto_corrigido), dtype=str, on_bad_lines='skip')
        else:
            df_sheets = pd.read_csv(io.StringIO(conteudo_bruto), dtype=str, on_bad_lines='skip')
            
        if df_sheets is None or df_sheets.empty:
            return None

        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper or 'INTERVALO' in col_upper or 'TEMPO' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'Recurso'
            
        df_final = df_sheets.rename(columns=colunas_mapeadas)
        st.session_state['dados_rota'] = df_final
        return df_final
    except:
        return None

# Executa a carga inteligente
df_planilha = carregar_dados_automatico()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = st.session_state.get('data_da_rota', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

if df_planilha is not None:
    df = df_planilha.copy()
    
    # Filtro de Janela
    col_janela = 'Janela de Serviço'
    if col_janela in df.columns:
        opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
        janela_sel = st.sidebar.selectbox("Janela Ativa:", opcoes_janela)
        df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # Filtro de Status: APENAS PENDENTES
    df_pendentes_geral = df_tela[df_tela['Status da Atividade'].str.upper() == 'PENDENTE'] if 'Status da Atividade' in df_tela.columns else pd.DataFrame()

    # Lógica de Separação (ABC | SP)
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_pendentes_geral.columns and not df_pendentes_geral.empty:
        for _, linha in df_pendentes_geral.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(linha)
            else:
                df_abc_lista.append(linha)
                
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)

    def desenhar_alertas(df_regiao, titulo_regiao):
        st.markdown(f'<div class="title-abc-sp">{titulo_regiao}</div>', unsafe_allow_html=True)
        
        if col_supervisor in df_tela.columns:
            todos_supervisores = sorted(df_tela[col_supervisor].dropna().unique())
        else:
            todos_supervisores = []
        
        if titulo_regiao == "SP":
            meus_supers = [s for s in todos_supervisores if "FRANCISCO" in s.upper() or "ALAN" in s.upper()]
        else:
            meus_supers = [s for s in todos_supervisores if "FRANCISCO" not in s.upper() and "ALAN" not in s.upper()]

        for super_nome in meus_supers:
            df_super_p = df_regiao[df_regiao[col_supervisor] == super_nome] if not df_regiao.empty else pd.DataFrame()
            
            with st.container(border=True):
                st.markdown(f"##### **{super_nome.upper()}**")
                
                if not df_super_p.empty:
                    for _, r in df_super_p.iterrows():
                        contrato_limpo = str(r['Contrato']).split('.')[0] if 'Contrato' in r else "N/A"
                        nome_tecnico = str(r['Recurso'])[:25] if 'Recurso' in r else "N/A"
                        
                        html_item = f'<div class="item-pendente-tv"><span class="tecnico-nome-tv">{nome_tecnico}</span><span class="contrato-numero-tv">{contrato_limpo}</span></div>'
                        st.markdown(html_item, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="no-pendente-tv">✅ Sem pendências nesta janela</div>', unsafe_allow_html=True)

    # Divisão em duas colunas principais
    c1, c2 = st.columns(2)
    with c1:
        desenhar_alertas(df_abc, "ABC")
    with c2:
        desenhar_alertas(df_sp, "SP")

    # === AUTOMAÇÃO MODO TV (RETORNA APÓS 30 SEGUNDOS) ===
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#tec1";
        }, 30000);
        </script>
    """, height=0)

else:
    st.error("⚠️ Não foi possível obter dados estáveis da planilha online ou os cabeçalhos não estão alinhados.")
