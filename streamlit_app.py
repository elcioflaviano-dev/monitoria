import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# 1. Configuração inicial obrigatória da página principal
st.set_page_config(
    page_title="Monitoria TEC1",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injeta os estilos globais se o arquivo existir
try:
    with open("style.css", "r") as f:
        st.markdown("<style>" + str(f.read()) + "</style>", unsafe_allow_html=True)
except:
    pass

st.markdown('<h1 style="font-size: 38px; font-weight: 900; color: #008080; text-align: center; margin-top: 25px; margin-bottom: 5px;">📊 MONITORIA OPERACIONAL</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666; font-size: 15px;">Use o menu lateral esquerdo para navegar pelos painéis e relatórios.</p>', unsafe_allow_html=True)

# === FUNÇÃO QUE FORÇA A CARGA E ATUALIZA AS OUTRAS PÁGINAS ===
def forcar_atualizacao_total():
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

        # Sincroniza fuso horário
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

        conteudo_bruto = resposta.text
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

        if df_sheets is not None and not df_sheets.empty:
            df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
            colunas_mapeadas = {}
            for col in df_sheets.columns:
                col_upper = col.upper()
                if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
                elif 'JANELA' in col_upper or 'INTERVALO' in col_upper or 'TEMPO' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
                elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
                elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
                elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'Recurso'
                elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo de Atividade'
                
            df_final = df_sheets.rename(columns=colunas_mapeadas)
            
            # Atualiza a memória global que as outras páginas usam
            st.session_state['dados_rota'] = df_final
            return df_final
    except:
        return None

# 🚨 SEMPRE EXECUTA AO CLICAR NA PÁGINA PARA GARANTIR ATUALIZAÇÃO DOS DADOS
forcar_atualizacao_total()

st.markdown("---")
data_atual = st.session_state.get('data_da_rota', 'Não sincronizado')
st.success(f"🔄 Dados atualizados com sucesso! Última carga: {data_atual}")
st.info("👈 Agora você pode abrir as páginas TEC1 ou TEC1 PENDENTES no menu lateral com os dados novos.")
