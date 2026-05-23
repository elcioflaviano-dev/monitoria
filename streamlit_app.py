import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# Configuração da página para modo amplo (ocupa a tela toda da TV/Monitor)
st.set_page_config(page_title="Painel de Supervisão", layout="wide")

st.title("📊 Painel Operacional de Rotas - ABC & SP")
st.write("---")
st.markdown("### Bem-vindo! Use o menu lateral para acessar os painéis.")

# Função de carga compatível com o ecossistema CSV do projeto
def carregar_dados_csv_compativel():
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

        # Sincroniza fuso horário de Brasília
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
            
            # Realiza o mapeamento exato de colunas exigido por 1_TEC1 e 2_TEC1_PENDENTES
            colunas_mapeadas = {}
            for col in df_sheets.columns:
                col_upper = col.upper()
                if 'SUPERVISOR' in col_upper: colunas_mapeadas[col] = 'SUPERVISOR'
                elif 'JANELA' in col_upper or 'INTERVALO' in col_upper or 'TEMPO' in col_upper: colunas_mapeadas[col] = 'Janela de Serviço'
                elif 'STATUS' in col_upper: colunas_mapeadas[col] = 'Status da Atividade'
                elif 'CONTRATO' in col_upper: colunas_mapeadas[col] = 'Contrato'
                elif 'RECURSO' in col_upper: colunas_mapeadas[col] = 'Recurso'
                elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): colunas_mapeadas[col] = 'Tipo de Atividade'
                
            # 🔥 CORREÇÃO CRÍTICA: Aplica e consolida a renomeação diretamente no DataFrame retornado
            df_renomeado = df_sheets.rename(columns=colunas_mapeadas)
            return df_renomeado
    except:
        return None

try:
    # Sempre força uma carga fresca ao clicar nesta página
    df_atualizado = carregar_dados_csv_compativel()
    
    if df_atualizado is not None and not df_atualizado.empty:
        # 🔥 Salva o arquivo já com a coluna 'Status da Atividade' batizada na memória global
        st.session_state['dados_rota'] = df_atualizado
        st.success("✅ Conexão estabelecida! Dados da planilha 'rota' atualizados.")
        
        # Mostra a métrica de linhas com base no dado injetado
        total_linhas = len(st.session_state['dados_rota'])
        st.metric(label="Total de Atividades na Base", value=f"{total_linhas} registros")
        
        data_sinc = st.session_state.get('data_da_rota', 'Agora')
        st.caption(f"Última atualização: {data_sinc}")
    else:
        raise Exception("A base retornou dados vazios ou formato inválido.")

except Exception as e:
    st.error("❌ Erro ao conectar com o Google Sheets. Verifique o link e se as permissões de compartilhamento estão públicas.")
    st.code(e)
