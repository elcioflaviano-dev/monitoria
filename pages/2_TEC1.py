import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. Configuração da página ampla
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

# Título TEC1 Centralizado e ajustado
st.markdown(
    '<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 5px;">TEC1</h1>', 
    unsafe_allow_html=True
)

# === FUNÇÃO DE CARGA OPERACIONAL DO GOOGLE SHEETS COM VARREDURA INTEGRA ===
def buscar_base_rotas_online():
    if 'dados_rota' in st.session_state:
        return st.session_state['dados_rota']
        
    try:
        url = st.secrets.get('public_gsheets_url', "https://docs.google.com/spreadsheets/d/1kB1YmUuhzHpfN1dLv8PaQn0ipXcHcd6kGKnI3nguT14/edit?gid=208394608#gid=208394608").strip()
        
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0].strip()
            csv_url = "https://docs.google.com/spreadsheets/d/" + id_planilha + "/export?format=csv"
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0].strip()
                csv_url += "&gid=" + gid
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resposta = requests.get(csv_url, headers=headers, timeout=15)
        
        if resposta.status_code != 200:
            return None
            
        # === BLOCO DE SINCRONIZAÇÃO DO HORÁRIO DE BRASÍLIA FIXO ===
        import zoneinfo
        fuso_sp = zoneinfo.ZoneInfo("America/Sao_Paulo")
        st.session_state['data_da_rota'] = datetime.now(fuso_sp).strftime('%d/%m/%Y às %H:%M:%S')

        conteudo_bruto = resposta.text
        if '<html' in conteudo_bruto.lower() or '<!doctype' in conteudo_bruto.lower():
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
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper): colunas_mapeadas[col] = 'Recurso'
            elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo de Atividade'
            
        df_final = df_sheets.rename(columns=colunas_mapeadas)
        st.session_state['dados_rota'] = df_final
        return df_final
    except:
        return None

# Executa a carga inteligente
df_planilha = buscar_base_rotas_online()

