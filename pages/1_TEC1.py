import streamlit as st
import pandas as pd
import requests
import io
from urllib.parse import unquote

# 1. Configuração da página - Mantém expandido para monitorar os filtros
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# 2. Carregar CSS externo
try:
    with open('style.css', 'r') as f:
        st.markdown('<style>' + str(f.read()) + '</style>', unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA OPERACIONAL ULTRA ESTÁVEL ===
def carregar_dados_sheets():
    try:
        url = st.secrets['public_gsheets_url']
        
        # Reconstrói a URL para forçar o formato de exportação de dados brutos CSV
        if 'spreadsheets/d/' in url:
            id_planilha = url.split('/spreadsheets/d/')[1].split('/')[0]
            csv_url = 'https://docs.google.com/spreadsheets/d/' + id_planilha + '/export?format=csv'
            if 'gid=' in url:
                gid = url.split('gid=')[1].split('#')[0].split('&')[0]
                csv_url += '&gid=' + gid
            else:
                csv_url += '&gid=208394608'
        else:
            csv_url = url

        # Busca os dados em modo texto
        resposta = requests.get(csv_url, timeout=15)
        if resposta.status_code != 200:
            st.error('⚠️ Falha de comunicação com o servidor do Google Sheets.')
            return None
            
        conteudo = resposta.text
        if '<html' in conteudo.lower() or '<!doctype' in conteudo.lower():
            st.error('🔒 Erro de Acesso: O link do Google Sheets está configurado como privado.')
            return None

        # Carrega a tabela de forma direta
        df_sheets = pd.read_csv(io.StringIO(conteudo), dtype=str)
        if df_sheets.empty:
            st.warning('⚠️ A planilha do Google Sheets não contém nenhuma linha de dados.')
            return None
            
        # Limpa espaços ocultos e formata cabeçalhos para texto limpo
        df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
        
        # Mapeamento dinâmico tolerante a maiúsculas/minúsculas
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'JANELA_SERVICO'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'CONTRATO'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'RECURSO'
            
        df = df_sheets.rename(columns=colunas_mapeadas)
        
        # Cria e popula colunas caso não existam, garantindo que o app nunca fique em branco
        if 'SUPERVISOR' not in df.columns:
            df['SUPERVISOR'] = 'N/A'
        if 'JANELA_SERVICO' not in df.columns:
            df['JANELA_SERVICO'] = 'Padrão / Sem Janela'
        if 'STATUS_ATIVIDADE' not in df.columns:
            df['STATUS_ATIVIDADE'] = 'PENDENTE'
            
        # CORREÇÃO DEFINITIVA: Formatação via apply garante que trate elemento por elemento sem bugar o DataFrame
        df['SUPERVISOR'] = df['SUPERVISOR'].fillna('N/A').apply(lambda x: str(x).strip())
        df['JANELA_SERVICO'] = df['JANELA_SERVICO'].fillna('Padrão / Sem Janela').apply(lambda x: str(x).strip())
        df['STATUS_ATIVIDADE'] = df['STATUS_ATIVIDADE'].fillna('PENDENTE').apply(lambda x: str(x).strip().upper())
        
        return df
    except Exception as e:
        st.error('Erro na extração: ' + str(e))
        return None

df = carregar_dados_sheets()

if df is not None:
    # --- FILTRO INTEGRAL DA JANELA ---
    col_janela = 'JANELA_SERVICO'
    janela_selecionada = unquote(st.query_params.get('janela', ''))

    opcoes_janela = sorted(df[col_janela].unique())
    if not opcoes_janela:
        opcoes_janela = ['Padrão / Sem Janela']
        
    default_index = 0
    if janela_selecionada in opcoes_janela:
        default_index = opcoes_janela.index(janela_selecionada)
    
    st.sidebar.markdown('### Filtros Operacionais')
    janela_sel = st.sidebar.selectbox(
        'Janela de Serviço Ativa:', 
        opcoes_janela, 
        index=default_index,
        key='sb_janela'
    )
    
    st.query_params['janela'] = janela_sel
    df_tela = df[df[col_janela] == janela_sel]

    # --- LÓGICA DE SUPERVISORES (ABC | SP) ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if not df_tela.empty:
        for idx, linha in df_tela.iterrows():
            nome_super = str(linha[col_supervisor]).upper()
            if 'FRANCISCO' in nome_super or 'ALAN' in nome_super: 
                df_sp_lista.append(linha)
            else: 
                df_abc_lista.append(linha)
                
        df_abc = pd.DataFrame(df_abc_lista) if df_abc_lista else pd.DataFrame(columns=df_tela.columns)
        df_sp = pd.DataFrame(df_sp_lista) if df_sp_lista else pd.DataFrame(columns=df_tela.columns)
    else:
        df_abc, df_sp = pd.DataFrame(columns=df.columns), pd.DataFrame(columns=df.columns)

    # --- RENDERIZAÇÃO DE COLUNAS NA TELA ---
    c_abc, c_sp = st.columns(2)
    
    with c_abc:
        st.markdown('<div class="title-abc-sp">ABC</div>', unsafe_allow_html=True)
        if not df_abc.empty:
            for supervisor in sorted(df_abc[col_supervisor].dropna().unique()):
                if str(supervisor).upper() != 'N/A' and str(supervisor).strip() != '':
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
        else:
            st.info('Nenhum dado ativo no ABC para a janela selecionada.')

    with c_sp:
        st.markdown('<div class="title-abc-sp">SP</div>', unsafe_allow_html=True)
        if not df_sp.empty:
            for supervisor in sorted(df_sp[col_supervisor].dropna().unique()):
                if str(supervisor).upper() != 'N/A' and str(supervisor).strip() != '':
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
        else:
            st.info('Nenhum dado ativo em SP para a janela selecionada.')
