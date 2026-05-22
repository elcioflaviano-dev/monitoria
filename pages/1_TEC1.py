import streamlit as st
import pandas as pd
from urllib.parse import unquote

# 1. Configuração obrigatória da página (Garante que a barra lateral exista sempre)
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# 2. Carregar CSS externo de forma segura
try:
    with open('style.css', 'r') as f:
        st.markdown('<style>' + str(f.read()) + '</style>', unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA BLINDADO CONTRA KEYERROR 0 ===
def carregar_dados_sheets():
    try:
        if 'public_gsheets_url' not in st.secrets:
            st.error("❌ A chave 'public_gsheets_url' não foi encontrada no Streamlit Secrets.")
            return None
            
        url = st.secrets['public_gsheets_url']
        
        # Reconstrói para formato oficial de exportação de CSV do Google
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0]
            csv_url = 'https://docs.google.com/spreadsheets/d/' + id_planilha + '/export?format=csv'
            
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0]
                csv_url += '&gid=' + gid
        else:
            csv_url = url

        # Tenta ler de forma direta e segura
        try:
            df_sheets = pd.read_csv(csv_url, dtype=str)
        except Exception as err_pandas:
            # Se der erro 0 ou token inválido, avisa mas não deixa o app morrer
            st.warning(f"⚠️ O link retornou uma estrutura ilegível para o Pandas: {str(err_pandas)}")
            return None
        
        if df_sheets is None or df_sheets.empty:
            return None
            
        # Limpeza de cabeçalhos
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'JANELA_SERVICO'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'CONTRATO'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'RECURSO'
            
        df = df_sheets.rename(columns=colunas_mapeadas)
        
        for col_obrigatoria in ['SUPERVISOR', 'JANELA_SERVICO', 'STATUS_ATIVIDADE']:
            if col_obrigatoria not in df.columns:
                df[col_obrigatoria] = 'N/A'
            else:
                df[col_obrigatoria] = df[col_obrigatoria].fillna('N/A')
                
        df['STATUS_ATIVIDADE'] = df['STATUS_ATIVIDADE'].apply(lambda x: str(x).strip().upper())
        return df
        
    except Exception as e:
        st.error('Erro geral no processador de dados: ' + str(e))
        return None

# Executa a carga
df = carregar_dados_sheets()

# SE O DF FALHAR (ERRO 0), RECORREMOS A UM MOCK TEMPORÁRIO PARA AJUSTAR O LINK
if df is None or df.empty:
    st.info("ℹ️ Exibindo dados de simulação temporários para que possa ajustar o link no Secrets.")
    # Cria uma tabela fictícia padrão apenas para manter o painel vivo e bonito
    df = pd.DataFrame({
        'SUPERVISOR': ['Aguardando Link Correto', 'Aguardando Link Correto'],
        'JANELA_SERVICO': ['Padrão / Sem Janela', 'Padrão / Sem Janela'],
        'STATUS_ATIVIDADE': ['PENDENTE', 'INICIADO']
    })

# === CRIAÇÃO DA INTERFACE OPERACIONAL (SEMPRE VISÍVEL) ===
st.sidebar.markdown('### Filtros Operacionais')

col_janela = 'JANELA_SERVICO'
janela_selecionada = unquote(st.query_params.get('janela', ''))

opcoes_janela = sorted(df[col_janela].dropna().astype(str).unique())
if not opcoes_janela or opcoes_janela == ['N/A']:
    opcoes_janela = ['Padrão / Sem Janela']
    
default_index = 0
if janela_selecionada in opcoes_janela:
    default_index = opcoes_janela.index(janela_selecionada)

janela_sel = st.sidebar.selectbox(
    'Janela de Serviço Ativa:', 
    opcoes_janela, 
    index=default_index,
    key='sb_janela'
)

st.query_params['janela'] = janela_sel
df_tela = df[df[col_janela] == janela_sel]

# --- SEPARAÇÃO ABC / SP ---
col_supervisor = 'SUPERVISOR'
df_abc_lista, df_sp_lista = [], []

if not df_tela.empty:
    for idx, Server_linha in df_tela.iterrows():
        nome_super = str(Server_linha[col_supervisor]).upper()
        if 'FRANCISCO' in nome_super or 'ALAN' in nome_super: 
            df_sp_lista.append(Server_linha)
        else: 
            df_abc_lista.append(Server_linha)
            
    df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
    df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
else:
    df_abc, df_sp = pd.DataFrame(columns=df.columns), pd.DataFrame(columns=df.columns)

# --- CARDS VISUAIS ---
c_abc, c_sp = st.columns(2)
with c_abc:
    st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
    if not df_abc.empty:
        for supervisor in sorted(df_abc[col_supervisor].dropna().unique()):
            df_super = df_abc[df_abc[col_supervisor] == supervisor]
            p = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE'])
            r = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA'])
            i = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO'])
            t = len(df_super)
            
            with st.container(border=True):
                header_texto = '#### **' + str(supervisor).upper() + '** <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(t) + '</span>'
                st.markdown(header_texto, unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                with m1: 
                    html_box = '<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(p) + '</div></div>'
                    st.markdown(html_box, unsafe_allow_html=True)
                with m2: st.metric(label='🟣 EM ROTA', value=r)
                with m3: st.metric(label='🟢 INICIADO', value=i)

with c_sp:
    st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
    if not df_sp.empty:
        for supervisor in sorted(df_sp[col_supervisor].dropna().unique()):
            df_super = df_sp[df_sp[col_supervisor] == supervisor]
            p = len(df_super[df_super['STATUS_ATIVIDADE'] == 'PENDENTE'])
            r = len(df_super[df_super['STATUS_ATIVIDADE'] == 'EM ROTA'])
            i = len(df_super[df_super['STATUS_ATIVIDADE'] == 'INICIADO'])
            t = len(df_super)
            
            with st.container(border=True):
                header_texto = '#### **' + str(supervisor).upper() + '** <span style="float:right; font-size:14px; background-color:#e1f5fe; padding:2px 8px; border-radius:4px; color:#0288d1;">Total: ' + str(t) + '</span>'
                st.markdown(header_texto, unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                with m1: 
                    html_box = '<div class="custom-pendente-box"><div class="custom-pendente-label">🔴 PENDENTES</div><div class="custom-pendente-value">' + str(p) + '</div></div>'
                    st.markdown(html_box, unsafe_allow_html=True)
                with m2: st.metric(label='🟣 EM ROTA', value=r)
                with m3: st.metric(label='🟢 INICIADO', value=i)