# --- EXIBIÇÃO DA DATA DE ATUALIZAÇÃO SINCADA ---
data_rota_texto = st.session_state.get('data_da_rota', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
st.markdown(f'<div style="text-align: center; color: #555; font-size: 13px; font-weight: bold; margin-bottom: 20px;">🔄 Base sincronizada em: <span style="color: #008080;">{data_rota_texto}</span></div>', unsafe_allow_html=True)

if df_planilha is not None:
    df = df_planilha.copy()
    
    # Padronização de strings para filtragem precisa
    df['Supervisor_Upper'] = df['SUPERVISOR'].fillna('N/A').astype(str).str.upper().str.strip()
    df['Recurso_Upper'] = df['Recurso'].fillna('N/A').astype(str).str.upper().str.strip()
    df['Contrato_Limpo'] = df['Contrato'].fillna('').astype(str).str.strip()
    
    if 'Status da Atividade' in df.columns:
        df['Status_Atividade_Upper'] = df['Status da Atividade'].fillna('').astype(str).str.upper().str.strip()
    else:
        df['Status_Atividade_Upper'] = ''
        
    # 🌟🌟🌟 MAPEAMENTO DOS FILTROS OPERACIONAIS DE LIMPEZA PESADA 🌟🌟🌟
    cond_contrato_valido = (
        (df['Contrato_Limpo'] != '') & 
        (df['Contrato_Limpo'] != 'nan') & 
        (~df['Supervisor_Upper'].isin(['#N/A', 'N/A', '', 'NAN'])) & # Descarta Supervisor #N/A ou vazio
        (df['SUPERVISOR'].notna()) &
        (df['Status_Atividade_Upper'] != "SUSPENSO") & # Descarta registros suspensos
        (~df['Recurso_Upper'].str.contains('TEC1|TEC 1', na=False)) # Expulsa "TEC1" e "TEC 1 PENDENTE"
    )
    
    # Remove as marcações operacionais de almoço (Refeicao)
    if 'Tipo de Atividade' in df.columns:
        cond_contrato_valido = cond_contrato_valido & (~df['Tipo de Atividade'].fillna('').astype(str).str.contains('Refeicao', case=False, na=False))
        
    df_limpo = df[cond_contrato_valido].copy()
    
    # Tratamento e montagem do filtro dinâmico de Janelas Válidas
    col_janela = 'Janela de Serviço'
    if col_janela in df_limpo.columns:
        df_limpo['Intervalo_Tratado'] = df_limpo[col_janela].fillna('').astype(str).str.strip()
        
        # Ignora textos corrompidos ou informativos de sistema da lista
        df_janelas_validas = df_limpo[
            (df_limpo['Intervalo_Tratado'] != '') & 
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('SEM JANELA')) &
            (~df_limpo['Intervalo_Tratado'].str.upper().str.contains('PADRAO'))
        ]
        
        opcoes_janela = sorted(df_janelas_validas['Intervalo_Tratado'].unique())
        
        if opcoes_janela:
            janela_sel = st.sidebar.selectbox("Janela de Serviço:", opcoes_janela)
            df_tela = df_limpo[df_limpo['Intervalo_Tratado'] == JANELA_SEL] if 'JANELA_SEL' in locals() else df_limpo[df_limpo['Intervalo_Tratado'] == opcoes_janela[0]]
        else:
            df_tela = df_limpo.copy()
            janela_sel = "N/A"
    else:
        df_tela = df_limpo.copy()
        janela_sel = "N/A"

    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns:
        for idx, Server_linha in df_tela.iterrows():
            nome_super = str(Server_linha[col_supervisor]).upper()
            if "FRANCISCO" in nome_super or "ALAN" in nome_super:
                df_sp_lista.append(Server_linha)
            else:
                df_abc_lista.append(Server_linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(), pd.DataFrame()

    col_coluna_abc, col_coluna_sp = st.columns(2)
    
    with col_coluna_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        
        if not df_abc.empty and col_supervisor in df_abc.columns:
            supervisores_abc = df_abc[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_abc):
                df_super = df_abc[df_abc[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'PENDENTE']) if 'Status da Atividade' in df_super.columns else 0
                em_rota = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'EM ROTA']) if 'Status da Atividade' in df_super.columns else 0
                iniciados = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'INICIADO']) if 'Status da Atividade' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo no ABC nesta janela.")

    with col_coluna_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        
        if not df_sp.empty and col_supervisor in df_sp.columns:
            supervisores_sp = df_sp[col_supervisor].dropna().unique()
            for supervisor in sorted(supervisores_sp):
                df_super = df_sp[df_sp[col_supervisor] == supervisor]
                
                pendentes = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'PENDENTE']) if 'Status da Atividade' in df_super.columns else 0
                em_rota = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'EM ROTA']) if 'Status da Atividade' in df_super.columns else 0
                iniciados = len(df_super[df_super['Status da Atividade'].fillna('').astype(str).str.upper() == 'INICIADO']) if 'Status da Atividade' in df_super.columns else 0
                total = len(df_super)
                
                with st.container(border=True):
                    st.markdown('<div style="font-size:20px; font-weight:bold; margin-bottom:10px;">' + str(supervisor).upper() + ' <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(total) + '</span></div>', unsafe_allow_html=True)
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown('<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(pendentes) + '</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.metric(label="🟣 EM ROTA", value=em_rota)
                    with m3:
                        st.metric(label="🟢 INICIADO", value=iniciados)
        else:
            st.info("Nenhum supervisor ativo em SP nesta janela.")

    # MODO TV AUTOMÁTICO SINCADO COM A NOVA NUMERAÇÃO DE PÁGINAS
    st.components.v1.html("""
        <script>
        setTimeout(function(){
            window.parent.location.hash = "#3-tec1-pendentes";
        }, 30000);
        </script>
    """, height=0)
else:
    st.error("⚠️ Planilha online indisponível ou fora do ar.")
