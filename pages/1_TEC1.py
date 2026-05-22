import streamlit as st
import pandas as pd
from urllib.parse import unquote

# 1. Configuração da página - Essencial para renderizar a interface antes dos dados
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# 2. Carregar CSS de forma segura
try:
    with open('style.css', 'r') as f:
        st.markdown('<style>' + str(f.read()) + '</style>', unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 42px; font-weight: 900; color: #006677; text-align: center; margin-top: 25px; margin-bottom: 20px;">TEC1</h1>', unsafe_allow_html=True)

# === MÓDULO DE CARGA INTELIGENTE (RESOLVE O ERRO 0) ===
def carregar_dados_sheets():
    try:
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

        # SOLUÇÃO DO ERRO 0: header=None impede o Pandas de quebrar se a linha 1 for inválida/mesclada
        df_bruto = pd.read_csv(csv_url, header=None, dtype=str)
        
        if df_bruto.empty:
            return None
            
        # Procura em qual linha da planilha estão os cabeçalhos reais (Varre as primeiras 15 linhas)
        linha_cabecalho_real = 0
        for idx, linha in df_bruto.head(15).iterrows():
            linha_texto = " ".join(linha.dropna().astype(str)).upper()
            if 'SUPERVISOR' in linha_texto or 'STATUS' in linha_texto or 'JANELA' in linha_texto:
                linha_cabecalho_real = idx
                break
                
        # Reconstrói o DataFrame usando a linha correta encontrada como cabeçalho
        colunas = df_bruto.iloc[linha_cabecalho_real].astype(str).str.strip().str.replace('\xa0', ' ').tolist()
        df_dados = df_bruto.iloc[linha_cabecalho_real + 1:].copy()
        df_dados.columns = colunas
        
        # Mapeamento de colunas flexível (Maiúsculas/Minúsculas)
        colunas_mapeadas = {}
        for col in df_dados.columns:
            col_upper = str(col).upper()
            if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
            elif 'JANELA' in col_upper: colunas_mapeadas[col] = 'JANELA_SERVICO'
            elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'STATUS_ATIVIDADE'
            elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'CONTRATO'
            elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'RECURSO'
            
        df = df_dados.rename(columns=colunas_mapeadas)
        
        # Garante a existência das colunas operacionais básicas
        for col_obrigatoria in ['SUPERVISOR', 'JANELA_SERVICO', 'STATUS_ATIVIDADE']:
            if col_obrigatoria not in df.columns:
                df[col_obrigatoria] = 'N/A'
            else:
                df[col_obrigatoria] = df[col_obrigatoria].fillna('N/A')
                
        df['STATUS_ATIVIDADE'] = df['STATUS_ATIVIDADE'].apply(lambda x: str(x).strip().upper())
        return df
    except Exception as e:
        st.error('Aviso na leitura da Planilha: ' + str(e))
        return None

# Executa a carga dos dados
df = carregar_dados_sheets()

# === CRIAÇÃO DOS MENUS (SEMPRE VISÍVEIS) ===
st.sidebar.markdown('### Filtros Operacionais')

if df is not None and not df.empty:
    col_janela = 'JANELA_SERVICO'
    janela_selecionada = unquote(st.query_params.get('janela', ''))

    if col_janela in df.columns:
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
        if janela_sel == 'Padrão / Sem Janela':
            df_tela = df.copy()
        else:
            df_tela = df[df[col_janela] == janela_sel]
    else:
        df_tela = df.copy()

    # --- SEPARAÇÃO ABC / SP ---
    col_supervisor = 'SUPERVISOR'
    df_abc_lista, df_sp_lista = [], []
    
    if col_supervisor in df_tela.columns and not df_tela.empty:
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
else:
    st.sidebar.info("Aguardando conexão válida com os dados.")
    st.warning("⚠️ O Painel está ativo, mas a aba lida do Google Sheets parece não conter cabeçalhos estruturados como 'SUPERVISOR' ou 'STATUS'.")
