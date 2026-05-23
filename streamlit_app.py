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
            # Força a limpeza total de nomes de colunas espelhados do Sheets
            df_sheets.columns = [str(c).strip().replace('\xa0', ' ') for c in df_sheets.columns]
            
            # Criamos um clone para mapear com segurança absoluta
            df_final = df_sheets.copy()
            
            # Mapeamento dinâmico super agressivo por correspondência de termos
            for col in df_sheets.columns:
                col_upper = col.upper()
                if 'SUPERVISOR' in col_upper: 
                    df_final['SUPERVISOR'] = df_sheets[col]
                elif 'JANELA' in col_upper or 'INTERVALO' in col_upper or 'TEMPO' in col_upper: 
                    df_final['Janela de Serviço'] = df_sheets[col]
                elif 'STATUS' in col_upper: 
                    # 🚨 BLINDAGEM MÁXIMA: Força a criação exata das duas variações possíveis de nome
                    df_final['Status da Atividade'] = df_sheets[col]
                    df_final['Status'] = df_sheets[col]
                elif 'CONTRATO' in col_upper: 
                    df_final['Contrato'] = df_sheets[col]
                elif 'RECURSO' in col_upper: 
                    df_final['Recurso'] = df_sheets[col]
                elif ('TIPO DE ATIVIDADE' in col_upper or 'TIPO ATIVIDADE' in col_upper): 
                    df_final['Tipo de Atividade'] = df_sheets[col]
            
            # Remove duplicações de colunas geradas pelo mapeamento se sobrarem
            df_final = df_final.loc[:, ~df_final.columns.duplicated()]
            return df_final
    except:
        return None

try:
    # Sempre força uma carga fresca ao clicar nesta página
    df_atualizado = carregar_dados_csv_compativel()
    
    if df_atualizado is not None and not df_atualizado.empty:
        # Salva o arquivo com garantia de colunas corretas para 1_TEC1 e 2_TEC1_PENDENTES
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
