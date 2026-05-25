import streamlit as st
import pandas as pd
import requests
import io
import os
from datetime import datetime

# 1. Configuração da página
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# 2. Carregar Estilos Globais
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📜 SISTEMA DE CERTIDÃO</h1>', unsafe_allow_html=True)

# === BANCO DE DADOS LOCAL (ARQUIVO PERMANENTE DE REGISTROS) ===
ARQUIVO_BANCO = "banco_certidoes.csv"

def carregar_banco_historico():
    colunas_padrao = ["Data/Hora", "Contrato", "Status", "Supervisor", "Recurso", "Intervalo de Tempo", "Observação"]
    if os.path.exists(ARQUIVO_BANCO):
        try:
            df_hist = pd.read_csv(ARQUIVO_BANCO, dtype=str)
            df_hist = df_hist[[c for c in df_hist.columns if c in colunas_padrao]]
            for col in colunas_padrao:
                if col not in df_hist.columns:
                    df_hist[col] = "N/A"
            return df_hist
        except:
            return pd.DataFrame(columns=colunas_padrao)
    return pd.DataFrame(columns=colunas_padrao)

# === FUNÇÃO DE CARGA OPERACIONAL ONLINE ===
def buscar_base_rotas_online():
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
        linhas_puras = conteudo_bruto.splitlines()
        
        linha_do_cabecalho_real = 0
        encontrou_cabecalho = False
        for i, texto_linha in enumerate(linhas_puras[:30]):
            linha_upper = texto_linha.upper()
            if 'SUPERVISOR' in linha_upper or 'CONTRATO' in linha_upper or 'INTERVALO' in linha_upper or 'STATUS' in linha_upper:
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
        df_final = df_sheets.copy()
        
        colunas_mapeadas = {}
        for col in df_sheets.columns:
            col_upper = col.upper()
            if 'SUPERVISOR' in col_upper and 'SUPERVISOR' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'SUPERVISOR'
            elif ('INTERVALO' in col_upper or 'TEMPO' in col_upper) and 'Intervalo de Tempo' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Intervalo de Tempo'
            elif 'STATUS DA ATIVIDADE' in col_upper or ('STATUS' in col_upper and 'ATIVIDADE' in col_upper) and 'Status da Atividade' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Status da Atividade'
            elif ('STATUS DA O.S 1' in col_upper or 'O.S 1' in col_upper or 'OS 1' in col_upper) and 'Status da O.S 1' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Status da O.S 1'
            elif 'CONTRATO' in col_upper and 'Contrato' not in colunas_mapeadas.values(): 
                colunas_mapeadas[col] = 'Contrato'
            elif ('RECURSO' in col_upper or 'TECNICO' in col_upper or 'TÉCNICO' in col_upper) and 'Recurso' not in colunas_mapeadas.values
